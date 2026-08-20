import win32api
import win32con
import time
from components.settings import (
	get_feature_state,
	get_monitor_corners,
	HOT_CORNER,
)
from miscellaneous.utils import keyup_all_keyboard_keys, is_app_fullscreen

__state = False
__last_state_time = 0
__active_corners_cache = []
__last_cache_update = 0


def refresh_active_corners():
	global __active_corners_cache, __last_cache_update

	try:
		monitors = win32api.EnumDisplayMonitors()
	except Exception:
		monitors = [(None, None, (0, 0, 1920, 1080))]

	new_active_corners = []

	for idx, (h_mon, hdc, rect) in enumerate(monitors):
		left, top, right, bottom = rect
		corners_config = get_monitor_corners(idx)

		if corners_config.get("top_left", False):
			new_active_corners.append((left, top, left + 6, top + 6))
		if corners_config.get("top_right", False):
			new_active_corners.append((right - 6, top, right, top + 6))
		if corners_config.get("bottom_left", False):
			new_active_corners.append((left, bottom - 6, left + 6, bottom))
		if corners_config.get("bottom_right", False):
			new_active_corners.append((right - 6, bottom - 6, right, bottom))

	__active_corners_cache = new_active_corners
	__last_cache_update = time.time()


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

	current_time = time.time()
	if not __active_corners_cache or (current_time - __last_cache_update) > 5.0:
		refresh_active_corners()

	in_corner = any(x1 <= x <= x2 and y1 <= y <= y2 for x1, y1, x2, y2 in __active_corners_cache)

	if in_corner:
		if not __state:
			if not is_app_fullscreen(x, y):
				__toggle_overview()
				__state = True
	else:
		__state = False

	return True
