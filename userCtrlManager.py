
import dbManager
import time

dbInstance = dbManager.dbManager()
now = time.localtime()
tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)

while True:
    instr = input("list(l), o(lock), u(unlock), t(test), q(quit): ")
    if instr == 'q':
        break
    elif instr == 'o':
        instr2 = input("code: ")
        if instr2 == 'q':
            continue
        elif instr2 != 'q':
            res = dbInstance.selectUserControlListByShcode(instr2,tempDate)
            if len(res) == 0:
                dbInstance.insertUserControlList(instr2,tempDate,"Lock")
            else:
                dbInstance.updateUserControlList("Lock", instr2, tempDate)
            res = dbInstance.selectUserControlListByShcode(instr2, tempDate)
            print(res)
    elif instr == 'u':
        instr2 = input("code: ")
        if instr2 == 'q':
            continue
        elif instr2 != 'q':
            dbInstance.updateUserControlList("UnLock",instr2,tempDate)
        res = dbInstance.selectUserControlListByShcode(instr2, tempDate)
        print(res)
    elif instr == 'l':
        res = dbInstance.selectUserControlList(tempDate)
        for i in res:
            print(i)
    elif instr == 't':
        instr2 = input("code: ")
        res = dbInstance.selectUserControlListByShcode(instr2, tempDate)
        # print(res[0]['undercontrol'])
        if res[0]['undercontrol'] == 'Lock' :
            print("Lock")
        elif res[0]['undercontrol'] == 'UnLock' :
            print("UnLock")