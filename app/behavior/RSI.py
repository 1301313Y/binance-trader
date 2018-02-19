from behavior.Behavior import Behavior
from Orders import Orders
import pandas as pd
from stockstats import StockDataFrame
from behavior.Advice import Advice
import matplotlib.pyplot as plt
import numpy as np


class RSI(Behavior):
    rsi_window = 14

    def __init__(self, option):
        super().__init__(option)
        self.rsi_window = self.options.rsi_window
        return

    def on_action(self, symbol):
        data = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64')
        data.columns = self.column_names
        stock_data = StockDataFrame.retype(data)
        window_ = stock_data['rsi_%d' % self.rsi_window]
        rsi = int(window_[window_.size - 1])
        if self.placed_order() is False and rsi < self.options.rsi_min:
            return Advice.BUY
        if self.placed_order() and rsi > self.options.rsi_cap:
            return Advice.SELL
        return Advice.HOLD

    def on_plot(self, symbol):
        df = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64').fillna(0)
        df.columns = self.column_names
        stock_data = StockDataFrame.retype(df)
        window_ = stock_data['rsi_%d' % self.rsi_window]

        df['Sell Entry'] = window_ > self.options.rsi_cap
        df['Buy Entry'] = window_ < self.options.rsi_min

        # Create empty "Position" column
        df['Position'] = np.nan

        # Set position to -1 for sell signals
        df.loc[df['Sell Entry'], 'Position'] = -1

        # Set position to -1 for buy signals
        df.loc[df['Buy Entry'], 'Position'] = 1

        # Set starting position to flat (i.e. 0)
        df['Position'].iloc[0] = 0

        # Forward fill the position column to show holding of positions through time
        df['Position'] = df['Position'].fillna(method='ffill')

        # Set up a column holding the daily Apple returns
        df['Market Returns'] = df['close'].pct_change()

        # Create column for Strategy Returns by multiplying the daily Apple returns by the position that was held at close
        # of business the previous day
        df['Strategy Returns'] = df['Market Returns'] * df['Position'].shift(1)

        # Finally plot the strategy returns versus Apple returns
        df[['Strategy Returns', 'Market Returns']].cumsum().plot(figsize=(20, 10))
        plt.title('RSI(%d) Strategy Performance' % self.rsi_window)
        plt.show()
