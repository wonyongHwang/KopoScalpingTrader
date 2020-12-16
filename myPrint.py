# source from http://ds.sumeun.org/?p=2119
from datetime import date
import botManager

if not 'reprint' in dir():
    reprint = print

def myprint(*argv, **kwarg):
    if 'end' in kwarg:
        reprint(*argv, end = kwarg['end'])
        reprint(*argv, end = kwarg['end'], file=fDebug)
    else:
        reprint(*argv, end='\n')
        reprint(*argv, end='\n', file=fDebug)
        fDebug.flush()
    if teleMsg == True:
        botManager.sendTeleMsg(str(argv[0:]))#.decode('string_escape').decode('utf-8')

print = myprint

debug = True
teleMsg = False
today = date.today()
fnDebug = 'log_'+today.strftime("%Y-%m-%d")+'.txt'
fDebug = open(fnDebug, 'a')