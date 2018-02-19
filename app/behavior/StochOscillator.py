from behavior.Behavior import Behavior
from Orders import Orders
import pandas as pd
from behavior.Advice import Advice
from stockstats import StockDataFrame
import matplotlib.pyplot as plt
import numpy as np


class StochOscillator(Behavior):

    def __init__(self, option):
        super().__init__(option)
        self.rsi_window = self.options.rsi_window
        return

    def on_action(self, symbol):
        data = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64').fillna(0)
        data.columns = self.column_names
        stock_data = StockDataFrame.retype(data)
        k_data = stock_data['kdjk_%d' % self.options.stoch_k]
        d_data = stock_data['kdjd_%d' % self.options.stoch_d]
        k_current = k_data[k_data.size - 1]
        d_current = d_data[d_data.size - 1]
        cross_downs = stock_data['kdjk_%d_xd_kdjd_%d' % (self.options.stoch_k, self.options.stoch_d)]
        cross_ups = stock_data['kdjk_%d_xu_kdjd_%d' % (self.options.stoch_k, self.options.stoch_d)]
        if cross_ups[cross_ups.size - 1] and self.placed_order() is False and k_current < self.options.stoch_min \
                and Orders.has_enough_to_trade(symbol, self.options.quantity):
            if d_current < self.options.stoch_min:
                return Advice.STRONG_BUY
            else:
                return Advice.BUY
        if cross_downs[cross_downs.size - 1] and self.placed_order() and k_current > self.options.stoch_cap and \
                Orders.has_enough_to_trade(symbol, buying=False, quantity=self.options.quantity):
            if d_current > self.options.stoch_cap:
                return Advice.STRONG_SELL
            else:
                return Advice.SELL
        return Advice.HOLD

    def on_plot(self, symbol):
        df = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64').fillna(0)
        df.columns = self.column_names
        df['L%d' % self.options.stoch_k] = df['low'].rolling(window=self.options.stoch_k).min()
        df['H%d' % self.options.stoch_k] = df['high'].rolling(window=self.options.stoch_k).max()

        df['%K'] = 100 * ((df['close'] - df['L%d' % self.options.stoch_k]) / (df['H%d' % self.options.stoch_k]
                                                                              - df['L%d' % self.options.stoch_k]))
        df['%D'] = df['%K'].rolling(window=self.options.stoch_d).mean()

        df['Sell Entry'] = ((df['%K'] < df['%D']) & (df['%K'].shift(1) >
        df['%D'].shift(1))) & (df['%D'] > self.options.stoch_cap)
        df['Buy Entry'] = ((df['%K'] > df['%D']) & (df['%K'].shift(1) <
        df['%D'].shift(1))) & (df['%D'] < self.options.stoch_min)

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
        plt.title('Stochastic(%d, %d)[%d, %d] Strategy Performance' % (self.options.stoch_k,
                  self.options.stoch_d, self.options.stoch_min, self.options.stoch_cap))
        plt.show()

    def weight(self):
        return 2
