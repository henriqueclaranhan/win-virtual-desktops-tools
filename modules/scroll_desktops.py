import win32gui
import win32api
import win32con

__invalid_scroll_item_classes = [
	"ReBarWindow32",
    "MSTaskSwWClass",
    "MSTaskListWClass",
    "TrayNotifyWnd",
]


def __switch_desktop(dy):
	ctrl_code = 0x11
	win_code = 0x5B

	if dy == -1:
		arrow_code = 0x27  # ->

	elif dy == 1:
		arrow_code = 0x25  # <-

	win32api.keybd_event(ctrl_code, 0, 0, 0)
	win32api.keybd_event(win_code, 0, 0, 0)
	win32api.keybd_event(arrow_code, 0, 0, 0)
	win32api.keybd_event(arrow_code, 0, win32con.KEYEVENTF_KEYUP, 0)
	win32api.keybd_event(win_code, 0, win32con.KEYEVENTF_KEYUP, 0)
	win32api.keybd_event(ctrl_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def __enum_child_windows_callback(hwnd, taskbar_buttons):
	taskbar_buttons.append(hwnd)


def on_scroll(x, y, dx, dy):
	taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
	taskbar_rect = win32gui.GetWindowRect(taskbar_hwnd)
	mouse_x, mouse_y = win32api.GetCursorPos()

	if win32gui.PtInRect(taskbar_rect, (mouse_x, mouse_y)):
		taskbar_items = []
		win32gui.EnumChildWindows(taskbar_hwnd, __enum_child_windows_callback, taskbar_items)

		for item in taskbar_items:
			if win32gui.GetClassName(item) in __invalid_scroll_item_classes:
				item_rect = win32gui.GetWindowRect(item)

				if win32gui.PtInRect(item_rect, (mouse_x, mouse_y)):
					return True

		__switch_desktop(dy)

	return True
