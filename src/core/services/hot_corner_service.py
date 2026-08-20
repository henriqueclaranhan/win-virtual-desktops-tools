from __future__ import annotations
import time
from typing import List, Tuple, Optional
from src.infrastructure.os.win32_adapter import WindowsAdapter
from src.infrastructure.storage.config_repository import ConfigRepository


class HotCornerService:
    """Detects when cursor hits configured monitor corners and triggers Windows Task View."""

    CORNER_SIZE_PX = 6
    DEBOUNCE_INTERVAL_SEC = 0.5
    CACHE_EXPIRATION_SEC = 5.0

    def __init__(
        self,
        config_repo: ConfigRepository,
        win_adapter: Optional[WindowsAdapter] = None,
    ):
        self._config_repo = config_repo
        self._win = win_adapter or WindowsAdapter()

        self._is_in_corner: bool = False
        self._last_trigger_time: float = 0.0
        self._active_corners_cache: List[Tuple[int, int, int, int]] = []
        self._last_cache_update: float = 0.0

        self._config_repo.add_listener(lambda _: self.refresh_active_corners())

    def refresh_active_corners(self) -> None:
        """Recalculates corner bounding rectangles for all connected monitors based on current config."""
        monitors = self._win.get_connected_monitors()
        config = self._config_repo.get_config()

        new_corners: List[Tuple[int, int, int, int]] = []
        sz = self.CORNER_SIZE_PX

        for mon in monitors:
            corners_cfg = config.get_monitor_corners(mon.index)
            rect = mon.rect

            if corners_cfg.top_left:
                new_corners.append((rect.left, rect.top, rect.left + sz, rect.top + sz))
            if corners_cfg.top_right:
                new_corners.append((rect.right - sz, rect.top, rect.right, rect.top + sz))
            if corners_cfg.bottom_left:
                new_corners.append((rect.left, rect.bottom - sz, rect.left + sz, rect.bottom))
            if corners_cfg.bottom_right:
                new_corners.append((rect.right - sz, rect.bottom - sz, rect.right, rect.bottom))

        self._active_corners_cache = new_corners
        self._last_cache_update = time.time()

    def handle_mouse_move(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Evaluates mouse position against active hot corners."""
        config = self._config_repo.get_config()
        if not config.hot_corner_enabled:
            self._is_in_corner = False
            return True

        if x is None or y is None:
            x, y = self._win.get_cursor_pos()

        now = time.time()
        if not self._active_corners_cache or (now - self._last_cache_update) > self.CACHE_EXPIRATION_SEC:
            self.refresh_active_corners()

        in_any_corner = any(
            x1 <= x <= x2 and y1 <= y <= y2
            for x1, y1, x2, y2 in self._active_corners_cache
        )

        if in_any_corner:
            if not self._is_in_corner:
                if not self._win.is_app_fullscreen(x, y):
                    self._trigger_task_view()
                    self._is_in_corner = True
        else:
            self._is_in_corner = False

        return True

    def _trigger_task_view(self) -> None:
        now = time.time()
        if now <= self._last_trigger_time + self.DEBOUNCE_INTERVAL_SEC:
            return

        self._win.trigger_task_view_shortcut()
        self._last_trigger_time = now
