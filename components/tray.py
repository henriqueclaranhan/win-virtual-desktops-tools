import os
import sys
import pystray
import win32api
from PIL import Image
from threading import Thread
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


def __handle_updates_behaviors(icon: pystray.Icon, menu_items: list):
	have_update = check_updates()

	if have_update:
		menu_items.insert(0, pystray.MenuItem("⚠️ Update Available", __on_click_update))

		image = Image.open(__get_resource_path("assets/icon-update.ico"))

		icon.icon = image
		icon.menu = pystray.Menu(*menu_items)


def setup_tray(listener):
	menu_items = [
		pystray.MenuItem("❎ Exit", lambda: __on_exit(icon, listener))
	]

	icon = pystray.Icon(
		icon=Image.open(__get_resource_path("assets/icon.ico")),
		name="Win Virtual Desktops Tools",
		title="Win Virtual Desktops Tools",
		menu=pystray.Menu(*menu_items)
	)

	Thread(target=__handle_updates_behaviors, args=(icon, menu_items)).start()

	icon.run()
