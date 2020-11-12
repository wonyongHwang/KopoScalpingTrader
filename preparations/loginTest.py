import win32com.client
import pythoncom

class XASessionEvents:
    logInState = 0
    def OnLogin(self, code, msg):
        print("OnLogin method is called")
        print(str(code))
        print(str(msg))
        if str(code) == '0000':
            XASessionEvents.logInState = 1

    def OnLogout(self):
        print("OnLogout method is called")

    def OnDisconnect(self):
        print("OnDisconnect method is called")


if __name__ == "__main__":

    server_addr = "demo.ebestsec.co.kr" # Operating Server : "hts.ebestsec.co.kr"
    server_port = 20001
    server_type = 0
    user_id = "*****"
    user_pass = "*******"
    user_certificate_pass = "************"

    inXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
    inXASession.ConnectServer(server_addr, server_port)
    inXASession.Login(user_id, user_pass, user_certificate_pass, server_type, 0)

    while XASessionEvents.logInState == 0:
        pythoncom.PumpWaitingMessages()

    num_account = inXASession.GetAccountListCount()
    for i in range(num_account):
        account = inXASession.GetAccountList(i)
        print(account)








