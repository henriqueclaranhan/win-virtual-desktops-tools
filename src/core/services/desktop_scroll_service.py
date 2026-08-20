from __future__ import annotations
import time
from typing import Optional
from src.infrastructure.os.win32_adapter import WindowsAdapter
from src.infrastructure.os.virtual_desktop_adapter import VirtualDesktopAdapter
from src.infrastructure.storage.config_repository import ConfigRepository
from src.core.services.window_manager_service import WindowManagerService


class DesktopScrollService:
    """Handles virtual desktop switching when scrolling over the taskbar or Task View."""

    DEBOUNCE_INTERVAL_SEC = 0.3

    def __init__(
        self,
        config_repo: ConfigRepository,
        window_mgr_service: WindowManagerService,
        win_adapter: Optional[WindowsAdapter] = None,
        vda_adapter: Optional[VirtualDesktopAdapter] = None,
    ):
        self._config_repo = config_repo
        self._window_mgr = window_mgr_service
        self._win = win_adapter or WindowsAdapter()
        self._vda = vda_adapter or VirtualDesktopAdapter()

        self._last_switch_time: float = 0.0
        self._current_desktop_number: int = self._vda.get_current_desktop_number()

    def handle_scroll(self, x: Optional[int] = None, y: Optional[int] = None, dy: int = 0) -> bool:
        """Called by mouse hook when wheel scroll event occurs."""
        config = self._config_repo.get_config()
        if not config.taskbar_scroll_enabled:
            return False

        if x is None or y is None:
            x, y = self._win.get_cursor_pos()

        if self._win.is_overview_foreground():
            return self._switch_desktop(dy)

        if self._win.is_point_over_taskbar(x, y):
            return self._switch_desktop(dy)

        return False

    def _switch_desktop(self, dy: int) -> bool:
        if dy == 0:
            return False

        now = time.time()
        if now < self._last_switch_time + self.DEBOUNCE_INTERVAL_SEC:
            return False

        current_desktop = self._vda.get_current_desktop_number()
        total_desktops = self._vda.get_desktop_count()
        next_desktop = current_desktop + (dy * -1)

        if next_desktop < 0 or next_desktop >= total_desktops:
            return False

        direction = 1 if dy < 0 else -1
        self._win.trigger_desktop_switch_shortcut(direction)
        self._last_switch_time = time.time()
        self._current_desktop_number = next_desktop

        self._window_mgr.sync_secondary_windows()
        return True

    def check_desktop_changed(self) -> None:
        """Polled periodically by background worker thread to sync secondary window pinning."""
        config = self._config_repo.get_config()
        if not config.keep_secondary_windows:
            return

        now = time.time()
        if self._last_switch_time and now < self._last_switch_time + self.DEBOUNCE_INTERVAL_SEC:
            return

        current_desktop = self._vda.get_current_desktop_number()
        if self._current_desktop_number != current_desktop:
            self._current_desktop_number = current_desktop

        self._window_mgr.sync_secondary_windows()
