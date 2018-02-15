from behavior.Behavior import Behavior
from Orders import Orders
import datetime
import pandas as pd
from pandas import Series


class EMA(Behavior):

    def __init__(self, option):
        super().__init__(option)
        return

    def get_closes_minute(self, symbol, limit):
        start = (datetime.datetime.now() - datetime.timedelta(minutes=limit)).strftime("%s") * 1000
        now = int(datetime.datetime.now().strftime("%s")) * 1000
        sticks = Orders.get_candle_sticks_limit(symbol, self.trading_period, start, now)
        close_prices = list()
        for s in sticks:
            close_prices.append(s[4])
        return close_prices

    def on_action(self, symbol):
        px = pd.DataFrame(Orders.get_candle_sticks(symbol, self.trading_period))
        px.dropna()

        return "WAIT"
