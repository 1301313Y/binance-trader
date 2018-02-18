from behavior.Behavior import Behavior
from Orders import Orders
import pandas as pd
from behavior.Advice import Advice
from stockstats import StockDataFrame


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
        if cross_ups[cross_ups.size - 1] and self.placed_order() is False and d_current < self.options.stoch_min \
                and Orders.has_enough_to_trade(symbol, self.options.quantity):
            if k_current < self.options.stoch_min:
                return Advice.STRONG_BUY
            else:
                return Advice.BUY
        if cross_downs[cross_downs.size - 1] and self.placed_order() and d_current > self.options.stoch_cap and \
                Orders.has_enough_to_trade(symbol, buying=False, quantity=self.options.quantity):
            if k_current > self.options.stoch_cap:
                return Advice.STRONG_SELL
            else:
                return Advice.SELL
        return Advice.HOLD

    def weight(self):
        return 2
