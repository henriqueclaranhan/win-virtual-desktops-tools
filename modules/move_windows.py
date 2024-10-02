import win32gui
import win32api
import win32con
from miscellaneous.virtual_desktop_accessor import VirtualDesktopAccessor


def __get_all_windows():
	windows = []

	win32gui.EnumWindows(lambda hwnd, _: windows.append(hwnd), None)

	visible_windows = []

	for hwnd in windows:
		if win32gui.IsWindowVisible(hwnd):
			rect = win32gui.GetWindowRect(hwnd)
			visible_windows.append((hwnd, rect))

	return visible_windows


def __get_primary_monitor_info():
	monitor = win32api.MonitorFromPoint((0, 0), win32con.MONITOR_DEFAULTTOPRIMARY)
	monitor_info = win32api.GetMonitorInfo(monitor)

	return monitor_info


def move_windows_to_next_desktop(next_desktop_number):
	primary_monitor_info = __get_primary_monitor_info()
	windows = __get_all_windows()

	for hwnd, rect in windows:
		window_monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
		window_monitor_info = win32api.GetMonitorInfo(window_monitor)

		if window_monitor_info['Device'] != primary_monitor_info['Device']:
			VirtualDesktopAccessor.MoveWindowToDesktopNumber(hwnd, next_desktop_number)
