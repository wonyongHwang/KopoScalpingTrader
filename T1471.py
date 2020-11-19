import win32com.client
import pythoncom
import time
import dbManager
import orderManager

# 거래량 상위 (반복)
class XAQueryEventsT1471:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT1471.query_state = 1

class XAT1471:


    def __init__(_self):
        _self.chetime=[]
        _self.close = []
        _self.sign = []
        _self.change = []
        _self.diff = []
        _self.chdegree = []
        _self.mdvolume = []
        _self.msvolume = []
        _self.revolume = []
        _self.mdchecnt = []
        _self.mschecnt = []
        _self.rechecnt = []
        _self.volume = []
        _self.open = []
        _self.high = []
        _self.low = []
        _self.cvolume = []
        _self.mdchecnttm = []
        _self.mschecnttm = []
        _self.totofferrem = []
        _self.totbidrem = []
        _self.mdvolumetm = []
        _self.msvolumetm = []
        #_self.t1471OutBlock=[]
        #print(_self.chetime)

    def appendData(_self, _shcode):
        #print("TRS")

        _self.T1471(_shcode)
        if _shcode == "111" :
            _self.chetime.append("111")
        else :
            _self.chetime.append("222")
        _self.t1471OutBlock=[_self.chetime]
        return _self.t1471OutBlock

    def T1471(_self, _shcode):
        instXAQueryT1471 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT1471)
        instXAQueryT1471.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1471.res"
        instXAQueryT1471.SetFieldData("t1471InBlock", "shcode", 0, _shcode)
        instXAQueryT1471.SetFieldData("t1471InBlock", "gubun", 0, "01") # 00:30sec, 01: 1min
        instXAQueryT1471.SetFieldData("t1471InBlock", "time", 0, "")
        instXAQueryT1471.SetFieldData("t1471InBlock", "cnt", 0, "500")
        instXAQueryT1471.Request(0)

        while instXAQueryT1471.query_state == 0:
            pythoncom.PumpWaitingMessages()
        XAQueryEventsT1471.query_state = 0  # 중요

        # sql = "insert into TB_TRADE_MIN(shcode, chetime,close,sign,change,diff,chdegree,mdvolume,msvolume,revolume,mdchecnt,mschecnt,rechecnt,volume,open,high,low,cvolume,mdchecnttm,mschecnttm,totofferrem,totbidrem,mdvolumetm,msvolumetm,ymd) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        now = time.localtime()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)

        rtime = instXAQueryT1471.GetFieldData("t1471OutBlock", "time", 0)
        price = instXAQueryT1471.GetFieldData("t1471OutBlock", "price", 0)
        sign = instXAQueryT1471.GetFieldData("t1471OutBlock", "sign", 0)
        change = instXAQueryT1471.GetFieldData("t1471OutBlock", "change", 0)
        diff = instXAQueryT1471.GetFieldData("t1471OutBlock", "diff", 0)
        volume  = instXAQueryT1471.GetFieldData("t1471OutBlock", "volume", 0)
        dbInstance = dbManager.dbManager()
        dbInstance.insert1471OB(_shcode, tempDate, rtime, price, sign, change, diff, volume)

        count = instXAQueryT1471.GetBlockCount("t1471OutBlock1")

        for i in range(count):
            strTempTime = instXAQueryT1471.GetFieldData("t1471OutBlock1", "time", i)
            preoffercha1 = instXAQueryT1471.GetFieldData("t1471OutBlock1", "preoffercha1", i)
            offerrem1 = instXAQueryT1471.GetFieldData("t1471OutBlock1", "offerrem1", i)
            offerho1 = instXAQueryT1471.GetFieldData("t1471OutBlock1", "offerho1", i)
            bidho1 = instXAQueryT1471.GetFieldData("t1471OutBlock1", "bidho1", i)
            bidrem1 = instXAQueryT1471.GetFieldData("t1471OutBlock1", "bidrem1", i)
            prebidcha1 = instXAQueryT1471.GetFieldData("t1471OutBlock1", "prebidcha1", i)
            totofferrem = instXAQueryT1471.GetFieldData("t1471OutBlock1", "totofferrem", i)
            totbidrem = instXAQueryT1471.GetFieldData("t1471OutBlock1", "totbidrem", i)
            totsun = instXAQueryT1471.GetFieldData("t1471OutBlock1", "totsun", i)
            msrate = instXAQueryT1471.GetFieldData("t1471OutBlock1", "msrate", i)
            close = instXAQueryT1471.GetFieldData("t1471OutBlock1", "close", i)
            dbInstance.insert1471OB_Occurs(_shcode, tempDate, strTempTime, preoffercha1, offerrem1, offerho1, bidho1,
                                           bidrem1, \
                                           prebidcha1, totofferrem, totbidrem, totsun, msrate, close)
            # print(strTempTime+" "+preoffercha1+" "+offerrem1+" "+offerho1+" "+bidrem1+" "+prebidcha1+" "+totofferrem+" "+totbidrem+" "+totsun+" "+msrate+" "+close)




# 매수 조건 검사
def T1471_SearchBuyCandidates(_shcode):
    df1471o, df1471ob = orderManager.t1471(종목코드=_shcode, 자료개수="001")

    now = time.localtime()
    tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)

    if df1471o.shape[0] == 0 :
        print("종목코드 ",_shcode, " 잔량 조회 결과 없음")
        return None
    rtime = df1471o["시간CTS"].values[0]
    price = df1471o["현재가"].values[0]
    sign = df1471o["전일대비구분"].values[0]
    change = df1471o["전일대비"].values[0]
    diff = df1471o["등락율"].values[0]
    volume = df1471o["누적거래량"].values[0]
    dbInstance = dbManager.dbManager()
    dbInstance.insert1471OB(_shcode, tempDate, rtime, price, sign, change, diff, volume)

    if df1471ob.shape[0] == 0 :
        print("종목코드 ",_shcode, " 잔량 조회 상세 결과 없음")
        return None
    for i in range(0, df1471ob.shape[0]):
        strTempTime = df1471ob["체결시간"].values[i]
        preoffercha1 = df1471ob["매도증감"].values[i]
        offerrem1 = df1471ob["매도우선잔량"].values[i]
        offerho1 = df1471ob["매도우선호가"].values[i]
        bidho1 = df1471ob["매수우선호가"].values[i]
        bidrem1 = df1471ob["매수우선잔량"].values[i]
        prebidcha1 = df1471ob["매수증감"].values[i]
        totofferrem = df1471ob["총매도"].values[i]
        totbidrem = df1471ob["총매수"].values[i]
        totsun = df1471ob["순매수"].values[i]
        msrate = df1471ob["매수비율"].values[i]
        close = df1471ob["종가"].values[i]

        #print(_shcode+" "+strTempTime+" "+preoffercha1+" "+offerrem1+" "+offerho1+" "+bidrem1+" "+prebidcha1+" "+totofferrem+" "+totbidrem+" "+totsun+" "+msrate+" "+close)

        dbInstance.insert1471OB_Occurs(_shcode, tempDate, strTempTime, preoffercha1, offerrem1, offerho1, bidho1,
                                       bidrem1, prebidcha1, totofferrem, totbidrem, totsun, msrate, close)
        if float(msrate) > 150 and float(bidrem1) < (float(offerrem1) * 2) :
            print("watch list",_shcode,tempDate,strTempTime,msrate,bidrem1,offerrem1,price)
            return (_shcode,tempDate,strTempTime,msrate,bidrem1,offerrem1,price)
            #dbInstance.insertObserverList(_shcode,tempDate,strTempTime,msrate,bidrem1,offerrem1,price)
        else :
            return None