from flask import Flask, render_template, redirect, request, flash, jsonify, Response, url_for, session, abort
import functools
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import config, bclient, khistory, btrader, chart_actions, btmanager, log_handler
import backtest
from pprint import pprint
from typing import Optional
import asyncio

bconnection = False
myClient: bclient.MyClient
my_btmanager: btmanager.BTManager
try:
    myClient = bclient.MyClient(config.Binance_Config())
    my_btmanager = btmanager.BTManager(myClient=myClient)
    bconnection = True
except Exception as e:
    print(e)

users = config.Login_Info().USERS   


trade_strats = config.Strategies.B_STRATS
all_intervals = config.Strategies.ALL_INTERVALS


#flask app 
app = Flask(__name__)   ###app = Flask(__name__, template_folder='template') #fix for not being able to find templates folder
app.secret_key = config.Flask_Config.SECRET_KEY


title = "Binance Trader"

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("registered_username") is None:
            flash("You are not logged in", "upper1")
            return redirect(url_for("login"))
            #abort(401)

        return route(*args, **kwargs)

    return route_wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("registered_username") is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users.keys() and password is not None:
            if pbkdf2_sha256.verify(password, users.get(username).get('password')):
                session["registered_username"] = username
                return redirect(url_for("index"))
            else:
                flash("Login information is not valid.", "upper1")
                return redirect(url_for("login"))
        else:
            flash("Login information is not valid.", "upper1")
            return redirect(url_for("login"))
            #abort(401)
    return render_template("login.html.j2",
                           title = title,
                           )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    flash("New account registration is currently disabled. Contact the developer for more information.", "upper1")
    return redirect(url_for("login"))
    ########################
    if request.method == "POST":
        
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if (username is None) or (email is None) or (password is None):
            flash("Values are not valid.", "upper1")
            return redirect(url_for("signup"))
        #(NOT FINAL)

        #Save new users to a database
        users[username] = {
            'email': email,
            'password': pbkdf2_sha256.hash(password)
        }
        # session["email"] = email
        # - Setting the session here would be okay if you
        # - want users to be logged in immediately after
        # - signing up.
        flash("Successfully signed up.", "upper1")
        return redirect(url_for("login"))
    return render_template("signup.html.j2",
                           title = title,
                           )
    

@app.route("/signout")
@login_required
def signout():
    session["registered_username"] = None
    flash("Successfully signed out.", "upper1")
    return redirect(url_for("login"))


@app.errorhandler(401)
def auth_error(error):
    return "Not authorized"


@app.route("/")
@login_required
def index():

    if bconnection is False:
        flash(f"Connection Error: {log_handler.myLogHandler.get_bclient_logs()[-1]}", "upper1")

    
    print("index")

    #display 1
    if "display1_trade_symbol" not in session:
        session["display1_trade_symbol"] = str(config.Trade_Info.DEFAULT_SYMBOL)
    if "display1_trade_interval" not in session:
        session["display1_trade_interval"] = str(config.Trade_Info.DEFAULT_INTERVAL)
    if "display1_trade_strat" not in session:
        session["display1_trade_strat"] = str(config.Trade_Info.DEFAULT_STRAT)

    display1_trade_symbol = session["display1_trade_symbol"]
    display1_trade_interval = session["display1_trade_interval"]

    print(display1_trade_symbol, display1_trade_interval)

    
    #quick trade
    if bconnection:
        assert myClient is not None
        acc_info = myClient.client.get_account()
        acc_balances = acc_info["balances"]

        exc_info = myClient.client.get_exchange_info()
        exc_trade_symbols = exc_info["symbols"]
    else:
        acc_balances = []
        exc_trade_symbols = []


    #Backtest Message
    backtest_message = ""
    if "backtest_message" in session:
        backtest_message = session["backtest_message"]
        session.pop("backtest_message", None)
    
    print(backtest_message)
    
    #Get All Traders Info
    btraders_info = []
    if bconnection:
        assert my_btmanager is not None
        btraders_info = my_btmanager.get_myTraders_info()

    
    session["btrader_id"] = "0"
    {
    #if "btrader_id" not in session:
    #    session["btrader_id"] = "-1"
    #btrader_id = int(session["btrader_id"])

    #if btrader_id != -1:
    }

    #Get All Trader Logs 
    try: 
        btrader_logs = log_handler.myLogHandler.get_btrader_logs_all_special()
    except Exception as e:
        btrader_logs = []
        print(e)
    
    # would be nice to have btraders_info reassigned here. Currently the same dictionary variable names has to be referenced in UI and backend

    return render_template("index2.html.j2", 
                           title = title, 
                           acc_balances= acc_balances, 
                           exc_trade_symbols = exc_trade_symbols, 
                           display1_trade_symbol=display1_trade_symbol,
                           display1_trade_interval = display1_trade_interval,
                           url_history = url_for("history"),
                           url_trader = url_for("trader"),
                           backtest_message = backtest_message,
                           btraders_info = btraders_info,
                           btrader_logs = btrader_logs,
                           trade_strats = trade_strats,
                           all_intervals= all_intervals,
                           binance_use_test_api = config.Binance_Config.BINANCE_USE_TEST_API,
                           registered_username=session.get("registered_username"),
                           )


@app.route("/quicktrade/", methods = ["POST"])
@login_required
def quicktrade():
    print(request.form)

    assert myClient is not None
    if bconnection is False:
        return redirect("/")

    #Quick Trade
    if request.form['trade_action'] == "buy":
        t_action = "BUY"
        qt_action_message = "Bought"
    elif request.form['trade_action'] == "sell":
        t_action = "SELL"
        qt_action_message = "Sold"
    else:
        flash("Quick Trade Failed: Invalid trade action", "qt_error")
        return redirect("/")

    q_trade_result, q_trade_msg, q_trade_avgprice = myClient.fill_order( request.form['trade_symbol'], t_action, False, float(request.form["trade_quantity"]))
    
    if q_trade_result != True:
        flash("Quick Trade Failed: " + str(q_trade_msg), "qt_error")
    else:
        summary = f"{qt_action_message} {float(request.form['trade_quantity'])} {request.form['trade_symbol']} with the average price of {q_trade_avgprice}"    
        flash(f"Quick Trade Successful, {summary}", "qt_message")
    
    return redirect("/")


@app.route("/debug/")
@login_required
def debug1():
    assert my_btmanager is not None
    my_btmanager.create_traders_from_env()
    my_btmanager.start_all_traders()

    return "debug01"


@app.route("/debug2/")
@login_required
def debug2():
    asd = log_handler.myLogHandler.get_error_logs()
    pprint(asd)
    return jsonify(asd)


@app.route("/debug3/")
@login_required
def debug3():
    
    #ti = my_btmanager.create_trader("BTCUSDT", "5m", 0.00003, config.Trade_Info.DEFAULT_STRAT)
    #my_btmanager.start_trader(ti)

    #my_btmanager.start_all_traders()
    #my_btmanager.start_trader(1)
    return "debug03"


@app.route("/debug4/")
@login_required
def debug4():
    
    asd = log_handler.myLogHandler.get_bclient_logs()
    pprint(asd)
    return jsonify(asd)


@app.route("/debug5/")
@login_required
def debug5():
    
    asd = log_handler.myLogHandler.get_btrader_logs_all_special()
    pprint(asd)
    return jsonify(asd)


@app.route("/trader")
@login_required
def trader():

    assert my_btmanager is not None
    if bconnection is False:
        return redirect(url_for("index"))
    
    btrader_id = request.args.get("btrader_id", default="-1", type=str)

    if int(btrader_id) < 0:
        btrader_id = session["btrader_id"]

    if int(btrader_id) < 0:
        return redirect(url_for("index")) 
    
    if btrader_id not in my_btmanager.get_myTraders_info():
        return redirect(url_for("index"))
    
    session["btrader_id"] = btrader_id
    
    myTrader_info = my_btmanager.get_myTraders_info()[btrader_id]

    display1_trade_symbol = myTrader_info["TRADE_SYMBOL"]
    display1_trade_interval = myTrader_info["TRADE_INTERVAL"]
    display1_trade_strat = myTrader_info["TRADE_STRAT"]

    session["display1_trade_symbol"]    = display1_trade_symbol
    session["display1_trade_interval"]  = display1_trade_interval
    session["display1_trade_strat"]     = display1_trade_strat 

    btrader_logs_info = log_handler.myLogHandler.get_btrader_logs_info( btrader_id= int(btrader_id))
    btrader_logs_special = log_handler.myLogHandler.get_btrader_logs_special(btrader_id= int(btrader_id))

    #Backtest Message
    backtest_message = ""
    if "backtest_message" in session:
        backtest_message = session["backtest_message"]
        session.pop("backtest_message", None)
    
    print(backtest_message)

    print(btrader_logs_info)
    
    return render_template("trader.html.j2", 
                           title = title, 
                           display1_trade_symbol=display1_trade_symbol,
                           display1_trade_interval = display1_trade_interval,
                           display1_trade_strat = display1_trade_strat,
                           url_history = url_for("history"),
                           url_trader = url_for("trader"),
                           url_trader_toggle_run = url_for("trader_toggle_run"),
                           backtest_message = backtest_message,
                           btrader_info = myTrader_info,
                           btrader_logs_special = btrader_logs_special,
                           btrader_logs_info = btrader_logs_info,
                           binance_use_test_api = config.Binance_Config.BINANCE_USE_TEST_API,
                           registered_username=session.get("registered_username"),
                           )


@app.route("/create_new_trader/", methods = ["POST"])
@login_required
def create_new_trader():

    all_trade_symbols = []

    assert myClient is not None
    assert my_btmanager is not None
    if bconnection:
        exc_info = myClient.client.get_exchange_info()
        exc_trade_symbols = exc_info["symbols"]
        for sym in exc_trade_symbols:
            all_trade_symbols.append(sym['symbol'])


    if "nt_trade_symbol" in request.form:
        nt_trade_symbol = request.form["nt_trade_symbol"]
        if nt_trade_symbol not in all_trade_symbols:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    
    if "nt_trade_interval" in request.form:
        nt_trade_interval = request.form["nt_trade_interval"]
        if nt_trade_interval not in all_intervals:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    
    if "nt_trade_strat" in request.form:
        nt_trade_strat = request.form["nt_trade_strat"]
        if nt_trade_strat not in trade_strats:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

    if "nt_trade_quantity" in request.form:
        nt_trade_quantity = request.form["nt_trade_quantity"]
        try:
            nt_trade_quantity = float(nt_trade_quantity)
        except:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    # Good Parameters
    nt_id = my_btmanager.create_trader(nt_trade_symbol, nt_trade_interval, nt_trade_quantity, nt_trade_strat)

    return redirect(url_for("trader", btrader_id = nt_id))


@app.route("/trader_toggle_run")
@login_required
def trader_toggle_run():
    assert myClient is not None
    assert my_btmanager is not None
    if bconnection is False:
        return redirect(url_for("index"))
    
    btrader_id = request.args.get("btrader_id", default=session["btrader_id"], type=str)
    toggle_start = "start"
    toggle_stop = "stop"
    toggle = request.args.get("toggle", default="toggle", type=str)
    
    if int(btrader_id) < 0:
        return redirect(url_for("index")) 
    
    if btrader_id not in my_btmanager.get_myTraders_info():
        return redirect(url_for("index"))
    
    myTrader_info = my_btmanager.get_myTraders_info()[btrader_id]

    if myTrader_info["Running"] is False and toggle != toggle_stop:
        my_btmanager.start_trader(int(btrader_id))
    
    elif myTrader_info["Running"] is True and toggle != toggle_start:
        my_btmanager.stop_trader(int(btrader_id))

    return redirect(request.referrer)


@app.route("/change_chart/", methods = ["POST"])
@login_required
def change_chart():
    all_trade_symbols = []

    assert myClient is not None
    if bconnection:
        exc_info = myClient.client.get_exchange_info()
        exc_trade_symbols = exc_info["symbols"]
        for sym in exc_trade_symbols:
            all_trade_symbols.append(sym['symbol'])


    if "d1_trade_symbol" in request.form:
        d1_trade_symbol = request.form["d1_trade_symbol"]
        if d1_trade_symbol not in all_trade_symbols:
            #session["backtest_message"] = "backtest Failed - Incorrect Strategy"
            return redirect(url_for("index"))
        session["display1_trade_symbol"] = d1_trade_symbol

    if "d1_trade_interval" in request.form:
        d1_trade_interval = request.form["d1_trade_interval"]
        if d1_trade_interval not in all_intervals:
            #session["backtest_message"] = "backtest Failed - Incorrect Strategy"
            return redirect(url_for("index"))
        session["display1_trade_interval"] = d1_trade_interval

    return redirect(url_for("index"))


@app.route("/history")
@login_required
def history():

    __TRADE_SYMBOL = request.args.get("TRADE_SYMBOL", default=config.Trade_Info.DEFAULT_SYMBOL, type=str)
    __TRADE_INTERVAL = request.args.get("TRADE_INTERVAL", default=config.Trade_Info.DEFAULT_INTERVAL, type=str)

    assert myClient is not None
    if bconnection:
        #candlesticks = myClient.client.get_historical_klines(config.Trade_Info.TRADE_SYMBOLS[0], config.Trade_Info.TRADE_INTERVALS[0], "15 days")
        candlesticks = myClient.client.get_klines(symbol = __TRADE_SYMBOL, interval = __TRADE_INTERVAL)
        p_klines = chart_actions.process_klineslist_to_chartdictformat(candlesticks)
        return(jsonify(p_klines))
    else:
        return jsonify({"error": "bconnection is False"})


@app.route("/bg-run-backtest/", methods = ["POST"])
@login_required
def bg_run_backtest():
    print(request.form)
    redirect_url = request.referrer
    date_start = request.form["date_start"]
    date_end = request.form["date_end"]
    if "trade_strat" in request.form:
        trade_strat = request.form["trade_strat"]
        if trade_strat not in config.Strategies.B_STRATS:
            session["backtest_message"] = "backtest Failed - Incorrect Strategy"
            return redirect(redirect_url)
        session["display1_trade_strat"] = trade_strat
    
    if date_end =="" or date_start == "":
        session["backtest_message"] = "backtest Failed - Enter Dates"
        return redirect(redirect_url)
    
    datetime_start = datetime.strptime(date_start, '%Y-%m-%d')
    datetime_end = datetime.strptime(date_end, '%Y-%m-%d')

    if datetime_end <= datetime_start:
        session["backtest_message"] = "backtest Failed - Wrong Dates"
        return redirect(redirect_url)
    
    

    #set up symbol and interval
    if "display1_trade_symbol" not in session:
        session["display1_trade_symbol"] = str(config.Trade_Info.DEFAULT_SYMBOL)
    if "display1_trade_interval" not in session:
        session["display1_trade_interval"] = str(config.Trade_Info.DEFAULT_INTERVAL)
    if "display1_trade_strat" not in session:
        session["display1_trade_strat"] = str(config.Trade_Info.DEFAULT_STRAT)

    display1_trade_symbol = session["display1_trade_symbol"]
    display1_trade_interval = session["display1_trade_interval"]
    display1_trade_strat = session["display1_trade_strat"]
    #download and save kline history as a csv file
    assert myClient is not None
    if(bconnection): 
        asyncio.run(khistory.download_khistory(myClient.client, display1_trade_symbol, display1_trade_interval, DATE_PROMPT_START= date_start, DATE_PROMPT_END= date_end)) 

    csv_name = khistory.get_csv_name(display1_trade_symbol, display1_trade_interval)
    
    backtest.myBacktester.run1(csv_name= csv_name, TRADE_INTERVAL= display1_trade_interval, strategy_str=display1_trade_strat)
    
    session["backtest_message"] = "Success"
    return redirect(redirect_url)

#debug1()