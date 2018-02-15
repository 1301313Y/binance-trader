from behavior.Behavior import Behavior
from Orders import Orders
import datetime
import pandas as pd
from pandas import Series


class MACD(Behavior):

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
        px.dropna()
        px['26 EMA'] = Series.ewm(px[4], span=26).mean()
        px['12 EMA'] = Series.ewm(px[4], span=12).mean()
        px['MACD'] = (px['12 EMA'] - px['26 EMA'])
        px['Signal'] = Series.ewm(px['MACD'], span=9).mean()
        print(px['Signal'][px['Signal'].size - 1] - px['MACD'][px['MACD'].size - 1])
        signal = px['Signal']  # Your signal line
        macd = px['MACD']  # The MACD that need to cross the signal line
        list_long_short = ["No data"]  # Since you need at least two days in the for loop
        for i in range(1, len(signal)):
            # If the MACD crosses the signal line upward
            if macd[i] > signal[i] and macd[i - 1] <= signal[i - 1]:
                list_long_short.append("BUY")
            # The other way around
            elif macd[i] < signal[i] and macd[i - 1] >= signal[i - 1]:
                list_long_short.append("SELL")
            # Do nothing if not crossed
            else:
                list_long_short.append("HOLD")

        px['Advice'] = list_long_short

        # The advice column means "Buy/Sell/Hold" at the end of this day or
        #  at the beginning of the next day, since the market will be closed

        print(px['Advice'][px['Advice'].size - 1])
        return "WAIT"
