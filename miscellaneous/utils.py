import win32api
import win32con


def keyup_all_keyboard_keys():
	for key_code in range(256):
		if win32api.GetAsyncKeyState(key_code):
			win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
