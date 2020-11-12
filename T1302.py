import win32com.client
import pythoncom
from scipy import stats
import time
import numpy as np
import pylab

# 거래량 상위 (반복)
class XAQueryEventsT1302:
    query_state = 0
    def OnReceiveData(self, code):
        XAQueryEventsT1302.query_state = 1

class XAT1302:


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
        #_self.t1302OutBlock=[]
        #print(_self.chetime)

    def appendData(_self, _shcode):
        #print("TRS")

        _self.T1302(_shcode)
        if _shcode == "111" :
            _self.chetime.append("111")
        else :
            _self.chetime.append("222")
        _self.t1302OutBlock=[_self.chetime]
        return _self.t1302OutBlock

    def T1302(_self,_shcode,cur, conn):
        instXAQueryT1302 = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventsT1302)
        instXAQueryT1302.ResFileName = "C:\\eBEST\\xingAPI\\Res\\t1302.res"
        instXAQueryT1302.SetFieldData("t1302InBlock", "shcode", 0, _shcode)
        instXAQueryT1302.SetFieldData("t1302InBlock", "gubun", 0, 2) # 0:30sec, 1: 1min, 2: 3min, 3: 5min, 4:10min, 5: 30min, 6:60min
        instXAQueryT1302.SetFieldData("t1302InBlock", "time", 0, "")
        instXAQueryT1302.SetFieldData("t1302InBlock", "cnt", 0, "50")
        instXAQueryT1302.Request(0)

        while instXAQueryT1302.query_state == 0:
            pythoncom.PumpWaitingMessages()
        XAQueryEventsT1302.query_state = 0  # 중요

        sql = "insert into TB_TRADE_MIN(shcode, chetime,close,sign,change,diff,chdegree,mdvolume,msvolume,revolume,mdchecnt,mschecnt,rechecnt,volume,open,high,low,cvolume,mdchecnttm,mschecnttm,totofferrem,totbidrem,mdvolumetm,msvolumetm,ymd) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        now = time.localtime()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        count = instXAQueryT1302.GetBlockCount("t1302OutBlock1")
        for i in range(count):
            _self.chetime.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "chetime", i))
            _self.close.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "close", i))
            _self.sign.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "sign", i))
            _self.change.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "change", i))
            _self.diff.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "diff", i))
            _self.chdegree.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "chdegree", i))
            _self.mdvolume.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "mdvolume", i))
            _self.msvolume.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "msvolume", i))
            _self.revolume.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "revolume", i))
            _self.mdchecnt.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "mdchecnt", i))
            _self.mschecnt.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "mschecnt", i))
            _self.rechecnt.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "rechecnt", i))
            _self.volume.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "volume", i))
            _self.open.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "open", i))
            _self.high.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "high", i))
            _self.low.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "low", i))
            _self.cvolume.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "cvolume", i))
            _self.mdchecnttm.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "mdchecnttm", i))
            _self.mschecnttm.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "mschecnttm", i))
            _self.totofferrem.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "totofferrem", i))
            _self.totbidrem.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "totbidrem", i))
            _self.mdvolumetm.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "mdvolumetm", i))
            _self.msvolumetm.insert(0,instXAQueryT1302.GetFieldData("t1302OutBlock1", "msvolumetm", i))
            try:
                cur.execute(sql, (_shcode,_self.chetime[0],_self.close[0],_self.sign[0],_self.change[0],_self.diff[0],_self.chdegree[0],_self.mdvolume[0],_self.msvolume[0],_self.revolume[0],_self.mdchecnt[0],_self.mschecnt[0],_self.rechecnt[0],_self.volume[0],_self.open[0],_self.high[0],_self.low[0],_self.cvolume[0],_self.mdchecnttm[0],_self.mschecnttm[0],_self.totofferrem[0],_self.totbidrem[0],_self.mdvolumetm[0],_self.msvolumetm[0],tempDate))
            except Exception as e :
                print ("db insert error on TB_TRADE_MIN" ,e)
                pass

        conn.commit()
        #_self.t1302OutBlock = [_self.chetime]
        sql = "insert into TB_TRADE_MIN_LINEREGRESS(shcode,chetime,p_val,r_val,grad,intercept,std_err,ymd,open,high,low) values (?,?,?,?,?,?,?,?,?,?,?)"

        tempX = list(map(int, _self.chetime))
        tempY = list(map(int, _self.open))
        print(tempX)
        print(tempY)
        grad, intercept, r_square, p_value, std_err = stats.linregress(tempX, tempY)
        print("grad ", grad)
        print("intercept ", intercept)
        #print("r_square ", r_square**2) # 중요
        print("p_value", p_value)
        print("std_err", std_err)
        try:
            cur.execute(sql, (_shcode, _self.chetime[-1], p_value, r_square**2, grad, intercept, std_err,tempDate,_self.open[-1],_self.high[-1],_self.low[-1]))
        except Exception as e:
            print("db insert error on TB_TRADE_MIN_LINEREGRESS ", e)
            conn.commit()

        """
        # Calculate some additional outputs
        x = np.array(tempX)
        y = np.array(tempY)
        predict_y = intercept + grad * x
        pred_error = y - predict_y
        degrees_of_freedom = len(x) - 2
        #residual_std_error = np.sqrt(np.sum(pred_error ** 2) / degrees_of_freedom)

        # Plotting
        pylab.plot(tempX, tempY, 'o')
        pylab.plot(tempX, predict_y, 'k-')
        pylab.show()        """

        if grad > 0 and r_square**2 >= 0.64:
            return grad
        else:
            return -1




# print("t1302test ", t1302OutBlock[0][0])
# print("t1302test ", t1302OutBlock[0][1])



"""

        """

