import win32api
import win32con
import win32gui

__ingore_fullscreen_classes = [
	"WorkerW",
	"XamlExplorerHostIslandWindow",
]

key_codes_release = [
    win32con.VK_LSHIFT, win32con.VK_RSHIFT, win32con.VK_LCONTROL, win32con.VK_RCONTROL,
    win32con.VK_LMENU, win32con.VK_RMENU, win32con.VK_LWIN, win32con.VK_RWIN,
]


def keyup_all_keyboard_keys():
	for key in key_codes_release:
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)


def is_app_fullscreen():
	x, y = win32api.GetCursorPos()

	window_hwnd = win32gui.WindowFromPoint((x, y))

	if window_hwnd == 0 or win32gui.GetClassName(window_hwnd) in __ingore_fullscreen_classes:
		return False

	monitor = win32api.MonitorFromWindow(window_hwnd, win32con.MONITOR_DEFAULTTONULL)

	if monitor:
		window_rect = win32gui.GetWindowRect(window_hwnd)
		monitor_info = win32api.GetMonitorInfo(monitor)
		monitor_rect = monitor_info["Monitor"]

		return window_rect == monitor_rect

	return False
