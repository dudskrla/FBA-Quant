import time
from . import hist_data, MACD, stochastic, ohlc_dict, api

def main(tickers):
    global stoch_signal
    max_pos = 3000
    historicalData = hist_data(tickers, '1Min')
    MACD(historicalData)
    stochastic(historicalData)
    positions = api.list_positions()
    for ticker in tickers.split(','):
        historicalData[ticker].dropna(inplace=True)
        existing_pos = False

        if ohlc_dict[ticker]['%K']<20:
            stoch_signal[ticker] = 'oversold'
        elif ohlc_dict[ticker]['%K'] > 80:
             stoch_signal[ticker]='overbought'

        for position in positions:
            if len(positions)>0:
                if position.symbol == ticker and position.qty !=0:
                    existing_pos = True
            
        if historicalData[ticker]['macd'].iloc[-1] > historicalData[ticker]['signal'].iloc[-1] and \
           historicalData[ticker]['macd'].iloc[-2] < historicalData[ticker]['signal'].iloc[-2] and \
           stoch_signal[ticker]=='oversold' and existing_pos == False:
            api.submit_order(ticker, max(1, int(max_pos/historicalData[ticker]['close'].iloc[-1])), 'buy', 'market', 'ioc')
            time.sleep(2)
            try:
                filled_qty = api.get_position(ticker).qty
                time.sleep(1)
                api.submit_order(ticker, int(filled_qty), 'sell', 'trailing_stop', 'day', trail_percent=1.5)
            except Exception as e:
                print(ticker, e)


starttime = time.time()
timeout = starttime + 60*60*1
while time.time() <= timeout :
    print("starting iteration at {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    main()
    time.sleep(60-((time.time()-starttime %60)))

api.close_all_positions()
time.sleep(5)
api.cancel_all_orders()
time.sleep(5)