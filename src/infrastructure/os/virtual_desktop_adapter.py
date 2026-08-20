from __future__ import annotations
import ctypes
import ctypes.wintypes
import os
from typing import Optional
from src.infrastructure.storage.path_resolver import PathResolver


class VirtualDesktopAdapter:
    """Wrapper for VirtualDesktopAccessor.dll providing access to Windows virtual desktop APIs."""

    def __init__(self, dll_path: Optional[str] = None):
        self._dll_path = dll_path or PathResolver.get_dll_path()
        self._dll: Optional[ctypes.WinDLL] = None
        self._load_dll()

    def _load_dll(self) -> None:
        if not os.path.exists(self._dll_path):
            print(f"[VirtualDesktopAdapter] Warning: DLL not found at '{self._dll_path}'")
            return

        try:
            self._dll = ctypes.WinDLL(self._dll_path)
            self._setup_signatures()
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Failed to load DLL from '{self._dll_path}': {err}")

    def _setup_signatures(self) -> None:
        if not self._dll:
            return

        try:
            if hasattr(self._dll, "GetCurrentDesktopNumber"):
                self._dll.GetCurrentDesktopNumber.restype = ctypes.c_int
                self._dll.GetCurrentDesktopNumber.argtypes = []

            if hasattr(self._dll, "GetDesktopCount"):
                self._dll.GetDesktopCount.restype = ctypes.c_int
                self._dll.GetDesktopCount.argtypes = []

            if hasattr(self._dll, "MoveWindowToDesktopNumber"):
                self._dll.MoveWindowToDesktopNumber.restype = ctypes.c_int
                self._dll.MoveWindowToDesktopNumber.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]

            if hasattr(self._dll, "IsPinnedWindow"):
                self._dll.IsPinnedWindow.restype = ctypes.c_int
                self._dll.IsPinnedWindow.argtypes = [ctypes.wintypes.HWND]

            if hasattr(self._dll, "PinWindow"):
                self._dll.PinWindow.restype = ctypes.c_int
                self._dll.PinWindow.argtypes = [ctypes.wintypes.HWND]

            if hasattr(self._dll, "UnPinWindow"):
                self._dll.UnPinWindow.restype = ctypes.c_int
                self._dll.UnPinWindow.argtypes = [ctypes.wintypes.HWND]

            if hasattr(self._dll, "IsPinnedApp"):
                self._dll.IsPinnedApp.restype = ctypes.c_int
                self._dll.IsPinnedApp.argtypes = [ctypes.wintypes.HWND]

            if hasattr(self._dll, "PinApp"):
                self._dll.PinApp.restype = ctypes.c_int
                self._dll.PinApp.argtypes = [ctypes.wintypes.HWND]

            if hasattr(self._dll, "UnPinApp"):
                self._dll.UnPinApp.restype = ctypes.c_int
                self._dll.UnPinApp.argtypes = [ctypes.wintypes.HWND]

            if hasattr(self._dll, "GoToDesktopNumber"):
                self._dll.GoToDesktopNumber.restype = ctypes.c_int
                self._dll.GoToDesktopNumber.argtypes = [ctypes.c_int]

            if hasattr(self._dll, "GetDesktopName"):
                self._dll.GetDesktopName.restype = ctypes.c_int
                self._dll.GetDesktopName.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t]
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error setting up signatures: {err}")

    def get_current_desktop_number(self) -> int:
        if not self._dll:
            return 0
        try:
            return int(self._dll.GetCurrentDesktopNumber())
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error GetCurrentDesktopNumber: {err}")
            return 0

    def get_desktop_count(self) -> int:
        if not self._dll:
            return 1
        try:
            return int(self._dll.GetDesktopCount())
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error GetDesktopCount: {err}")
            return 1

    def move_window_to_desktop_number(self, hwnd: int, desktop_number: int) -> bool:
        if not self._dll:
            return False
        try:
            res = self._dll.MoveWindowToDesktopNumber(hwnd, desktop_number)
            return res == 1 or res == 0
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error MoveWindowToDesktopNumber: {err}")
            return False

    def is_pinned_window(self, hwnd: int) -> bool:
        if not self._dll:
            return False
        try:
            return bool(self._dll.IsPinnedWindow(hwnd) == 1)
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error IsPinnedWindow: {err}")
            return False

    def pin_window(self, hwnd: int) -> bool:
        if not self._dll:
            return False
        try:
            return bool(self._dll.PinWindow(hwnd) == 1)
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error PinWindow: {err}")
            return False

    def unpin_window(self, hwnd: int) -> bool:
        if not self._dll:
            return False
        try:
            return bool(self._dll.UnPinWindow(hwnd) == 1)
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error UnPinWindow: {err}")
            return False

    def is_pinned_app(self, hwnd: int) -> bool:
        if not self._dll:
            return False
        try:
            return bool(self._dll.IsPinnedApp(hwnd) == 1)
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error IsPinnedApp: {err}")
            return False

    def pin_app(self, hwnd: int) -> bool:
        if not self._dll:
            return False
        try:
            return bool(self._dll.PinApp(hwnd) == 1)
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error PinApp: {err}")
            return False

    def unpin_app(self, hwnd: int) -> bool:
        if not self._dll:
            return False
        try:
            return bool(self._dll.UnPinApp(hwnd) == 1)
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error UnPinApp: {err}")
            return False
