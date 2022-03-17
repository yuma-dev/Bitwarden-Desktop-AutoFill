import os,urllib.request,sys
try:
    import urllib.request,threading,time,os,shutil
    from progress.spinner import PixelSpinner

    def get_secrets():
        import PySimpleGUI as sg   
        sg.theme('DarkGrey13')
        layout = [[sg.Text('Please fill out the following information:')],      
                        [sg.T("ClientID", size=(15, 1)),sg.InputText(key='ID',size=(20, 1))],
                        [sg.T("ClientSecret", size=(15, 1)),sg.InputText(key='SECRET',size=(20, 1))],
                        [sg.T("Password", size=(15, 1)),sg.InputText(key='PASSWORD',size=(20, 1))],
                        [sg.Submit(bind_return_key=True)]]      

        window = sg.Window('Bitwarden Autofill Account Selection', layout,no_titlebar=True,keep_on_top=True,grab_anywhere=True)
        event, values = window.read()    
        window.close()

        clientid = values['ID']
        clientsecret = values['SECRET']
        masterpassword = values['PASSWORD']
        if masterpassword=="" or clientsecret=="" or clientid=="":
            sg.popup("Cancel", "Not all info supplied!")
            return get_secrets()
        else:
            return clientid, clientsecret, masterpassword

    class spin():

        def downloadSpinner(Text,interval):
            spinner = PixelSpinner(Text+' ')
            global state
            state = "UNFINISHED"
            while state != 'FINISHED':
                time.sleep(interval)
                spinner.next()
                
        def start(Text,interval=0.1):
            os.system("cls")
            spinnerThread = threading.Thread(target=spin.downloadSpinner,args=[Text,interval])
            spinnerThread.start()

            
        def stop():
            global state
            state = "FINISHED"
            time.sleep(0.1)
            os.system("cls")
            print("Done!")
            
    spin.start("Downloading")
    urllib.request.urlretrieve("https://github.com/yuma-dev/Bitwarden-Desktop-AutoFill/archive/refs/heads/main.zip","main.zip")
    spin.stop()
    spin.start("Unzipping")
    shutil.unpack_archive("main.zip", "main")
    spin.stop()
    spin.start("Deleting Zip")
    os.remove("main.zip")
    spin.stop()

    source = "main/Bitwarden-Desktop-AutoFill-main"
    final = "main/"
    files = os.listdir(source)
    for file in files:
        file_name = os.path.join(source, file)
        spin.start(f"Moving {file_name} to {source}")
        shutil.move(file_name, final)
        spin.stop()

    spin.start("Removing old Directory")
    os.rmdir("main/Bitwarden-Desktop-AutoFill-main")
    spin.stop()

    removeList = [".gitattributes",".gitignore","requirements.txt","README.md","installer.py"]
    for filename in removeList:
        spin.start(f"Removing {filename}")
        os.remove("main/"+filename)
        spin.stop()
        
    input("For the next steps you need your API ClientID and ClientSecret : https://bitwarden.com/help/personal-api-key/\nPress Enter to continue...")
    clientid, clientsecret, masterpassword= get_secrets()
    with open("main/config.py","w") as f:
        f.write(f"CLIENTID = '{clientid}'\nCLIENTSECRET = '{clientsecret}'\nPASSWORD = '{masterpassword}'\nHOTKEY = 'shift+windows+d'")
    os.remove(sys.argv[0])
    exit()
except ImportError:
    githuburl= "https://raw.githubusercontent.com/yuma-dev/Bitwarden-Desktop-AutoFill/main/requirements.txt"
    urllib.request.urlretrieve(githuburl,'requirements.txt')
    os.system("python -m pip install -r requirements.txt")
    os.system("cls")
    print("Done installing modules...")
    os.remove("requirements.txt")
    os.execv(sys.executable, ['py'] + sys.argv)