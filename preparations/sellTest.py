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

df1, df2 = orderManager.t0424(accountNumber, accountPwd, 체결구분='2')  # 계좌번호, 비밀번호
for i in range(0, df2.shape[0]):
    print("종목번호:", df2["종목번호"].values[i], "종목명:", df2["종목명"].values[i], "평균단가:", df2["평균단가"].values[i], \
      "현재가:", df2["현재가"].values[i], "매도가능수량:", df2["매도가능수량"].values[i], "잔고수량:", df2["잔고수량"].values[i])

    orderRes = orderManager.CSPAT00600(accountNumber, accountPwd, df2["종목번호"].values[i],
                                       df2["잔고수량"].values[i], '', '1', '03', '000', '0')  # 시장가로 매도, df2["현재가"].values[i]
    if orderRes[1]["주문번호"].values[0] == 0:  # 장 종료 등의 사유
        print("주문접수 불가")
    else:
        print(orderRes[1]["주문번호"].values[0])

