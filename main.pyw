import os,json,time,psutil,sys,win32gui,win32process,keyboard,threading,pystray,pyperclip,ast
import PySimpleGUI as sg
import pyautogui as pag
from subprocess import check_output
from PIL import Image
from config import CLIENTID,CLIENTSECRET,PASSWORD,HOTKEY
from pystray import MenuItem as item
from cryptography.fernet import Fernet



def load_key():
    """
    Loads the key named `secret.key` from the current directory or creates it.
    """
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key","wb") as f:
            f.write(key)
        
    else:
        with open("secret.key","rb") as f:
            key = f.read()
            
    return key

fernet = Fernet(load_key())


icon_path = "sprites/icon.ico"
sg.theme('DarkGrey13')
os.environ['BW_CLIENTID'] = CLIENTID
os.environ['BW_CLIENTSECRET'] = CLIENTSECRET
os.environ['BW_PASSWORD'] = PASSWORD



def on_restart(self):
    icon.stop()
    os.execv(sys.executable, ['pyw'] + sys.argv)

def on_exit(self):
    psutil.Process(os.getpid()).terminate()
    
def on_update():
    update()

image = Image.open(icon_path)
menu = pystray.Menu(
    item('Restart', on_restart),
    #item('Open Logs', open_logs),
    item('Update', on_update),
    item('Exit', on_exit)
    )
icon = pystray.Icon("RPC", image, "Bitwarden", menu)

def startTray():
    icon.run()

def reset():
    icon.stop()
    os.execv(sys.executable, ['pyw'] + sys.argv)

def encrypt_message(message):
    """
    Encrypts a message
    """
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message
    
def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return decrypted_message.decode()

def update(retry=False):
    try:
        session = check_output("bw unlock --passwordenv BW_PASSWORD",shell = True)
        sessionKey = session.split()[-1]
        sessionKey = rf"{sessionKey}"[2:-1]
        print(sessionKey)
        output = check_output(f'bw sync --session {sessionKey}',shell = True)
        print(output)
        output = check_output(f'bw list items --session {sessionKey}',shell = True)
        if output == b"[]" or output == [] or output == "[]":
            print("1.21.1 bug detected")
            bitwardenDir = os.path.expandvars(r'%APPDATA%\Bitwarden CLI')
            if os.path.exists(bitwardenDir+r"\data.json"):
                os.remove(bitwardenDir+r"\data.json")
                print("removed data.json, retrying...")
                update(retry=True)
            else:
                print("data.json not found")
        print(output)
        data = json.loads(output)
        with open('data/enc', 'wb') as outfile:
            outfile.write(encrypt_message(str(data)))
        icon.notify("Synchronization completed!")
    except Exception as e:
        if retry:
            raise Exception(e)
        else:
            print(e)
            print(os.system("bw login --apikey"))
            update(retry=True)

def get_matches(name):
    if type(name) != str:
        return AttributeError("False input type")
    matches = []
    with open('data/enc','rb') as f:
        decData = decrypt_message(f.read())

    print(decData)
    
    y = ast.literal_eval(decData)
    
    for site in y:
        try:
            for uri in site["login"]["uris"]:
                try:
                    #if uri["uri"].startswith(name):
                    if uri["uri"] == name:
                        matches.append(site)
                except KeyError:
                    pass
        except KeyError:
            pass
    
    return matches

def get_data(name):
    matches = get_matches(name)
    print(f"matches:{matches}")
    amount = len(matches)
    print(f"length:{amount}")
    if amount == 0:
        return amount,[]
    if amount == 1:
        username = matches[0]['login']['username']
        password = matches[0]['login']['password']
        return amount,{"username":username, "password":password}
    if amount>1:
        matchess = []
        for site in matches:
            username = site['login']['username']
            password = site['login']['password']
            matchess.append({'username': username, 'password': password})
        return amount,matchess

def choose_account(accounts):
    usernames = []
    print(f'accounts:{accounts}')
    for account in accounts:
        usernames.append(account['username'])
    layout = [[sg.Text('What Account do you want autofilled?')],      
                    [sg.Listbox(values=usernames, size=(20, len(usernames)), bind_return_key=True, key='-choice-',no_scrollbar=True)],      
                    [sg.Submit(bind_return_key=True), sg.Cancel()]]      

    window = sg.Window('Bitwarden Autofill Account Selection', layout,no_titlebar=True,keep_on_top=True,grab_anywhere=True)
    event, values = window.read()    
    window.close()

    choice = values['-choice-']   
    return choice

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

def write_data(data):
    
    username = data['username']
    password = data['password']
    print(f"username : {username} password : {password}")
    
    time.sleep(0.1)
    pag.hotkey('ctrl','a')
    pag.press('backspace')
    keyboard.write(username)
    
    keyboard.press_and_release('tab')
    time.sleep(0.1)
    pag.hotkey('ctrl','a')
    pag.press('backspace')
    
    keyboard.write(password)

def hotkey():
    print("hotkey!!!")
    windowtitle = str(get_window_title())
    print(f"windowtitle:'{windowtitle}'")
    amount,data = get_data(windowtitle)
    print(f"amount:{amount}, data={data}")
    if amount == 0:
        pyperclip.copy(windowtitle)
        icon.notify(f'No Match found!\nAdd a URI with "{windowtitle}"\nCopied {windowtitle} to your clipboard.')
    elif amount == 1:
        write_data(data)
        print("wrote Data")
    else:
        print("data")
        chosen_username = choose_account(data)
        print('multiple, asked which')
        print(f"got :{chosen_username}")
        if chosen_username != []:
            for user in data:
                if user['username']==chosen_username[0]:
                    print(f"writing 'username':{user['username']},'password':{user['password']}")
                    data = {'username':user['username'],'password':user['password']}
                    write_data(data)

def register_hotkey():
    while True:
        keyboard.wait(hotkey=HOTKEY)
        hotkey()
        time.sleep(1)

def main():
    update()
    sTray = threading.Thread(target=startTray)
    sTray.start()
    hotkeyLoopThread = threading.Thread(target=register_hotkey)
    hotkeyLoopThread.start()

if __name__ == "__main__":
    main()