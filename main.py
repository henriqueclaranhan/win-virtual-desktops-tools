import threading
import time
from pynput.mouse import Listener
from modules import scroll_desktops, hot_corner
from components import tray
from miscellaneous import utils


def on_move(x, y):
	try:
		if not utils.is_app_fullscreen():
			hot_corner.on_move()

	except Exception as err:
		print(f"Unexpected {err=}, {type(err)=}")
		raise


def on_scroll(x, y, dx, dy):
	try:
		if not utils.is_app_fullscreen():
			scroll_desktops.on_scroll(dy)

	except Exception as err:
		print(f"Unexpected {err=}, {type(err)=}")
		raise


def check_virtual_desktop_switch():
	while True:
		scroll_desktops.check_desktop_changed()
		time.sleep(0.2)


listener = Listener(on_move=on_move, on_scroll=on_scroll)
listener.start()

desktop_monitor_thread = threading.Thread(target=check_virtual_desktop_switch, daemon=True)
desktop_monitor_thread.start()

tray.setup_tray(listener)
