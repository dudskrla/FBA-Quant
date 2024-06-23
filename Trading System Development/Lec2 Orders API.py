'''
1) Placing Market Orders : market_order(symbol, quantity, side, time_in_force)
2) Placing Limit Orders : limit_order(symbol, quantity, side, time_in_force, limit_price)
3) Placing Stop Loss Orders : stop_order(symbol, quantity, side, time_in_force, stop_price)
4) Placing Stop Loss Limit Orders : stop_limit_order(symbol, quantity, side, time_in_force, stop_price, limit_price)
5) Placing Trailing Stop Loss Orders : trail_stop_order(symbol, quantity, side, time_in_force, trail_price)
6) Placing Bracket Orders : bracket_order(symbol, quantity, side, time_in_force, tplp, slsp, sllp)
7) Extracting Orders Information : order_list(status="open", limit=50)
8) Cancelling Open Orders : order_cancel(order_id="")
9) Replacing Open Orders : order_replace(order_id, params)
'''

import json
import requests 
import pandas as pd

HEADERS = json.loads(open("./key.txt", 'r').read())
ENDPOINT = "https://paper-api.alpaca.markets"

def market_order(symbol, quantity, side, time_in_force):
    '''

    1) Placing Market Orders
    
    A market order is the most basic type of trade order, 
    executed immediately at the current market price. 
    It guarantees execution but not the execution price.

    '''
    order_url = ENDPOINT + "/v2/orders"
    params = {
        "symbol": symbol,
        "qty": str(quantity),
        "side": side,
        "type": "market",
        "time_in_force": time_in_force
    }
    r = requests.post(order_url, headers=HEADERS, json=params)
    return r.json()


def limit_order(symbol, quantity, side, time_in_force, limit_price):
    '''

    2) Placing Limit Orders
    
    A limit order specifies the maximum or minimum price 
    at which you are willing to buy or sell a security. 
    This type of order only executes at the limit price or better.

    '''
    order_url = ENDPOINT + "/v2/orders"
    params = {
        'symbol': symbol,
        'qty': str(quantity),
        'side': side,
        'type': 'limit',
        'time_in_force': time_in_force,
        'limit_price': limit_price
    }
    r = requests.post(order_url, headers=HEADERS, json=params)
    return r.json()


def stop_order(symbol, quantity, side, time_in_force, stop_price):
    '''

    3) Placing Stop Loss Orders
    
    A stop order, also known as a stop-loss order, 
    becomes a market order once a specified price (stop price) is reached. 
    It's used primarily to limit a loss or protect a profit on a security's position.

    '''
    order_url = ENDPOINT + "/v2/orders"
    params = {
        "symbol": symbol,
        "qty": str(quantity),
        "side": side,
        "type": "stop",
        "time_in_force": time_in_force,
        "stop_price" : stop_price
    }
    r = requests.post(order_url, headers=HEADERS, json=params)
    return r.json()


def stop_limit_order(symbol, quantity, side, time_in_force, stop_price, limit_price):
    '''

    4) Placing Stop Loss Limit Orders
    
    A stop limit order becomes a limit order, rather than a market order, 
    once a specified price (stop price) is reached. 
    This type of order specifies two prices: the stop price and the limit price, 
    and will only execute at the limit price or better after the stop price has been reached.

    '''
    order_url = ENDPOINT + "/v2/orders"
    params = {
        "symbol": symbol,
        "qty": str(quantity),
        "side": side,
        "type": "stop_limit",
        "time_in_force": time_in_force,
        "stop_price": stop_price,
        "limit_price": limit_price
    }
    r = requests.post(order_url, headers=HEADERS, json=params)
    return r.json()


def trail_stop_order(symbol, quantity, side, time_in_force, trail_price):
    '''

    5) Placing Trailing Stop Loss Orders
    
    A trailing stop order sets the stop price 
    at a fixed amount or percentage away from the market price. 
    This distance trails the market price as it moves, 
    allowing for profit maximization and loss limitation.

    '''
    order_url = ENDPOINT + "/v2/orders"
    params = {
        "symbol": symbol,
        "qty": str(quantity),
        "side": side,
        "type": "trailing_stop",
        "time_in_force": time_in_force,
        "trail_price": trail_price
    }
    r = requests.post(order_url, headers=HEADERS, json=params)
    return r.json()


def bracket_order(symbol, quantity, side, time_in_force, tplp, slsp, sllp):
    '''

    6) Placing Bracket Orders
    
    A bracket order combines a main order with simultaneous take-profit and stop-loss orders. 
    This complex order type ensures that once the main order is executed, 
    it will automatically set a sell order at a profit target and a stop-loss order to limit potential losses.

    '''
    order_url = ENDPOINT + "/v2/orders"
    params = {
        "symbol": symbol,
        "qty": str(quantity),
        "side": side,
        "type": "market",
        "time_in_force": time_in_force,
        "order_class": "bracket",
        "take_profit": {
            "limit_price": tplp
        },
        "stop_loss": {
            "stop_price": slsp,
            "limit_price": sllp
        }
    }
    r = requests.post(order_url, headers=HEADERS, json=params)
    return r.json()


def order_list(status="open", limit=50):
    '''

    7) Extracting Orders Information

    '''
    order_url = ENDPOINT + "/v2/orders"
    params = {
        "status": status
    }
    r = requests.get(order_url, headers=HEADERS, json=params)
    data = r.json()
    return pd.DataFrame(data)


def order_cancel(order_id=""):
    '''

    8) Cancelling Open Orders
    
    ex. For certain symbols : order_cancel(order_df[order_df["symbol"]=="AMZN"]["id"].to_list()[0]) # order_df = order_list()
    ex. For all symbols : order_cancel()

    '''
    if len(order_id) > 1:
        order_url = ENDPOINT + "/v2/orders/{}".format(order_id)
    else:
        order_url = ENDPOINT + "/v2/orders"
    requests.delete(order_url, headers=HEADERS)


def order_replace(order_id, params):
    '''

    9) Replacing Open Orders
    
    supported parameters:
        qty
        time_in_force
        limit_price
        stop_price
        trail
        client_order_i
    
    ex. order_replace(order_df[order_df["symbol"]=="CSCO"]["id"].to_list()[0],
              {"qty": 10, "trail": 3})

    '''
    order_url = ENDPOINT + "/v2/orders/{}".format(order_id)
    r = requests.patch(order_url, headers=HEADERS, json=params)
    return r.json()