'''
1) Storing Bar Data in Dataframes : hist_data(symbols, timeframe="15Min", limit=200, start="", end="")
2) Getting Last Traded Price : last_trade(symbols)
3) Getting Last Quote Information : last_quote(symbols)
4) Fetching Historical Data Iteratively : hist_data_iter(symbols, period_hr=8, timeframe="1Min", start="", end="")
5) Historical Data v2 API Introduction : hist_data_v2(symbols, timeframe="15Min", limit=200, start="", end="")
'''

import json
import time
import requests 
import pandas as pd
from datetime import datetime

HEADERS = json.loads(open("./key.txt", 'r').read())
ENDPOINT = "https://data.alpaca.markets"

def hist_data(symbols, timeframe="15Min", limit=200, start="", end=""):
    '''
    1) Storing Bar Data in Dataframes
    
    data_dump = hist_data("META,CSCO,AMZN", timeframe="5Min", start="2020-01-01") 
    symbols 입력 시 띄어쓰기 X

    '''
    df_data = {}
    bar_url = ENDPOINT + "/v2/stocks/bars?"
    params = {"symbols" : symbols,
                "limit" : limit,
                "timeframe" : timeframe,
                "start" : datetime.strptime(start, '%Y-%m-%d').date(),
                "end" : end
                }
    r = requests.get(bar_url, headers=HEADERS, params=params)
    json_dump = r.json()
    
    for symbol in json_dump['bars']:
        temp = pd.DataFrame(json_dump['bars'][symbol])
        temp.rename({"t": "time", "o": "open", "l": "low", "c": "close", "v": "volume"}, axis=1, inplace=True)
        temp["time"] = pd.to_datetime(temp["time"]) # , unit="s")
        temp.set_index("time", inplace=True)
        temp.index = temp.index.tz_convert("America/Indiana/Petersburg") # tz_aware : tz_localize("UTC")
        df_data[symbol] = temp
    return df_data


def last_trade(symbols):
    '''
    2) Getting Last Traded Price
    
    info = last_trade("CSCO")
    
    '''
    last_trade_url = ENDPOINT + "/v2/stocks/trades/latest"
    params = {"symbols" : symbols}
    r = requests.get(last_trade_url, headers=HEADERS, params=params)
    json_dump = r.json()
    
    last_info = dict()
    for symbol in json_dump['trades']:
        last_price = json_dump['trades'][symbol]['p']
        last_size = json_dump['trades'][symbol]['s']
        last_info[symbol] = {"price" : last_price,
                             "size" : last_size}
    return (last_info)


def last_quote(symbols):
    '''
    3) Getting Last Quote Information
    
    info = last_quote("CSCO")
    
    '''
    last_trade_url = ENDPOINT + "/v2/stocks/quotes/latest"
    params = {"symbols" : symbols}
    r = requests.get(last_trade_url, headers=HEADERS, params=params)
    json_dump = r.json()
    
    last_info = dict()
    for symbol in json_dump['quotes']:
        last_time = json_dump['quotes'][symbol]['t']
        ask_price = json_dump['quotes'][symbol]['ap']
        ask_size = json_dump['quotes'][symbol]['as']
        bid_price = json_dump['quotes'][symbol]['bp']
        bid_size = json_dump['quotes'][symbol]['bs']
        last_info[symbol] = {"last_time" : last_time,
                             "ask_price" : ask_price,
                             "ask_size" : ask_size,
                             "bid_price" : bid_price,
                             "bid_size" : bid_size
                             }
    return last_info


def hist_data_iter(symbols, period_hr=8, timeframe="1Min", start="", end=""):
    '''
    
    4) Fetching Historical Data Iteratively
    
    '''
    starttime = time.time()
    timeout = starttime + 60*60*period_hr
    while time.time() <= timeout:
        for _ in symbols:
            # 1) 1Min 의 interval 로 market data 가져오기
            print(hist_data(symbols, timeframe=timeframe, start=start, end=end))
        # 2) starttime 기준으로 정확히 1분간 멈추기
        time.sleep(5 - ((time.time() - starttime) % 5))


def hist_data_v2(symbols, timeframe="15Min", limit=200, start="", end=""):
    '''
    
    5) Historical Data v2 API Introduction
    
    info = hist_data_v2("META,CSCO,AMZN", start="2024-03-25")
    
    '''
    data = dict()
    for symbol in symbols.split(","):
        data[symbol] = pd.DataFrame()
    df_data = {"bars" : data, 
                "next_page_token" : '',
                "symbol" : symbols}
    bar_url = ENDPOINT + "/v2/stocks/bars?"
    params = {"symbols" : symbols,
                "limit" : limit,
                "timeframe" : timeframe,
                "start" : datetime.strptime(start, '%Y-%m-%d').date(),
                "end" : end
                }
    
    while True:
        r = requests.get(bar_url, headers=HEADERS, params=params)
        json_dump = r.json()
        
        for symbol in json_dump['bars']:
            temp = pd.DataFrame(json_dump['bars'][symbol])
            temp.rename({"t": "time", "o": "open", "l": "low", "c": "close", "v": "volume"}, axis=1, inplace=True)
            temp["time"] = pd.to_datetime(temp["time"]) # , unit="s")
            temp.set_index("time", inplace=True)
            temp.index = temp.index.tz_convert("America/Indiana/Petersburg") # tz_aware : tz_localize("UTC")
            df_data["bars"][symbol] = pd.concat([df_data["bars"][symbol], temp])
            
        if json_dump["next_page_token"] == None:
            break
        else:
            params["page_token"] = json_dump["next_page_token"] # page_token 업데이트
            df_data["next_page_token"] = json_dump["next_page_token"]
    return df_data