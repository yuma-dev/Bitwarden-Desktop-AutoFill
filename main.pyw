import os,json,time,psutil,sys,win32gui,win32process,keyboard,threading,pystray,pyperclip,ast
import pyautogui as pag


from config import CLIENTID,CLIENTSECRET,PASSWORD,HOTKEY

from system_hotkey import SystemHotkey
from modules import debug as debugging,trayicon,backend,gui

hk = SystemHotkey()

os.environ['BW_CLIENTID'] = CLIENTID
os.environ['BW_CLIENTSECRET'] = CLIENTSECRET
os.environ['BW_PASSWORD'] = PASSWORD

def debug(*objects):
    debugging.printDebug(objects,args=sys.argv)

def startTray():
    trayicon.icon.run()

def get_window_title():
    w=win32gui #shortversion
    try:
        
        pid = win32process.GetWindowThreadProcessId(w.GetForegroundWindow()) #get ForegroundWindow ID
        openwindow = psutil.Process(pid[-1]).name() #get the window name through the ID
        openwindow = openwindow[:-4] #remove .exe
        openwindowtitle = w.GetWindowText(w.GetForegroundWindow())
    except Exception as e:
        print(e)    
    return openwindowtitle

def hotkey(x):
    debug("hotkey!!!")
    windowtitle = str(get_window_title())
    debug(f"windowtitle:'{windowtitle}'")
    amount,data = backend.get_data(windowtitle)
    #debug(f"amount:{amount}, data={data}")
    if amount == 0:
        mousepos = pag.position()
        data = gui.choose_search(windowtitle)
        if data is not None:
            backend.write_data(data,mousepos)
    elif amount == 1:
        backend.write_data(data)
        debug("wrote Data")
    else:
        debug("data")
        
        mousepos = pag.position()
        chosen_username = gui.choose_account(data)
        debug('multiple, asked which')
        debug(f"got :{chosen_username}")
        if chosen_username != []:
            for user in data:
                if user['username']==chosen_username[0]:
                    debug(f"writing 'username':{user['username']},'password':{user['password']}")
                    data = {'username':user['username'],'password':user['password']}
                    backend.write_data(data,mousepos)

def register_hotkey():
    hk.register((HOTKEY), callback=hotkey)
    print("registered hotkey : {}!".format(HOTKEY))

def main():
    backend.update()
    register_hotkey()
    sTray = threading.Thread(target=startTray)
    sTray.start()
    print("ready!")

if __name__ == "__main__":
    main()