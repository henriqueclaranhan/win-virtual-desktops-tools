import win32api
import win32con
import win32gui

__ignore_fullscreen_classes = {
	"WorkerW",
	"XamlExplorerHostIslandWindow",
	"Shell_TrayWnd",
	"Shell_SecondaryTrayWnd",
	"Progman",
}

key_codes_release = [
    win32con.VK_LSHIFT, win32con.VK_RSHIFT, win32con.VK_LCONTROL, win32con.VK_RCONTROL,
    win32con.VK_LMENU, win32con.VK_RMENU, win32con.VK_LWIN, win32con.VK_RWIN,
]


def keyup_all_keyboard_keys():
	for key in key_codes_release:
		win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)


def is_app_fullscreen(x=None, y=None):
	if x is None or y is None:
		x, y = win32api.GetCursorPos()

	window_hwnd = win32gui.WindowFromPoint((x, y))

	if window_hwnd == 0 or win32gui.GetClassName(window_hwnd) in __ignore_fullscreen_classes:
		return False

	monitor = win32api.MonitorFromWindow(window_hwnd, win32con.MONITOR_DEFAULTTONULL)

	if monitor:
		window_rect = win32gui.GetWindowRect(window_hwnd)
		monitor_info = win32api.GetMonitorInfo(monitor)
		monitor_rect = monitor_info["Monitor"]

		return window_rect == monitor_rect

	return False

