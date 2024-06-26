import backtrader as bt
#from TradeStrategies import *
from TradeStrategies.bstrategy import bStrategy
from TradeStrategies import rsi_strategy01 as rsi_strategy01
from TradeStrategies import rsi_sma_volume_01 as rsi_sma_volume_01

from typing import Callable
from config import Strategies 




def get_strategy_bt(strategy_str: str) -> bt.Strategy:
    sclass = rsi_strategy01.Backtest
    if strategy_str == Strategies.B_STRATS[0]: #"rsi_strategy01"
        sclass = rsi_strategy01.Backtest
    if strategy_str == Strategies.B_STRATS[1]: #"rsi_sma_volume_01"
        sclass = rsi_sma_volume_01.Backtest
    #other strategies will go here with an if block
    return sclass


def get_strategy_live(strategy_str: str, report_info: Callable[[str, str], None], trade_action: Callable[[str, float, bool], bool]) -> bStrategy:
    my_ts = rsi_strategy01.Live(report_info=report_info, trade_action=trade_action)
    if strategy_str == Strategies.B_STRATS[0]: #"rsi_strategy01"
        my_ts = rsi_strategy01.Live(report_info=report_info, trade_action=trade_action)
    if strategy_str == Strategies.B_STRATS[1]: #"rsi_sma_volume_01"
        my_ts = rsi_sma_volume_01.Live(report_info=report_info, trade_action=trade_action)
    #other strategies will go here with an if block    
    return my_ts