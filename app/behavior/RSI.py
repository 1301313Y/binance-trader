from behavior.Behavior import Behavior
from Orders import Orders
import datetime
import pandas as pd
from pandas import Series

import decimal, numpy
import pandas.stats.moments


class RSI(Behavior):
    rsi_window = 14

    def __init__(self, option):
        super().__init__(option)
        self.rsi_window = self.options.rsi_window
        return

    def on_action(self, symbol):
        data = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64')
        delta = data[4].dropna().diff()
        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0

        RolUp = Series.rolling(dUp, self.rsi_window).mean()
        RolDown = Series.rolling(dDown, self.rsi_window).mean().abs()

        RS = RolUp / RolDown
        print("RSI: %d%%" % int(RS[RS.size - 1] * 100))
        return "WAIT"

    def rsi(price, n=14):
        ''' rsi indicator '''
        gain = (price - price.shift(1)).fillna(0)  # calculate price gain with previous day, first row nan is filled with 0

        def rsiCalc(p):
            # subfunction for calculating rsi for one lookback period
            avgGain = p[p > 0].sum() / n
            avgLoss = -p[p < 0].sum() / n
            rs = avgGain / avgLoss
            return 100 - 100 / (1 + rs)

        # run for all periods with rolling_apply
        return pd.rolling_apply(gain, n, rsiCalc)
