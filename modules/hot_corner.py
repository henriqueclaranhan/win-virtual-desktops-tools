import win32api
import win32con
import time
from components.settings import get_feature_state, HOT_CORNER
from miscellaneous.utils import keyup_all_keyboard_keys, is_app_fullscreen

__state = False
__last_state_time = 0
__monitors_cache = []
__last_monitors_update = 0


def __get_monitors_corners():
	global __monitors_cache, __last_monitors_update

	current_time = time.time()
	if not __monitors_cache or (current_time - __last_monitors_update) > 5.0:
		try:
			__monitors_cache = [
				(rect[0], rect[1])
				for _, _, rect in win32api.EnumDisplayMonitors()
			]
			__last_monitors_update = current_time
		except Exception:
			if not __monitors_cache:
				__monitors_cache = [(0, 0)]

	return __monitors_cache


def __toggle_overview():
	global __last_state_time

	current_time = time.time()

	if current_time <= __last_state_time + 0.5:
		return

	win_code = 0x5B
	tab_code = 0x09

	keyup_all_keyboard_keys()

	win32api.keybd_event(win_code, 0, 0, 0)
	win32api.keybd_event(tab_code, 0, 0, 0)
	win32api.keybd_event(win_code, 0, win32con.KEYEVENTF_KEYUP, 0)
	win32api.keybd_event(tab_code, 0, win32con.KEYEVENTF_KEYUP, 0)

	__last_state_time = current_time


def on_move(x=None, y=None):
	global __state

	if not get_feature_state(HOT_CORNER):
		__state = False
		return True

	if x is None or y is None:
		x, y = win32api.GetCursorPos()

	corners = __get_monitors_corners()
	in_corner = any(left <= x <= left + 6 and top <= y <= top + 6 for left, top in corners)

	if in_corner:
		if not __state:
			if not is_app_fullscreen(x, y):
				__toggle_overview()
				__state = True
	else:
		__state = False

	return True

