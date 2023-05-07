import win32api
import win32con
import win32gui


def keyup_all_keyboard_keys():
	for key_code in range(256):
		if win32api.GetAsyncKeyState(key_code):
			win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def is_app_fullscreen():
	foreground_window_hwnd = win32gui.GetForegroundWindow()

	if foreground_window_hwnd == 0 or win32gui.GetClassName(foreground_window_hwnd) == "XamlExplorerHostIslandWindow":
		return False

	window_rect = win32gui.GetWindowRect(foreground_window_hwnd)
	monitor = win32api.MonitorFromWindow(foreground_window_hwnd, win32con.MONITOR_DEFAULTTONULL)

	if monitor:
		monitor_info = win32api.GetMonitorInfo(monitor)
		monitor_rect = monitor_info["Monitor"]

		return window_rect == monitor_rect
