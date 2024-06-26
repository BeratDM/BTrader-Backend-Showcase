from dotenv import load_dotenv, dotenv_values 
from pathlib import Path
import os, json
import ast
import binance.enums as b_enums

dotenv_path = Path(__file__).with_name('.env') #path to .env file

load_dotenv(dotenv_path = dotenv_path)

class Strategies:
    B_STRATS = json.loads(os.getenv("B_STRATEGIES", "{}"))

    ALL_INTERVALS = [b_enums.KLINE_INTERVAL_1SECOND,
                     b_enums.KLINE_INTERVAL_1MINUTE,
                     b_enums.KLINE_INTERVAL_3MINUTE,
                     b_enums.KLINE_INTERVAL_5MINUTE,
                     b_enums.KLINE_INTERVAL_15MINUTE,
                     b_enums.KLINE_INTERVAL_30MINUTE,
                     b_enums.KLINE_INTERVAL_1HOUR,
                     b_enums.KLINE_INTERVAL_2HOUR,
                     b_enums.KLINE_INTERVAL_4HOUR,
                     b_enums.KLINE_INTERVAL_6HOUR,
                     b_enums.KLINE_INTERVAL_8HOUR,
                     b_enums.KLINE_INTERVAL_12HOUR,
                     b_enums.KLINE_INTERVAL_1DAY,
                     b_enums.KLINE_INTERVAL_3DAY,
                     b_enums.KLINE_INTERVAL_1WEEK,
                     b_enums.KLINE_INTERVAL_1MONTH]

class Trade_Info:
    #Set Trade Informations    
    TRADE_SYMBOLS = json.loads(os.getenv("TRADE_SYMBOLS", "{}"))
    TRADE_INTERVALS = json.loads(os.getenv("TRADE_INTERVALS", "{}"))
    TRADE_STRATS = json.loads(os.getenv("TRADE_STRATS", "{}"))
    
    DEFAULT_SYMBOL = "LTCUSDT"
    DEFAULT_INTERVAL = "15m"
    DEFAULT_STRAT = "rsi_strategy01"

    TRADE_BOTS = ast.literal_eval(os.getenv("TRADE_BOTS", "{}"))

class Binance_Config:
    # Set Binance API Keys
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
    #tld: "us" for usa based IP and "com" for global.
    BINANCE_CLIENT_TLD = "com"
    BINANCE_USE_TEST_API = os.getenv("BINANCE_USE_TEST_API", 'False').lower() in ('true', '1')


class Flask_Config:
    # Set Flask Environment Variables From .env
    DEBUG = os.getenv("FLASK_DEBUG", 'False').lower() in ('true', '1')
    SERVER = os.getenv("FLASK_SERVER", "0.0.0.0")
    SECRET_KEY = bytes(os.getenv("FLASK_SECRET_KEY", "{}"), encoding="utf-8")

    DEFAULT_PORT = int(os.getenv("DEFAULT_PORT", "5000"))
    SHOULD_SERVE = os.getenv("SHOULD_SERVE", 'False').lower() in ('true', '1')


class Login_Info:
    #Set Users Dictionary
    USERS = ast.literal_eval(os.getenv("USERS", "{}"))
