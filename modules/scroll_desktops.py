import win32gui
import win32api
import win32con
import time
from miscellaneous.utils import keyup_all_keyboard_keys

__last_switch_time = None

__invalid_scroll_item_classes = [
	"ReBarWindow32",
	"MSTaskSwWClass",
	"MSTaskListWClass",
	"TrayNotifyWnd",
]


def __switch_desktop(dy):
	global __last_switch_time

	current_time = time.time()

	if not __last_switch_time or current_time >= __last_switch_time + 0.2:
		ctrl_code = 0x11
		win_code = 0x5B

		if dy == -1:
			arrow_code = 0x27  # ->
		elif dy == 1:
			arrow_code = 0x25  # <-

		keyup_all_keyboard_keys()

		win32api.keybd_event(ctrl_code, 0, 0, 0)
		win32api.keybd_event(win_code, 0, 0, 0)
		win32api.keybd_event(arrow_code, 0, 0, 0)
		win32api.keybd_event(arrow_code, 0, win32con.KEYEVENTF_KEYUP, 0)
		win32api.keybd_event(win_code, 0, win32con.KEYEVENTF_KEYUP, 0)
		win32api.keybd_event(ctrl_code, 0, win32con.KEYEVENTF_KEYUP, 0)

		__last_switch_time = current_time


def __enum_taskbar_items_callback(hwnd, taskbar_buttons):
	taskbar_buttons.append(hwnd)


def __enum_taskbars_callback(hwnd, taskbars):
	class_name = win32gui.GetClassName(hwnd)

	if class_name == "Shell_TrayWnd" or class_name == "Shell_SecondaryTrayWnd":
		taskbars.append(hwnd)

	return True


def __handle_overview_scroll(dy):
	foreground_window_hwnd = win32gui.GetForegroundWindow()

	if foreground_window_hwnd != 0 and win32gui.GetClassName(foreground_window_hwnd) == "XamlExplorerHostIslandWindow":
		__switch_desktop(dy)


def __handle_taskbar_scroll(dy):
	taskbars = []

	win32gui.EnumWindows(__enum_taskbars_callback, taskbars)

	for taskbar_hwnd in taskbars:
		taskbar_rect = win32gui.GetWindowRect(taskbar_hwnd)
		mouse_x, mouse_y = win32api.GetCursorPos()

		if win32gui.PtInRect(taskbar_rect, (mouse_x, mouse_y)):
			taskbar_items = []
			win32gui.EnumChildWindows(taskbar_hwnd, __enum_taskbar_items_callback, taskbar_items)

			for item in taskbar_items:
				if win32gui.GetClassName(item) in __invalid_scroll_item_classes:
					item_rect = win32gui.GetWindowRect(item)

					if win32gui.PtInRect(item_rect, (mouse_x, mouse_y)):
						return True

			__switch_desktop(dy)


def on_scroll(dy):
	__handle_overview_scroll(dy)
	__handle_taskbar_scroll(dy)

	return True
