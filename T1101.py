import win32com.client
import pythoncom
from scipy import stats
import time
import numpy as np
import pylab


class XAQueryEventsT1101:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT1101.query_state = 1

class XAT1101:

    def T1101(_self,_shcode):
        instXAQueryT1101 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT1101)
        instXAQueryT1101.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1101.res"
        instXAQueryT1101.SetFieldData("t1101InBlock", "shcode", 0, _shcode)
        instXAQueryT1101.Request(0)

        while instXAQueryT1101.query_state == 0:
            pythoncom.PumpWaitingMessages()
        XAQueryEventsT1101.query_state = 0  # 중요

        #sql = "insert into TB_TRADE_MIN(shcode, chetime,close,sign,change,diff,chdegree,mdvolume,msvolume,revolume,mdchecnt,mschecnt,rechecnt,volume,open,high,low,cvolume,mdchecnttm,mschecnttm,totofferrem,totbidrem,mdvolumetm,msvolumetm,ymd) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        now = time.localtime()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)

        hname = instXAQueryT1101.GetFieldData("t1101OutBlock", "hname", 0)
        shcode = instXAQueryT1101.GetFieldData("t1101OutBlock", "shcode", 0)
        price = instXAQueryT1101.GetFieldData("t1101OutBlock", "price", 0)

        sign = instXAQueryT1101.GetFieldData("t1101OutBlock", "sign", 0)
        change = instXAQueryT1101.GetFieldData("t1101OutBlock", "change", 0)
        diff = instXAQueryT1101.GetFieldData("t1101OutBlock", "sign", 0)
        volume = instXAQueryT1101.GetFieldData("t1101OutBlock", "sign", 0)
        jnilclose = instXAQueryT1101.GetFieldData("t1101OutBlock", "sign", 0)

        offerho1 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho1", 0)
        bidho1 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho1", 0)
        offerrem1 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem1", 0)
        bidrem1 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem1", 0)
        preoffercha1 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha1", 0)
        prebidcha1 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha1", 0)

        offerho2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho2", 0)
        bidho2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho2", 0)
        offerrem2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem2", 0)
        bidrem2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem2", 0)
        preoffercha2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha2", 0)
        prebidcha2 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha2", 0)

        offerho3 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho3", 0)
        bidho3 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho3", 0)
        offerrem3 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem3", 0)
        bidrem3 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem3", 0)
        preoffercha3 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha3", 0)
        prebidcha3 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha3", 0)

        offerho4 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho4", 0)
        bidho4 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho4", 0)
        offerrem4 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem4", 0)
        bidrem4 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem4", 0)
        preoffercha4 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha4", 0)
        prebidcha4 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha4", 0)

        offerho5 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho5", 0)
        bidho5 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho5", 0)
        offerrem5 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem5", 0)
        bidrem5 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem5", 0)
        preoffercha5 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha5", 0)
        prebidcha5 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha5", 0)

        offerho6 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho6", 0)
        bidho6 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho6", 0)
        offerrem6 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem6", 0)
        bidrem6 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem6", 0)
        preoffercha6 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha6", 0)
        prebidcha6 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha6", 0)

        offerho7 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho7", 0)
        bidho7 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho7", 0)
        offerrem7 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem7", 0)
        bidrem7 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem7", 0)
        preoffercha7 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha7", 0)
        prebidcha7 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha7", 0)

        offerho8 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho8", 0)
        bidho8 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho8", 0)
        offerrem8 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem8", 0)
        bidrem8 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem8", 0)
        preoffercha8 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha8", 0)
        prebidcha8 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha8", 0)

        offerho9 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho9", 0)
        bidho9 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho9", 0)
        offerrem9 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem9", 0)
        bidrem9 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem9", 0)
        preoffercha9 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha9", 0)
        prebidcha9 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha9", 0)

        offerho10 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerho10", 0)
        bidho10 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidho10", 0)
        offerrem10 = instXAQueryT1101.GetFieldData("t1101OutBlock", "offerrem10", 0)
        bidrem10 = instXAQueryT1101.GetFieldData("t1101OutBlock", "bidrem10", 0)
        preoffercha10 = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha10", 0)
        prebidcha10 = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha10", 0)

        offer = instXAQueryT1101.GetFieldData("t1101OutBlock", "offer", 0)
        bid = instXAQueryT1101.GetFieldData("t1101OutBlock", "bid", 0)
        preoffercha = instXAQueryT1101.GetFieldData("t1101OutBlock", "preoffercha", 0)
        prebidcha = instXAQueryT1101.GetFieldData("t1101OutBlock", "prebidcha", 0)
        hotime = instXAQueryT1101.GetFieldData("t1101OutBlock", "hotime", 0)
        yeprice = instXAQueryT1101.GetFieldData("t1101OutBlock", "yeprice", 0)
        yevolume = instXAQueryT1101.GetFieldData("t1101OutBlock", "yevolume", 0)
        yesign = instXAQueryT1101.GetFieldData("t1101OutBlock", "yesign", 0)
        yechange = instXAQueryT1101.GetFieldData("t1101OutBlock", "yechange", 0)
        yediff = instXAQueryT1101.GetFieldData("t1101OutBlock", "yediff", 0)
        tmoffer = instXAQueryT1101.GetFieldData("t1101OutBlock", "tmoffer", 0)
        tmbid = instXAQueryT1101.GetFieldData("t1101OutBlock", "tmbid", 0)
        ho_status = instXAQueryT1101.GetFieldData("t1101OutBlock", "ho_status", 0)

        uplmtprice = instXAQueryT1101.GetFieldData("t1101OutBlock", "uplmtprice", 0)
        dnlmtprice = instXAQueryT1101.GetFieldData("t1101OutBlock", "dnlmtprice", 0)

        open = instXAQueryT1101.GetFieldData("t1101OutBlock", "open", 0)
        high = instXAQueryT1101.GetFieldData("t1101OutBlock", "high", 0)
        low = instXAQueryT1101.GetFieldData("t1101OutBlock", "low", 0)



        print(        "  hname              ="+hname+ \
        "  shcode             ="+shcode+\
        "  price              ="+price          +\
        "  sign               ="+sign           +\
        "  change             ="+change         +\
        "  diff               ="+diff           +\
        "  volume             ="+volume         +\
        "  jnilclose          ="+jnilclose      +\
        "  offerho1           ="+offerho1       +\
        "  bidho1             ="+bidho1         +\
        "  offerrem1          ="+offerrem1      +\
        "  bidrem1            ="+bidrem1        +\
        "  preoffercha1       ="+preoffercha1   +\
        "  prebidcha1         ="+prebidcha1     +\
		"  offerho2           ="+offerho2       +\
        "  bidho2             ="+bidho2         +\
        "  offerrem2          ="+offerrem2      +\
        "  bidrem2            ="+bidrem2        +\
        "  preoffercha2       ="+preoffercha2   +\
        "  prebidcha2         ="+prebidcha2     +\
		"  offerho3           ="+offerho3       +\
        "  bidho3             ="+bidho3         +\
        "  offerrem3          ="+offerrem3      +\
        "  bidrem3            ="+bidrem3        +\
        "  preoffercha3       ="+preoffercha3   +\
        "  prebidcha3         ="+prebidcha3     +\
		"  offerho4           ="+offerho4       +\
        "  bidho4             ="+bidho4         +\
        "  offerrem4          ="+offerrem4      +\
        "  bidrem4            ="+bidrem4        +\
        "  preoffercha4       ="+preoffercha4   +\
        "  prebidcha4         ="+prebidcha4     +\
		"  offerho5           ="+offerho5       +\
        "  bidho5             ="+bidho5         +\
        "  offerrem5          ="+offerrem5      +\
        "  bidrem5            ="+bidrem5        +\
        "  preoffercha5       ="+preoffercha5   +\
        "  prebidcha5         ="+prebidcha5     +\
		"  offerho6           ="+offerho6       +\
        "  bidho6             ="+bidho6         +\
        "  offerrem6          ="+offerrem6      +\
        "  bidrem6            ="+bidrem6        +\
        "  preoffercha6       ="+preoffercha6   +\
        "  prebidcha6         ="+prebidcha6     +\
		"  offerho7           ="+offerho7       +\
        "  bidho7             ="+bidho7         +\
        "  offerrem7          ="+offerrem7      +\
        "  bidrem7            ="+bidrem7        +\
        "  preoffercha7       ="+preoffercha7   +\
        "  prebidcha7         ="+prebidcha7     +\
		"  offerho8           ="+offerho8       +\
        "  bidho8             ="+bidho8         +\
        "  offerrem8          ="+offerrem8      +\
        "  bidrem8            ="+bidrem8        +\
        "  preoffercha8       ="+preoffercha8   +\
        "  prebidcha8         ="+prebidcha8     +\
		"  offerho9           ="+offerho9       +\
        "  bidho9             ="+bidho9         +\
        "  offerrem9          ="+offerrem9      +\
        "  bidrem9            ="+bidrem9        +\
        "  preoffercha9       ="+preoffercha9   +\
        "  prebidcha9         ="+prebidcha9     +\
		"  offerho10          ="+offerho10      +\
        "  bidho10            ="+bidho10        +\
        "  offerrem10         ="+offerrem10     +\
        "  bidrem10           ="+bidrem10       +\
        "  preoffercha10      ="+preoffercha10  +\
        "  prebidcha10        ="+prebidcha10    +\
        "  offer              ="+offer          +\
        "  bid                ="+bid            +\
        "  preoffercha        ="+preoffercha    +\
        "  prebidcha          ="+prebidcha      +\
        "  hotime             ="+hotime         +\
        "  yeprice            ="+yeprice        +\
        "  yevolume           ="+yevolume       +\
        "  yesign             ="+yesign         +\
        "  yechange           ="+yechange       +\
        "  yediff             ="+yediff         +\
        "  tmoffer            ="+tmoffer        +\
        "  tmbid              ="+tmbid          +\
        "  ho_status          ="+ho_status      +\
        "  uplmtprice         ="+uplmtprice     +\
        "  dnlmtprice         ="+dnlmtprice     +\
        "  high               ="+high           +\
        "  open               ="+open           +\
        "  low                ="+low            )

