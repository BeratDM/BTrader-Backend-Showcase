import json, pprint, talib, numpy
import binance.enums as b_enums
import bclient, log_handler
import asyncio, websockets, threading
from typing import Callable
import strategy_manager as s_manager
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Callable


class bTrader():
    def __init__(self, trader_id: int, myClient: bclient.MyClient, report_position_info: Callable[[int, bool, float], None], TRADE_SYMBOL: str, TRADE_INTERVAL: str, ALLOCATED_TRADE_QUANTITY: float, strategy_str = "rsi_strategy01", ) -> None:
        self.trader_id = trader_id
        self.myClient = myClient
        self.report_position_info = report_position_info
        self.TRADE_SYMBOL = TRADE_SYMBOL
        self.TRADE_INTERVAL = TRADE_INTERVAL
        self.ALLOCATED_TRADE_QUANTITY = ALLOCATED_TRADE_QUANTITY

        self.candle_limit = 200
        self.executor1 = ThreadPoolExecutor(max_workers=1)

        self.strategy = s_manager.get_strategy_live(strategy_str, report_info= self.add_log, trade_action= self.trade_action)

        self.ws_running = False
        if myClient.BinanceConfig.BINANCE_USE_TEST_API == True:
            wss_url = "wss://testnet.binance.vision/ws"
        else:
            wss_url = "wss://stream.binance.com:9443/ws"
        self.SOCKET = "{}/{}@kline_{}".format(wss_url, TRADE_SYMBOL.lower(), TRADE_INTERVAL)
        self.init_closes()

        
        self.websocket_handler = WebSocketHandler(self.SOCKET, self.on_message, self.add_log)
        
        #self.start()
    

    def init_closes(self):
        kdata = self.myClient.client.get_klines(symbol= self.TRADE_SYMBOL, interval = self.TRADE_INTERVAL)
        kdata = kdata[-self.candle_limit:]

        self.candles = convert_to_dicts(kdata)
        
        #for candle in self.candles:
        #    self.strategy.process_candles(candles=self.candles, calculate_order=False)
        

        self.add_log(f"a bTrader instance is initiated with {len(self.candles)} starting values. Running: {self.ws_running}", level="setting")


    def add_log(self, msg: str, level = "info"):
        current_time = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        text1 = f"-{current_time} {level}  bTrader: {str(self.trader_id)}-{str(self.TRADE_SYMBOL)}-{str(self.TRADE_INTERVAL)}: {str(msg)}"
        
        log_handler.myLogHandler.add_btrader_log(btrader_id= self.trader_id, level=level, msg=text1)
        

    def get_logs_info(self) -> list:
        return log_handler.myLogHandler.get_btrader_logs_info(self.trader_id)
    

    def get_logs_special(self) -> list:
        return log_handler.myLogHandler.get_btrader_logs_special(self.trader_id)


    def start(self):
        if self.ws_running is False:
            self.websocket_handler.start()
            self.ws_running = True
            self.add_log("Started.", level="setting")


    def stop(self):
        if self.ws_running is True:
            self.websocket_handler.stop()
            self.ws_running = False
            self.add_log("Stopped.", level="setting")


    def on_message(self, message: str):
            
        self.add_log("received message")
        json_message = json.loads(message)
        
        #look-up the payload of the websocket stream on here https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md  
        candle = json_message["k"]
        is_candle_closed = candle['x']
        price_closed = candle['c']
        self.add_log(price_closed)
        #initiate logic upon new candle information.
        if is_candle_closed:
            self.add_log("candle closed at {}".format(price_closed))
            #self.closes.append(float(price_closed))
            #self.closes = self.closes[-200:] # keep the list to 200 elements
            #self.add_log("closes")
            #self.add_log(self.closes)
            #self.add_log(len(self.closes))
            self.new_candle_closed(candle)


    def new_candle_closed(self, candle):
        self.candles.append(candle)
        self.candles = self.candles[-self.candle_limit:]

        
        self.executor1.submit(self.strategy.process_candles, candles=self.candles, calculate_order=True)
        #self.strategy.process_candle(candle=candle, calculate_order=True)


    def trade_action(self, side: str, quantity = 1.0, is_asset_percentage = False) -> bool:
        
        #This is the place to calculate quantity over orders with a percentage of the total asset in the future. Not yet implemented(works with allocated quantity)
        final_quantity = float(quantity) * float(self.ALLOCATED_TRADE_QUANTITY)

        self.add_log(f"Order signal received. allowed: {self.ALLOCATED_TRADE_QUANTITY}, strategy: {quantity}, final: {final_quantity}, pair: {self.TRADE_SYMBOL}, side: {side}", "order")
        order_success, msg, avg_price = self.myClient.fill_order(trade_symbol= self.TRADE_SYMBOL, side_order= side, use_asset_percentage= is_asset_percentage, trade_quantity= final_quantity, report_str=self.add_log)
        if order_success:
            inPosition = False
            if side == "BUY":
                inPosition = True
            else:
                inPosition = False
            if self.report_position_info is not None:
                #report new info to btmanager.
                self.report_position_info(self.trader_id, inPosition, avg_price)
        return order_success
        

class WebSocketHandler:
    def __init__(self, SOCKET: str, on_message: Callable[[str], None], report_error_str: Callable[[str, str], None]) -> None:
        self.SOCKET = SOCKET
        self.on_message = on_message
        self.report_error_str = report_error_str
        self.stop_flag = False
        self.thread = None
        self.reconnection_limit = 10
        self.reconnection_count = 0

    
    def start(self):
        self.stop_flag = False
        self.thread = threading.Thread(target=self.websocket_loop)
        self.thread.start()

    
    def stop(self):
        self.stop_flag = True
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    
    def websocket_loop(self):
        try:
            self.report_error_str("Starting Websocket", "info")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            conn = websockets.connect(uri = self.SOCKET) # type: ignore

            async def inner_websocket_loop():
                while not self.stop_flag:
                    try:
                        async with conn as ws:
                            self.report_error_str(f"Websocket connection started.", "local setting")
                            while not self.stop_flag:
                                try:
                                    message = await ws.recv()
                                except Exception as e:
                                    if str(e) == "received 1001 (going away); then sent 1001 (going away)" or str(e) == "no close frame received or sent":
                                        self.report_error_str(f"Connection error occurred in Websocket: {e}", "local error")
                                    else:
                                        self.report_error_str(f"Connection error occurred in Websocket: {e}", "error")
                                    break
                                
                                try:
                                    self.on_message(message)
                                except Exception as e:
                                    self.report_error_str(f"An error occurred in Inner_Websocket_Loop while processing message: {e}", "error")
                                    break
                    except Exception as e:
                        self.report_error_str(f"Restarting Connection after an error: {e}", "error")
                    finally:
                        self.report_error_str(f"Websocket connection ended.", "local setting")
                        if not self.stop_flag and self.reconnection_limit > self.reconnection_count:
                            self.report_error_str(f"Restarting Connection.", "local")
                            self.report_error_str(f"Restart Count: {self.reconnection_count}", "info")
                            await asyncio.sleep(2)


            loop.run_until_complete(inner_websocket_loop())
        except Exception as e:
            self.report_error_str(f"An error occurred in the base Websocket_Loop: {e}", "error")


def convert_to_dicts(list_of_lists):
    # https://i.imgur.com/3Cwe3dF.png
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
    # https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md
    # This function converts list of candle lists(kline streams from BinanceAPI) into a dictionary same as received from the websocket streams
    keys = ["t", "o", "h", "l", "c", "v", "T", "q", "n", "V", "Q", "B"]
    return [dict(zip(keys, sublist)) for sublist in list_of_lists]
