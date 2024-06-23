'''
HTTP Connection: Client (browser) needs to pull information whenever required 
VS. 
Websocket Connection: Data pushed to the client whenever made available

Documentations: https://docs.alpaca.markets/docs/streaming-market-data

# pip install websocket_client

1) Split tickers into two types ("Trades", "Quotes"): return_tickers(streams, tick_type="trades")
2) Storing Tick Data in SQL DB: insert_ticks(tick)
3) Create SQL DB Tables: create_tables(db, tickers, tick_type)
4) Streaming Market Data: stream_data(streams)
5) Resampling Ticks Data to Candles: get_bars(db, ticker)
'''

import json
import sqlite3
import websocket
import pandas as pd
import datetime as datetime

HEADERS = json.loads(open("./key.txt", 'r').read())
DB_TRADE_PATH = "./DB/trades_ticks.db"
DB_QUOTE_PATH = "./DB/quotes_ticks.db"
DB_TRADE = sqlite3.connect(DB_TRADE_PATH)
DB_QUOTE = sqlite3.connect(DB_QUOTE_PATH)
# STREAMS = ["T.AAPL", "T.TSLA", "T.GOOG", "T.AMZN",
#            "Q.AAPL", "Q.TSLA", "Q.GOOG", "Q.AMZN"]

def return_tickers(streams, tick_type="trades"):
    """
    
    1) Split tickers into two types ("Trades", "Quotes")
    
    """
    tickers = []
    if tick_type == "quotes":
        for symbol in streams:
            t_t, ticker = symbol.split(".")
            if t_t == "Q": # and ticker not in tickers:
                tickers.append(ticker)
    elif tick_type == "trades":
        for symbol in streams:
            t_t, ticker = symbol.split(".")
            if t_t == "T": #  and ticker not in tickers:
                tickers.append(ticker)    
    return tickers


def insert_ticks(tick):
    """
    
    2) Storing Tick Data in SQL DB 
    
    """
    if tick["stream"].split(".")[0] == "T":
        c = DB_TRADE.cursor()
        for ms in range(100):
            try:
                tabl = tick["streams"].split(".")[-1]
                vals = [datetime.datetime.fromtimestamp(int(tick["data"]["t"])/10**9) # from nanoseconds to seconds
                    + datetime.timedelta(milliseconds=ms), # to make unique timestamps
                    tick["data"]["p"], tick["data"]["s"]]
                query = "INSERT INTO t{} (timestamp, price, volume) \
                        VALUES (?, ?, ?)".format(tabl)
                c.execute(query, vals)
            except Exception as e:
                print(e)
        try: 
            DB_TRADE.commit()
        except:
            DB_TRADE.rollback()
    if tick["stream"].split(".")[0] == "Q":
        c = DB_QUOTE.cursor()
        for ms in range(100):
            try:
                tabl = tick["streams"].split(".")[-1]
                vals = [datetime.datetime.fromtimestamp(int(tick["data"]["t"])/10**9) # from nanoseconds to seconds
                    + datetime.timedelta(milliseconds=ms), # to make unique timestamps
                    tick["data"]["p"], tick["data"]["P"], tick["data"]["s"], tick["data"]["S"]]
                query = "INSERT INTO q{} (timestamp, bid_price, ask_price, bid_volume, ask_volume) \
                        VALUES (?, ?, ?, ?, ?)".format(tabl)
                c.execute(query, vals)
            except Exception as e:
                print(e)
        try: 
            DB_QUOTE.commit()
        except:
            DB_QUOTE.rollback()


def create_tables(db, tickers, tick_type):
    """
    
    3) Create SQL DB Tables
    
    """
    c = db.cursor()
    if tick_type == "trades":
        for ticker in tickers:
            c.execute("CREATE TABLE IF NOT EXISTS t{} \
                        (timestamp datetime primary key, \
                        price real(15, 5), \
                        volume integer)".format(ticker))
    if tick_type == "quotes":
        for ticker in tickers:
            c.execute("CREATE TABLE IF NOT EXISTS q{} \
                        (timestamp datetime primary key, \
                        bid_price real(15, 5), \
                        ask_price real(15, 5), \
                        bid_volume integer \
                        ask_volume integer)".format(ticker))
    try: 
        db.commit()
    except:
        db.rollback()
        

def stream_data(streams):
    """
    
    4) Streaming Market Data
    
    """
    def on_open(ws):
        auth = {
            "action": "auth",
            "key": HEADERS["APCA-API-KEY-ID"],
            "secret": HEADERS["APCA-API-SECRET-KEY"]
        }
        ws.send(json.dumps(auth))
        message = {
            "action": "subscribe", 
            "trades": return_tickers(streams, "trades"),
            "quotes": return_tickers(streams, "quotes")
            }
        ws.send(json.dumps(message))

    def on_message(ws, message):
        print(message)
        tick = json.loads(message)
        insert_ticks(tick)

    create_tables(DB_TRADE, return_tickers(streams, "trades"), "trades")
    create_tables(DB_QUOTE, return_tickers(streams, "quotes"), "quotes")

    ws = websocket.WebSocketApp(
        "wss://stream.data.alpaca.markets/v2/{}".format("iex"), # source: iex
        on_open=on_open,
        on_message=on_message
    )
    ws.run_forever()


def get_bars(db, ticker, days=12):
    """
    
    5) Resampling Ticks Data to Candles
    
    """
    data = pd.read_sql(
        "SELECT * FROM {} WHERE timestamp >= date() = - '{}days'".format(ticker, days),
        con=db) # fetch all ticks in the past 12 days
    data.set_index(['timestamp'], inplace=True)
    data.index = pd.to_datetime(data.index)
    price_ohlc = data.loc[:, ['price']].resample('1min').ohlc().dropna()
    price_ohlc.columns = ["open", "high", "low", "close"]
    vol_ohlc = data.loc[:,['volume']].resample('1min').apply({"volumne":"sum"}).dropna()
    df = price_ohlc.merge(vol_ohlc, left_index=True, right_index=True)
    return df