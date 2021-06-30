import threading, time
import dbManager
import orderManager
import pythoncom
import talib as ta
import numpy as np
import myPrint
from myPrint import print
import pandas as pd
from google.cloud import texttospeech
from playsound import playsound
import os
# import botManager
class XAQueryEventsT1471:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT1471.query_state = 1


class SellAgent(threading.Thread):
    accountId = 'your id'
    accountNumber = 'your account number' 
    accountPwd = 'your accound password (4 digit number)'
    password = 'your passowrd'
    pkpwd = 'your cert password'
    ordqty = 1
    numberOfPortfolio = 5
    principalNfee = 0.01026
    tolerance = 0.001
    stdmsrate = 80
    sleeptime = 15
    # balanced2 = 0
    # netAssest = 0

    def __init__(self):
        threading.Thread.__init__(self)

    def prgCheck(self, _shcode=""):
        dbInstance = dbManager.dbManager()
        res = dbInstance.selectGubunRecommendList(_shcode)
        if len(res) != 0 :
            gubun = res[0]["gubun"] == "KOSPI" and "0" or "1"
        else :
            print("no info exists in recommendList")
            return False

        df = orderManager.t1636(구분=gubun, 종목코드=_shcode)
        tmpDf = df['종목코드'] == _shcode
        df = df[tmpDf]
        if df.shape[0] == 0:
            print("프로그램 추세 정보 알 수 없음(%s)" % _shcode)
            return False
        # for i in range(0, df.shape[0]):
        #     if df["종목코드"].values[i] == _shcode:
        print("종목명:", df["종목명"].values[0], "종목코드:", _shcode)
        print("순위:", df["순위"].values[0], "종목명:", df["종목명"].values[0], "현재가:", df["현재가"].values[0], \
              "대비구분:", df["대비구분"].values[0], "대비:", df["대비"].values[0], "등락률:", df["등락률"].values[0], \
              "거래량:", df["거래량"].values[0], "순매수수량:", df["순매수수량"].values[0], "비중:",
              df["비중"].values[0],
              "순매수금액", df["순매수금액"].values[0], "매수금액", df["매수금액"].values[0])
        if float(df["순매수금액"].values[0]) <= 0:
            return True # 매도
        else :
            return False
    def msmdVolumeCheck(self, _shcode):
        df1471o, df1471ob = orderManager.t1471(종목코드=_shcode, 분구분="00", 자료개수="001") # 30초 단위 매수/매도 호가물량 점검
        totofferrem = df1471ob["총매도"].values[0]
        totbidrem = df1471ob["총매수"].values[0]
        msrate = df1471ob["매수비율"].values[0]
        print("현재가", df1471o["현재가"].values[0], "총매도:", totofferrem, "총매수:", totbidrem, "체결강도:", msrate, "매도우선잔량",df1471ob["매도우선잔량"].values[0],"매수우선잔량",df1471ob["매수우선잔량"].values[0])
        if totofferrem * 2 < totbidrem or float(msrate) < 100.0:
            return True

    def checkBaseLine(self, df='', curPrice=0):
        #     dfnew = dfnew.apply(pd.to_numeric)
        if df.shape[0] < 10:
            print("df size is under 10")
            return False

        df = df.iloc[:10, :]
        print(df.shape[0])
        for i in range(df.shape[0] - 1, 2, -1):
            print(i)
            print("종가", df["종가"].values[i], "종가 -1봉", df["종가"].values[i - 1], "종가 -2봉", df["종가"].values[i - 2])
            if float(df["종가"].values[i]) >= float(df["종가"].values[i - 1]) * 1.01 or float(df["종가"].values[i]) >= float(df["종가"].values[i - 2]) * 1.01:
                basePrice = float(df["종가"].values[i]) / 2
                if basePrice > curPrice:
                    print("저지선", basePrice, "> 현재가", curPrice)
                    return True
        return False

    def weirdConditionCheck(self, shcode, hname):
        totcnt = 0
        totmdvolume = totmsvolume = 0
        for i in range(0, 5):
            if i == 0:
                df, df1 = orderManager.t1310(종목번호=shcode)
                # print(df1.head(20))
            else:
                df, df1 = orderManager.t1310(종목번호=shcode, 종료시간=df["시간CTS"].values[0], CTS=df["시간CTS"].values[0])
                # print(df1.head(20))
            if df1.shape[0] == 0 :
                print("t1310 responded null and we skip abnormal tr check")
                return False
            df1 = df1.apply(pd.to_numeric)
            tmpdf = df1[df1['체결수량'].lt(12)]
            totcnt += int(tmpdf.shape[0])
            totmdvolume += (df1['매도체결수량'].values[0] - df1['매도체결수량'].values[-1])
            totmsvolume +=  (df1['매수체결수량'].values[0] - df1['매수체결수량'].values[-1])
        print("이상 매매 건수:", totcnt,"총매도체결수량:",totmdvolume,"총매수체결수량:",totmsvolume)

        if totmdvolume > totmsvolume :
            print("매도세 우위로 매수 포기")
            SellAgent.ttsAlert(self, shcode, hname, totmdvolume - totmsvolume)
            return True
        else:
            return False

    def rsiCheck(self, msprice, _shcode="", curPrice=0):

        df = orderManager.t8412(단축코드=_shcode, 단위="2", 요청건수="36")

        if df.shape[0] > 0:  # rsi 9 구하기
            upper, middle, low = ta.BBANDS(df['종가'], 20, 2, 2)
            upper = np.asarray(upper)
            # middle = np.asarray(middle)
            print("볼린저 상한:", upper[-1], "종가:", df['종가'].values[-1])
            dbInstance = dbManager.dbManager()
            now = time.localtime()
            tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
            if float(upper[-1]) <= float(df['종가'].values[-1]):  # mark that record
                dbInstance.updateOrdListBB(_shcode, tempDate)
                if msprice * 1.013 <= df['종가'].values[-1]:
                    print("RSI 조건(BB상단 돌파 및 1% 수익)에 의하여 50%매도")
                    return 2
            elif float(upper[-1]) > float(df['종가'].values[-1]):
                res = dbInstance.selectOrdListBB(_shcode, tempDate)
                if len(res) != 0:
                    print("BB 상한 돌파 이력 조회 결과:", res[0]['reserve2'])
                    if res[0]['reserve2'] == '1':
                        print("BB 상한 + -> - 로 매도")
                        return 1

            rsi9 = ta.RSI(np.asarray(df['종가']), 9)
            rsi9 = rsi9[~np.isnan(rsi9)]  # remove nan
            if rsi9.size == 0:
                print("rsi size exception")
                return -1
            rsiTgt = rsi9[-1]
            simpleMA9 = ta.MA(rsi9, timeperiod=9)

            simpleMA9Tgt = simpleMA9[-1]
            # print('----------[RSI SIGNAL JUDGE]----------')
            if rsiTgt < simpleMA9Tgt :
                print('rsi', rsiTgt, '<', 'signal', simpleMA9Tgt)
                #df = orderManager.t8412(단축코드=_shcode, 단위="5", 요청건수="36")
                simpleMA5 = ta.MA(np.asarray(df['종가'], dtype = np.double), timeperiod=5)
                simpleMA20 = ta.MA(np.asarray(df['종가'], dtype=np.double), timeperiod=20)
                print("종가:", df['종가'].values[-1], "5MA: ", simpleMA5[-1],"20MA", simpleMA20[-1])
                taadx = ta.ADX(df['고가'], df['저가'], df['종가'], 9)
                taadxSig = ta.MA(taadx, timeperiod=9)
                taadx = np.asarray(taadx)
                taadxSig = np.asarray(taadxSig)
                if float(taadx[-1]) <= float(taadxSig[-1]):
                    if float(simpleMA5[-1]) <= float(df['종가'].values[-1]) :
                        return 0
                else:
                    if float(simpleMA20[-1]) <= float(df['종가'].values[-1]) :
                        return 0
                return 1 # 매도
            # elif rsiTgt >= 75 and rsiTgt <= 80: # 75
            #     df = orderManager.t8412(단축코드=_shcode, 단위="2", 요청건수="3")
            #     if df.shape[0] == 0 :
            #         print("분봉 정보 조회 불가")
            #         return False
            #     if df['종가'].values[-1] < df['종가'].values[-2] and df['종가'].values[-2] < df['종가'].values[-3] :
            #         print("RSI 75~80 에서 하락 2봉으로 매도")
            #         return True
            #     SellAgent.sleeptime = 60
            #     return False
            elif rsiTgt > 75:
                # df = orderManager.t8412(단축코드=_shcode, 단위="2", 요청건수="36")
                # check if close price > BB upper bound
                if df['종가'].values[-1] < df['종가'].values[-2] and df['종가'].values[-2] < df['종가'].values[-3] :
                    simpleMA5 = ta.MA(np.asarray(df['종가'], dtype=np.double), timeperiod=5)
                    if float(df['종가'].values[-1]) < float(simpleMA5[-1]) :
                        print("RSI 75 초과에서 하락 2봉 + 5MA(2min) 이하로 매도 ", simpleMA5[-1])
                        return 1
                    else:
                        return 0
                # 매수 1,2 호가 물량 체크
                # elif SellAgent.msmdVolumeCheck(self, _shcode) == True:
                #     print("총매수 잔량 조건으로 50% 매도")
                #     return 2

                simpleMA10 = ta.MA(np.asarray(df['종가'], dtype=np.double), timeperiod=10)
                print("종가:", df['종가'].values[-1], "10MA(2Min.): ", simpleMA10[-1])
                if float(simpleMA10[-1]) > float(df['종가'].values[-1]):
                    return 1
                return 0
                # 장대양봉 존재할 경우, 장대양봉의 중간 지지선 붕괴 여부 검사
            elif SellAgent.checkBaseLine(self, df, float(curPrice)) == True:
                print("장대양봉의 지지선 붕괴로 매도")
                return 1
            else :
                print('rsi > ', rsiTgt, '>', 'signal', simpleMA9Tgt)
                return 0

        return 0

    def getOneUnderHoga(self, shcode, price): # 1: KOPSI, 2:KOSDAQ
        price = int(price)
        ret = price
        dbInstance = dbManager.dbManager()
        res = dbInstance.selectGubunRecommendList(shcode)
        if len(res) == 0:
            print("unknown code yet in recommend list")
            return ret
        print("[호가조정] 종목명: ",res[0]['hname']," 구분: " , res[0]['gubun'])
        gubun  = res[0]['gubun']
        if price < 1000 :
            ret -= 1
        elif price >= 1000 and price < 5000:
            ret -= 5
        elif price >= 5000 and price < 10000:
            ret -= 10
        elif price >= 10000 and price < 50000:
            ret -= 50
        elif price >= 50000 and price < 100000:
            ret -= 100
        elif price >= 100000 and price < 500000:
            temp = gubun == 1 and 500 or 100
            ret -= temp
        elif price >= 500000 :
            temp = gubun == 1 and 1000 or 100
            ret -= temp
        else :
            print("호가 알 수 없음")
        return str(ret)

    def ttsAlert(self, alertCode, hname, diff):
        client = texttospeech.TextToSpeechClient()
        # Set the text input to be synthesized
        tmpStr = hname + " 매도 경고" # + str(diff)
        print(tmpStr + str(diff))
        synthesis_input = texttospeech.SynthesisInput(text=tmpStr)

        if not os.path.exists("alert"):
            os.mkdir("alert")
        if os.path.isfile("alert/" + alertCode + ".mp3") == True:
            playsound("alert/" + alertCode + ".mp3")
        else:  # 해당 종목코드 mp3가 존재하지 않을경우,
            # Build the voice request, select the language code ("en-US") and the ssml
            # voice gender ("neutral")
            voice = texttospeech.VoiceSelectionParams(language_code="ko-KR",ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
            # Select the type of audio file you want returned
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            # Perform the text-to-speech request on the text input with the selected
            # voice parameters and audio file type
            response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            with open("alert/" + alertCode + ".mp3", "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
            playsound("alert/" + alertCode + ".mp3")
            # os.remove("output.mp3") # playsound(None)

    def run(self):
        pythoncom.CoInitialize()
        orderManager.Login(id=SellAgent.accountId, pwd=SellAgent.password, cert=SellAgent.pkpwd)
        # instXAQueryT1471 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT1471)
        # instXAQueryT1471.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1471.res"
        now = time.localtime()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        dbInstance = dbManager.dbManager()

        cnt = 0
        while True :
            # print(cnt, "회전(Sell Manager)")
            # botManager.queryMine(isToday=True) # ,date='20201209')

            cnt += 1

            df1, df2 = orderManager.t0424(SellAgent.accountNumber, SellAgent.accountPwd, 체결구분='2')  # 계좌번호, 비밀번호
            while df2.shape[0] == 0 :
                df1, df2 = orderManager.t0424(SellAgent.accountNumber, SellAgent.accountPwd, 체결구분='2')  # 계좌번호, 비밀번호
                print("보유 종목 갯수 : ", df2.shape[0])
                time.sleep(1)

            sellyn = False
            sellHalfYn = False

            for i in range(0,df2.shape[0]):
                tmpres = dbInstance.selectUserControlListByShcode(df2["종목번호"].values[i],tempDate)
                if len(tmpres) != 0 and tmpres[0]['undercontrol'] == 'Lock':
                    print('수동 컨트럴 중으로 skip')
                    continue

                print("종목번호:", df2["종목번호"].values[i],"종목명:", df2["종목명"].values[i],"평균단가:", df2["평균단가"].values[i], \
                      "현재가:", df2["현재가"].values[i],"매도가능수량:", df2["매도가능수량"].values[i],"잔고수량:", df2["잔고수량"].values[i])
                if df2["매도가능수량"].values[i] != df2["잔고수량"].values[i] :
                    # 기존 매도주문 취소 및 reset (잔고수량과 매도가능수량이 다른 경우는 이미 매도주문이 들어가서 부분 매도된 경우이다.)
                    # 이러한 경우는 남은 물량을 현재가로 정정주문(매도) 한다.
                    # 잔고 수량 - 매도가능수량
                    # 모의투자 정정주문은 시장가 지정 불가능
                    ordno = dbInstance.selectOrdNo(str(df2["종목번호"].values[i]),tempDate)
                    if len(ordno) == 0 : # HTS 등 타 시스템에서 주문한 경우 스킵
                        continue
                    print("[정정주문] 원주문번호: ",ordno[0]['ordno'])
                    orderRes = orderManager.CSPAT00700(ordno[0]['ordno'], SellAgent.accountNumber, SellAgent.accountPwd,
                                                       str(df2["종목번호"].values[i]),
                                                       str(df2["잔고수량"].values[i] - df2["매도가능수량"].values[i]), '00', '0', SellAgent.getOneUnderHoga(self,str(df2["종목번호"].values[i]),str(df2["현재가"].values[i]) ))
                    if orderRes[1]["주문번호"].values[0] == 0:  # 장 종료 또는 기존주문 미체결 상태 등의 사유
                        print("정정 주문접수 불가")
                        # 일단 취소, 상위 반복문에서 다시 매도 시도로 연결됨
                        calcelRes = orderManager.CSPAT00800(ordno[0]['ordno'], SellAgent.accountNumber, SellAgent.accountPwd,
                                                       str(df2["종목번호"].values[i]), str(int(df2["잔고수량"].values[i]) - int(df2["매도가능수량"].values[i])))
                        if calcelRes[1]["주문번호"].values[0] == 0:
                            print("취소 주문접수 불가")
                        else:
                            dbInstance.insertOrderList(str(orderRes[0]["종목번호"].values[0]),
                                                       str(orderRes[0]["주문수량"].values[0]),
                                                       "0",
                                                       str(orderRes[1]["모주문번호"].values[0]), tempDate,
                                                       str(orderRes[1]["주문시각"].values[0]),
                                                       str(orderRes[1]["종목명"].values[0]), "3","0") # 취소

                    else:
                        print(orderRes[1]["주문번호"].values[0])

                        dbInstance.insertOrderList(str(orderRes[0]["종목번호"].values[0]),
                                                   str(orderRes[0]["주문수량"].values[0]),
                                                   str(orderRes[1]["주문금액"].values[0]),
                                                   str(orderRes[1]["주문번호"].values[0]), tempDate,
                                                   str(orderRes[1]["주문시각"].values[0]),
                                                   str(orderRes[1]["종목명"].values[0]), "1","4") # 정정
                    continue
                if df2["매도가능수량"].values[i] == 0:
                    #매도가능한 수량이 없기 때문에 이후 로직을 검사할 필요가 없다.
                    continue
                # 판단1 : 평단 < 현재가 * (1.033 - tolerance) # 매도잔량: 7273 매수잔량: 23468 체결강도: 458.71
                if SellAgent.weirdConditionCheck(self,df2["종목번호"].values[i],df2["종목명"].values[i] ) == True :
                    print("!!!!!!!!!!!!!!!!매도 경고!!!!!!!!!!!!!!!!")
                if float(df2["평균단가"].values[i]) * (1 - (SellAgent.principalNfee - SellAgent.tolerance)) > df2["현재가"].values[i]  :
                    print("한계 초과로 매도")
                    sellyn = True
                if sellyn == False and float(df2["평균단가"].values[i]) * 1.013 <= float(df2["현재가"].values[i]) :
                    print("1% 수익 확보, 50% 매도시도")
                    sellyn = True
                    sellHalfYn = True
                # if sellyn == False and SellAgent.weirdConditionCheck(self, df2["종목번호"].values[i]) == True:
                #     sellyn = True

                if sellyn == False :
                    #if (float(totbidrem1) >= float(totofferrem1)  and float(msrate) <= SellAgent.stdmsrate) or float(msrate) <= SellAgent.stdmsrate - 50 :
                    rsiChkRet = SellAgent.rsiCheck(self,df2["평균단가"].values[i], _shcode=df2["종목번호"].values[i], curPrice = df2["현재가"].values[i])
                    if rsiChkRet == 1 :
                        print("RSI 조건에 의하여 매도")
                        #dbInstance.insertObserverList(df2["종목번호"].values[i], tempDate, strTempTime, msrate, bidrem1, offerrem1, price)
                        dbInstance.updateObserverList(df2["종목번호"].values[i], tempDate)
                        sellyn = True
                    elif rsiChkRet == 2 :
                        dbInstance.updateObserverList(df2["종목번호"].values[i], tempDate)
                        sellyn = True
                        sellHalfYn = True
                    # if sellyn == False: #and SellAgent.prgCheck(self, _shcode=df2["종목번호"].values[i]) == True  :
                    #     print("프로그램 순매도 조건으로 매도")
                    #     sellyn = True
                    # elif float(bidrem1) >= (float(offerrem1) * 3 ) :
                    #     print("매수잔량 >= 매도잔량 * 2  매도")
                    #     dbInstance.insertObserverList(df2["종목번호"].values[i], tempDate, strTempTime, msrate, bidrem1,
                    #                                   offerrem1, price)
                    #     dbInstance.updateObserverList(df2["종목번호"].values[i])
                    #     sellyn = True
                if sellyn == True :
                    # 매도
                    sellQuantity = sellHalfYn == True and str(int(int(df2["매도가능수량"].values[i]) / 2)) or df2["매도가능수량"].values[i]
                    if sellHalfYn == True and sellQuantity == '0': # 매도가능수량이 1인 경우 예외처리
                        sellQuantity = df2["매도가능수량"].values[i]
                    try:
                        orderRes = orderManager.CSPAT00600(SellAgent.accountNumber, SellAgent.accountPwd, df2["종목번호"].values[i],
                                                           sellQuantity ,'', '1', '03', '000', '0') # 시장가로 매도, df2["현재가"].values[i]
                        if orderRes[1]["주문번호"].values[0] == 0:  # 장 종료 등의 사유
                            print("주문접수 불가")
                        else:
                            print(orderRes[1]["주문번호"].values[0])

                            dbInstance.insertOrderList(str(orderRes[0]["종목번호"].values[0]), str(orderRes[1]["실물주문수량"].values[0]), str(orderRes[1]["주문금액"].values[0]),
                                                       str(orderRes[1]["주문번호"].values[0]), tempDate,
                                                       str(orderRes[1]["주문시각"].values[0]),
                                                       str(orderRes[1]["종목명"].values[0]),"1","0")
                    except Exception as e:
                        print("Exception Occur : ", e)

                    sellyn = False
                    sellHalfYn = False
            time.sleep(SellAgent.sleeptime)

        pythoncom.CoUninitialize()



now = time.localtime()
myPrint.fnDebug = '[SELL] log_' + "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday) + '.txt'
myPrint.fDebug = open(myPrint.fnDebug, 'a') #, buffering=1)
# myPrint.teleMsg = False
sell = SellAgent()
sell.start()