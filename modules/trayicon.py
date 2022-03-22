import pystray,modules.backend as backend,psutil,os,sys
from PIL import Image
from pystray import MenuItem as item

icon_path = "sprites/icon.ico"

def on_restart(self):
    icon.stop()
    os.execv(sys.executable, ['pyw'] + sys.argv)

def on_exit(self):
    icon.stop()
    psutil.Process(os.getpid()).terminate()
    
def on_update():
    backend.update()

image = Image.open(icon_path)
menu = pystray.Menu(
    item('Restart', on_restart),
    #item('Open Logs', open_logs),
    item('Update', on_update),
    item('Exit', on_exit)
    )
icon = pystray.Icon("RPC", image, "Bitwarden", menu)