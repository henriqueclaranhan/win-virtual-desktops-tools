from __future__ import annotations
from typing import Optional
from src.infrastructure.os.win32_adapter import WindowsAdapter
from src.infrastructure.os.virtual_desktop_adapter import VirtualDesktopAdapter
from src.infrastructure.storage.config_repository import ConfigRepository


class WindowManagerService:
    """Manages window positions and pinning across virtual desktops and monitors."""

    def __init__(
        self,
        config_repo: ConfigRepository,
        win_adapter: Optional[WindowsAdapter] = None,
        vda_adapter: Optional[VirtualDesktopAdapter] = None,
    ):
        self._config_repo = config_repo
        self._win = win_adapter or WindowsAdapter()
        self._vda = vda_adapter or VirtualDesktopAdapter()

    def sync_secondary_windows(self) -> bool:
        """
        Pins windows on secondary monitors so they natively stay visible across all virtual desktops.
        Unpins windows located on the primary monitor or if the feature is disabled.
        """
        config = self._config_repo.get_config()
        if not config.keep_secondary_windows:
            self.unpin_all_secondary_windows()
            return False

        monitors = self._win.get_connected_monitors()
        if len(monitors) <= 1:
            self.unpin_all_secondary_windows()
            return False

        primary_device = self._win.get_primary_monitor_device()
        if not primary_device:
            return False

        windows = self._win.get_all_visible_top_level_windows()

        for hwnd in windows:
            try:
                window_device = self._win.get_window_monitor_device(hwnd)
                if window_device and window_device != primary_device:
                    if not self._vda.is_pinned_window(hwnd):
                        self._vda.pin_window(hwnd)
                elif window_device and window_device == primary_device:
                    if self._vda.is_pinned_window(hwnd):
                        self._vda.unpin_window(hwnd)
            except Exception:
                continue

        return True

    def unpin_all_secondary_windows(self) -> None:
        """Unpins all currently pinned visible windows."""
        try:
            windows = self._win.get_all_visible_top_level_windows()
            for hwnd in windows:
                try:
                    if self._vda.is_pinned_window(hwnd):
                        self._vda.unpin_window(hwnd)
                except Exception:
                    continue
        except Exception as err:
            print(f"[WindowManagerService] Error unpinning windows: {err}")

    def move_secondary_windows_to_desktop(self, target_desktop_number: int) -> bool:
        """Legacy compatibility wrapper that syncs secondary window pinning."""
        return self.sync_secondary_windows()
