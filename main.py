import os
import sys
import pystray
from PIL import Image
from pynput.mouse import Listener
from modules import scroll_desktops, hot_corner


def get_resource_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


def on_exit(icon):
	listener.stop()
	icon.stop()


def setup_tray_icon():
	image = Image.open(get_resource_path("icon.ico"))

	icon = pystray.Icon("Win Virtual Desktops Tools", image)
	icon.title = "Win Virtual Desktops Tools"
	icon.menu = pystray.Menu(pystray.MenuItem("Exit", on_exit))

	icon.run()


listener = Listener(on_move=hot_corner.on_move, on_scroll=scroll_desktops.on_scroll)
listener.start()

setup_tray_icon()
