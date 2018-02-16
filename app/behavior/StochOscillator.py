from behavior.Behavior import Behavior
from Orders import Orders
import pandas as pd
from stockstats import StockDataFrame
from behavior.Advice import Advice


class StochOscillator(Behavior):
    rsi_window = 14

    def __init__(self, option):
        super().__init__(option)
        self.rsi_window = self.options.rsi_window
        return

    def on_action(self, symbol):
        data = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64')
        data.columns = self.column_names
        stock_data = StockDataFrame.retype(data)
        k = stock_data['kdjk']
        d = stock_data['kdjd']
        k_current = int(k[k.size - 1])
        d_current = int(d[d.size - 1])
        if self.placed_order() is False and d_current < self.options.stoch_min:
            if k_current < self.options.stoch_min:
                return Advice.STRONG_BUY
            else:
                return Advice.BUY
        if self.placed_order() and d_current > self.options.stoch_cap:
            if k_current > self.options.stoch_cap:
                return Advice.STRONG_SELL
            else:
                return Advice.SELL
        return Advice.HOLD

    def weight(self):
        return 2
