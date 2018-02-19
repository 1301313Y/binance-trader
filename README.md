# Binance Trader (B-1.0.0)(In Development)

This is an experimental bot for auto trading the binance.com exchange. Originally written by [@yasinkuyu](https://twitter.com/yasinkuyu). Behavior support will be a main focus for this fork of the bot, as I believe
having a single type of trading behavior can lead to dissapointing results. The behavior structure will be designed around
the idea of it being used as a tool which gives the bot advice on what should be the next move in trading. These behaviors
will be able to be written by the user, and can be paired with others to give stronger trading advice. I believe with
these tools, the user can define their success with this bot. Though remember with this power, also comes repsonsiblity.
Because if you fail, just as with success you only have yourself to blame.

**USE THIS BOT AT YOUR OWN RISK! PROFITS ARE NOT GUARANTEED!**

![Screenshot](https://github.com/yasinkuyu/binance-trader/blob/master/img/screenshot.png)

## Requirements
* Python 3.x
* [requests](http://docs.python-requests.org/en/master/)
* [stockstats](https://pypi.python.org/pypi/stockstats)
* [pandas](https://pandas.pydata.org/)
* [numpy](http://www.numpy.org/)
* [pyplot](https://matplotlib.org/api/pyplot_api.html)
```
Standard Libraries:
import os
import sys
import time
import config
import argparse
import threading
import sqlite3
 ```

## First Time Configuration

1. Signup Binance ( Referral url: https://www.binance.com/?ref=10701111 )
2. Enable Two-factor Authentication    
3. Go API Center, https://www.binance.com/userCenter/createApi.html
4. Create New Key

        [✓] Read Info [✓] Enable Trading [X] Enable Withdrawals 
5. If needed, install the required packages.

        pip install requests
        pip install pandas
        pip install stockstats
6. Rename config.sample.py to config.py / orders.sample.db to orders.db
7. Get your API and Secret Key from step 4, and insert into config.py

        # API key for account access
        api_key = ''
        # Secret key for account access
        api_secret = ''

        API Docs: https://www.binance.com/restapipub.html
7. Optional: run as an excutable application in Docker containers


## Usage

    python trader.py --symbol XVGBTC
    
    Example parameters
    
    # Profit mode (default)
    python trader.py --symbol XVGBTC --quantity 300 --profit 1.3
    or by amount
    python trader.py --symbol XVGBTC --amount 0.0022 --profit 3
    
    # Range mode
    python trader.py --symbol XVGBTC --mode range --quantity 300 --buyprice 0.00000780 --sellprice 0.00000790
    or by amount
    python trader.py --symbol XVGBTC --mode range --amount 0.0022 --buyprice 0.00000780 --sellprice 0.00000790
    --plotting          Buy/Sell Quantity (default False)
    --p_behavior        The Behavior To Use While In Plotting Mode (default= STOCH)
    --quantity          Buy/Sell Quantity (default 0) (If zero, auto calc)
    --amount            Buy/Sell BTC Amount (default 0)
    --symbol            Market Symbol (default XVGBTC or XVGETH)
    --profit            Target Profit Percentage (default 1.3)
    --stop_loss         Decrease sell price at loss Percentage (default 0)
    --orderid           Target Order Id (default 0)
    --wait_time         Wait Time (seconds) (default 0.7)
    --increasing        Buy Price Increasing  +(default 0.00000001)
    --decreasing        Sell Price Decreasing -(default 0.00000001)
    --prints            Scanning Profit Screen Print (default True)
    --loop              Loop (default 0 unlimited)
    --trading_period    Candle Stick Period (default 15m) (See 'Available Trading Periods' section below for all options)
    --rsi_window        The window size for the RSI indicator (default 14)
    --macd_uv           The MACD Positive Cross Up Validations (default 4) 
    --macd_dv           MACD Negative Cross Down Validations (default 0) 
    
    --mode          Working modes profit or range (default profit)
                        profit: Profit Hunter. Find defined profit, buy and sell. (Ex: 1.3% profit)
                        range: Between target two price, buy and sell. (Ex: <= 0.00000780 buy - >= 0.00000790 sell )
                   
    --buyprice     Buy price (Ex: 0.00000780)
    --sellprice    Buy price (Ex: 0.00000790)

    Symbol structure;
        XXXBTC  (Bitcoin)
        XXXETH  (Ethereum)
        XXXBNB  (Binance Coin)
        XXXUSDT (Tether)

    All binance symbols are supported.
    
    Every coin can be different in --profit and --quantity.
    If quantity is empty --quantity is automatically calculated to the minimum qty.
    
    Variations;
        trader.py --symbol TBNBTC --quantity 50 --profit 3
        trader.py --symbol NEOBTC --amount 0.1 --profit 1.1
        trader.py --symbol ETHUSDT --quantity 0.3 --profit 1.5
        ...
## Plot Mode
One issue with command line tools, is the inability to visual the data sets you are working with. To aid this issues
I have implemented a plotting mode, to show performance of strategies over the course of a given period.
This is so you can visually see the results of each behavior before applying them to a real trade situation.

You can easily run this mode using the following parameters (Results In Image Below):<br>
`trader.py --plotting True --symbol XVGETH --p_behavior STOCH`<br>
_Note that all normal options apply_

Available Behaviors:
* `STOCH`   (Stochastic Oscillator)
* `RSI`     (Relative Strength Index)
* `MACD`    (Moving Average Convergence Divergence)

Here is a example of the Stochastic Behavior for XVG/ETH, plotted over 500 15-minute periods.
![Screenshot](https://github.com/yasinkuyu/binance-trader/blob/master/img/stoch_graph_example.png)

## Available Trading Periods
* _m -> minutes;_
* _h -> hours;_
* _d -> days;_
* _w -> weeks;_
* _M -> months_
* Supported Periods:

        1m
        3m
        5m
        15m
        30m
        1h
        2h
        4h
        6h
        8h
        12h
        1d
        3d
        1w
        1M
    
## Run in a Docker container

    docker build -t trader .

    docker run trader
 
## DISCLAIMER

    I am not responsible for anything done with this bot. 
    You use it at your own risk. 
    There are no warranties or guarantees expressed or implied. 
    You assume all responsibility and liability.
     
## Contributing
    
    Current Fork Developed By: @1301313Y
    
    Fork this Repo
    Commit your changes (git commit -m 'Add some feature')
    Push to the changes (git push)
    Create a new Pull Request
    
    Thanks all for your contributions...
    
    Contributors
        @WeSpeakCrypto
        @afoke
        @omerfarukz
        @plgonzalezrx8
    
## Failure

    Filter failure: MIN_NOTIONAL
    https://support.binance.com/hc/en-us/articles/115000594711-Trading-Rule

    Filter failure: PRICE_FILTER
    https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md
    
    Timestamp for this request was 1000ms ahead of the server's time.
    https://github.com/yasinkuyu/binance-trader/issues/63#issuecomment-355857901
    
## Roadmap

    - Behavior Support (EMA, RSI, MACD, Etc...)
    - EMA Behavior (Completed)
    - RSI Behavior (Completed)
    - MACD Behavior (Completed)
    - Stochastic Behavior (Finalized - Tuning)
    - Multi-Behavior Advice Risk Factor Analysis (Initial Complettion)
    - Stop-Loss implementation
    
 ## Modes  
    Working:
        - profit: Find defined profit, buy and sell. (Ex: 1.3% profit)
        - range:  Between target two price, buy and sell. (Ex: <= 0.00100 buy - >= 0.00150 sell )
    In Development:
        Behavior Support: This will allow the user to add custom behaviors, which can be used to provide customized advice
        for trading. These behaviors will be able to be used as pairs, so that you can have stronger advice before executing a trade.
        - behavior: Uses a single behavior for advice.
        - multi-behavior: Uses multiple behaviors, and bases advice on risk factor.
        
 ## Releases
    - October 7, 2017 Beta
    - January 6, 2018 RC
    - January 15, 2018 RC 1
    - January 20, 2018 RC 2
    - TBA, 2018 B-1.0.0 (In Development)
     
## License
    Code released under the MIT License.

#### Tip Box
Original Author:
* [Wallets](http://yasinkuyu.net/wallet)

Me:
* BTC: `148UCoHdsiRQShaYpLBD3ymagMxZ3ypjfp`
* ETH: `0xdC88283D6DeD303CeAF88221869B6F3e6F1f69Ab`
* ETN: `etnkKhGvXtCFt8QFXFMcm65GG4yZqXCgjabKop7vDsCGV7ftYEGie8HMWUS5DPx3HhVJXMT6MWsDk2Bivy5YBKQD2VyQ98tNjs`

---
