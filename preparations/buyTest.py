import orderManager
import os

accountId = 'YOUR ID'
accountNumber = 'YOUR ACCOUNT NUMBER'
accountPwd = '0000'
password = 'YOUR PWD'
pkpwd = 'your cert password'
balancedD2 = 0 #D2 예수금
netAssest = 0 #추정순자산
shCode = "005930"
ordqty = 1
orderPrice = "67800"
orderManager.Login(id=accountId, pwd=password, cert=pkpwd)

try:
    orderRes = orderManager.CSPAT00600(accountNumber, accountPwd, shCode, ordqty, orderPrice, '2', '00', '000', '0')
    if orderRes[1]["주문번호"].values[0] == 0: # 장 종료 등의 사유
        exit()
    else:
        print(orderRes[1]["주문번호"].values[0])
except Exception as e:
    print("Exception Occur : ", e)