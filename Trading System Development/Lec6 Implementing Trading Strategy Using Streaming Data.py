"""
Things to keep in mind:
    - Position sizing is crucial
    - How to handle repeat signals?
    - Order type?
    - Consider the expected lag every time you make an API request
    - Pay special attention to Time in Force when placing orders
    - Need to be very careful with the data type of the values returned by the API call. 
      If it is string, convert it to float before applying any mathematical operation.
"""
import time
import json
import requests
import websocket
import threading
import pandas as pd
import alpaca_trade_api as tradeapi
from collections import defaultdict

#######################################
## Multithreading using Event object ##
#######################################

def NumGen():
    '''
    
    NumGen()은 Daemon program으로 실행되어 greeting()이 끝나면 같이 종료된다.
    
    '''
    for a in range(30):
        if event.is_set():
            break
        else:
            print(a)
            time.sleep(1)
event = threading.Event()
thr2 = threading.Thread(target=NumGen)
thr2.start()

def greeting():
    for i in range(10):
        print('Hello')
        time.sleep(1)
        
greeting()
event.set()

##########################################
## Top Gainers/Losers Scanning Strategy ##
##########################################

# 30 Tech stocks and calculating what is their percentage gain or what is the percentage loss based

ENDPOINT = 'wss://stream.data.alpaca.markets/v2/iex'
HEADERS = json.loads(open('key.txt', 'r').read())
API = tradeapi.REST(
    key_id=HEADERS['APCA-API-KEY-ID'], 
    secret_key=HEADERS['APCA-API-SECRET-KEY'], 
    base_url='https://paper-api.alpaca.markets'
    )

endpoint = 'wss://stream.data.alpaca.markets/v2/iex'
headers = json.loads(open('key.txt', 'r').read())
api = tradeapi.REST(key_id=headers['APCA-API-KEY-ID'], secret_key=headers['APCA-API-SECRET-KEY'], base_url='https://paper-api.alpaca.markets')
tickers = 'AAPL,MSFT'
streams = [t for t in tickers.split(',')]
ltp = {}
prev_close = {}
perc_change = {}
traded_tickers = []
max_pos = 3000

def hist_data(tickers, timeframe, start, end='', limit=1000):
    bar_url = 'https://data.alpaca.markets/v2/stocks/bars'
    params = {'symbols': tickers,
            'timeframe': timeframe,
            'start': start,
            'end': end,
            'limit': limit
            }
    temp = {}
    for t in tickers.split(','):
        temp[t] = defaultdict(list)
    while True:
        r = requests.get(bar_url, headers=HEADERS, json=params)
        r = r.json()
        for t in list(r['bars'].keys()):
            temp[t]['bars'] += r['bars'][t]

        if r['next_page_token'] == None:
            break
        else:
            params['page_token'] = r['next_page_token']
    df_data = {}
    for k in temp.keys():
        df_temp = pd.DataFrame(temp[k]['bars'])
        df_temp['t'] = pd.to_datetime(df_temp['t'])
        df_temp.set_index('t', inplace=True)
        df_data[k] = df_temp
    return df_data

data_dump = hist_data(tickers, timeframe='1D', start='2024-03-01')
for ticker in tickers.split(','):
    prev_close[ticker] = data_dump[ticker]['c'].iloc[-2]
    ltp[ticker] = data_dump[ticker]['c'].iloc[-2]
    perc_change[ticker] = 0

def on_open(ws):
    auth = {
        'action': 'auth',
        'key': HEADERS['APCA-API-KEY-ID'], 
        'secret': HEADERS['APCA-API-SECRET-KEY']
        }
    ws.send(json.dumps(auth))
    message = {
        'action': 'subscribe',
        'trades': streams,
        }
    ws.send(json.dumps(message))

def on_message(ws, message):
    tick = json.loads(message)
    tkr = tick[-1]['S']
    ltp[tkr] = tick[-1]['p']
    perc_change[tkr] = round((ltp[tkr]/prev_close[tkr] - 1) * 100, 2)

def connect():
    ws = websocket.WebSocketApp(ENDPOINT, 
                                on_open=on_open, 
                                on_message=on_message
                                )
    ws.run_forever()


def quantity(ticker):
    return int(max_pos/ltp[ticker])


def signal(traded_tickers):
    for ticker, pc in perc_change.items():
        if pc > 1 and ticker not in traded_tickers:
            API.submit_order(ticker, quantity(ticker), 'buy', 'market', 'ioc')
            time.sleep(2)
            try:
                filled_qty = API.get_position(ticker).qty
                time.sleep(1)
                API.submit_order(ticker, int(filled_qty), 'sell', 'trailing_stop', 'day', trail_percent='1.5')
                traded_tickers.append(ticker)
            except Exception as e:
                print(ticker, e)

        if pc < -1 and ticker not in traded_tickers:
            API.submit_order(ticker, quantity(ticker), 'sell', 'market', 'ioc')
            time.sleep(2)
            try:
                filled_qty = API.get_position(ticker).qty
                time.sleep(1)
                API.submit_order(ticker, -int(filled_qty), 'buy', 'trailing_stop', 'day', trail_percent='1.5')
                traded_tickers.append(ticker)
            except Exception as e:
                print(ticker, e)

con_thread = threading.Thread(target=connect, daemon=True)
con_thread.start()

starttime = time.time()
timeout = starttime + 60*5
while time.time() < timeout:
    for ticker in tickers.split(','):
        print('percentage change for {} is {}'.format(ticker, perc_change[ticker]))
        signal(traded_tickers)
    time.sleep(30 - ((time.time() - starttime) % 30))

API.cancel_all_orders()
API.close_all_positions()
time.sleep(5)