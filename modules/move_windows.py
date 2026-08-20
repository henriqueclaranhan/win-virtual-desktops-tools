import win32gui
import win32api
import win32con
from components.settings import get_feature_state, KEEP_WINDOWS
from miscellaneous.virtual_desktop_accessor import VirtualDesktopAccessor


def __get_all_windows():
	windows = []

	def enum_callback(hwnd, _):
		if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowTextLength(hwnd) > 0 and win32gui.GetParent(hwnd) == 0:
			windows.append(hwnd)

	win32gui.EnumWindows(enum_callback, None)
	return windows


def __get_primary_monitor_info():
	monitor = win32api.MonitorFromPoint((0, 0), win32con.MONITOR_DEFAULTTOPRIMARY)
	return win32api.GetMonitorInfo(monitor)


def move_windows_to_next_desktop(next_desktop_number):
	if not get_feature_state(KEEP_WINDOWS):
		return False

	# If there is only one monitor, there are no secondary windows to move
	try:
		if len(win32api.EnumDisplayMonitors()) <= 1:
			return False
	except Exception:
		pass

	primary_monitor_info = __get_primary_monitor_info()
	primary_device = primary_monitor_info.get("Device")
	windows = __get_all_windows()

	for hwnd in windows:
		try:
			window_monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
			window_monitor_info = win32api.GetMonitorInfo(window_monitor)

			if window_monitor_info.get("Device") != primary_device:
				VirtualDesktopAccessor.MoveWindowToDesktopNumber(hwnd, next_desktop_number)
		except Exception:
			continue

