import win32com.client
import pythoncom
import time, threading
from threading import Thread
import queue
import buyManager
import winsound as ws

import random
from collections import defaultdict
import T1302
import T1471
import T1101
import orderManager

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

class Agent(threading.Thread):

    def __init__(self,name, status):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.name = name
        self.status = status

    def run(self):
        return

    def setCode(self, _code, _name):
        self.code = _code
        self.name = _name

    def setStatus(self, _status):
        self.status = _status

    # 주식 분별 데이터 기준 판단 로직
    def takebet(self):
        return

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
    lock = threading.Lock()


    now = time.localtime()
    server_addr = "demo.ebestsec.co.kr"
    server_port = 20001
    server_type = 0
    user_id = "*****"
    user_pass = "*****"
    user_certificate_pass = "!******"

    inXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
    inXASession.ConnectServer(server_addr, server_port)
    inXASession.Login(user_id, user_pass, user_certificate_pass, server_type, 0)

    while XASessionEvents.logInState == 0:
        pythoncom.PumpWaitingMessages()

    num_account = inXASession.GetAccountListCount()
    for i in range(num_account):
        account = inXASession.GetAccountList(i)
        print(account)

    listT1452=[["null" for col in range(5)] for row in range(120)]

    # 전날 데이터 수신 (1: today 2: yesterday)
    def T1452(idx=0, isToday=1):
        # Exit Condition
        idxTemp = int(idx)
        print("idxTemp = ",idxTemp)
        if idxTemp >= 120 :
            return

        instXAQueryT1452 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT1452)
        instXAQueryT1452.ResFileName = "Res\\t1452.res"
        instXAQueryT1452.SetFieldData("t1452InBlock", "gubun", 0, "1")
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
        T1452(idx, isToday=1) # recursive call

    # 코스피 코드정보 조회 (0:all, 1: kospi, 2:kosdaq)
    def T8430(gubun=1):
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
            expcode = instXAQueryT8430.GetFieldData("t8430OutBlock", "expcode", i)
            etfgubun = instXAQueryT8430.GetFieldData("t8430OutBlock", "etfgubun", i)
            myShcode.append(shcode)
            print(i, hname, shcode, expcode, etfgubun)
        return myShcode

    def searchCandidates():
        pythoncom.CoInitialize()
        t1471i = T1471.XAT1471()
        # for i in T8430():
        #     t1471i.T1471_SearchBuyCandidates(i)  # 매수 조건 검사
        #     time.sleep(3)
        for row in listT1452:
            t1471i.T1471_SearchBuyCandidates(row[6])  # 매수 조건 검사
            time.sleep(2)
        pythoncom.CoUninitialize()

    def beepsound():
        freq = 2000  # range : 37 ~ 32767
        dur = 3000  # ms
        ws.Beep(freq, dur)  # winsound.Beep(frequency, duration)

    T1452()
    beepsound()
    while True:
        searchCandidates()
        beepsound()
        print("------------------------------")
        print("--- KOPO          ------------")
        print("--- dept. of SMART FINANCE ---")
        print("------------------------------")
        time.sleep(60)








