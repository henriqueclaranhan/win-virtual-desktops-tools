import os
import sys
import pystray
from PIL import Image


def __get_resource_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


def __on_exit(icon, listener):
	listener.stop()
	icon.stop()


def setup_tray(listener):
	image = Image.open(__get_resource_path("icon.ico"))

	icon = pystray.Icon("Win Virtual Desktops Tools", image)
	icon.title = "Win Virtual Desktops Tools"

	icon.menu = pystray.Menu(
		pystray.MenuItem("Exit", lambda: __on_exit(icon, listener))
	)

	icon.run()
