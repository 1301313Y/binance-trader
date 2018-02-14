# -*- coding: UTF-8 -*-
# @yasinkuyu

import os
import sqlite3

# Define Custom import vars
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../db/orders.db')
conn = sqlite3.connect(path, check_same_thread=False)


class Database:

    # Database (Todo: Not completed)
    @staticmethod
    def write(data):
        """
        Save order
        data = orderid,symbol,amount,price,side,quantity,profit
        Create a database connection
        """
        cur = conn.cursor()
        cur.execute('''INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()

    @staticmethod
    def read(order_id):
        """
        Query order info by id
        :param order_id: the buy/sell order id
        :return:
        """
        cur = conn.cursor()
        cur.execute('SELECT * FROM orders WHERE orderid = ?', (order_id,))
        return cur.fetchone()
