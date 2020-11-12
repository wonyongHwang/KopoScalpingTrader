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

#i = dbManager()
#print(i.cursor)
#print(i.stock_db)
#i.insert1471OB('30','40','3','4','5','6','7','8')