import win32api
import win32con
from miscellaneous.utils import keyup_all_keyboard_keys

__state = False


def __toggle_overview():
	win_code = 0x5B
	tab_code = 0x09

	keyup_all_keyboard_keys()

	win32api.keybd_event(win_code, 0, 0, 0)
	win32api.keybd_event(tab_code, 0, 0, 0)
	win32api.keybd_event(win_code, 0, win32con.KEYEVENTF_KEYUP, 0)
	win32api.keybd_event(tab_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def on_move(x, y):
	global __state

	if x <= 6 and y <= 6:
		if not __state:
			__toggle_overview()
			__state = True
	else:
		__state = False

	return True
