from typing import Callable
from .bstrategy import bStrategy
import backtrader as bt
from binance.enums import SIDE_BUY, SIDE_SELL
import numpy, talib


'''
buy condition:
RSI-14 < 30

sell:
RSI-14 > 70
if up %2
'''


class Backtest(bt.Strategy):
    def __init__(self):
        self.RSI_PERIOD = 14
        self.RSI_OVERBOUGHT = 70
        self.RSI_OVERSOLD = 30

        self.price_of_position = 10
        self.sell_if_up = True
        self.sell_if_up_ratio = 1.02

        self.rsi = bt.talib.RSI(self.data.close, period=self.RSI_PERIOD) # type: ignore

    def next(self):
        last_close = self.data.close[-1] 
        last_rsi = self.rsi[-1]

        #sell current position
        if last_rsi > self.RSI_OVERBOUGHT or (self.position and self.sell_if_up and (last_close > self.price_of_position *self.sell_if_up_ratio )):
            if self.position:
                self.close()
                self.price_of_position = 10

        #buy new position
        if last_rsi < self.RSI_OVERSOLD and not self.position:
            half_cash = self.broker.getcash() / 2
            size = half_cash / self.data.close[-1]
            self.buy(size=size)
            self.price_of_position = last_close


''' 
#This is how a simple Backtest(backtrader) Strategy class should work
class Backtest(bt.Strategy):
    def __init__(self):
        self.rsi = bt.talib.RSI(self.data, period=14)
    def next(self):
        if self.rsi < 30 and not self.position:
            self.buy(size=1)
      
        if self.rsi > 70 and self.position:
            self.close()
'''

#This is the live strategy to trade with realtime
class Live(bStrategy):
    def __init__(self, report_info: Callable[[str, str], None], trade_action: Callable[[str, float, bool], bool]):
        super().__init__(report_info, trade_action)

        self.RSI_PERIOD = 14
        self.RSI_OVERBOUGHT = 70
        self.RSI_OVERSOLD = 30

        self.in_position = False
        self.price_of_position = 10
        self.sell_if_up = True
        self.sell_if_up_ratio = 1.02

        self.closes = []

    
    def process_candles(self, candles, calculate_order: bool):
        # look-up the payload of the websocket stream on here https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md 
        # Payload: 
        # {
        #     "t": 1672515780000, // Kline start time
        #     "T": 1672515839999, // Kline close time
        #     "s": "BNBBTC",      // Symbol
        #     "i": "1m",          // Interval
        #     "f": 100,           // First trade ID
        #     "L": 200,           // Last trade ID
        #     "o": "0.0010",      // Open price
        #     "c": "0.0020",      // Close price
        #     "h": "0.0025",      // High price
        #     "l": "0.0015",      // Low price
        #     "v": "1000",        // Base asset volume
        #     "n": 100,           // Number of trades
        #     "x": false,         // Is this kline closed?
        #     "q": "1.0000",      // Quote asset volume
        #     "V": "500",         // Taker buy base asset volume
        #     "Q": "0.500",       // Taker buy quote asset volume
        #     "B": "123456"       // Ignore
        # }
        try:
            candles = candles[-50:]
            self.closes.clear
        
            for candle in candles:
                price_closed = float(candle['c'])
                self.closes.append(price_closed)

            if calculate_order:
                self.calculate_order()
        except Exception as e:
            self.report_info(f"process_candles: {e}", "strategy_error")


    # 
    def calculate_order(self):
        try:
            self.report_info("in position: {}".format(self.in_position), "info")
            self.report_info("price of position: {}".format(self.price_of_position), "info")
            closes = self.closes
            
            
            self.report_info("Calculating The Market", "info")
            if len(closes) > self.RSI_PERIOD:
                np_closes = numpy.array(closes, dtype=float)
                rsi = talib.RSI(np_closes, self.RSI_PERIOD) #talib.RSI returns multiple RSI values # type: ignore

                last_rsi = rsi[-1]
                self.report_info("the current rsi is {}".format(last_rsi), "info")
                self.report_info("in position: {}".format(self.in_position), "info")
                last_close = closes[-1]

            
                #sell current position
                if last_rsi > self.RSI_OVERBOUGHT or (self.in_position and self.sell_if_up and (last_close > self.price_of_position *self.sell_if_up_ratio )):
                    if last_rsi > self.RSI_OVERBOUGHT:
                        self.report_info("in overbought area.", "info")
                    if (last_close > self.price_of_position *self.sell_if_up_ratio and self.sell_if_up ):
                        self.report_info("current profit is above the percentage of {}".format(self.sell_if_up_ratio), "info")
                    self.report_info(str(self.in_position), "info")
                    if self.in_position:
                        self.report_info("Sell! Sell! Sell!", "info")
                        
                        
                        order_success = self.trade_action(SIDE_SELL, 1.0, False)
                        if order_success:
                            self.in_position = False
                            self.price_of_position = 10
                        #Binance sell logic
                    else:
                        self.report_info("It is overbough, but I am not in position to sell.", "info")
                    
                #buy new position
                if last_rsi < self.RSI_OVERSOLD:
                    self.report_info("in oversold area.", "info")
                    self.report_info(str(self.in_position), "info")
                    if self.in_position:
                        self.report_info("it is oversold, but I am already in position.", "info")
                    else:
                        self.report_info("Buy! Buy! Buy!", "info")
                        
                        
                        order_success = self.trade_action(SIDE_BUY, 1.0, False)
                        if order_success:
                            self.in_position = True
                            self.price_of_position = last_close
                        #Binance buy logic
        except Exception as e:
            self.report_info(f"calculate_order: {e}", "strategy_error")
