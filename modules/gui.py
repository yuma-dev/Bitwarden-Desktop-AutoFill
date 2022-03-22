import PySimpleGUI as sg
import modules.crypt as crypt,sys,modules.backend as backend
sg.theme('DarkGrey13')

def debug(*objects):
    import modules.debug as debugging,sys
    debugging.printDebug(objects,args=sys.argv)

def choose_search(windowtitle):
    windowtitle = windowtitle.replace("-"," ").replace("."," ").replace("_"," ").replace("   "," ").replace("  "," ").replace("    "," ")
    unparsedresults = backend.get_estimated_matches(windowtitle)
    results,database = backend.parse(unparsedresults)
    debug('\n\nRESULTS : \n\n')
    debug(results)
    debug('\n\nRESULTS END \n\n')
    debug('\n\DATABASE : \n\n')
    debug(database)
    debug('\n\DATABASE END \n\n')
    layout = [
        [
            sg.Input(
                windowtitle, 
                size=(40, 1), 
                key='-TERM-'
                )
        ],
        
        [
            sg.Column(
                [[
                    sg.Checkbox('Only User'),
                    sg.Checkbox('Only Pw')
                ]],justification='center'
            )
        ],
        
        [
            sg.Table(
                values=results,
                size=(None,len(results)),
                justification='left',
                headings=['Entryname','Username'],
                hide_vertical_scroll = True,
                bind_return_key = True,
                key = '-TABLE-',
            )
        ],
        
        [sg.Column(
            [[sg.Submit(key='-SUBMIT-',button_color=('white','#335e1f')),
                sg.Cancel(key='-CANCEL-',button_color=('white', '#471b1b')),
                sg.Button("Username",tooltip='Writes only the Username in the field you hovered over while opening Autofill'),
                sg.Button("Password",tooltip='Writes only the Username in the field you hovered over while opening Autofill')
                ]
              ], key = '-BUTTONS-',justification='center')
        ]
        
        ]

    window = sg.Window('Search Engine',layout=layout, finalize=True, alpha_channel=0.9,transparent_color='#232323', use_default_focus=True,return_keyboard_events=True,no_titlebar=True,keep_on_top=True,grab_anywhere=True)
    window.force_focus()
    window['-BUTTONS-'].hide_row()
    x,y = window.current_location()
    window.move(x,0)
    # main event loop
    cancelled = False
    while True:
        
        event, values = window.read()
        debug("event:",event," | values:", values)
        if event == sg.WINDOW_CLOSED:
            window.close()
            return None
        if event == '-CANCEL-' or str(event).lower().startswith("escape"):
            cancelled = True
            window.close()
            return None
        if not cancelled:
            if str(event).lower() in "abcdefghijklmnopqrstuvwxyz" or str(event).lower().startswith("backspace"):
                search = values['-TERM-']
                if search != '':
                    #debug(search)
                    searchvalues = backend.get_estimated_matches(search)
                    #debug(searchvalues)
                    parsed,database = backend.parse(searchvalues)
                    #debug(parse(searchvalues))
                    height =len(parsed)
                    if height > 50:
                        height = 51
                        

                    length = len(parsed)
                    if length > 50:
                        length = 50
                    window['-TABLE-'].set_size(size=(None,length))
                    window['-TABLE-'].Update(values=parsed)
                    window['-TABLE-'].unhide_row()

                else:
                    window['-TABLE-'].Update(values=[])
                    window['-TABLE-'].hide_row()
            if event == '-SUBMIT-' or str(event) == "-TABLE-":
                indx = int(str(values['-TABLE-'])[1:-1])
                debug(f"DONE! {indx}")
                db = database[indx]
                window.close()
                return db
            

def choose_account(accounts):
    usernames = []
    debug(f'accounts:{accounts}')
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
