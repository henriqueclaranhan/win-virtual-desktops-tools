from __future__ import annotations
import threading
import time
from typing import Optional
from src.infrastructure.storage.config_repository import ConfigRepository
from src.infrastructure.os.win32_adapter import WindowsAdapter
from src.infrastructure.os.virtual_desktop_adapter import VirtualDesktopAdapter
from src.core.services.window_manager_service import WindowManagerService
from src.core.services.hot_corner_service import HotCornerService
from src.core.services.desktop_scroll_service import DesktopScrollService


class AppContext:
    """Central application context and dependency container."""

    def __init__(self, config_repo: Optional[ConfigRepository] = None):
        self.config_repo = config_repo or ConfigRepository()
        self.win_adapter = WindowsAdapter()
        self.vda_adapter = VirtualDesktopAdapter()

        self.window_mgr_service = WindowManagerService(
            config_repo=self.config_repo,
            win_adapter=self.win_adapter,
            vda_adapter=self.vda_adapter,
        )
        self.hot_corner_service = HotCornerService(
            config_repo=self.config_repo,
            win_adapter=self.win_adapter,
        )
        self.desktop_scroll_service = DesktopScrollService(
            config_repo=self.config_repo,
            window_mgr_service=self.window_mgr_service,
            win_adapter=self.win_adapter,
            vda_adapter=self.vda_adapter,
        )

        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

    def start_background_workers(self) -> None:
        """Starts background daemon threads (e.g. desktop switch polling)."""
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._desktop_monitor_loop,
            daemon=True,
            name="VirtualDesktopMonitorThread",
        )
        self._monitor_thread.start()

    def stop(self) -> None:
        self._running = False

    def _desktop_monitor_loop(self) -> None:
        while self._running:
            try:
                self.desktop_scroll_service.check_desktop_changed()
            except Exception as err:
                print(f"[AppContext] Error in desktop monitor loop: {err}")
            time.sleep(0.2)
