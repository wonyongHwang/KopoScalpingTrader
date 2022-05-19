import talib as ta
import orderManager
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc # pip install mplfinance

shcode = "005930"
accountId = 'YOUR ID'
password = 'YOUR PWD'
pkpwd = 'your cert password'


orderManager.Login(id=accountId, pwd=password, cert=pkpwd)
df = orderManager.t8412(단축코드=shcode, 단위="2", 요청건수="36")

taadx = ta.ADX(df['고가'], df['저가'], df['종가'], 9)
taadxSig = ta.MA(taadx, timeperiod=9)
taadx = np.asarray(taadx)
taadxSig = np.asarray(taadxSig)
print("ADX ", taadx)
print("ADX Sig", taadxSig)

rsi9 = ta.RSI(np.asarray(df['종가']), 9)
rsi9 = rsi9[~np.isnan(rsi9)]  # remove nan
if rsi9.size == 0:
    print("rsi size exception")
simpleMA9 = ta.MA(rsi9, timeperiod=9)


obv = ta.OBV(np.asarray(df['종가'], dtype = np.double), np.asarray(df['거래량'], dtype = np.double))
obvSignal = ta.MA(obv, timeperiod=9)

plt.figure(figsize=(30, 30))
plt.subplot(221)
plt.title(str(shcode))
plt.plot(obv)
plt.plot(obvSignal)
plt.legend(["obv", "obv signal"])

plt.subplot(222)
plt.plot(rsi9)
plt.plot(simpleMA9)
# plt.text(0, 10, "rg:" + str(format(grad, "3.2%")))
plt.legend(["rsi", "rsi signal"])

plt.subplot(223)
plt.plot(taadx)
plt.plot(taadxSig)
plt.legend(["adx", "adx sig"])

ax = plt.subplot(224)
dfnew = df[['시가', '고가', '저가', '종가']]
day_list = range(len(df))
dfnew.insert(0, '시각', day_list)
dfnew = dfnew.apply(pd.to_numeric)
candlestick_ohlc(ax, dfnew.values, width=0.5, colorup='r', colordown='b')
plt.grid()
plt.show()
plt.close()
