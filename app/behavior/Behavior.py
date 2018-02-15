# Define Custom imports
import Database
import Orders

import time


class Behavior:
    # Define Trade Parameters
    order_id = 0
    order_data = None

    buy_filled = True
    sell_filled = True

    buy_filled_qty = 0
    sell_filled_qty = 0

    # Stop Loss Percent (When you drop 10%, sell panic.)
    stop_loss = 0

    # Buy & Sell Quantity
    quantity = 0

    # Pair Key Amount (Currency Used In Trading; Ex. BTC, ETH)
    amount = 0

    # Trade Data Step Size (step_size * math.floor(float(free)/step_size))
    step_size = 0
    trading_period = '15m'

    # Define static vars
    WAIT_TIME_BUY_SELL = 1  # seconds
    WAIT_TIME_CHECK_BUY_SELL = 0.2  # seconds
    WAIT_TIME_CHECK_SELL = 5  # seconds
    WAIT_TIME_STOP_LOSS = 20  # seconds

    def __init__(self, option):
        self.options = option
        # Define parser vars
        self.trading_period = self.options.trading_period
        self.rsi_window = int(self.trading_period[:-1])
        self.order_id = self.options.orderid
        self.quantity = self.options.quantity
        self.wait_time = self.options.wait_time
        self.stop_loss = self.options.stop_loss

        self.increasing = self.options.increasing
        self.decreasing = self.options.decreasing

        # Pair Key Amount (Currency Used In Trading; Ex. BTC, ETH)
        self.amount = self.options.amount
        return

    def on_action(self, symbol):
        return "WAIT"

    def check_order(self):
        # If there is an open order, exit.
        if self.order_id > 0:
            exit(1)

    def calculate(self, last_bid):
        try:
            return last_bid + (last_bid * self.options.profit / 100)
        except Exception as e:
            print('c: %s' % e)
            return
