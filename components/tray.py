import os
import sys
import pystray
import win32api
from PIL import Image
from _version import check_updates, __releases_url__


def __get_resource_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


def __on_click_update():
	win32api.ShellExecute(0, 'open', __releases_url__, None, None, 1)


def __on_exit(icon, listener):
	listener.stop()
	icon.stop()


def setup_tray(listener):
	have_update = check_updates()

	icon_filename = "icon" if not have_update else "icon-update"
	image = Image.open(__get_resource_path(f"assets/{icon_filename}.ico"))
	icon = pystray.Icon("Win Virtual Desktops Tools", image, "Win Virtual Desktops Tools")

	icon.menu = pystray.Menu(
		pystray.MenuItem("Update Available", __on_click_update, visible=have_update),
		pystray.MenuItem("Exit", lambda: __on_exit(icon, listener))
	)

	icon.run()
