import threading, time
import dbManager
import orderManager
#import pythoncom
import myPrint
from myPrint import print
import talib as ta
import numpy as np
import pandas as pd
from google.cloud import texttospeech
from playsound import playsound
import os

class BuyAgent():
    accountId = 'your id'
    accountNumber = 'your account number' 
    accountPwd = 'your accound password (4 digit number)'
    password = 'your passowrd'
    pkpwd = 'your cert password'
    ordqty = 1
    numberOfPortfolio = 1
    balanced2 = 0
    netAssest = 0


    def __init__(self):
        threading.Thread.__init__(self)

    def checkAccount(self):
        # [START] 자산 조회 로직 0424는 추정단계, 12300은 확정단계
        orderInstance = orderManager.t0424(BuyAgent.accountNumber, BuyAgent.accountPwd)  # 계좌번호, 비밀번호
        if orderInstance[0].shape[0] == 0 :
            print("0424 account record info error")
            return False
        df1, df2 = orderManager.CSPAQ12200(레코드갯수='1', 관리지점번호='', 계좌번호=BuyAgent.accountNumber, 비밀번호=BuyAgent.accountPwd, 잔고생성구분='0')
        # BuyAgent.balanced2 = orderInstance[0]["추정D2예수금"].values[0]
        BuyAgent.netAssest = orderInstance[0]["추정순자산"].values[0]
        if df2.shape[0] == 0 :
            print("CSPAQ12200 info error")
            return False
        BuyAgent.balanced2 = df2['D2예수금'].values[0]

        print("예수금(D2) : ", BuyAgent.balanced2, "추정순자산 : ", BuyAgent.netAssest)
        # [END] 자산 조회 로직
        # [START] 미체결 주문금액을 반영한 자산 반영 로직 -> 13700 오동작
        # res1, res2, res3 = orderManager.CSPAQ13700(계좌번호=BuyAgent.accountNumber, 입력비밀번호=BuyAgent.password)

        # balanced2 에서 미체결 주문금액을 빼야 함
        # db 조회 후, 확인한 종목코드, 주문수량, 주문총액 - 해당 종목의 t0425 totrem
        now = time.localtime()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        dbInstance = dbManager.dbManager()
        res = dbInstance.selectbuylistford2(tempDate, '2')

        tempAmount = 0
        for i in res:
            time.sleep(2)
            shcode = i["shcode"]
            ordqty = i["ordqty"]
            ordprc = i["ordprc"]
            df, df1 = orderManager.t0425(계좌번호=BuyAgent.accountNumber, 비밀번호=BuyAgent.accountPwd, 종목번호=shcode, 체결구분='2', 매매구분='2', 정렬순서='2', 주문번호='')
            tmpCnt = 0

            while df.shape[0] == 0:
            #if df.shape[0] == 0 :
                time.sleep(2)
                df, df1 = orderManager.t0425(계좌번호=BuyAgent.accountNumber, 비밀번호=BuyAgent.accountPwd, 종목번호=shcode, 체결구분='2', 매매구분='2', 정렬순서='2', 주문번호='')
                tmpCnt += 1
                if tmpCnt > 2 :
                    dbInstance.updateBuyListford2(shcode, tempDate)  # 미체결 수량 없음
                    break
            # else:
            #
            now = time.localtime()
            for i in range(0, df1.shape[0]):
                tmpOrderTime = df1['주문시간'].values[i]
                print("주문번호:", df1['주문번호'].values[i], " 종목번호:", df1['종목번호'].values[i], "주문시간", tmpOrderTime, " 주문수량:", df1['주문수량'].values[i])
                print("현재 시각: ", now.tm_hour, ":", now.tm_min)

                delayedCancel = False
                if now.tm_hour - int(tmpOrderTime[:2]) == 1 :
                    print(int(now.tm_min) + 60 - int(tmpOrderTime[2:4]))
                    if int(now.tm_min) + 60 - int(tmpOrderTime[2:4]) >= 2:
                        delayedCancel = True
                elif now.tm_hour - int(tmpOrderTime[:2]) > 1 :
                    delayedCancel = True
                elif int(tmpOrderTime[:2]) == now.tm_hour and int(now.tm_min) != int(tmpOrderTime[2:4]):
                    if int(now.tm_min) - int(tmpOrderTime[2:4]) >= 2:
                        delayedCancel = True
                else:
                    tempAmount += ((int(ordprc) / int(ordqty)) * int(df['총미체결수량'].values[0]))
                    print('[미체결 정보] 종목번호', shcode, '주문수량', ordqty, '주문가격', ordprc, '미체결수량', df['총미체결수량'].values[0])
                    print('누적 미체결 금액 : ', tempAmount)

                if delayedCancel == True:
                    now = time.localtime()
                    print("매수취소 시도: ", now.tm_hour,":",now.tm_min)
                    calcelRes = orderManager.CSPAT00800(df1['주문번호'].values[i], BuyAgent.accountNumber, BuyAgent.accountPwd, df1['종목번호'].values[i], df['총미체결수량'].values[0] ) #df1['주문수량'].values[i])

                    if calcelRes[1]["주문번호"].values[0] == 0:
                        print("매수취소 주문접수 불가")
                        tempAmount += ((int(ordprc) / int(ordqty)) * int(df['총미체결수량'].values[0]))
                        print('[미체결 정보] 종목번호', shcode, '주문수량', ordqty, '주문가격', ordprc, '미체결수량', df['총미체결수량'].values[0])
                        print('누적 미체결 금액 : ', tempAmount)
                    else:
                        print("매수취소 주문접수 완료")
                        print(df1['종목번호'].values[i], df1['주문수량'].values[i], "0", df1['주문번호'].values[i], tempDate,
                              calcelRes[1]["주문시각"].values[0], calcelRes[1]["종목명"].values[0], "3", "0")
                        # `shcode`, `ordqty`, `ordprc`, `ordno`, `orderdate`, `ordtime`, `isunm`,`bnstpcode`,`strategy`)
                        #dbInstance.insertOrderList(str(df1['종목번호'].values[i]), str(df1['주문수량'].values[i]), "0", str(df1['주문번호'].values[i]), tempDate,  str(calcelRes[1]["주문시각"].values[0]),  str(calcelRes[1]["종목명"].values[0]), "3","0") # 취소
                        dbInstance.deleteOrderList(tempDate, df1['종목번호'].values[i])
        BuyAgent.balanced2 -= tempAmount
        print("미체결금액 반영한 D2 : ", BuyAgent.balanced2)
        # [END] 미체결 주문금액을 반영한 자산 반영 로직
        return True

    def checkmsBaseLine(df='', curPrice=0):
        dfnew = df.apply(pd.to_numeric)
        dfnew = dfnew.iloc[:20, :]
        #     dfnew['종가'].argmax()
        print(dfnew.head())
        basePrice = 0
        max = tmp = 0
        for i in range(1, df.shape[0]):
            #         print("종가",df["종가"].values[i],"종가 -1봉", df["종가"].values[i-1], "종가 -2봉",df["종가"].values[i-2] )
            if float(df["고가"].values[i]) >= float(df["저가"].values[i]) and float(df["고가"].values[i]) >= float(df["저가"].values[i - 1]) * 1.05:
                print("장대양봉 고가:",df["고가"].values[i],"저가:",df["저가"].values[i])
                tmp = float(df["고가"].values[i]) - float(df["저가"].values[i])
                if max < tmp:
                    max = tmp
                    basePrice = float(df["고가"].values[i]) / 2
                    print('저지선: ', basePrice)
        if basePrice > curPrice:
            print("저지선", basePrice, "> 현재가", curPrice)
            return True

        if  (float(df["고가"].values[i]) - float(df["종가"].values[i])) / (float(df["고가"].values[i]) - float(df["저가"].values[i])) >= 0.8 :
            print("상승 저항이 강력하여 매수 포기")
            print("고가:",df["고가"].values[i],"종가:",df["종가"].values[i], "저가", df["저가"].values[i])
            return True

        if basePrice == 0 or curPrice == 0:
            print("이전 20봉 이내 장대양봉 없음")
            return False

        return False

    def upperLimitCheck(self, shcode):
        df1475 = orderManager.t1475(shcode)
        if df1475.shape[0] == 0:
            print("t1475 responded null")
            return 0
        if float(df1475['등락율'].values[0]) > 23 :
            print("전일대비 과열(23% 초과)로 매수 제외:",float(df1475['등락율'].values[0]))
            return 1

    def msquantityCheck(self, shcode): # 매수잔량 검사(매수벽 확인)
        df1101 = orderManager.t1101(shcode)
        df1101 = df1101.apply(pd.to_numeric)
        print(df1101.head())
        tot = df1101.sum(axis=1).values[0]

        print('매수호가수량1', df1101['매수호가수량1'].values[0], '매수호가수량2', df1101['매수호가수량2'].values[0], '총매수잔량', tot)
        if df1101['매수호가수량1'].values[0] < 2000 or df1101['매수호가수량2'].values[0] < 2000 :
            print("매수잔량 점검 부적격 < 2000")
            return True

        if df1101['매수호가수량1'].values[0] < tot * 0.005 or df1101['매수호가수량2'].values[0] < tot * 0.005 :
            print("매수잔량 점검 부적격")
            return True

        df1471o, df1471ob = orderManager.t1471(종목코드=shcode, 분구분="00", 자료개수="001")  # 30초 단위 매수/매도 호가물량 점검
        totofferrem = df1471ob["총매도"].values[0]
        totbidrem = df1471ob["총매수"].values[0]
        msrate = df1471ob["매수비율"].values[0]
        print("현재가", df1471o["현재가"].values[0], "총매도:", totofferrem, "총매수:", totbidrem, "체결강도:", msrate, "매도우선잔량",
              df1471ob["매도우선잔량"].values[0], "매수우선잔량", df1471ob["매수우선잔량"].values[0])
        if int(totofferrem) * 2 < int(totbidrem):
            print("총매수/매도 확인 점검 부적격")
            return True
        if float(msrate) < 100.0:
            print("순간 체결 강도 100 미만 부적격")
            return True


    def weirdConditionCheck(self, shcode):
        totcnt = 0
        totmdvolume = totmsvolume = 0
        price = 0
        for i in range(0, 3):
            if i == 0:
                df, df1 = orderManager.t1310(종목번호=shcode)
                print(df1.tail())
                price = int(df1['현재가'].values[0])
                if price > 100000 : # 현재가 100000 초과인 경우 체결빈도, 단주매매 검사 스킵
                    return False
                tmpTopHour = int(df1['시간'].values[0][:2])
                tmpBottomHour = int(df1['시간'].values[-1][:2])
                tmpGap = 0
                if tmpTopHour == tmpBottomHour :
                    tmpGap = int(df1['시간'].values[0]) - int(df1['시간'].values[-1])
                else:
                    tmpGap = int(df1['시간'].values[0]) - 4000 - int(df1['시간'].values[-1]) # 1시간 빼고 , 60분 더해주고.
                print("tmpTopHour",tmpTopHour,"tmpBottomHour",tmpBottomHour," 20개 체결 간격: ", tmpGap)
                if tmpGap > 70:  # 100 at 1 ea / 3 sec
                    print("체결 빈도 검사에서 탈락 :", tmpGap)
                    return True
            else:
                df, df1 = orderManager.t1310(종목번호=shcode, 종료시간=df["시간CTS"].values[0], CTS=df["시간CTS"].values[0])
                print(df1.tail())
                tmpTopHour = int(df1['시간'].values[0][:2])
                tmpBottomHour = int(df1['시간'].values[-1][:2])
                tmpGap = 0
                if tmpTopHour == tmpBottomHour:
                    tmpGap = int(df1['시간'].values[0]) - int(df1['시간'].values[-1])
                else:
                    tmpGap = int(df1['시간'].values[0]) - 4000 - int(df1['시간'].values[-1])
                print("tmpTopHour", tmpTopHour, "tmpBottomHour", tmpBottomHour, " 20개 체결 간격: ", tmpGap)
                if tmpGap > 50:  # 100 at 1 ea / 3 sec
                    print("체결 빈도 검사에서 탈락")
                    return True

            if df1.shape[0] == 0 :
                print("t1310 responded null and we skip abnormal tr check")
                return False
            df1 = df1.apply(pd.to_numeric)
            tmpdf = df1[df1['체결수량'].lt(12)]
            totcnt += int(tmpdf.shape[0])
            totmdvolume += (df1['매도체결수량'].values[0] - df1['매도체결수량'].values[-1])
            totmsvolume +=  (df1['매수체결수량'].values[0] - df1['매수체결수량'].values[-1])
        print("이상 매매 건수:", totcnt,"총매도체결수량:",totmdvolume,"총매수체결수량:",totmsvolume)
        if totcnt >= 30:
            print("이상 매매 건수 초과로 매수 포기")
            return True
        elif totmdvolume > totmsvolume :
            print("매도세 우위로 매수 포기")
            return True
        else:
            return False

    def upperBoundCheck(self, df, upper, middle, low, curPrice):
        print("볼린저 상:",upper[-1],"중",middle[-1],"하", low[-1], "종가:", df['종가'].values[-1],"현재가",curPrice)
        if float(upper[-1]) < float(curPrice) or  float(upper[-1]) < float(df['종가'].values[-1]):
            print("BB 상한 초과")
            return 2
        # elif float(middle[-1]) >= float(df['종가'].values[-1]):
        #     print("BB 중간 이하")
        #     return 0
        # elif float(df['종가'].values[-1]) * 1.013 >= float(upper[-1]) :
        #     print("종가 수익예상이 BB 상한 초과")
        #     return 1
        elif (float(upper[-1]) + float(middle[-1])) / 2 >= float(curPrice) or (float(upper[-1]) + float(middle[-1])) / 2 >= float(df['종가'].values[-1]) :
            print("BB 중상 이하")
            return 0 # 매수 가능
        else:
            print("BB 중상 이상")
            return 1

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

    def run(self):
        #pythoncom.CoInitialize()
        orderManager.Login(id=BuyAgent.accountId, pwd=BuyAgent.password, cert=BuyAgent.pkpwd)

        now = time.localtime()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        # dbInstance = dbManager.dbManager()
        while False == buy.checkAccount() :
            time.sleep(1)

        cnt = 0
        while True :
            dbInstance = dbManager.dbManager()
            res = dbInstance.selectObserverList(tempDate,'1',tempDate)
            if cnt != 0 and cnt % 3 == 0:
                BuyAgent.checkAccount(self)
            orderPrice = 0
            #print(res)
            for i in res:
                nPortfolio = BuyAgent.numberOfPortfolio
                # time.sleep(5)
                df1, df2, df3 = orderManager.CSPAQ12300(레코드갯수='1', 계좌번호=BuyAgent.accountNumber, 비밀번호=BuyAgent.accountPwd, 잔고생성구분='0', 수수료적용구분='1',
                                           D2잔고기준조회구분='0', 단가구분='0')
                tmpdf = df3[(df3['종목번호'] == i["shcode"])]
                if tmpdf.shape[0] > 0:
                    print("현재 보유 중, Skip")
                    continue

                # nPortfolio -= df3.shape[0]
                # if nPortfolio <= 0 :
                #     print("포트폴리오 초과 매수불가")
                #     continue

                tmpres = dbInstance.selectUserControlListByShcode(i["shcode"], tempDate)
                if len(tmpres) != 0 and tmpres[0]['undercontrol'] == 'Lock':
                    print('수동 컨트럴 중으로 skip')
                    continue

                df8407 = orderManager.t8407(종목코드=i["shcode"])
                print(df8407["종목명"].values[0],df8407["현재가"].values[0])
                if int(df8407["현재가"].values[0]) < 1000 :
                    print("동전주 skip")
                    continue
                client = texttospeech.TextToSpeechClient()
                # Set the text input to be synthesized
                synthesis_input = texttospeech.SynthesisInput(text=df8407["종목명"].values[0])

                if not os.path.exists("audio"):
                    os.mkdir("audio")
                # 해당 종목코드 mp3가 존재한다면,
                if os.path.isfile("audio/"+i["shcode"]+".mp3") == True :
                    playsound("audio/"+i["shcode"]+".mp3")
                else :  # 해당 종목코드 mp3가 존재하지 않을경우,
                    # Build the voice request, select the language code ("en-US") and the ssml
                    # voice gender ("neutral")
                    voice = texttospeech.VoiceSelectionParams(
                        language_code="ko-KR", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
                    # Select the type of audio file you want returned
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
                    # Perform the text-to-speech request on the text input with the selected
                    # voice parameters and audio file type
                    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
                    with open("audio/"+i["shcode"]+".mp3", "wb") as out:
                        # Write the response to the output file.
                        out.write(response.audio_content)
                    playsound("audio/"+i["shcode"]+".mp3")
                    # os.remove("output.mp3") # playsound(None)

                # if BuyAgent.checkExcludedList(self, df8407["종목명"].values[0]) == True :
                #     print("인덱스 종목 제외 ",df8407["종목명"].values[0])
                #     continue

                BuyAgent.checkAccount(self)
                #BuyAgent.ordqty = int((min(BuyAgent.balanced2, BuyAgent.netAssest) / nPortfolio) / int(df8407["현재가"].values[0]))
                BuyAgent.ordqty = int((min(BuyAgent.balanced2, BuyAgent.netAssest)) / int(df8407["현재가"].values[0]))
                print("[INFO] ", "포폴# ",nPortfolio, "D2추정: ",BuyAgent.balanced2,"추정순자산", BuyAgent.netAssest )
                #if BuyAgent.ordqty < 1 or df2["D2예수금"].values[0] < (BuyAgent.ordqty * float(i["price"])) :
                if BuyAgent.ordqty < 1 or BuyAgent.balanced2 < (BuyAgent.ordqty * float(df8407["현재가"].values[0])):
                    print("[잔고부족] ","#종목코드",str(i["shcode"]),"예수금 ",df2["D2예수금"].values[0],"VS. 물량 ",str(BuyAgent.ordqty),"가격", str(df8407["현재가"].values[0]), )
                    dbInstance.updateObserverList(i["shcode"], tempDate)
                    continue

                # 상한가 임박 or 단주 매수 필터 아웃
                if BuyAgent.upperLimitCheck(self, i["shcode"]) == 1 or True == BuyAgent.weirdConditionCheck(self, i["shcode"]) or True == BuyAgent.msquantityCheck(self,i["shcode"]):
                    print("매수 포기")
                    dbInstance.updateObserverList(i["shcode"], tempDate)
                    continue
                orderPrice = int(df8407["현재가"].values[0])
                # 이전 장대양봉 기준선(중간값)이하일 경우 매수 포기하는 로직 -> 주석 처리 210110
                # df = orderManager.t8412(단축코드=i["shcode"], 단위="2", 요청건수="36")
                # if BuyAgent.checkmsBaseLine(df,float(df8407["현재가"].values[0]) ) == True:
                #     print("장대양봉 기준선 이하로 매수 포기")
                #     dbInstance.updateObserverList(i["shcode"], tempDate)
                #     continue

                # 볼린저 밴드 상한 초과시 포기, 중상일 경우 호가를 골드라인으로 조정 -> 로직 주석 처리 210110
                df8412 = orderManager.t8412(단축코드=i["shcode"], 단위="2", 요청건수="36")
                upper, middle, low = ta.BBANDS(df8412['종가'], 20, 2, 2) # 2 sigma 에서 3 sigma로 변경 210118
                upper = np.asarray(upper)
                middle = np.asarray(middle)
                low = np.array(low)
                tmpUpperCheck = BuyAgent.upperBoundCheck(self, df8412, upper, middle, low, df8407["현재가"].values[0])
                orderPrice = int(df8407["현재가"].values[0])
                if tmpUpperCheck == 1 :
                    print("매수 호가 하향 조정 시도, 현재가:",orderPrice)
                    while (float(upper[-1]) + float(middle[-1])) / 2 < orderPrice:
                        orderPrice = int(BuyAgent.getOneUnderHoga(self,i["shcode"],orderPrice))
                        print("orderPrice: ", orderPrice)
                elif tmpUpperCheck == 2 :
                    print("매수 포기")
                    dbInstance.updateObserverList(i["shcode"], tempDate)
                    continue

                print("매수시도 종목코드: " , i["shcode"] , " 수량: " , BuyAgent.ordqty, " 가격: ", orderPrice)
                try:
                    orderRes = orderManager.CSPAT00600(BuyAgent.accountNumber, BuyAgent.accountPwd, i["shcode"], BuyAgent.ordqty, str(orderPrice), '2', '00', '000', '0')
                    if orderRes[1]["주문번호"].values[0] == 0: # 장 종료 등의 사유
                        # observerList 테이블에서 해당 Row의 excluded칼럼을 1로 업데이트
                        dbInstance.updateObserverList(i["shcode"],tempDate)
                        continue
                    else:
                        print(orderRes[1]["주문번호"].values[0])
                        # bnstpcode 2: 매수, strategy 1: 전략1
                        dbInstance.insertOrderList(orderRes[0]["종목번호"].values[0], str(BuyAgent.ordqty),str(orderRes[1]["주문금액"].values[0]), str(orderRes[1]["주문번호"].values[0]), tempDate, str(orderRes[1]["주문시각"].values[0]), str(orderRes[1]["종목명"].values[0]),"2","1")
                        #dbInstance.deleteOrderList(tempDate,i["shcode"])

                        client = texttospeech.TextToSpeechClient()
                        # Set the text input to be synthesized
                        tmpStr = df8407["종목명"].values[0] + " 매수하겠습니다."
                        synthesis_input = texttospeech.SynthesisInput(text=tmpStr)
                        # Build the voice request, select the language code ("en-US") and the ssml
                        # voice gender ("neutral")
                        voice = texttospeech.VoiceSelectionParams(
                            language_code="ko-KR", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
                        # Select the type of audio file you want returned
                        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
                        # Perform the text-to-speech request on the text input with the selected
                        # voice parameters and audio file type
                        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
                        with open("output.mp3", "wb") as out:
                            # Write the response to the output file.
                            out.write(response.audio_content)
                            print('Audio content written to file "output.mp3"')
                        playsound("output.mp3")
                        os.remove("output.mp3")
                except Exception as e:
                    print("Exception Occur : ", e)
            time.sleep(5)
            cnt += 1
            print(str(cnt)," 회전(Buy Manager)")

    #pythoncom.CoUninitialize()

now = time.localtime()
myPrint.fnDebug = '[BUY] log_' + "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday) + '.txt'
myPrint.fDebug = open(myPrint.fnDebug, 'a') #, buffering=1)
myPrint.teleMsg = False
buy = BuyAgent()
buy.run()