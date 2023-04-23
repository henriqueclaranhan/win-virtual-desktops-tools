import win32api
import win32con


state = False


def __toggle_overview():
	win_code = 0x5B
	tab_code = 0x09

	win32api.keybd_event(win_code, 0, 0, 0)
	win32api.keybd_event(tab_code, 0, 0, 0)
	win32api.keybd_event(win_code, 0, win32con.KEYEVENTF_KEYUP, 0)
	win32api.keybd_event(tab_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def on_move(x, y):
	global state

	if x <= 10 and y <= 10:
		if not state:
			__toggle_overview()
			state = True
	else:
		state = False

	return True
