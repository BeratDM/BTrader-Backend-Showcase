import bclient, btrader, log_handler
from config import Strategies, Trade_Info
import time


class BTManager:
    # python 3.9 enables to use list[str] instead of List[str] from typing module
    def __init__(self, myClient: bclient.MyClient) -> None:
        self.myClient = myClient
        self.next_trader_id = 0
        # self.myTraders = list[btrader.bTrader]
        self.myTraders = []
        self.myTraders_info = {}

        try:
            # self.create_traders_from_env()
            # self.start_all_traders()
            pass
        except Exception as e:
            print(e)

    def get_myTraders_info(self, index=-1) -> dict:
        if index == -1:
            return self.myTraders_info
        else:
            return self.myTraders_info[str(index)]

    def set_myTraders_info(
        self,
        index: int,
        TRADE_SYMBOL: str,
        TRADE_INTERVAL: str,
        TRADE_STRAT: str,
        ALLOCATED_TRADE_QUANTITY: float,
        Running: bool,
        InPosition: bool,
        PositionPrice: float,
    ):
        self.myTraders_info[str(index)] = dict(
            {
                "TRADE_SYMBOL": TRADE_SYMBOL,
                "TRADE_INTERVAL": TRADE_INTERVAL,
                "TRADE_STRAT": TRADE_STRAT,
                "ALLOCATED_TRADE_QUANTITY": ALLOCATED_TRADE_QUANTITY,
                "Running": Running,
                "InPosition": InPosition,
                "PositionPrice": PositionPrice,
            }
        )

    def create_trader(
        self,
        TRADE_SYMBOL: str,
        TRADE_INTERVAL: str,
        ALLOCATED_TRADE_QUANTITY: float,
        TRADE_STRAT: str,
    ) -> int:
        index = self.next_trader_id  # len(self.myTraders) - 1
        try:
            self.myTraders.append(
                btrader.bTrader(
                    trader_id=self.next_trader_id,
                    myClient=self.myClient,
                    report_position_info=self.update_position_info,
                    TRADE_SYMBOL=TRADE_SYMBOL,
                    TRADE_INTERVAL=TRADE_INTERVAL,
                    ALLOCATED_TRADE_QUANTITY=ALLOCATED_TRADE_QUANTITY,
                    strategy_str=TRADE_STRAT,
                )
            )

            self.set_myTraders_info(
                index=index,
                TRADE_SYMBOL=TRADE_SYMBOL,
                TRADE_INTERVAL=TRADE_INTERVAL,
                TRADE_STRAT=TRADE_STRAT,
                ALLOCATED_TRADE_QUANTITY=ALLOCATED_TRADE_QUANTITY,
                Running=False,
                InPosition=False,
                PositionPrice=0.00,
            )
            """
            
            self.myTraders_info[str(index)] = dict({
                "TRADE_SYMBOL" : TRADE_SYMBOL,
                "TRADE_INTERVAL" : TRADE_INTERVAL,
                "TRADE_STRAT" : TRADE_STRAT,
                "ALLOCATED_TRADE_QUANTITY" : ALLOCATED_TRADE_QUANTITY,
                "Running" : False,
                "InPosition" : False,
                "PositionPrice" : 0.00

            })
            
            """
        except Exception as e:
            print(e)
            log_handler.myLogHandler.add_error_log(
                f"btmanager error: {e}", "critical", -4
            )
        self.next_trader_id += 1

        return index

    def start_trader(self, index: int):
        if self.myTraders[int(index)] is not None:
            self.myTraders[int(index)].start()
            self.myTraders_info[str(index)]["Running"] = True
            time.sleep(2)
            return True
        return False

    def stop_trader(self, index: int):
        if self.myTraders[int(index)] is not None:
            self.myTraders[int(index)].stop()
            self.myTraders_info[str(index)]["Running"] = False

    def update_position_info(self, index: int, InPosition: bool, PositionPrice: float):
        if self.myTraders[int(index)] is not None:
            self.myTraders_info[str(index)]["InPosition"] = InPosition
            self.myTraders_info[str(index)]["PositionPrice"] = PositionPrice

    def create_traders_from_env(self):
        for tbots in Trade_Info.TRADE_BOTS:
            if all(
                mykey in tbots
                for mykey in (
                    "TRADE_SYMBOL",
                    "TRADE_INTERVAL",
                    "TRADE_STRAT",
                    "ALLOCATED_TRADE_QUANTITY",
                )
            ):
                if isinstance(tbots["ALLOCATED_TRADE_QUANTITY"], (int, float)):
                    T_SYMBOL = tbots["TRADE_SYMBOL"]
                    T_INTERVAL = tbots["TRADE_INTERVAL"]
                    T_STRAT = tbots["TRADE_STRAT"]
                    T_ALLOCATED_TRADE_QUANTITY = float(
                        tbots["ALLOCATED_TRADE_QUANTITY"]
                    )
                    self.create_trader(
                        TRADE_SYMBOL=T_SYMBOL,
                        TRADE_INTERVAL=T_INTERVAL,
                        ALLOCATED_TRADE_QUANTITY=T_ALLOCATED_TRADE_QUANTITY,
                        TRADE_STRAT=T_STRAT,
                    )

    def start_all_traders(self):
        # for btindex, btrader in enumerate(self.myTraders):
        #    self.start_trader(btindex)
        for index in range(len(self.myTraders)):
            wait = self.start_trader(index=index)
            # waits for the function to respond before starting next trader
            if wait is True:
                pass
