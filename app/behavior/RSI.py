from behavior.Behavior import Behavior
from Orders import Orders
import pandas as pd
from stockstats import StockDataFrame

COLUMN_NAMES = ['opendate', 'open', 'high', 'low', 'close', 'volume', 'close date', 'quote',
                'trades', 'takerbuybasevol','takerbuyquotevol', 'ignore']


class RSI(Behavior):

    rsi_window = 14

    def __init__(self, option):
        super().__init__(option)
        self.rsi_window = self.options.rsi_window
        return

    def on_action(self, symbol):
        data = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64')
        data.columns = COLUMN_NAMES
        stock_data = StockDataFrame.retype(data)
        window_ = stock_data['rsi_%d' % self.rsi_window]
        print("RSI(%d): %0.8f" % (self.rsi_window, int(window_[window_.size - 1])))
        return "WAIT"
