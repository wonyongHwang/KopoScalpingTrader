import talib as ta
import orderManager
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc  # pip install mplfinance

shcode = "005930"
accountId = 'YOUR ID'
password = 'YOUR PWD'
pkpwd = 'your cert password'

orderManager.Login(id=accountId, pwd=password, cert=pkpwd)
df = orderManager.t8412(단축코드=shcode, 단위="2", 요청건수="136")

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

macd, macdsignal, macdhist = ta.MACD(df['종가'], fastperiod=12, slowperiod=26, signalperiod=9)
macd = macd[~np.isnan(macd)]  # remove nan
macdsignal = macdsignal[~np.isnan(macdsignal)]  # remove nan
macdhist = macdhist[~np.isnan(macdhist)]  # remove nan
print("macd>> ",macd)

upper, middle, low = ta.BBANDS(df['종가'], 20, 3, 3)  # 3 sigma
upper = np.asarray(upper)
middle = np.asarray(middle)
low = np.array(low)

obv = ta.OBV(np.asarray(df['종가'], dtype=np.double), np.asarray(df['거래량'], dtype=np.double))
obvSignal = ta.MA(obv, timeperiod=9)

fastk, fastd = ta.STOCHF(high=df['고가'], low=df['저가'], close=df['종가'], fastk_period=12, fastd_period=3, fastd_matype=0) # SMA
fastk = fastk[~np.isnan(fastk)]
fastd = fastd[~np.isnan(fastd)]
print("fastk>> ", fastk)
print("fastd>> ", fastd)

slowk, slowd = ta.STOCH(high=df['고가'], low=df['저가'], close=df['종가'], fastk_period=12, slowk_period=3, slowk_matype=0,slowd_period=3,slowd_matype=0)
slowk = slowk[~np.isnan(slowk)]
slowd = slowd[~np.isnan(slowd)]
print("slowk>> ", fastk)
print("slowd>> ", fastd)

cci = ta.CCI(high=df['고가'], low=df['저가'], close=df['종가'],timeperiod=14)
cciSig = ta.MA(cci, timeperiod=9)
cci = cci[~np.isnan(cci)]
cciSig = cciSig[~np.isnan(cciSig)]
print("cci>> ",cci)

plt.figure(figsize=(30, 30))
plt.subplot(331)
plt.title(str(shcode))
plt.plot(obv)
plt.plot(obvSignal)
plt.legend(["obv", "obv signal"])

plt.subplot(332)
plt.plot(rsi9)
plt.plot(simpleMA9)
# plt.text(0, 10, "rg:" + str(format(grad, "3.2%")))
plt.legend(["rsi", "rsi signal"])

plt.subplot(333)
plt.plot(taadx)
plt.plot(taadxSig)
plt.legend(["adx", "adx sig"])

ax = plt.subplot(334)
dfnew = df[['시가', '고가', '저가', '종가']]
day_list = range(len(df))
dfnew.insert(0, '시각', day_list)
dfnew = dfnew.apply(pd.to_numeric)
candlestick_ohlc(ax, dfnew.values, width=0.5, colorup='r', colordown='b')

plt.subplot(335)
plt.title("MACD")
plt.plot(macd)
plt.plot(macdsignal)
plt.plot(macdhist)
plt.legend(["macd", "macdsignal","macdhist"])

plt.subplot(336)
plt.title("Bollinger Band")
plt.plot(upper)
plt.plot(middle)
plt.plot(low)
plt.legend(["upper", "middle","low"])

plt.subplot(337)
plt.title("Stochastic Fast  K={} D={}".format(12,3))
plt.plot(fastk)
plt.plot(fastd)
plt.legend(["fastk", "fastd"])

plt.subplot(338)
plt.title("Stochastic Slow K=%d D=%d" % (12,3))
plt.plot(slowk)
plt.plot(slowd)
plt.legend(["slowk", "slowd"])

plt.subplot(339)
plt.title("CCI")
plt.plot(cci)
plt.plot(cciSig)
plt.legend(["cci", "cciSig"])

plt.grid()
plt.show()
plt.close()



def hello():
    print("hello")

