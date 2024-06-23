import numpy as np
from copy import copy
from . import hist_data, MACD, stochastic

def CAGR(df_dict):
    cagr={}
    for df in df_dict:
        abs_return = (1+df_dict[df]['return']).cumprod().iloc[-1]
        n = len(df_dict[df])/252
        cagr[df] = (abs_return)**(1/n)-1
    return cagr


def volatility(df_dict):
    vol={}
    for df in df_dict:
        vol[df] = df_dict[df]["return"].std()*np.sqrt(252)
    return vol


def sharpe(df_dict, rf_rate):
    sharpe={}
    cagr = CAGR(df_dict)
    vol = volatility(df_dict)
    for df in df_dict:
        sharpe[df] = (cagr[df]-rf_rate)/vol[df]
    return sharpe


def max_dd(df_dict):
    max_drawdown = {}
    for df in df_dict:
        df_dict[df]["cum_return"] = (1+df_dict[df]["return"]).cumprod()
        df_dict[df]['cum_max'] = df_dict[df]["cum_return"].cummax()
        df_dict[df]["drawdown"] = df_dict[df]['cum_max'] - df_dict[df]["cum_return"]
        df_dict[df]['drawdown_pct'] = df_dict[df]['drawdown']/df_dict[df]['cum_max']
        max_drawdown[df] = df_dict[df]["drawdown_pct"].max()
        df_dict[df].drop(['cum_return', 'cum_max', 'drawdown', 'drawdown_pct'], axis=1, inplace=True)
    return max_drawdown


def winRate(DF):
    df = DF['return']
    pos = df[df>1]
    neg = df[df<1]
    return (len(pos)/(len(pos)+len(neg)))*100


def meanretpertrade(DF):
    df = DF['return']
    df_temp = (df-1).dropna()
    return df_temp[df_temp!=0].mean()


def meanretwintrade(DF):
    df = DF['return']
    df_temp = (df-1).dropna()
    return df_temp[df_temp>0].mean()


def meanretlosttrade(DF):
    df = DF["return"]
    df_temp = (df-1).dropna()
    return df_temp[df_temp<0].mean()


def maxconsectvloss(DF):
    df = DF['return']
    df_temp = df.dropna(axis=1)
    df_temp2 = np.where(df_temp<1, 1, 0)
    count_consecutive = []
    seek = 0
    for i in range(len(df_temp2)):
        if df_temp2[i] == 0:
            if seek >0:
                count_consecutive.append(seek)
            seek = 0
        else:
            seek +=1
    if len(count_consecutive)>0:
        return max(count_consecutive)
    else:
        return 0
    
tickers = "MSFT, AAPL, META, AMZN, INTC, GOOG, NVDA, NFLX, PYPL"
historicalData = hist_data(tickers, limit=1000)
ohlc_dict = copy.deepcopy(historicalData)
stoch_signal = {}
tickers_signal = {}
tickers_ret = {}
trade_count = {}
trade_data = {}
hwm = {}

MACD(ohlc_dict)
stochastic(ohlc_dict)

for ticker in tickers.split(','):
    ohlc_dict[ticker].dropna(inplace=True)
    stoch_signal[ticker] = ''
    tickers_signal[ticker]=''
    trade_count[ticker]=0
    hwm[ticker]=0
    tickers_ret[ticker]=[0]
    trade_data[ticker]={}

for ticker in tickers.split(','):
    print('Calculation returns for ', ticker)
    for i in range(1, len(ohlc_dict[ticker])-1):
        if ohlc_dict[ticker]['%K']<20:
            stoch_signal[ticker] = 'oversold'
        elif ohlc_dict[ticker]['%K'] > 80:
             stoch_signal[ticker]='overbought'
        
        if tickers_signal[ticker]=="":
            tickers_ret[ticker].append(0)
            if ohlc_dict[ticker]['macd'][i] > ohlc_dict[ticker]['signal'][i] and \
               ohlc_dict[ticker]['macd'][i-1] < ohlc_dict[ticker]['signal'][i-1] and \
               stoch_signal[ticker] == "oversold":
                tickers_signal[ticker]='Buy'
                trade_count[ticker]+=1
                trade_data[ticker][trade_count[ticker]] = [ohlc_dict[ticker]['open'][i+1]]
                hwm[ticker]=ohlc_dict[ticker]['open'][i+1]
        
        elif tickers_signal[ticker]=="Buy":
            if ohlc_dict[ticker]['low'][i] < 0.985*hwm[ticker]:
                tickers_signal[ticker] = ""
                trade_count[ticker]+=1
                trade_data[ticker][trade_count[ticker]].append(0.985*hwm[ticker])
                tickers_ret[ticker].append((0.985*hwm[ticker]/ohlc_dict[ticker]['close'][i-1])-1)
            else:
                hwm[ticker] = max(hwm[ticker], ohlc_dict[ticker]['high'])
                tickers_ret[ticker].append((ohlc_dict[ticker]['close'][i]/ohlc_dict[ticker]['close'][i-1])-1)

    if trade_count%2!=0:
        trade_data[ticker][trade_count[ticker]].append(ohlc_dict[ticker]['close'][-1])
    tickers_ret[ticker].append(0)
    ohlc_dict[ticker]['ret'] = np.array(tickers_ret[ticker])