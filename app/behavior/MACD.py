from behavior.Behavior import Behavior
from Orders import Orders
import datetime
import pandas as pd
from stockstats import StockDataFrame
from behavior.Advice import Advice


class MACD(Behavior):

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
        px = pd.DataFrame(Orders.get_candle_sticks(symbol, self.trading_period))
        data = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64')
        data.columns = self.column_names
        stock_data = StockDataFrame.retype(data)
        macd = stock_data['macd']
        signal = stock_data['macds']
        list_long_short = [Advice.NAN]  # Since you need at least two days in the for loop
        has_crossed_up = False
        crossed_up_validations = 0
        has_crossed_down = False
        crossed_down_validations = 0
        for i in range(1, len(signal)):
            # If the MACD crosses the signal line upward
            macd_point = macd[i]
            signal_point = signal[i]
            macd_prev_point = macd[i - 1]
            signal_prev_point = signal[i - 1]
            if has_crossed_up:
                if macd_point > signal_point:
                    crossed_up_validations += 1
                    if crossed_up_validations > self.options.macd_uv:
                        list_long_short.append(Advice.BUY)
                        has_crossed_up = False
                        crossed_up_validations = 0
                        continue
                else:
                    has_crossed_up = False
                    crossed_up_validations = 0
                list_long_short.append(Advice.HOLD)
            elif has_crossed_down:
                if macd_point < signal_point:
                    crossed_down_validations += 1
                    if crossed_down_validations > self.options.macd_dv:
                        list_long_short.append(Advice.SELL)
                        has_crossed_down = False
                        crossed_down_validations = 0
                        continue
                else:
                    has_crossed_down = False
                    crossed_down_validations = 0
                list_long_short.append(Advice.HOLD)
            else:
                if macd_point > signal_point and macd_prev_point <= signal_prev_point:
                    has_crossed_up = True
                # The other way around
                elif macd_point < signal_point and macd_prev_point >= signal_prev_point:
                    has_crossed_down = True
                list_long_short.append(Advice.HOLD)

        px['Advice'] = list_long_short
        return px['Advice'].last(0)

    def pos_threshold(self, value):
        return value * self.options.macd_pt

    def neg_threshold(self, value):
        return value * self.options.macd_nt
