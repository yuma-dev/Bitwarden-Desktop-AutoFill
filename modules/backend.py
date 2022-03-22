from subprocess import check_output
import modules.crypt as crypt,os,json,ast,keyboard,time
import pyautogui as pag

def debug(*objects):
    import modules.debug as debugging,sys
    debugging.printDebug(objects,args=sys.argv)

def update(retry=False):
    """
    1. Login to Bitwarden CLI
    2. Get Session Key
    3. Synchronize CLI
    4. 
    """
    try:
        try:
            output = os.system("bw login --apikey")
            debug(output)
        except Exception as e:
            print(e)
            print("Could not log in, please check your config.py") 
            exit()
        session = check_output("bw unlock --passwordenv BW_PASSWORD",shell = True)
        sessionKey = session.split()[-1]
        sessionKey = rf"{sessionKey}"[2:-1]
        debug(sessionKey)
        output = check_output(f'bw sync --session {sessionKey}',shell = True)
        debug(output)
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
        debug(output)
        data = json.loads(output)
        try:
            os.makedirs('data')
        except OSError:
            debug("data folder already exists.")
        with open('data/enc', 'wb') as outfile:
            outfile.write(crypt.encrypt_message(str(data)))
    except Exception as e:
        if retry:
            raise Exception(e)
        else:
            print(e)
            try:
                print(os.system("bw login --apikey"))
            except Exception as e:
                print(e)
                print("Could not log in, please check your config.py")
            update(retry=True)

def get_matches(name):
    if type(name) != str:
        return AttributeError("False input type")
    matches = []
    with open('data/enc','rb') as f:
        decData = crypt.decrypt_message(f.read())

    debug(decData)
    
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

def get_estimated_matches(name):
    
    if type(name) != str:
        return AttributeError("False input type")
    keywords = name.lower().split() #not the fault for duplicates
    matches = []
    with open('data/enc','rb') as f:
        decData = crypt.decrypt_message(f.read())
    
    decData = ast.literal_eval(decData)#not the fault for duplicates
    
    #debug(str("\n\ndecData : \n\n"+decData+"\n\nDONE!\n\n"))
    
    for keyword in keywords: #not the fault for duplicates
        for site in decData: #for dict in list
            if site not in matches: #if dict not in m list
                try:
                    
                    found = False
                    for uri in site["login"]["uris"]:
                        if not found:
                            try:
                                #if uri["uri"].startswith(name):
                                if keyword in str(site["name"]).lower():
                                    matches.append(site)
                                    found = True
                                elif keyword in str(uri["uri"]).lower():
                                    matches.append(site)
                                    found = True
                            except Exception as e:
                                debug(e)
                                pass
                except Exception as e:
                    debug(e)
                    pass
    
    if debug  : print("\n\nMATCHES : \n\n",matches,"\n\nDONE!\n\n")
    fMatches = []
    for match in matches:
        try:
            name = match["name"]
            url = match["login"]["uris"][0]["uri"]
            username = match["login"]["username"]
            password = match["login"]["password"]
            fMatches.append({"name":name, "url":url, "username":username,"password":password})
        except KeyError:
            pass
    
    
    return fMatches

def get_data(name):
    matches = get_matches(name)
    debug(f"matches:{matches}")
    amount = len(matches)
    debug(f"length:{amount}")
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

def parse(unparsed):
    debug(unparsed)
    parsed = []
    urls=[]
    database = []
    for result in unparsed:
        if result not in parsed:
            try:
                lst = []
                index = unparsed.index(result)
                name = result['name']
                url = result['url']
                username = result['username']
                password = result['password']
                lst.append(name)
                lst.append(username)
                parsed.append(lst)
                database.append({"username":username,"password":password})
            except KeyError as e:
                print(e)
                pass
    return parsed,database

def write_data(data,mousepos=None):
    
    username = data['username']
    password = data['password']
    
    if username is None:
        username = ''
        debug(f"username : {username} password : {password}")
        if mousepos is not None:
            time.sleep(0.1)
            pag.click(mousepos)
        time.sleep(0.1)
        keyboard.write(password)
        
    if password is None:
        password = ''
        debug(f"username : {username} password : {password}")
        if mousepos is not None:
            time.sleep(0.1)
            pag.click(mousepos)
        time.sleep(0.1)
        keyboard.write(username)
        time.sleep(0.1)      

    if username is not None and password is not None:
        debug(f"username : {username} password : {password}")
        if mousepos is not None:
            time.sleep(0.1)
            pag.click(mousepos)
        time.sleep(0.1)
        keyboard.write(username)
        time.sleep(0.1)
        keyboard.press_and_release('tab')
        time.sleep(0.1)
        keyboard.write(password)
        
    if username is None and password is None:
        print("No Username and no Password!")
