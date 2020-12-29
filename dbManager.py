import pymysql
import json
class dbManager:
    stock_db = pymysql.connect(
        user='root',
        passwd='!gcgp1920',
        host='127.0.0.1',
        db='kopo_stock',
        charset='utf8')
    cursor = stock_db.cursor(pymysql.cursors.DictCursor)

    def __init__(_self):

        return
    def insert1471OB(_self, *args):
        # for i in args:
        #     print(i)
        # data = ('1','2','3','4','5','6','7','8')
        # sql = '''INSERT INTO `t1471outblock` (`shcode`, `date`, `time`, `price`, `sign`, `change`, `diff`, `volume`) VALUES ('1','2','3','4','5','6','7','8');'''
        sql = '''INSERT INTO `t1471outblock` (`shcode`, `date`, `time`, `price`, `sign`, `change`, `diff`, `volume`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'''
        dbManager.cursor.execute(sql,args)
        dbManager.stock_db.commit()

    def insert1471OB_Occurs(_self, *args):
        sql = '''INSERT INTO `t1471outblockoccurs` (`shcode`, `date`, `time`, `preoffercha1`, `offerrem1`, `offerho1`, `bidho1`, `bidrem1`,`prebidcha1`, `totofferrem`, `totbidrem`,`totsun`, `msrate`, `close`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s);'''
        dbManager.cursor.execute(sql,args)
        dbManager.stock_db.commit()

    def insertObserverList(_self, *args):
        sql = '''INSERT INTO `observerlist` (`shcode`, `date`,`time`,`msrate`, `bidrem`, `offerrem`, `price`,`excluded`,`strategy`,`reserve1`) VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s);'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()

    def selectObserverList(_self, *args):
        #sql = '''select * from observerlist where date=%s and excluded!=1 group by shcode order by time desc, msrate desc, offerrem desc limit 5;'''
        #sql = '''select * from observerlist a, orderlist b where a.date = %s and a.excluded != 1 and a.strategy = %s and time >  date_format(subdate(now(), Interval 10 Minute), '%%H%%i%%s') and a.shcode not in (select shcode from orderlist where orderdate= %s) group by a.shcode order by time desc, msrate desc, offerrem - bidrem desc limit 5; '''
        sql = '''select * from observerlist a where a.date = %s and a.excluded != 1 and a.strategy = %s and a.time >  date_format(subdate(now(), Interval 10 Minute), '%%H%%i%%s') and a.shcode not in (select shcode from orderlist where orderdate= %s) group by a.shcode order by time desc; '''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        #print(result)
        return result

    def updateObserverList(_self, *args):
        sql = '''update `observerlist` set `excluded` = 1 where `shcode` = %s and `date` = %s;'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()

    def insertOrderList(_self, *args):
        sql = '''INSERT INTO `orderlist` (`shcode`, `ordqty`, `ordprc`, `ordno`, `orderdate`, `ordtime`, `isunm`,`bnstpcode`,`strategy`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s);'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()

    def deleteOrderList(_self, *args):
        sql = '''delete from `orderlist` where orderdate= %s and shcode='%s and bnstpcode='2';'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()

    def selectOrdNo(_self, *args):
        sql = '''select ordno from orderlist where shcode = %s and orderdate = %s and bnstpcode = '1' order by ordtime desc;'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        return result

    def selectbuylistford2(_self, *args):
        sql = '''select * from orderlist where orderdate = %s and bnstpcode = %s and reserve1 is null order by ordtime desc;'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        return result

    def updateBuyListford2(_self, *args):
        # reserve1 = 1 : 미체결 없음을 의미
        sql = '''update `orderlist` set `reserve1` = '1' where shcode=%s and orderdate=%s;'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()

    def updateOrdListBB(_self, *args):
        # reserve1 = 1 : 미체결 없음을 의미
        sql = '''update `orderlist` set `reserve2` = '1' where shcode=%s and orderdate=%s and bnstpcode='2';'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()

    def selectOrdListBB(_self, *args):
        sql = '''select reserve2 from orderlist where shcode=%s and orderdate = %s and bnstpcode = '2';'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        return result

    def selectLatestBoughtItemByStrategy(_self, *args):
        sql = '''select * from orderlist where shcode=%s and strategy=%s order by orderdate desc limit 1;'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        return result

    def insertDailyRecommendList(_self, *args):
        sql = '''INSERT INTO `dailyrecommend` (`shcode`, `date`,`gubun`,`minclose`, `d60ma`,`rsitgt`, `rsisignal`, `time`, `hname`,`reserve1`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()

    def selectDailyRecommendList(_self, *args):
        #sql = '''select distinct shcode, hname from dailyrecommend where gubun=%s and if( weekday(curdate()) <= 4, date >= date_add(now(), interval -2 day),date >= date_add(now(), interval -4 day) ) and shcode not in (select shcode from orderlist where orderdate= %s) group by shcode'''
        sql = '''select distinct shcode, hname from dailyrecommend where gubun=%s and if( weekday(curdate()) = 0,date >= date_add(now(), interval -4 day), date >= date_add(now(), interval -2 day)) and shcode not in (select shcode from orderlist where orderdate= %s) group by shcode'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        return result

    def selectGubunRecommendList(_self, *args):
        sql = '''select gubun, hname from dailyrecommend where shcode=%s limit 1;'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        return result

    def selectOrderListByDate(_self, *args):
        sql = '''select * from orderlist where orderdate=%s group by isunm;'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        return result

    def selectBoughtDateFromOrderList(_self, *args):
        sql = '''select * from orderlist where shcode=%s and bnstpcode=2 and orderdate < %s order by orderdate desc limit 1'''
        dbManager.cursor.execute(sql, args)
        dbManager.stock_db.commit()
        result = dbManager.cursor.fetchall()
        return result

#i = dbManager()
#print(i.cursor)
#print(i.stock_db)
#i.insert1471OB('30','40','3','4','5','6','7','8')