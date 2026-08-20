import threading
import time
from pynput.mouse import Listener
from modules import scroll_desktops, hot_corner
from components import tray


def on_move(x, y):
	try:
		hot_corner.on_move(x, y)
	except Exception as err:
		print(f"Unexpected {err=}, {type(err)=}")


def on_scroll(x, y, dx, dy):
	try:
		scroll_desktops.on_scroll(x, y, dy)
	except Exception as err:
		print(f"Unexpected {err=}, {type(err)=}")


def check_virtual_desktop_switch():
	while True:
		try:
			scroll_desktops.check_desktop_changed()
		except Exception as err:
			print(f"Error checking desktop switch: {err}")
		time.sleep(0.2)


listener = Listener(on_move=on_move, on_scroll=on_scroll)
listener.start()

desktop_monitor_thread = threading.Thread(target=check_virtual_desktop_switch, daemon=True)
desktop_monitor_thread.start()

tray.setup_tray(listener)

