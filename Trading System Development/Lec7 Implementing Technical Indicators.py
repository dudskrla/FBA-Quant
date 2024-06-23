def MACD(df_dict, a, b, c):
    for df in df_dict:
        df_dict[df]["ma_fast"] = df_dict[df]["close"].ewm(span=a, min_periods=a).mean()
        df_dict[df]["ma_slow"] = df_dict[df]["close"].ewm(span=b, min_periods=b).mean()
        df_dict[df]["macd"] = df_dict[df]["ma_fast"]-df_dict[df]["ma_slow"]
        df_dict[df]["signal"] = df_dict[df]["macd"].ewm(span=c, min_period=c).mean()
        df_dict[df].drop(["ma_fast","ma_slow"], axis=1, inplace=True)
        
        
def ATR(df_dict, n=14):
    for df in df_dict:
        df_dict[df]["H-L"] = df_dict[df]["high"] - df_dict[df]["low"]
        df_dict[df]["H-PC"] = abs(df_dict[df]["high"] - df_dict[df]["close"].shift(1))
        df_dict[df]["L-PC"] = abs(df_dict[df]["low"] - df_dict[df]["close"].shift(1))
        df_dict[df]["TR"] = df_dict[df][["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
        df_dict[df]["ATR"] = df_dict[df]["TR"].ewm(span=n, min_periods=n).mean()
        df_dict[df].drop(["H-L", "H-PC", "L-PC", "TR"], axis=1, inplace=True)


def BollBand(df_dict, n):
    for df in df_dict:
        df_dict[df]["MB"] = df_dict[df]["close"].rolling(n).mean()
        df_dict[df]["UB"] = df_dict[df]["MB"] + 2*df_dict[df]["close"].rolling(n).std(ddof=0)
        df_dict[df]["LB"] = df_dict[df]["MB"] - 2*df_dict[df]["close"].rolling(n).std(ddof=0)
        df_dict[df]["BB Width"] = df_dict[df]["UB"] - df_dict[df]["LB"]
        

def RSI(df_dict, n=14):
    for df in df_dict:
        df_dict["change"] = df_dict["close"] - df_dict["close"].shift(1)
        df_dict[df]["gain"] = np.where(df_dict[df]["change"]==0, df_dict[df]["change"], 0)
        df_dict[df]["loss"] = np.where(df_dict[df]["change"]<0, -1*df_dict[df]["change"], 0)
        df_dict[df]["avgGain"] = df_dict[df]["gain"].ewm(alpha = 1/n, min_periods=n).mean()
        df_dict[df]["avgLoss"] = df_dict[df]["loss"].ewm(alpha = 1/n, min_periods=n).mean()
        df_dict[df]["rs"] = df_dict[df]["avgGain"]/df_dict[df]["avgLoss"]
        df_dict["rsi"] = 100 - (100/(1+df_dict[df]["rs"]))
        df_dict[df].drop(["change","gain","loss","avgGain","avgLoss","rs"], axis=1, inplace=True)        


def stochastic(df_dict, lookback=14, k=3, d=3):
    for df in df_dict:
        df_dict[df]["HH"] = df_dict[df]["high"].rolling(lookback).max()
        df_dict[df]["LL"] = df_dict[df]["low"].rolling(lookback).min()
        df_dict[df]["%K"] = (100*(df_dict[df]["close"]-df_dict[df]["close"] - df_dict[df]["LL"])/(df_dict[df]["HH"]-df_dict[df]["LL"])).rolling(k).mean()
        df_dict[df]["%D"] = df_dict[df]["%K"].rolling(d).mean()