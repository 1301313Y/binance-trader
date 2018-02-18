# -*- coding: UTF-8 -*-
# @yasinkuyu
import config
import datetime
import pandas as pd

from BinanceAPI import BinanceAPI
from Messages import Messages

# Define Custom import vars
client = BinanceAPI(config.api_key, config.api_secret)


class Orders:

    @staticmethod
    def has_enough_to_trade(symbol, buying=True, quantity=0):
        last_price = Orders.get_ticker(symbol)
        if quantity > 0:
            order_notional = quantity * last_price
        else:
            coin_balance, currency_balance = Orders.get_balance(symbol)
            if buying:
                order_notional = currency_balance
            else:
                order_notional = coin_balance * last_price
        min_notional = Orders.get_min_notional(symbol)
        return order_notional > min_notional

    @staticmethod
    def get_min_notional(symbol):
        data_frame = pd.DataFrame(client.get_exchange_info()['symbols']).set_index('symbol')
        data_frame = pd.DataFrame(data_frame.loc[symbol]['filters']).set_index('filterType')
        return data_frame.loc['MIN_NOTIONAL']['minNotional']

    @staticmethod
    def get_balance(symbol):
        coin_order, currency_order = client.get_balance(symbol)

        if 'msg' in coin_order:
            Messages.get(coin_order['msg'])
        if 'msg' in currency_order:
            Messages.get(currency_order['msg'])

        # Buy order created.
        return coin_order['free'], currency_order['free']

    @staticmethod
    def buy_limit(symbol, quantity, buy_price):
        order = client.buy_limit(symbol, quantity, buy_price)

        if 'msg' in order:
            Messages.get(order['msg'])

        # Buy order created.
        return order['orderId']

    @staticmethod
    def sell_limit(symbol, quantity, sell_price):

        order = client.sell_limit(symbol, quantity, sell_price)

        if 'msg' in order:
            Messages.get(order['msg'])

        return order

    @staticmethod
    def get_server_time():
        time = client.get_server_time()
        if 'msg' in time:
            Messages.get(time['msg'])
        return datetime.datetime.fromtimestamp(time['serverTime'] / 1000.0)

    @staticmethod
    def buy_market(symbol, quantity):

        order = client.buy_market(symbol, quantity)

        if 'msg' in order:
            Messages.get(order['msg'])

        return order

    @staticmethod
    def sell_market(symbol, quantity):

        order = client.sell_market(symbol, quantity)

        if 'msg' in order:
            Messages.get(order['msg'])

        return order

    @staticmethod
    def cancel_order(symbol, order_id):

        try:

            order = client.cancel(symbol, order_id)
            if 'msg' in order:
                Messages.get(order['msg'])

            print('Profit loss, called order, %s' % order_id)

            return True

        except Exception as e:
            print('co: %s' % e)
            return False

    @staticmethod
    def get_candle_sticks(symbol, interval):
        try:
            return client.get_kline(symbol, interval)
        except Exception as e:
            print('kl: %s' % e)
            return None

    @staticmethod
    def get_candle_sticks_limit(symbol, interval, start_time, end_time):
        try:
            return client.get_kline_limit(symbol, interval, start_time, end_time)
        except Exception as e:
            print('kl: %s' % e)
            return None

    @staticmethod
    def get_order_book(symbol):
        try:

            orders = client.get_order_books(symbol, 5)
            last_bid = float(orders['bids'][0][0])  # last buy price (bid)
            last_ask = float(orders['asks'][0][0])  # last sell price (ask)

            return last_bid, last_ask

        except Exception as e:
            print('ob: %s' % e)
            return 0, 0

    @staticmethod
    def get_order(symbol, order_id):
        try:

            order = client.query_order(symbol, order_id)

            if 'msg' in order:
                # Messages.get(order['msg']) - TODO
                return False

            return order

        except Exception as e:
            print('go: %s' % e)
            return False

    @staticmethod
    def get_order_status(symbol, order_id):
        try:

            order = client.query_order(symbol, order_id)

            if 'msg' in order:
                Messages.get(order['msg'])

            return order['status']

        except Exception as e:
            print('gos: %s' % e)
            return None

    @staticmethod
    def get_ticker(symbol):
        try:

            ticker = client.get_ticker(symbol)

            return float(ticker['lastPrice'])
        except Exception as e:
            print('gt: %s' % e)

    @staticmethod
    def get_info(symbol):
        try:
            info = client.get_exchange_info()
            if symbol != "":
                return [market for market in info['symbols'] if market['symbol'] == symbol][0]
            return info
        except Exception as e:
            print('gi: %s' % e)
