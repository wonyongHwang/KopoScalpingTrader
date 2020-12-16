# pip install python-telegram-bot --upgrade

import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import orderManager
import dbManager
import pandas as pd
import pythoncom
import time

my_token = 'your token should be here'   #토큰을 변수에 저장합니다.
accountId = 'id'
accountNumber = 'account number'
accountPwd = 'account pwd'
password = 'pwd'
pkpwd = 'pkpwd'


bot = telegram.Bot(token = my_token)   #bot을 선언합니다.

# updates = bot.getUpdates()  #업데이트 내역을 받아옵니다.
#
# for u in updates :   # 내역중 메세지를 출력합니다.
#     print(u.message)

#chat_id = bot.getUpdates()[-1].message.chat.id  # 가장 최근에 온 메세지의 chat id를 가져옵니다
# print(chat_id)
# bot.sendMessage(chat_id=chat_id, text="저는 봇입니다.")

# res = bot.sendMessage(chat_id='-1001490131647', text="I'm bot") #@channel로 메세지를 보냅니다.
# print(res)

def sendTeleMsg(str=''):
    res = bot.sendMessage(chat_id='-1001490131647', text=str)  # @channel로 메세지를 보냅니다.
    #print(res)

def sendImage(path =''):
    bot.send_photo(chat_id='-1001490131647', photo=open(path, 'rb'))

print('start telegram chat bot')


# message reply function
def get_message(update, context) :
    # update.message.reply_text("<got text>")
    # update.message.reply_text(update.message.text)
    return

def queryProfit(tempDate='', isToday = True):
    # pythoncom.CoInitialize()
    # orderManager.Login(id=accountId, pwd=password, cert=pkpwd)

    dbInstance = dbManager.dbManager()
    res = dbInstance.selectOrderListByDate(tempDate)
    if len(res) == 0:
        print("There is no ordered list yet")
        return

    if isToday == True:
        df = orderManager.t0150(accountNumber)
    else:
        df = orderManager.t0151(tempDate,accountNumber)

    if df.shape[0] == 0:
        print("매매내역 조회 실패")
        sendTeleMsg("매매내역 조회 실패")
        return
    totmdsum = 0
    totmssum = 0
    totStr = '[당일매매 수익현황]\n'
    for i in res:
        tmpdf = df[(df['종목번호'] == i["shcode"]) & (df['매매구분'] == '매도')]
        if tmpdf.shape[0] == 0:
            print("해당 종목 해당일 매도 내역 없음")
            continue
        mdsum = tmpdf['정산금액'].apply(pd.to_numeric).sum()
        totmdsum += mdsum
        mssum = 0
        tmpdf = df[(df['종목번호'] == i["shcode"]) & (df['매매구분'] == '매수')]
        if tmpdf.shape[0] == 0:
            print("금일 매수 내역 없음, 전일 조회 시작")
            innerRes = dbInstance.selectBoughtDateFromOrderList(i["shcode"],tempDate)
            if len(innerRes) == 0:
                print("매수 조회 실패")
                continue
            print("매수 일자: ", innerRes[0]['orderdate'])
            df1 = orderManager.t0151(innerRes[0]['orderdate'], accountNumber)
            df1 = df1[(df1['종목번호'] == i["shcode"]) & (df1['매매구분'] == '매수')]
            mssum = df1['정산금액'].apply(pd.to_numeric).sum()
            totmssum += mssum
        else:
            mssum = tmpdf['정산금액'].apply(pd.to_numeric).sum()
            totmssum += mssum

        if mssum == 0:
            print("매수금액 계산 오류")
            continue
        profitRate = (((float(mdsum) * 0.9972 - float(mssum))) / float(mssum))
        profitRate = format(profitRate, "3.2%")  # '{:.3%}".format(0.25666)
        tmpStr = i['isunm'] + ' 매수금액: ' + str(mssum) + ' 매도금액: ' + str(mdsum) + ' 수익률: ' + str(profitRate) + '\n'
        print(tmpStr, end='')
        totStr += tmpStr

    sendTeleMsg(totStr)

    if totmssum == 0:
        print("정산 대상 총매수금액 : 0")
        return
    tmpStr = '총매수: ' + str(totmssum) + ' 총매도: ' + str(totmdsum) + ' 총수익: ' + format(
        (float(totmdsum) * 0.9972 - float(totmssum)) / float(totmssum), "10.2%")
    print(tmpStr)
    sendTeleMsg(tmpStr)
    # pythoncom.CoUninitialize()


# help reply function
def queryMine(isToday=True,date='') :

    if isToday == True :
        now = time.localtime()
        tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
        queryProfit(tempDate,isToday)
    else :
        queryProfit(date,~isToday)

# def help_command(update, context) :
#         update.message.reply_text("계좌 조회..")
#         if len(context.args) == 0:
#             now = time.localtime()
#             tempDate = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday - 1)
#             queryProfit(tempDate, True)
#         else:
#             print("args[0]", context.args[0])
#             queryProfit(context.args[0], False)

# updater = Updater(my_token, use_context=True)
#
# message_handler = MessageHandler(Filters.text & (~Filters.command), get_message) # 메세지중에서 command 제외
# updater.dispatcher.add_handler(message_handler)
#
# help_handler = CommandHandler('st', help_command)
# updater.dispatcher.add_handler(help_handler)
#
#
# updater.start_polling(timeout=3, clean=True)
# updater.idle()

