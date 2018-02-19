# -*- coding: UTF-8 -*-
# @yasinkuyu

import sys
import argparse
from Trading import Trading
from plotting import Plotting

sys.path.insert(0, './app')

if __name__ == '__main__':
    
    # Set parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--plotting', type=bool, help='Enables Plotting Mode For Testing (No Trading)', default=False)
    parser.add_argument('--p_behavior', type=str, help='The Behavior To Use While In Plotting Mode', default='WILL')
    parser.add_argument('--quantity', type=float, help='Buy/Sell Quantity', default=0)
    parser.add_argument('--amount', type=float, help='Buy/Sell BTC Amount (Ex: 0.002 BTC)', default=0)
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVGBTC - XVGETH)', required=True)
    parser.add_argument('--profit', type=float, help='Target Profit', default=1.3)

    parser.add_argument('--stop_loss', type=float, help='Target Stop-Loss % (If the price drops by 6%, sell market_price.)', default=0) 

    parser.add_argument('--increasing', type=float, help='Buy Price +Increasing (0.00000001)', default=0.00000001)
    parser.add_argument('--decreasing', type=float, help='Sell Price -Decreasing (0.00000001)', default=0.00000001)

    # Manually defined --orderid try to sell 
    parser.add_argument('--orderid', type=int, help='Target Order Id (use balance.py)', default=0)

    parser.add_argument('--wait_time', type=float, help='Wait Time (seconds)', default=0.7)
    parser.add_argument('--test_mode', type=bool, help='Test Mode True/False', default=False)
    parser.add_argument('--prints', type=bool, help='Scanning Profit Screen Print True/False', default=True)
    parser.add_argument('--debug', type=bool, help='Debug True/False', default=True)
    parser.add_argument('--loop', type=int, help='Loop (0 unlimited)', default=0)

    # Working Modes
    #  - profit: Profit Hunter. Find defined profit, buy and sell. (Ex: 1.3% profit)
    #  - range: Between target two price, buy and sell. (Ex: <= 0.00100 buy - >= 0.00150 sell )
    parser.add_argument('--mode', type=str, help='Working Mode', default='profit')
    parser.add_argument('--buyprice', type=float, help='Buy Price (Price is greater than equal <=)', default=0)
    parser.add_argument('--sellprice', type=float, help='Sell Price (Price is small than equal >=)', default=0)
    parser.add_argument('--trading_period', type=str, help='Trading Period', default='15m')
    parser.add_argument('--rsi_window', type=int, help='Relative Strength Index Window Size', default=14)
    parser.add_argument('--rsi_cap', type=int, help='Relative Strength Index Cap', default=70)
    parser.add_argument('--rsi_min', type=int, help='Relative Strength Index Minimum', default=30)
    parser.add_argument('--macd_uv', type=int, help='MACD Positive Cross Up Validations', default=4)
    parser.add_argument('--macd_dv', type=int, help='MACD Negative Cross Down Validations', default=0)
    parser.add_argument('--stoch_k', type=int, help='Stoch Oscillator K Window Size', default=14)
    parser.add_argument('--stoch_d', type=int, help='Stoch Oscillator D Window Size', default=3)
    parser.add_argument('--stoch_cap', type=int, help='Stoch Oscillator Alert Cap', default=80)
    parser.add_argument('--stoch_min', type=int, help='Stoch Oscillator Minimum Alert', default=20)
    parser.add_argument('--will_window', type=int, help='Williams Price Range window size', default=6)
    parser.add_argument('--will_cap', type=int, help='Williams Price Range percent cap', default=80)
    parser.add_argument('--will_min', type=int, help='Williams Price Range percent minimum', default=20)
    parser.add_argument('--will_uv', type=int, help='Williams Price Range up cross validations', default=2)
    parser.add_argument('--will_dv', type=int, help='Williams Price Range down cross validations', default=0)
    option = parser.parse_args()
    if option.plotting:
        p = Plotting(option)
        p.plot()
    # Get start
    else:
        t = Trading(option)
        t.run()
