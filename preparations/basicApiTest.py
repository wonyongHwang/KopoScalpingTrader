import win32com.client
import pythoncom
import time
from datetime import date, timedelta

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

# 주식 차트(일/주/월 추이)
class XAQueryEventsT8413:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT8413.query_state = 1

# 단일종목 상세 조회
class XAQueryEventsT1102:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT1102.query_state = 1

# 종목 코드정보 (반복)
class XAQueryEventsT8430:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT8430.query_state = 1



# 단일종목 상세조회
def singleStockRead(shcode):
    instXAQueryT1102 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT1102)
    instXAQueryT1102.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1102.res"
    instXAQueryT1102.SetFieldData("t1102InBlock", "shcode", 0, shcode)
    instXAQueryT1102.Request(0)

    while XAQueryEventsT1102.query_state == 0:
        pythoncom.PumpWaitingMessages()
    XAQueryEventsT1102.query_state=0;
    name = instXAQueryT1102.GetFieldData("t1102OutBlock", "hname", 0)
    price = instXAQueryT1102.GetFieldData("t1102OutBlock", "price", 0)
    print(name+" : "+price)


def singleChartRead(code):
    # 차트 데이터 받아오기
    instXAQueryT8413 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT8413)
    instXAQueryT8413.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t8413.res"

    today = date.today()
    yesterday = date.today() - timedelta(5)
    today = today.strftime('%Y%m%d')
    yesterday = yesterday.strftime('%Y%m%d')

    instXAQueryT8413.SetFieldData("t8413InBlock", "shcode", 0, code)
    instXAQueryT8413.SetFieldData("t8413InBlock", "gubun", 0, "2")  # 2: 일, 3: 주, 4: 월
    instXAQueryT8413.SetFieldData("t8413InBlock", "sdate", 0, yesterday)
    instXAQueryT8413.SetFieldData("t8413InBlock", "edate", 0, today)
    instXAQueryT8413.SetFieldData("t8413InBlock", "comp_yn", 0, "N")  # 압축여부

    instXAQueryT8413.Request(0)

    while XAQueryEventsT8413.query_state == 0:
        pythoncom.PumpWaitingMessages()
    XAQueryEventsT8413.query_state = 0

    count = instXAQueryT8413.GetBlockCount("t8413OutBlock1")
    print("날짜   시가  고가  저가  종가"+ str(count))
    for i in range(count):
        mydate = instXAQueryT8413.GetFieldData("t8413OutBlock1", "date", i)
        open = instXAQueryT8413.GetFieldData("t8413OutBlock1", "open", i)
        high = instXAQueryT8413.GetFieldData("t8413OutBlock1", "high", i)
        low = instXAQueryT8413.GetFieldData("t8413OutBlock1", "low", i)
        close = instXAQueryT8413.GetFieldData("t8413OutBlock1", "close", i)
        print(mydate, open, high, low, close)

if __name__ == "__main__":
    server_addr = "demo.ebestsec.co.kr" # Operating Server : "hts.ebestsec.co.kr"
    server_port = 20001
    server_type = 0
    user_id = "******"
    user_pass = "********"
    user_certificate_pass = "!***********"

    inXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
    inXASession.ConnectServer(server_addr, server_port)
    inXASession.Login(user_id, user_pass, user_certificate_pass, server_type, 0)

    while XASessionEvents.logInState == 0:
        pythoncom.PumpWaitingMessages()

    num_account = inXASession.GetAccountListCount()
    for i in range(num_account):
        account = inXASession.GetAccountList(i)
        print(account)

    # 반복 데이터 조회하기
    instXAQueryT8430 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT8430)
    instXAQueryT8430.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t8430.res"
    instXAQueryT8430.SetFieldData("t8430InBlock", "gubun", 0, 1)
    instXAQueryT8430.Request(0)

    while XAQueryEventsT8430.query_state == 0:
        pythoncom.PumpWaitingMessages()

    count = instXAQueryT8430.GetBlockCount("t8430OutBlock")
    print("total count = ", count)
    myShcode = []
    for i in range(count):
        hname = instXAQueryT8430.GetFieldData("t8430OutBlock", "hname", i)
        shcode = instXAQueryT8430.GetFieldData("t8430OutBlock", "shcode", i)
        expcode = instXAQueryT8430.GetFieldData("t8430OutBlock", "expcode", i)
        etfgubun = instXAQueryT8430.GetFieldData("t8430OutBlock", "etfgubun", i)
        myShcode.append(shcode)
        print(i, hname, shcode, expcode, etfgubun)


    for i in myShcode:
        singleStockRead(i)
        time.sleep(0.3)

    for i in myShcode:
        singleChartRead(i)
        time.sleep(2)

    # singleChartRead('000070')
    # singleChartRead('000075')
    # singleChartRead('000080')









