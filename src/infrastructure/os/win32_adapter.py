from __future__ import annotations
import win32api
import win32con
import win32gui
from typing import List, Tuple, Optional
from src.core.models.monitor import MonitorInfo, MonitorRect


class WindowsAdapter:
    """Encapsulates Windows API interactions, Win32 window manipulation, and input synthesis."""

    IGNORE_FULLSCREEN_CLASSES = {
        "WorkerW",
        "XamlExplorerHostIslandWindow",
        "Shell_TrayWnd",
        "Shell_SecondaryTrayWnd",
        "Progman",
    }

    INVALID_SCROLL_ITEM_CLASSES = {
        "Start",
        "ReBarWindow32",
        "MSTaskSwWClass",
        "MSTaskListWClass",
        "TrayNotifyWnd",
    }

    MODIFIER_KEY_CODES = [
        win32con.VK_LSHIFT, win32con.VK_RSHIFT,
        win32con.VK_LCONTROL, win32con.VK_RCONTROL,
        win32con.VK_LMENU, win32con.VK_RMENU,
        win32con.VK_LWIN, win32con.VK_RWIN,
    ]

    VK_LWIN = 0x5B
    VK_TAB = 0x09
    VK_LEFT = 0x25
    VK_RIGHT = 0x27
    VK_CONTROL = 0x11

    @staticmethod
    def get_cursor_pos() -> Tuple[int, int]:
        return win32api.GetCursorPos()

    @classmethod
    def get_connected_monitors(cls) -> List[MonitorInfo]:
        """Enumerates all active display monitors with coordinates and primary monitor indicator."""
        monitors: List[MonitorInfo] = []
        try:
            enum_mons = win32api.EnumDisplayMonitors()
            primary_device = cls.get_primary_monitor_device()

            for idx, (h_mon, hdc, rect) in enumerate(enum_mons):
                info = win32api.GetMonitorInfo(h_mon)
                device = info.get("Device", f"Display {idx + 1}")
                is_primary = (device == primary_device)
                m_rect = MonitorRect(left=rect[0], top=rect[1], right=rect[2], bottom=rect[3])
                monitors.append(MonitorInfo(
                    index=idx,
                    device_name=device,
                    rect=m_rect,
                    is_primary=is_primary
                ))
        except Exception as err:
            print(f"[WindowsAdapter] Error enumerating monitors: {err}")
            monitors.append(MonitorInfo(
                index=0,
                device_name="Display 1",
                rect=MonitorRect(left=0, top=0, right=1920, bottom=1080),
                is_primary=True
            ))

        return monitors

    @staticmethod
    def get_primary_monitor_device() -> Optional[str]:
        try:
            primary_mon = win32api.MonitorFromPoint((0, 0), win32con.MONITOR_DEFAULTTOPRIMARY)
            primary_info = win32api.GetMonitorInfo(primary_mon)
            return primary_info.get("Device")
        except Exception:
            return None

    @classmethod
    def is_app_fullscreen(cls, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Checks if the window at (x, y) is currently taking up the full monitor space."""
        if x is None or y is None:
            x, y = cls.get_cursor_pos()

        window_hwnd = win32gui.WindowFromPoint((x, y))
        if window_hwnd == 0 or win32gui.GetClassName(window_hwnd) in cls.IGNORE_FULLSCREEN_CLASSES:
            return False

        monitor = win32api.MonitorFromWindow(window_hwnd, win32con.MONITOR_DEFAULTTONULL)
        if monitor:
            window_rect = win32gui.GetWindowRect(window_hwnd)
            monitor_info = win32api.GetMonitorInfo(monitor)
            monitor_rect = monitor_info.get("Monitor")
            return window_rect == monitor_rect

        return False

    @classmethod
    def get_taskbar_windows(cls) -> List[int]:
        """Returns HWNDs of all primary and secondary taskbars."""
        taskbars = []
        primary = win32gui.FindWindowEx(0, 0, "Shell_TrayWnd", None)
        if primary:
            taskbars.append(primary)

        secondary = 0
        while True:
            secondary = win32gui.FindWindowEx(0, secondary, "Shell_SecondaryTrayWnd", None)
            if not secondary:
                break
            taskbars.append(secondary)

        return taskbars

    @classmethod
    def is_point_over_taskbar(cls, x: int, y: int) -> bool:
        """Checks if the coordinate is over a valid taskbar area (excluding invalid items like Start/Task items)."""
        taskbars = cls.get_taskbar_windows()

        for tb_hwnd in taskbars:
            tb_rect = win32gui.GetWindowRect(tb_hwnd)
            if win32gui.PtInRect(tb_rect, (x, y)):
                hwnd_under_cursor = win32gui.WindowFromPoint((x, y))
                curr = hwnd_under_cursor
                while curr and curr != 0:
                    if win32gui.GetClassName(curr) in cls.INVALID_SCROLL_ITEM_CLASSES:
                        return False
                    if curr == tb_hwnd:
                        break
                    curr = win32gui.GetParent(curr)
                return True

        return False

    @classmethod
    def is_overview_foreground(cls) -> bool:
        """Checks if Windows Task View (Overview) is currently in the foreground."""
        fg_hwnd = win32gui.GetForegroundWindow()
        if fg_hwnd != 0 and win32gui.GetClassName(fg_hwnd) == "XamlExplorerHostIslandWindow":
            return True
        return False

    @classmethod
    def get_all_visible_top_level_windows(cls) -> List[int]:
        """Returns HWNDs of visible top-level application windows with titles."""
        windows: List[int] = []

        def enum_callback(hwnd, _):
            if (
                win32gui.IsWindowVisible(hwnd)
                and win32gui.GetWindowTextLength(hwnd) > 0
                and win32gui.GetParent(hwnd) == 0
            ):
                windows.append(hwnd)

        win32gui.EnumWindows(enum_callback, None)
        return windows

    @staticmethod
    def get_window_monitor_device(hwnd: int) -> Optional[str]:
        try:
            window_monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
            window_monitor_info = win32api.GetMonitorInfo(window_monitor)
            return window_monitor_info.get("Device")
        except Exception:
            return None

    @classmethod
    def release_all_modifier_keys(cls) -> None:
        """Releases any stuck modifier keys before sending simulated keyboard input."""
        for key in cls.MODIFIER_KEY_CODES:
            win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

    @classmethod
    def trigger_task_view_shortcut(cls) -> None:
        """Simulates Win + Tab to toggle Task View."""
        cls.release_all_modifier_keys()
        win32api.keybd_event(cls.VK_LWIN, 0, 0, 0)
        win32api.keybd_event(cls.VK_TAB, 0, 0, 0)
        win32api.keybd_event(cls.VK_LWIN, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(cls.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)

    @classmethod
    def trigger_desktop_switch_shortcut(cls, direction: int) -> None:
        """Simulates Ctrl + Win + Left/Right to switch virtual desktops (direction: 1 for right, -1 for left)."""
        arrow_code = cls.VK_RIGHT if direction > 0 else cls.VK_LEFT

        cls.release_all_modifier_keys()
        win32api.keybd_event(cls.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(cls.VK_LWIN, 0, 0, 0)
        win32api.keybd_event(arrow_code, 0, 0, 0)
        win32api.keybd_event(arrow_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(cls.VK_LWIN, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(cls.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
