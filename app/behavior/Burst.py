from behavior.Behavior import Behavior

from app.Orders import Orders
from behavior.Advice import Advice
import pandas as pd
from stockstats import StockDataFrame
from behavior.Advice import Advice
import numpy as np
import matplotlib.pyplot as plt


class Burst(Behavior):

    def __init__(self, option):
        super().__init__(option)

    def on_action(self, symbol):
        # Order amount
        quantity = self.quantity

        # Fetches the ticker price
        last_price = Orders.get_ticker(symbol)

        # Order book prices
        last_bid, last_ask = Orders.get_order_book(symbol)

        # Target buy price, add little increase #87
        buy_price = last_bid + self.increasing

        # Target sell price, decrease little 
        sell_price = last_ask - self.decreasing

        # Spread ( profit )
        profitable_selling_price = self.calculate(last_bid)

        # Check working mode
        if self.options.mode == 'range':
            buy_price = float(self.options.buyprice)
            sell_price = float(self.options.sellprice)
            profitable_selling_price = sell_price

        # analyze = threading.Thread(target=analyze, args=(symbol,))
        # analyze.start()

        if self.order_id > 0:
            # Profit mode
            if self.order_data is not None:
                order = self.order_data
                # Last control
                new_profitable_selling_price = self.calculate(float(order['price']))
                if last_ask >= new_profitable_selling_price:
                    profitable_selling_price = new_profitable_selling_price
            # range mode
            if self.options.mode == 'range':
                profitable_selling_price = self.options.sellprice
            return Advice.SELL

        '''
        Did profit get caught
        if ask price is greater than profit price, 
        buy with my buy price,    
        '''
        if (last_ask >= profitable_selling_price and self.options.mode == 'profit') or \
                (last_price <= float(self.options.buyprice) and self.options.mode == 'range'):

            if self.order_id == 0:
                return Advice.BUY
                # self.buy(symbol, quantity, buy_price)

                # Perform check/sell action
                # checkAction = threading.Thread(target=self.check, args=(symbol, self.order_id, quantity,))
                # checkAction.start()
        return Advice.HOLD

    def on_plot(self, symbol):
        df = pd.DataFrame(Orders.get_candle_sticks(symbol, self.options.trading_period), dtype='float64').fillna(0)
        # TODO
        plt.show()
