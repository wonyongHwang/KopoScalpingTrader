import win32com.client
import pythoncom
import time
import queue

import winsound as ws

import orderManager
import dbManager
import talib as ta
import numpy as np
from pyfiglet import Figlet
from scipy import stats
import myPrint
from myPrint import print
from matplotlib import pyplot as plt
# import botManager
import os
from pandas import DataFrame
from mplfinance.original_flavor import candlestick_ohlc # pip install mplfinance
import pandas as pd

class MyPriorityQueue(queue.PriorityQueue):
    def __init__(self):
        queue.PriorityQueue.__init__(self)
        self.counter = 0

    def put(self, item, priority):
        queue.PriorityQueue.put(self, (priority, self.counter, item))
        self.counter += 1

    def get(self, *args, **kwargs):
        _, _, item = queue.PriorityQueue.get(self, *args, **kwargs)
        return item

class XASessionEvents:
    logInState = 0
    def OnLogin(self, code, msg):
        print("OnLogin method is called")
        print(str(code))
        print(str(msg))
        if str(code) == '0000':
            XASessionEvents.logInState = 1

    def OnLogout(self):
        print("OnLogout method is called")

    def OnDisconnect(self):
        print("OnDisconnect method is called")

# 거래량 상위 (반복)
class XAQueryEventsT1452:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT1452.query_state = 1

class XAQueryEventsT8430:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT8430.query_state = 1

if __name__ == "__main__":
    pythoncom.CoInitialize()
    t = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    now = time.localtime()
    myPrint.fnDebug = '[KOSDAQ] log_' + "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday) + '.txt'
    myPrint.fDebug = open(myPrint.fnDebug, 'a') #, buffering=1)

    server_addr = "hts.ebestsec.co.kr"
    server_port = 20001
    server_type = 0
    user_id = "your id"
    user_pass = "your password"
    user_certificate_pass = "your certification password"
    g_rsiTgt = 0
    g_simpleMA9Tgt = 0
    inXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
    inXASession.ConnectServer(server_addr, server_port)
    inXASession.Login(user_id, user_pass, user_certificate_pass, server_type, 0)

    dbInstance = dbManager.dbManager()
    while XASessionEvents.logInState == 0:
        pythoncom.PumpWaitingMessages()

    num_account = inXASession.GetAccountListCount()
    for i in range(num_account):
        account = inXASession.GetAccountList(i)
        print(account)

    #listT1452=[["null" for col in range(5)] for row in range(120)]
    listT1452 = [["null" for col in range(1)] for row in range(280)]
    # 전날 데이터 수신 (1: today 2: yesterday)
    def T1452(idx=0, isToday=1):
        # Exit Condition
        idxTemp = int(idx)
        print("idxTemp = ",idxTemp)
        if idxTemp >= 280 :
            return

        instXAQueryT1452 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT1452)
        instXAQueryT1452.ResFileName = "Res\\t1452.res"
        instXAQueryT1452.SetFieldData("t1452InBlock", "gubun", 0, "2") # 1: KOPSPI 2:KOSDAQ
        instXAQueryT1452.SetFieldData("t1452InBlock", "jnilgubun", 0, isToday)
        instXAQueryT1452.SetFieldData("t1452InBlock", "ediff", 0, "7")
        instXAQueryT1452.SetFieldData("t1452InBlock", "jc_num", 0, "139608960")
        instXAQueryT1452.SetFieldData("t1452InBlock", "eprice", 0, "100000")
        instXAQueryT1452.SetFieldData("t1452InBlock", "idx", 0, idx)
        instXAQueryT1452.Request(1)

        while instXAQueryT1452.query_state == 0:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.1)
        XAQueryEventsT1452.query_state = 0 # 중요

        idx = instXAQueryT1452.GetFieldData("t1452OutBlock", "idx", 0)
        count = instXAQueryT1452.GetBlockCount("t1452OutBlock1")
        print("idx = ", idx,"  count = ",count)
        #sql = "insert into DailyVolume(hname,price,sign,diff,volume,vol,shcode,jnilvolume,bef_diff,date) values (?,?,?,?,?,?, ?,?,?,?)"
        tempDate = "%04d-%02d-%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        for i in range(count):
            hname = instXAQueryT1452.GetFieldData("t1452OutBlock1", "hname", i)
            price = instXAQueryT1452.GetFieldData("t1452OutBlock1", "price", i)
            sign = instXAQueryT1452.GetFieldData("t1452OutBlock1", "sign", i)
            diff = instXAQueryT1452.GetFieldData("t1452OutBlock1", "diff", i)
            volume = instXAQueryT1452.GetFieldData("t1452OutBlock1", "volume", i) # 누적거래량
            vol = instXAQueryT1452.GetFieldData("t1452OutBlock1", "vol", i)  # 회전율
            shcode = instXAQueryT1452.GetFieldData("t1452OutBlock1", "shcode", i)
            jnilvolume = instXAQueryT1452.GetFieldData("t1452OutBlock1", "jnilvolume", i)
            bef_diff = instXAQueryT1452.GetFieldData("t1452OutBlock1", "bef_diff", i)
            listT1452[idxTemp+i] = [hname, price, sign, diff, volume, vol, shcode, jnilvolume, bef_diff]
            print(i, hname, price, sign, diff, volume, vol, shcode, jnilvolume, bef_diff)
        print("------------------------------------------------------------------------")
        print("재귀호출] idx ",idx)
        if int(idx) == 0 : # Xing API 응답에서 40개 미만의 데이터를 주고 끝나는 경우 idx가 0으로 응답된다. 무한재귀 호출에 빠지지 않도록 idx에 끝값을 대입한다.
            T1452(280, isToday=1)
        else :
            T1452(idx, isToday=1) # recursive call

    # 코스피 코드정보 조회 (0:all, 1: kospi, 2:kosdaq)
    def T8430(gubun=2):
        instXAQueryT8430 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT8430)
        instXAQueryT8430.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t8430.res"
        instXAQueryT8430.SetFieldData("t8430InBlock", "gubun", 0, gubun)
        instXAQueryT8430.Request(0)

        while XAQueryEventsT8430.query_state == 0:
            pythoncom.PumpWaitingMessages()
        XAQueryEventsT8430.query_state = 0

        count = instXAQueryT8430.GetBlockCount("t8430OutBlock")
        print("# of codes = ", count)
        myShcode = []
        for i in range(count):
            hname = instXAQueryT8430.GetFieldData("t8430OutBlock", "hname", i)
            shcode = instXAQueryT8430.GetFieldData("t8430OutBlock", "shcode", i)
            #expcode = instXAQueryT8430.GetFieldData("t8430OutBlock", "expcode", i)
            #etfgubun = instXAQueryT8430.GetFieldData("t8430OutBlock", "etfgubun", i)
            myShcode.append(shcode)
            print(i, hname, shcode)
        return myShcode

    def calcADI(df):
        res = []
        for i in range(0, df.shape[0]):
            # print(df['종가'].values[i], df['시가'].values[i], df['고가'].values[i], df['저가'].values[i])
            tmp = float(df['종가'].values[i]) - float(df['시가'].values[i])
            if float(df['고가'].values[i]) == float(df['저가'].values[i]):
                print("[ADI] 고가 = 저가", df['고가'].values[i], float(df['저가'].values[i]))
                tmp /= 1
            else:
                tmp /= (float(df['고가'].values[i]) - float(df['저가'].values[i]))
            tmp *= float(df['거래량'].values[i])
            res.append(tmp)
        adi = DataFrame(data=res, columns=["ADI"])
        return adi

    def rsiCheck(_shcode="",hname=''):
        global g_rsiTgt
        global g_simpleMA9Tgt
        now = time.localtime()
        tempToday = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        if not os.path.exists(tempToday):
            os.mkdir(tempToday)

        df1475 = orderManager.t1475(_shcode)
        if df1475.shape[0] == 0:
            print("t1475 responded null")
        elif df1475.shape[0] != 0 and float(df1475['당일VP'].values[0]) < 100:
            strTemp = "체결강도 100 미만으로 후보 탈락:" + hname
            print(strTemp)
            # botManager.sendTeleMsg(strTemp)
            return 0

        df = orderManager.t8412(단축코드=_shcode, 단위="2", 요청건수="36")

        if df.shape[0] > 0:  # rsi 9 구하기

            try:
                taadx = ta.ADX(df['고가'], df['저가'], df['종가'], 9)
                taadxSig = ta.MA(taadx, timeperiod=9)
                taadx = np.asarray(taadx)
                taadxSig = np.asarray(taadxSig)
                print("ADX ", taadx)
                print("ADX Sig", taadxSig)
                if float(taadx[-1]) <= float(taadxSig[-1]):
                    print("ADX condition mismatched")
                    return 0
                adxgrad, intercept, adi_r_square, p_value, std_err = stats.linregress(list(range(len(taadx[-30:-1]))), taadx[-30:-1])
                if adxgrad < 0 :
                    print("ADX downturn")
                    return 0
            except Exception as e:
                print("Exception Occur : ", e)

            # adi = calcADI(df)
            # # mincond = adi['ADI'] < 0
            # # adi = adi[mincond]
            # tempY = list(map(float, np.asarray(adi)))
            # sortTemp = sorted(tempY)
            # sortTemp = sortTemp[0:5]
            # print("저점 ADI: ",sortTemp)
            # newTempY = []
            # for i in tempY:
            #     if i in sortTemp:
            #         newTempY.append(i)
            # print("저점 정렬 ADI: ", newTempY)
            # tempX = list(range(len(newTempY)))
            # adigrad, intercept, adi_r_square, p_value, std_err = stats.linregress(tempX, newTempY)
            # print("adi 저점정보", adigrad, intercept, adi_r_square, p_value, std_err)

            rsi9 = ta.RSI(np.asarray(df['종가']), 9)
            rsi9 = rsi9[~np.isnan(rsi9)]  # remove nan
            if rsi9.size == 0:
                print("rsi size exception")
                return 0
            rsiTgt = rsi9[-1]
            simpleMA9 = ta.MA(rsi9, timeperiod=9)

            simpleMA9Tgt = simpleMA9[-1]
            print('----------[RSI SIGNAL JUDGE]----------')
            if np.isnan(rsiTgt) == True or  np.isnan(simpleMA9Tgt) == True :
                print("Not Enough Data")
                return 1
            if int(rsiTgt) < int(simpleMA9Tgt): # or int(rsiTgt) >= 75:
                print('rsi', rsiTgt, 'signal', simpleMA9Tgt)
                return 1
            # elif int(rsiTgt) > int(simpleMA9Tgt) and int(rsiTgt) <= 30:
            #     print('rsi > ', rsiTgt, '>', 'signal', simpleMA9Tgt)
            #     g_rsiTgt = round(rsiTgt, 2)
            #     g_simpleMA9Tgt = round(simpleMA9Tgt,2)
            #     return 2
            obv = ta.OBV(np.asarray(df['종가'], dtype = np.double), np.asarray(df['거래량'], dtype = np.double))

            if obv[-1] < 8000 :
                print("latest obv cut", obv[-1])
                return 1
            if obv[-1] - obv[-3] <= 0 or obv[-1] - obv[-2] <= 0 :
                print("obv is downturned")
                return 1
            obvSignal = ta.MA(obv, timeperiod=9)
            #obvSignal = obvSignal[~np.isnan(obvSignal)]
            # if obvSignal[-1] < 0:
            #     print("latest obv signal is under zero")
            #     return 1
            tempX = list(range(len(obv)))
            tempY = list(map(float, obv))

            obvgrad, intercept, r_square, p_value, std_err = stats.linregress(tempX, tempY)
            print("OBV ",obvgrad, intercept, r_square, p_value, std_err)
            # if obvgrad <=0:
            #     print("OBV grad <= 0")
            #     return 1
            tempXSignal = list(range(len(obvSignal)))
            tempYSignal = list(map(float, obvSignal))
            tempXSignal = tempXSignal[-16:-1]
            tempYSignal = tempYSignal[-16:-1]
            obvSignalgrad, intercept, r_square, p_value, std_err = stats.linregress(tempXSignal, tempYSignal)
            print("OBV Signal ", obvSignalgrad, intercept, r_square, p_value, std_err)
            if obvSignalgrad <=0:
                print("obvSignalgrad grad <= 0")
                return 1

            # plt.show()
            # print(obv)
            # print(obvSignal)
            #obv always above 0, but signal can be lower than 0
            if obv[-1] < obvSignal[-1] or obv[-2] < obvSignal[-2]:
                print("Signal Condition Unsuited")
                return 1

            # if abs(obvSignal[-1]) / (obv[-1] + (obvSignal[-1] < 0 and abs(obvSignal[-1]) or 0)) > 0.9 or abs(obvSignal[-2]) / (obv[-2]+(obvSignal[-1] < 0 and abs(obvSignal[-1]) or 0)) > 0.9:
            #     print("OBV Gap Flattened")
            #     return 1


            # RSI Gap Condition Check : reg grad +,  abs(gap[-1]) < 10
            # rsiGap = rsi9 - simpleMA9
            # rsiGap = rsiGap[~np.isnan(rsiGap)]
            # rsiGap = abs(rsiGap)
            # print("rsi gap : ", rsiGap)
            # tempX = list(range(len(rsiGap)))
            # tempY = list(map(float, rsiGap))
            # tempX = tempX[-8:-1]
            # tempY = tempY[-8:-1]
            # g_rsiTgt = round(rsiTgt, 2)
            # g_simpleMA9Tgt = round(simpleMA9Tgt, 2)
            # grad, intercept, r_square, p_value, std_err = stats.linregress(tempX, tempY)
            # print("regression result: ", grad, intercept, r_square, p_value, std_err)
            # print("type rsi... ",type(rsi9[-1]))

            if rsi9[-1] - rsi9[-3] <= 0 or rsi9[-1] - rsi9[-2] <= 0 :
                print("rsi is downturned")
                return 0
            print("type simpleMA9... ",type(simpleMA9[-1]))
            # if grad <= 0 and rsi9[-1] > simpleMA9[-1] and rsi9[-2] > simpleMA9[-2]: # and r_square <= -0.6 and p_value < 0.05 and rsiGap[-2] >= rsiGap[-1]:
            if rsi9[-1] > simpleMA9[-1] and rsi9[-2] > simpleMA9[-2]:  # and r_square <= -0.6 and p_value < 0.05 and rsiGap[-2] >= rsiGap[-1]:
                # gapFlag = 0
                # for i in tempY:
                #     if i > 11:
                #         gapFlag += 1
                # if gapFlag < 2:
                #     print("no rsi condition(gap flag is flatten) matched")
                #     return 0
                print("RSI Gap Condition Check OK")
                plt.figure(figsize=(30, 30))
                plt.subplot(221)
                plt.title(str(_shcode))
                plt.plot(obv)
                plt.plot(obvSignal)
                plt.text(0, 10, "og:" + str(format(obvgrad, "8.2%")))
                plt.legend(["obv", "obv signal"])
                # tempStr = tempToday + "/" + str(_shcode) + " obv" + ".png"
                # plt.savefig(tempStr)
                # botManager.sendImage(tempStr)
                plt.subplot(222)
                plt.plot(rsi9)
                plt.plot(simpleMA9)
                # plt.text(0, 10, "rg:" + str(format(grad, "3.2%")))
                plt.legend(["rsi", "rsi signal"])

                # plt.subplot(413)
                # plt.plot(newTempY)
                # plt.text(0, newTempY[0], "g"+str(format(adigrad,"3.2%"))+"r^2:" + str(format(adi_r_square*adi_r_square,"3.2%")))
                # plt.legend(["new adi"])

                plt.subplot(223)
                plt.plot(taadx)
                plt.plot(taadxSig)
                plt.text(20, taadxSig[-1], "g:" + str(format(adxgrad, "3.2%")))
                plt.legend(["adx","adx sig"])

                ax = plt.subplot(224)
                dfnew = df[['시가', '고가', '저가', '종가']]
                day_list = range(len(df))
                dfnew.insert(0, '시각', day_list)

                #dfnew = dfnew.set_index('날짜')
                dfnew = dfnew.apply(pd.to_numeric)
                candlestick_ohlc(ax, dfnew.values, width=0.5, colorup='r', colordown='b')
                plt.grid()

                tempStr = tempToday + "/" + str(_shcode) +" "+ hname+ ".png"
                plt.savefig(tempStr)
                plt.close()
                # botManager.sendImage(tempStr)
                # msrate check added

                return 3
            else :
                print("no rsi condition matched")
                return 0
        print("RSI Calc Err")
        return 0
    def checkExcludedList(hname):
        if hname.startswith("KODEX") == True:
            return True
        elif hname.startswith("TIGER") == True:
            return True
        elif hname.startswith("KBSTAR") == True:
            return True
        elif hname.startswith("KINDEX") == True:
            return True
        elif hname.startswith("ARIRANG") == True:
            return True
        elif hname.startswith("KOSEF") == True:
            return True
        elif hname.startswith("WTI") == True:
            return True
        elif hname.startswith("맥쿼리") == True:
            return True
        elif ('금융' in hname) == True: # 금융주 제외
            return True
        elif ('증권' in hname) == True:  # 금융주 제외
            return True
        elif ('WTI' in hname) == True:
            return True
        elif ('&' in hname) == True:
            return True
        else:
            return False

    def strategy2(_shcode, tempDate,refname=''):
        print("종목명:", refname)
        if checkExcludedList(refname) == True:
            return
        now = time.localtime()
        strTempTime = "%02d%02d%02d" % (now.tm_hour, now.tm_min, now.tm_sec)

        # tdf8412 = orderManager.t8412(단축코드=_shcode, 단위="10", 요청건수="60", 시작일자="", 종료일자="99999999", cts_date="",
        #                              comp_yn="N")
        # if tdf8412.shape[0] == 0:
        #     print('[ERR] 8412 주식차트(10분) 조회 불가')
        #     return
        # tempX = list(range(tdf8412.shape[0]))
        # tempY = list(map(int, tdf8412["종가"]))
        # tempX = tempX[-10:-1]
        # tempY = tempY[-10:-1]
        # grad, intercept, r_square, p_value, std_err = stats.linregress(tempX, tempY)
        # print(grad, intercept, r_square, p_value, std_err)
        #
        # if grad < 0:
        #     return
        #
        # ma60 = ta.MA(np.asarray(tdf8412['종가']), timeperiod=60)
        # ma60 = ma60[~np.isnan(ma60)]
        # if len(ma60) == 0:
        #     print("MA60 Error")
        #     return
        # print("regression result(10분봉): ", grad, intercept, r_square, p_value, std_err)
        # print("10분봉 종가", tdf8412["종가"].values[-1], "VS 60MA", ma60[-1])
        # if int(tdf8412["종가"].values[-1]) <= int(ma60[-1]):
        #     return
        rsiRes = rsiCheck(_shcode=_shcode, hname=refname)
        if rsiRes == 2 or rsiRes == 3:
            close15mma = "0" # round(tdf8412["종가"].values[-1], 2)
            close60dma = "0" # round(ma60[-1], 2)
            beepsound(freq=1000, dur=1500)
            now = time.localtime()
            if now.tm_hour <= 15:
                if now.tm_hour == 15 and now.tm_min >= 30:
                    pass
                else:
                    dbInstance.insertObserverList(_shcode, tempDate, strTempTime, '', '', '', '', "1", str(rsiRes))
            tmpStr = "KOSDAQ 종목: "+ refname+ " 포착시각 : "+ str(now.tm_hour)+ ":"+ str(now.tm_min) # +" 현재가: "+str(tdf8412["종가"].values[-1])
            print(tmpStr)
            # botManager.sendTeleMsg(tmpStr)
            dbInstance.insertDailyRecommendList(_shcode, tempDate, "KOSDAQ", str(close15mma), str(close60dma), str(g_rsiTgt), str(g_simpleMA9Tgt), strTempTime, refname, str(rsiRes))

    # strategy1 : 상승호가에서 프로그램 매수 유입시 매도
    def strategy1(_shcode, tempDate, msrate, bidrem1, offerrem1, price, skip=False, refname=''):
        print("PG 순매수 스킵여부 :", skip, "종목명:", refname)
        now = time.localtime()
        strTempTime = "%02d%02d%02d" % (now.tm_hour, now.tm_min, now.tm_sec)
        prognetbuy = 0
        if skip == False :
            df = orderManager.t1636(구분="1",종목코드=_shcode)
            tmpDf = df['종목코드'] == _shcode
            df = df[tmpDf]
            if df.shape[0] == 0:
                print("프로그램 추세 정보 알 수 없음(%s)" % _shcode)
                return
            # for i in range(0, df.shape[0]):
            #     if df["종목코드"].values[i] == _shcode:
            print("종목명:", df["종목명"].values[0], "종목코드:",_shcode)
            print("순위:", df["순위"].values[0], "종목명:", df["종목명"].values[0], "현재가:", df["현재가"].values[0], \
                  "대비구분:", df["대비구분"].values[0], "대비:", df["대비"].values[0], "등락률:", df["등락률"].values[0], \
                  "거래량:", df["거래량"].values[0], "순매수수량:", df["순매수수량"].values[0], "비중:",
                  df["비중"].values[0],
                  "순매수금액", df["순매수금액"].values[0], "매수금액", df["매수금액"].values[0])
            prognetbuy = float(df["순매수금액"].values[0])
        if skip == True or prognetbuy > 0 : # float(df["등락률"].values[0]) > 0 and float(df["순매수금액"].values[0]) > 0:
           tdf8412 = orderManager.t8412(단축코드=_shcode, 단위="15", 요청건수="1", 시작일자="", 종료일자="99999999", cts_date="",
                                         comp_yn="N")
           if tdf8412.shape[0] == 0 :
                print('[ERR] 8412 주식차트(분) 조회 불가')
                return
           close15mma = tdf8412.iloc[-1]['종가']
           print('close15mma', close15mma)
           tdf8413 = orderManager.t8413(단축코드=_shcode, 요청건수='60')
           if tdf8413.shape[0] == 0:
                print('[ERR] 8413 주식차트(일) 조회 불가')
                return
           pandas_ma60 = tdf8413['종가'].rolling(window=60).mean()  # tdf8413.종가.rolling(window=60).mean()
           close60dma = pandas_ma60.iloc[-1]
           print('close60dma', close60dma)
           if np.isnan(close60dma) == True:
               return
           if int(close15mma) > int(close60dma):
                tdf8412 = orderManager.t8412(단축코드=_shcode, 단위="10", 요청건수="10", 시작일자="", 종료일자="99999999", cts_date="", comp_yn="N")
                if tdf8412.shape[0] == 0:
                    print('[ERR] 8412 주식차트(10분) 조회 불가')
                    return
                tempX = list(range(tdf8412.shape[0]))
                tempY = list(map(int, tdf8412["종가"]))
                grad, intercept, r_square, p_value, std_err = stats.linregress(tempX, tempY)
                print(grad, intercept, r_square, p_value, std_err)

                if grad < 0:
                    return

                tdf8412 = orderManager.t8412(단축코드=_shcode, 단위="10", 요청건수="60", 시작일자="", 종료일자="99999999", cts_date="", comp_yn="N")
                ma60 = ta.MA(np.asarray(tdf8412['종가']), timeperiod = 60)
                ma60 = ma60[~np.isnan(ma60)]
                print("regression result(10분봉): ", grad, intercept, r_square, p_value, std_err)
                print("10분봉 종가", tdf8412["종가"].values[-1],"VS 60MA",ma60[-1] )
                if int(tdf8412["종가"].values[-1]) <= int(ma60[-1]):
                    return

                rsiRes = rsiCheck(_shcode=_shcode,hname=refname)
                if rsiRes == 2 or rsiRes == 3:
                    close15mma = round(close15mma, 2)
                    close60dma = round(close60dma, 2)
                    beepsound(freq=1000, dur=1500)
                    now = time.localtime()

                    if now.tm_hour <= 15 :
                        if now.tm_hour == 15 and now.tm_min >= 30:
                            pass
                        else:
                            dbInstance.insertObserverList(_shcode, tempDate, strTempTime, msrate, bidrem1, offerrem1, price, "1",  str(rsiRes))
                    if skip == True:
                        print("종목: ", refname, "포착시각 : ", now.tm_hour, ":", now.tm_min)
                        dbInstance.insertDailyRecommendList(_shcode, tempDate, "KOSPI", str(close15mma), str(close60dma), str(g_rsiTgt), str(g_simpleMA9Tgt), strTempTime, refname, str(rsiRes))
                    else:
                        print("종목: ", df["종목명"].values[0], "포착시각 : ", now.tm_hour, ":", now.tm_min)
                        dbInstance.insertDailyRecommendList(_shcode, tempDate, "KOSPI", str(close15mma), str(close60dma), str(g_rsiTgt), str(g_simpleMA9Tgt), strTempTime, df["종목명"].values[0], str(rsiRes))


    # strategy3 : 15분봉 RSI 저점 상승 & 30상승 돌파시  & 15분봉 vs 60일선 돌파 : 매수
    #             15분봉 RSI 고점 하락 & 70하락 돌파시   : 매도

    def searchCandidates(condtion=1):
        now = time.localtime()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)

        # strategy1("078860", tempDate, '', '', '', '', skip=False, refname="아이오케이")

        if condtion == 1:
            dft1533 = orderManager.t1533("1")

            for i in range(0, 3):
                df = orderManager.t1537(dft1533["테마코드"].values[i])
                for j in range(0, df.shape[0]):
                    print("[테마] 종목명", df["종목명"].values[j], "종목코드", df["종목코드"].values[j])
                    strategy2(df["종목코드"].values[j], tempDate, refname=df["종목명"].values[j])

            df1, df2 = orderManager.t1825(검색코드="6412", 구분="2") #양음양 6006 # 거래량 6412
            for i in range(0, df2.shape[0]):
                # strategy1(df2["종목코드"].values[i], tempDate, '', '', '', '',skip=False,refname=df2["종목명"].values[i])
                strategy2(df2["종목코드"].values[i], tempDate, refname=df2["종목명"].values[i])
            df1, df2 = orderManager.t1825(검색코드="6306", 구분="2") #프로그램순매수 100
            for i in range(0, df2.shape[0]):
                # strategy1(df2["종목코드"].values[i], tempDate, '', '', '', '', skip=True, refname=df2["종목명"].values[i])
                strategy2(df2["종목코드"].values[i], tempDate, refname=df2["종목명"].values[i])
        else :
            for idx, row in enumerate(listT1452):
                # t1471i = T1471.XAT1471()
                # ret = T1471.T1471_SearchBuyCandidates(row[6])
                # if ret == None:
                #     pass
                # else:
                #     (_shcode, tempDate, strTempTime, msrate, bidrem1, offerrem1, price) = ret
                #     strategy1(_shcode, tempDate, strTempTime, msrate, bidrem1, offerrem1, price)

                print(">>>", idx, row[0])
                if row[0] == "null" :
                    return
                # strategy1(row[6], tempDate, '', '', '', '',skip=False, refname=row[0])
                strategy2(row[6], tempDate, row[0])
                # time.sleep(3)

    def rollout():
        now = time.localtime()
        start = time.time()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        dbInstance = dbManager.dbManager()
        res = dbInstance.selectDailyRecommendList("KOSDAQ",tempDate)
        for idx, row in enumerate(res):
            print(">>>", idx, "shcode", row["shcode"])
            # strategy1(row["shcode"], tempDate, '', '', '', '',skip=False, refname=row["hname"])
            strategy2(row["shcode"], tempDate, row["hname"])

            # time.sleep(3)
        print("rollout 수행 시간: ", time.time() - start)


    def beepsound(freq=1000, dur=1000):
        ws.Beep(freq, dur)



    while True:
        f = Figlet(font='slant')
        now = time.localtime()
        print(f.renderText('K O P O'))
        #beepsound()
        #now = time.localtime()
        # strategy1('096040','', '', '', '', '', skip=True, refname='이트론' )

        rollout()
        #else:
        start = time.time()
        n = time.localtime().tm_wday
        # T1452()
        if t[n] == 'sat' or t[n] == 'sun':
            T1452()
            searchCandidates(condtion=2)
            print("searchCandidates 수행 시간: ", time.time() - start)
            break

        if now.tm_hour <= 15 :
            if (now.tm_hour == 15 and now.tm_min >= 30) or now.tm_hour < 9 :
                T1452()
                searchCandidates(condtion=2)
                print("searchCandidates 수행 시간: ", time.time() - start)
                break
            else :
                searchCandidates(condtion=1)
        else:
            T1452()
            searchCandidates(condtion=2)
            print("searchCandidates 수행 시간: ", time.time() - start)
            break
        print("searchCandidates 수행 시간: ", time.time() - start)


    pythoncom.CoUninitialize()







