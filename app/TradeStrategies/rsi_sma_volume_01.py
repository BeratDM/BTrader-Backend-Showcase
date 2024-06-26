from typing import Callable
from .bstrategy import bStrategy
import backtrader as bt
from binance.enums import SIDE_BUY, SIDE_SELL
import numpy as np
import talib # type: ignore


'''
buy condition:
rsi>60
SMA 8 crosses SMA 21 upwards
volume is above the last average volume of last 45 candlestick volumes

sell:
SMA 8 crosses SMA 21 downwards  
'''


class Backtest(bt.Strategy):
    def __init__(self):
        self.RSI_PERIOD = 14
        self.RSI_OVERBOUGHT = 60
        self.RSI_OVERSOLD = 30
        self.SMA_SHORT = 8
        self.SMA_LONG = 21
        self.VOLUME_PERIOD = 35

        self.rsi = bt.talib.RSI(self.data.close, period=self.RSI_PERIOD)             # type: ignore
        self.sma_short = bt.talib.SMA(self.data.close, period=self.SMA_SHORT)        # type: ignore
        self.sma_long = bt.talib.SMA(self.data.close, period=self.SMA_LONG)          # type: ignore
        #self.volume = bt.talib.SMA(self.data.volume, period=self.VOLUME_PERIOD)      # type: ignore

    def next(self):
        # Check if we are in the market
        if not self.position:
            # We are not in the market, check if we should enter
            if self.rsi[-1] > self.RSI_OVERBOUGHT and self.sma_short[-1] > self.sma_long[-1]: # and self.data.volume[-1] > self.volume[-1]:     # type: ignore
                # Buy condition met
                half_cash = self.broker.getcash() / 2
                size = half_cash / self.data.close[-1]
                self.buy(size=size)
        else:
            # We are in the market, check if we should sell
            if self.sma_short[-1] < self.sma_long[-1]:
                # Sell condition met
                self.close()


class Live(bStrategy):
    def __init__(self, report_info: Callable[[str, str], None], trade_action: Callable[[str, float, bool], bool]):
        super().__init__(report_info, trade_action)

        self.RSI_PERIOD = 14
        self.RSI_OVERBOUGHT = 60
        self.RSI_OVERSOLD = 30
        self.SMA_SHORT = 8
        self.SMA_LONG = 21
        self.VOLUME_PERIOD = 35

        self.in_position = False
        self.price_of_position = 10

        self.closes = []
        self.volumes = []

    def process_candles(self, candles, calculate_order: bool):
        try:
            candles = candles[-50:]
            self.closes.clear()
            self.volumes.clear()
        
            for candle in candles:
                price_closed = float(candle['c'])
                volume = float(candle['v'])
                self.closes.append(price_closed)
                self.volumes.append(volume)

            if calculate_order:
                self.calculate_order()
        except Exception as e:
            self.report_info(f"process_candles: {e}", "strategy_error")

    def calculate_order(self):
        closes = np.array(self.closes)
        volumes = np.array(self.volumes)
        
        self.report_info("Calculating The Market", "info")
        if len(closes) > self.RSI_PERIOD:
            np_closes = np.array(closes)
            np_volumes = np.array(volumes)
            rsi = talib.RSI(np_closes, self.RSI_PERIOD) # type: ignore
            sma_short = talib.SMA(np_closes, self.SMA_SHORT) # type: ignore
            sma_long = talib.SMA(np_closes, self.SMA_LONG) # type: ignore
            avg_volume = np.mean(np_volumes[-self.VOLUME_PERIOD:])

            last_rsi = rsi[-1]
            last_sma_short = sma_short[-1]
            last_sma_long = sma_long[-1]
            last_volume = volumes[-1]
            last_close = closes[-1]

            try:
                #sell current position
                if last_sma_short < last_sma_long:
                    self.report_info("SMA 8 crossed SMA 21 downwards.", "info")
                    if self.in_position:
                        self.report_info("Sell! Sell! Sell!", "info")
                        order_success = self.trade_action(SIDE_SELL, 1.0, False)
                        if order_success:
                            self.in_position = False
                            self.price_of_position = 10
                    else:
                        self.report_info("SMA 8 crossed SMA 21 downwards, but I am not in position to sell.", "info")
                    
                #buy new position
                if last_rsi > self.RSI_OVERBOUGHT and last_sma_short > last_sma_long and last_volume > avg_volume:
                    self.report_info(f"RSI is over {self.RSI_OVERBOUGHT}, SMA 8 crossed SMA 21 upwards, and volume is above average.", "info")
                    if self.in_position:
                        self.report_info("Conditions met, but I am already in position.", "info")
                    else:
                        self.report_info("Buy! Buy! Buy!", "info")
                        order_success = self.trade_action(SIDE_BUY, 1.0, False)
                        if order_success:
                            self.in_position = True
                            self.price_of_position = last_close
            except Exception as e:
                self.report_info(f"calculate_order: {str(e)}", "strategy_error")