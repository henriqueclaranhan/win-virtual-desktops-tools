from __future__ import annotations
import ctypes
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
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Failed to load DLL from '{self._dll_path}': {err}")

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
            self._dll.MoveWindowToDesktopNumber(hwnd, desktop_number)
            return True
        except Exception as err:
            print(f"[VirtualDesktopAdapter] Error MoveWindowToDesktopNumber: {err}")
            return False
