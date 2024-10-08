import win32api
import win32con
import time
from components.settings import get_feature_state, HOT_CORNER
from miscellaneous.utils import keyup_all_keyboard_keys

__state = False
__last_state_time = None


def __toggle_overview():
	global __last_state_time

	current_time = time.time()

	if __last_state_time and current_time <= __last_state_time + 0.5:
		return

	win_code = 0x5B
	tab_code = 0x09

	keyup_all_keyboard_keys()

	win32api.keybd_event(win_code, 0, 0, 0)
	win32api.keybd_event(tab_code, 0, 0, 0)
	win32api.keybd_event(win_code, 0, win32con.KEYEVENTF_KEYUP, 0)
	win32api.keybd_event(tab_code, 0, win32con.KEYEVENTF_KEYUP, 0)

	__last_state_time = current_time


def on_move():
	global __state

	x, y = win32api.GetCursorPos()

	monitor_handle = win32api.MonitorFromPoint((x, y), win32con.MONITOR_DEFAULTTONEAREST)
	monitor_rect = win32api.GetMonitorInfo(monitor_handle)["Monitor"]

	if x <= monitor_rect[0] + 6 and y <= 6:
		if not __state and get_feature_state(HOT_CORNER):
			__toggle_overview()
			__state = True
	else:
		__state = False

	return True
