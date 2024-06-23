'''
# pip install alpaca-trade-api
Github : https://github.com/alpacahq/alpaca-trade-api-python
'''

import json
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame

HEADERS = json.loads(open("./key.txt", 'r').read())
ENDPOINT = "https://paper-api.alpaca.markets"
API = tradeapi.REST(
    HEADERS['APCA-API-KEY-ID'], 
    HEADERS['APCA-API-SECRET-KEY'], 
    base_url=ENDPOINT
)

# Lec1 - 1) Storing Bar Data in Dataframes
data = API.get_bars('AAPL', TimeFrame.Minute, '2024-01-01', '2024-03-01', adjustment='all').df
trades = API.get_trades('GOOG', '2024-01-01', '2024-03-01', limit=10).df 
quotes = API.get_quotes('AMZN', '2024-01-01', '2024-03-01', limit=10).df

# Lec1 - 2) Getting Last Traded Price
last_trade = API.get_latest_trade('CSCO').price

# Lec1 - 3) Getting Last Quote Information
last_quote = API.get_latest_quote('CSCO').ask_price


# Lec2 - 1) Placing Market Orders
API.submit_order('META', 1, 'buy', 'market', 'day')

# Lec2 - 2) Placing Limit Orders
API.submit_order('CSCO', 1, 'buy', 'limit', 'day', '44.8') # 지정가 매매

# Lec2 - 3) Placing Stop Loss Orders
API.submit_order('META', 10, 'buy', 'stop', 'day', stop_price = '271') # 청산가 지정


# Lec3 - 1) Getting Position Information
pos_list = API.list_positions()

# Lec3 - 2) Closing Positions
API.close_all_positions()

# Lec3 - 3) Getting Account Information
account_info = API.get_account()