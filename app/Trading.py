# -*- coding: UTF-8 -*-
# @yasinkuyu

# Define Python imports
import time
import threading
import math
from app.behavior.RSI import RSI
from app.behavior.MACD import MACD

# Define Custom imports
from Database import Database
from Orders import Orders


class Trading:
    # Define trade vars
    order_id = 0
    order_data = None

    buy_filled = True
    sell_filled = True

    buy_filled_qty = 0
    sell_filled_qty = 0

    # percent (When you drop 10%, sell panic.)
    stop_loss = 0

    # Buy/Sell qty
    quantity = 0

    # BTC amount
    amount = 0

    # float(step_size * math.floor(float(free)/step_size))
    step_size = 0
    behavior = None

    # Define static vars
    WAIT_TIME_BUY_SELL = 1  # seconds
    WAIT_TIME_CHECK_BUY_SELL = 0.2  # seconds
    WAIT_TIME_CHECK_SELL = 5  # seconds
    WAIT_TIME_STOP_LOSS = 20  # seconds

    MAX_TRADE_SIZE = 7  # int

    def __init__(self, option):
        # Behavior
        self.behavior = RSI(option)
        # Get argument parse options
        self.option = option

        # Define parser vars
        self.order_id = self.option.orderid
        self.quantity = self.option.quantity
        self.wait_time = self.option.wait_time
        self.stop_loss = self.option.stop_loss

        self.increasing = self.option.increasing
        self.decreasing = self.option.decreasing

        # BTC amount
        self.amount = self.option.amount

    def buy(self, symbol, quantity, buy_price):

        # Do you have an open order?
        self.check_order()

        try:
            # Create order
            order_id = Orders.buy_limit(symbol, quantity, buy_price)
            # Database log
            Database.write([order_id, symbol, 0, buy_price, 'BUY', quantity, self.option.profit])
            print('Buy order created id:%d, q:%.8f, p:%.8f' % (order_id, quantity, float(buy_price)))
            self.order_id = order_id
            return order_id

        except Exception as e:
            print('bl: %s' % e)
            time.sleep(self.WAIT_TIME_BUY_SELL)
            return None

    def sell(self, symbol, quantity, order_id, sell_price, last_price):

        """
        The specified limit will try to sell until it reaches.
        If not successful, the order will be canceled.
        """

        buy_order = Orders.get_order(symbol, order_id)

        if buy_order['status'] == 'FILLED' and buy_order['side'] == "BUY":
            print("Buy order filled... Try sell...")
        else:
            time.sleep(self.WAIT_TIME_CHECK_BUY_SELL)
            if buy_order['status'] == 'FILLED' and buy_order['side'] == "BUY":
                print("Buy order filled after 0.1 second... Try sell...")
            elif buy_order['status'] == 'PARTIALLY_FILLED' and buy_order['side'] == "BUY":
                print("Buy order partially filled... Try sell... Cancel remaining buy...")
                self.cancel(symbol, order_id)
            else:
                self.cancel(symbol, order_id)
                print("Buy order fail (Not filled) Cancel order...")
                self.order_id = 0
                return

        sell_order = Orders.sell_limit(symbol, quantity, sell_price)

        sell_id = sell_order['orderId']
        print('Sell order create id: %d' % sell_id)

        time.sleep(self.WAIT_TIME_CHECK_SELL)

        if sell_order['status'] == 'FILLED':
            print('Sell order (Filled) Id: %d' % sell_id)
            print('LastPrice : %.8f' % last_price)
            print('Profit: %%%s. Buy price: %.8f Sell price: %.8f'
                  % (self.option.profit, float(sell_order['price']), sell_price))

            self.order_id = 0
            self.order_data = None

            return

        '''
        If all sales trials fail, 
        the grievance is stop-loss.
        '''

        if self.stop_loss > 0:
            # If sell order failed after 5 seconds, 5 seconds more wait time before selling at loss
            time.sleep(self.WAIT_TIME_CHECK_SELL)
            if self.stop(symbol, quantity, sell_id, last_price):
                if Orders.get_order(symbol, sell_id)['status'] != 'FILLED':
                    print('We apologize... Sold at loss...')
            else:
                print('We apologize... Cant sell even at loss... Please sell manually... Stopping program...')
                self.cancel(symbol, sell_id)
                exit(1)
            sell_status = Orders.get_order(symbol, sell_id)['status']
            while sell_status != "FILLED":
                time.sleep(self.WAIT_TIME_CHECK_SELL)
                sell_status = Orders.get_order(symbol, sell_id)['status']
                last_price = Orders.get_ticker(symbol)
                print('Status: %s Current price: %.8f Sell price: %.8f' % (sell_status, last_price, sell_price))
                print('Sold! Continue trading...')

            self.order_id = 0
            self.order_data = None

    def stop(self, symbol, quantity, order_id, last_price):
        # If the target is not reached, stop-loss.
        stop_order = Orders.get_order(symbol, order_id)

        stop_price = self.calc(float(stop_order['price']))

        loss_price = stop_price - (stop_price * self.stop_loss / 100)

        status = stop_order['status']

        # Order status
        if status == 'NEW' or status == 'PARTIALLY_FILLED':

            if self.cancel(symbol, order_id):

                # Stop loss
                if last_price >= loss_price:

                    sell_orders = Orders.sell_market(symbol, quantity)

                    print('Stop-loss, sell market, %s' % last_price)

                    sell_id = sell_orders['orderId']

                    if sell_orders:
                        return True
                    else:
                        # Wait a while after the sale to the loss.
                        time.sleep(self.WAIT_TIME_STOP_LOSS)
                        status_loss = sell_orders['status']
                        if status_loss != 'NEW':
                            print('Stop-loss, sold')
                            return True
                        else:
                            self.cancel(symbol, sell_id)
                            return False
                else:
                    sell_orders = Orders.sell_limit(symbol, quantity, loss_price)
                    print('Stop-loss, sell limit, %s' % loss_price)
                    time.sleep(self.WAIT_TIME_STOP_LOSS)
                    status_loss = sell_orders['status']
                    if status_loss != 'NEW':
                        print('Stop-loss, sold')
                        return True
                    else:
                        sell_id = sell_orders['orderId']
                        self.cancel(symbol, sell_id)
                        return False
            else:
                print('Cancel did not work... Might have been sold before stop loss...')
                return True

        elif status == 'FILLED':
            self.order_id = 0
            self.order_data = None
            print('Order filled')
            return True
        else:
            return False

    def check(self, symbol, order_id, quantity):
        # If profit is available and there is no purchase from the specified price, take it with the market.

        # Do you have an open order?
        self.check_order()

        trading_size = 0
        time.sleep(self.WAIT_TIME_BUY_SELL)

        while trading_size < self.MAX_TRADE_SIZE:

            # Order info
            order = Orders.get_order(symbol, order_id)

            # side = order['side']
            price = float(order['price'])

            # TODO: Sell partial qty
            orig_qty = float(order['origQty'])
            self.buy_filled_qty = float(order['executedQty'])

            status = order['status']

            print('Wait buy order: %s id:%d, price: %.8f, orig_qty: %.8f' % (symbol, order['orderId'], price, orig_qty))

            if status == 'NEW':

                if self.cancel(symbol, order_id):

                    buy_orders = Orders.buy_market(symbol, quantity)

                    print('Buy market order')

                    self.order_id = buy_orders['orderId']
                    self.order_data = buy_orders

                    if buy_orders:
                        break
                    else:
                        trading_size += 1
                        continue
                else:
                    break

            elif status == 'FILLED':
                self.order_id = order['orderId']
                self.order_data = order
                print("Filled")
                break
            elif status == 'PARTIALLY_FILLED':
                print("Partial filled")
                break
            else:
                trading_size += 1
                continue

    def cancel(self, symbol, order_id):
        # If order is not filled, cancel it.
        check_order = Orders.get_order(symbol, order_id)

        if not check_order:
            self.order_id = 0
            self.order_data = None
            return True

        if check_order['status'] == 'NEW' or check_order['status'] != "CANCELLED":
            Orders.cancel_order(symbol, order_id)
            self.order_id = 0
            self.order_data = None
            return True

    def calc(self, last_bid):
        try:
            return last_bid + (last_bid * self.option.profit / 100)
        except Exception as e:
            print('c: %s' % e)
            return

    def check_order(self):
        # If there is an open order, exit.
        if self.order_id > 0:
            exit(1)

    def action(self, symbol):
        # Order amount
        quantity = self.quantity
        # Fetches the ticker price
        last_price = Orders.get_ticker(symbol)
        # Order book prices
        last_bid, last_ask = Orders.get_order_book(symbol)
        # Target buy price, add little increase #87
        buy_price = last_bid + self.increasing

        # Target sell price, decrease little 
        # sell_price = last_ask - self.decreasing

        # Spread ( profit )
        profitable_selling_price = self.calc(last_bid)
        # Check working mode
        if self.option.mode == 'range':
            buy_price = float(self.option.buyprice)
            sell_price = float(self.option.sellprice)
            profitable_selling_price = sell_price
        # Screen log
        if self.option.prints and self.order_id == 0:
            spread_perc = (last_ask / last_bid - 1) * 100.0
            print('[%s] Last Price:%.8f, Buy Price:%.8f, Profit Sell:%.8f, '
                  'Last Bid:%.8f, Last Ask:%.8f, Spread:%.2f' % (
                      Orders.get_server_time(), last_price, buy_price, profitable_selling_price, last_bid, last_ask,
                      spread_perc))
        # analyze = threading.Thread(target=analyze, args=(symbol,))
        # analyze.start()

        if self.order_id > 0:
            # Profit mode
            if self.order_data is not None:
                order = self.order_data
                # Last control
                new_profitable_selling_price = self.calc(float(order['price']))
                if last_ask >= new_profitable_selling_price:
                    profitable_selling_price = new_profitable_selling_price
            # range mode
            if self.option.mode == 'range':
                profitable_selling_price = self.option.sellprice
            '''            
            If the order is complete, 
            try to sell it.
            '''
            # Perform buy action
            sell_action = threading.Thread(target=self.sell,
                                           args=(symbol, quantity, self.order_id, profitable_selling_price, last_price))
            sell_action.start()
            return

        '''
        Did profit get caught
        if ask price is greater than profit price, 
        buy with my buy price,    
        '''
        on_action = self.behavior.on_action(symbol)
        if on_action == 'BUY':
            self.buy(symbol, quantity, buy_price)
            # Perform check/sell action
            # checkAction = threading.Thread(target=self.check, args=(symbol, self.order_id, quantity,))
            # checkAction.start()
        action = on_action
        print(action)

    @staticmethod
    def logic():
        return 0

    def filters(self):
        symbol = self.option.symbol
        # Get symbol exchange info
        symbol_info = Orders.get_info(symbol)
        if not symbol_info:
            print("Invalid trading pair symbol! Please verify launch parameters, and try again...")
            exit(1)
        symbol_info['filters'] = {item['filterType']: item for item in symbol_info['filters']}
        return symbol_info

    @staticmethod
    def format_step(quantity, step_size):
        return float(step_size * math.floor(float(quantity) / step_size))

    def validate(self):
        valid = True
        symbol = self.option.symbol
        filters = self.filters()['filters']

        # Order book prices
        last_bid, last_ask = Orders.get_order_book(symbol)
        last_price = Orders.get_ticker(symbol)
        min_qty = float(filters['LOT_SIZE']['minQty'])
        min_price = float(filters['PRICE_FILTER']['minPrice'])
        min_notional = float(filters['MIN_NOTIONAL']['minNotional'])

        # stepSize defines the intervals that a quantity/icebergQty can be increased/decreased by.
        step_size = float(filters['LOT_SIZE']['stepSize'])

        # tickSize defines the intervals that a price/stopPrice can be increased/decreased by
        tick_size = float(filters['PRICE_FILTER']['tickSize'])

        # If option increasing default tickSize greater than
        if float(self.option.increasing) < tick_size:
            self.increasing = tick_size

        # If option decreasing default tickSize greater than
        if float(self.option.decreasing) < tick_size:
            self.decreasing = tick_size

        # Just for validation
        last_bid = last_bid + self.increasing

        # Set static
        # If quantity or amount is zero, minNotional increase 10%
        quantity = (min_notional / last_bid)
        quantity = quantity + (quantity * 10 / 100)

        if self.amount > 0:
            # Calculate amount to quantity
            quantity = (self.amount / last_bid)

        if self.quantity > 0:
            # Format quantity step
            quantity = self.quantity

        quantity = self.format_step(quantity, step_size)
        notional = last_bid * float(quantity)

        # Set Globals
        self.quantity = quantity
        self.step_size = step_size

        # minQty = minimum order quantity
        if quantity < min_qty:
            print("Invalid quantity, minQty: %.8f (u: %.8f)" % (min_qty, quantity))
            valid = False

        if last_price < min_price:
            print("Invalid price, minPrice: %.8f (u: %.8f)" % (min_price, last_price))
            valid = False

        # minNotional = minimum order value (price * quantity)
        if notional < min_notional:
            print("Invalid notional, minNotional: %.8f (u: %.8f)" % (min_notional, notional))
            valid = False

        if not valid:
            exit(1)

    def run(self):

        cycle = 0
        actions = []

        symbol = self.option.symbol

        print('Binance Trading Bot - B Fork @1301313Y, 2018')
        print('Original Application Written By: @yasinkuyu, 2018')

        print('-' * 80)
        # Validate symbol
        self.validate()
        print('Initializing Application...')
        print("Exchange: Binance")
        print("Trading Pair: %s" % symbol)
        print("Max Buy Quantity: %s" % self.option.quantity)
        print("Stop-Loss Amount: %s" % self.option.stop_loss)
        print("Trading Behavior: %s" % self.option.mode)
        if self.option.mode == 'range':
            if self.option.buyprice == 0 or self.option.sellprice == 0:
                print('Please enter --buyprice / --sellprice\n')
                exit(1)
            print("Range Mode Options:")
            print("\tPrice Targets:" % self.option.mode)
            print("\tBuy: %.8f", self.option.buyprice)
            print("\tSell: %.8f", self.option.sellprice)
        else:
            print("Profit Mode Options:")
            print("\tPreferred Profit: %0.2f%%" % self.option.profit)
            print("\tBuy Price : (Bid+ --increasing %.8f)" % self.increasing)
            print("\tSell Price: (Bid- --decreasing %.8f)" % self.decreasing)
        print("Application Successfully Initialized!\nStarting...")
        print('-' * 80)

        while cycle <= self.option.loop:
            start_time = time.time()
            action_trader = threading.Thread(target=self.action, args={symbol})
            actions.append(action_trader)
            action_trader.start()
            end_time = time.time()
            if end_time - start_time < self.wait_time:
                time.sleep(self.wait_time - (end_time - start_time))
                # 0 = Unlimited loop
                if self.option.loop > 0:
                    cycle = cycle + 1
