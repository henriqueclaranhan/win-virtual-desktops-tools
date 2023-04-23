from pynput.mouse import Listener
from modules import scroll_desktops, hot_corner
from components import tray


def on_move(x, y):
	hot_corner.on_move(x, y)


def on_scroll(x, y, dx, dy):
	scroll_desktops.on_scroll(dy)


listener = Listener(on_move=on_move, on_scroll=on_scroll)
listener.start()

tray.setup_tray(listener)
