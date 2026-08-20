from __future__ import annotations
from typing import Optional
from src.infrastructure.os.win32_adapter import WindowsAdapter
from src.infrastructure.os.virtual_desktop_adapter import VirtualDesktopAdapter
from src.infrastructure.storage.config_repository import ConfigRepository


class WindowManagerService:
    """Manages window positions across virtual desktops and monitors."""

    def __init__(
        self,
        config_repo: ConfigRepository,
        win_adapter: Optional[WindowsAdapter] = None,
        vda_adapter: Optional[VirtualDesktopAdapter] = None,
    ):
        self._config_repo = config_repo
        self._win = win_adapter or WindowsAdapter()
        self._vda = vda_adapter or VirtualDesktopAdapter()

    def move_secondary_windows_to_desktop(self, target_desktop_number: int) -> bool:
        """
        Moves all windows that reside on secondary monitors to the given virtual desktop.
        This keeps secondary monitor windows visible across virtual desktop switches on the primary monitor.
        """
        config = self._config_repo.get_config()
        if not config.keep_secondary_windows:
            return False

        monitors = self._win.get_connected_monitors()
        if len(monitors) <= 1:
            return False

        primary_device = self._win.get_primary_monitor_device()
        if not primary_device:
            return False

        windows = self._win.get_all_visible_top_level_windows()

        for hwnd in windows:
            try:
                window_device = self._win.get_window_monitor_device(hwnd)
                if window_device and window_device != primary_device:
                    self._vda.move_window_to_desktop_number(hwnd, target_desktop_number)
            except Exception:
                continue

        return True
