import win32gui
import win32api
import win32con
import time
from components.settings import get_feature_state, TASKBAR_SCROLL
from miscellaneous.utils import keyup_all_keyboard_keys
from modules.move_windows import move_windows_to_next_desktop
from miscellaneous.virtual_desktop_accessor import VirtualDesktopAccessor


__last_switch_time = None

__invalid_scroll_item_classes = [
	"Start",
	"ReBarWindow32",
	"MSTaskSwWClass",
	"MSTaskListWClass",
	"TrayNotifyWnd",
]


def __switch_desktop(dy):
	global __last_switch_time

	current_time = time.time()

	if not __last_switch_time or current_time >= __last_switch_time + 0.3:
		current_desktop_number = VirtualDesktopAccessor.GetCurrentDesktopNumber()
		next_desktop_number = current_desktop_number + dy * -1

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

		__last_switch_time = time.time()

		# Minimizes wallpaper flickering while switching between virtual desktops, sometimes it works
		time.sleep(0.075)

		move_windows_to_next_desktop(next_desktop_number)


def __enum_taskbar_items_callback(hwnd, taskbar_buttons):
	taskbar_buttons.append(hwnd)


def __handle_overview_scroll(dy):
	foreground_window_hwnd = win32gui.GetForegroundWindow()

	if foreground_window_hwnd != 0 and win32gui.GetClassName(foreground_window_hwnd) == "XamlExplorerHostIslandWindow" and get_feature_state(TASKBAR_SCROLL):
		__switch_desktop(dy)

		return True

	return False


def __get_taskbars():
	taskbars = []

	primary_taskbar = win32gui.FindWindowEx(0, 0, "Shell_TrayWnd", None)

	if primary_taskbar:
		taskbars.append(primary_taskbar)

	secondary_taskbar = 0

	while True:
		secondary_taskbar = win32gui.FindWindowEx(0, secondary_taskbar, "Shell_SecondaryTrayWnd", None)

		if not secondary_taskbar:
			break

		taskbars.append(secondary_taskbar)

	return taskbars


def __handle_taskbar_scroll(dy):
	taskbars = __get_taskbars()

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
						return False

			if get_feature_state(TASKBAR_SCROLL):
				__switch_desktop(dy)

				return True

	return False


def on_scroll(dy):
	if __handle_overview_scroll(dy):
		return True

	elif __handle_taskbar_scroll(dy):
		return True
