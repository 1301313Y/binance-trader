from behavior.Behavior import Behavior
from Orders import Orders
import datetime
import pandas as pd
from stockstats import StockDataFrame
from behavior.Advice import Advice
import numpy as np
import matplotlib.pyplot as plt


class WilliamsPR(Behavior):
    last_positive_cross = None
    last_negative_cross = None

    def __init__(self, option):
        super().__init__(option)
        return

    def get_closes_minute(self, symbol, limit):
        start = (datetime.datetime.now() - datetime.timedelta(minutes=limit)).strftime("%s") * 1000
        now = int(datetime.datetime.now().strftime("%s")) * 1000
        sticks = Orders.get_candle_sticks_limit(symbol, self.options.trading_period, start, now)
        close_prices = list()
        for s in sticks:
            close_prices.append(s[4])
        return close_prices

    def on_action(self, symbol):
        data = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64')
        data.columns = self.column_names
        stock_data = StockDataFrame.retype(data)
        wpr = stock_data['wr_%d' % self.options.will_window]
        last_value = wpr[wpr.size - 1]
        validate = self.validate(wpr, last_value)
        return validate

    def validate(self, wpr, last_value):
        test_slice = None
        buying = False
        if last_value > self.options.will_cap:
            buying = True
            test_slice = wpr[-(self.options.will_uv + 2):-1].reset_index(drop=True)
        elif last_value < self.options.will_min:
            test_slice = wpr[-(self.options.will_dv + 2):-1].reset_index(drop=True)
        if test_slice is not None:
            is_failed = False
            test_slice = test_slice.iloc[::-1]
            for current in test_slice:
                if buying:
                    if self.options.will_cap < current < last_value:
                        last_value = current
                    else:
                        is_failed = True
                        break
                else:
                    if self.options.will_min > current > last_value:
                        last_value = current
                    else:
                        is_failed = True
                        break
            if not is_failed:
                if buying:
                    return Advice.BUY
                else:
                    return Advice.SELL
        return Advice.HOLD

    def on_plot(self, symbol):
        df = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64').fillna(0)
        df.columns = self.column_names
        stock_data = StockDataFrame.retype(df)
        wpr = stock_data['wr_%d' % self.options.will_window]
        df['Sell Entry'] = (wpr < wpr.shift(1)) & (wpr > self.options.will_cap)
        df['Buy Entry'] = (wpr > wpr.shift(1)) & (wpr < self.options.will_min)
        # Create empty "Position" column
        df['Position'] = np.nan

        # Set position to -1 for sell signals
        df.loc[df['Sell Entry'], 'Position'] = -1

        # Set position to -1 for buy signals
        df.loc[df['Buy Entry'], 'Position'] = 1

        # Set starting position to flat (i.e. 0)
        df['Position'].reset_index(drop=True)

        # Forward fill the position column to show holding of positions through time
        df['Position'] = df['Position'].fillna(method='ffill')

        # Set up a column holding the daily Apple returns
        df['Market Returns'] = df['close'].pct_change()

        df['Strategy Returns'] = df['Market Returns'] * df['Position'].shift(1)

        # Finally plot the strategy returns versus Apple returns
        df[['Strategy Returns', 'Market Returns']].cumsum().plot(figsize=(20, 10))
        plt.title('Williams Price Range(%d)[%d, %d] Strategy Performance' % (self.options.will_window,
                                                                       self.options.will_min,
                                                                       self.options.will_cap))
        plt.show()
