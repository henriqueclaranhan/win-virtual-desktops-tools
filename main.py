from pynput.mouse import Listener
from modules import scroll_desktops, hot_corner
from components import tray
from miscellaneous import utils


def on_move(x, y):
	if utils.is_app_fullscreen():
		return

	hot_corner.on_move()


def on_scroll(x, y, dx, dy):
	if utils.is_app_fullscreen():
		return

	scroll_desktops.on_scroll(dy)


listener = Listener(on_move=on_move, on_scroll=on_scroll)
listener.start()

tray.setup_tray(listener)
