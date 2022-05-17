import orderManager
import os

accountId = 'YOUR ID'
accountNumber = 'YOUR ACCOUNT NUMBER'
accountPwd = '0000'
password = 'YOUR PWD'
pkpwd = 'your cert password'
balancedD2 = 0 #D2 예수금
netAssest = 0 #추정순자산

orderManager.Login(id=accountId, pwd=password, cert=pkpwd)
orderInstance = orderManager.t0424(accountNumber, accountPwd)  # 계좌번호, 비밀번호
if orderInstance[0].shape[0] == 0:
    print("0424 account record info error")
    exit()
df1, df2 = orderManager.CSPAQ12200(레코드갯수='1', 관리지점번호='', 계좌번호=accountNumber, 비밀번호=accountPwd, 잔고생성구분='0')
netAssest = orderInstance[0]["추정순자산"].values[0]

if df2.shape[0] == 0 :
    print("CSPAQ12200 info error")
    exit()
balancedD2 = df2['D2예수금'].values[0]

print("예수금(D2) : ", balancedD2, "추정순자산 : ", netAssest)

