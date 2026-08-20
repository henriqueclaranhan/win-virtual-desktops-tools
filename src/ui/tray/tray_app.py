from __future__ import annotations
import threading
from typing import Optional
from PIL import Image
import pystray
import win32api

from src.core.app_context import AppContext
from src.core.models.config import AppConfig
from src.infrastructure.storage.path_resolver import PathResolver
from src.infrastructure.updater.update_checker import UpdateChecker
from src.ui.listeners.mouse_listener import MouseListenerController
from src.ui.settings.hot_corner_dialog import open_hot_corner_settings_window


class TrayApp:
    """Manages the Windows System Tray icon, context menu, and background update alerts."""

    def __init__(self, app_context: AppContext, mouse_listener: MouseListenerController):
        self._ctx = app_context
        self._mouse_listener = mouse_listener
        self._icon: Optional[pystray.Icon] = None
        self._menu_items = []

    def start(self) -> None:
        """Initializes and runs the system tray event loop."""
        icon_image = self._load_image("assets/icon.ico")
        self._menu_items = self._build_menu_items()

        self._icon = pystray.Icon(
            name="Win Virtual Desktops Tools",
            title="Win Virtual Desktops Tools",
            icon=icon_image,
            menu=pystray.Menu(*self._menu_items),
        )

        threading.Thread(target=self._check_updates_worker, daemon=True).start()
        self._icon.run()

    def _load_image(self, relative_path: str) -> Image.Image:
        full_path = PathResolver.get_resource_path(relative_path)
        return Image.open(full_path)

    def _build_menu_items(self) -> list:
        config_repo = self._ctx.config_repo

        return [
            pystray.MenuItem(
                "⚙️ Features",
                pystray.Menu(
                    pystray.MenuItem(
                        AppConfig.KEY_HOT_CORNER,
                        lambda: config_repo.toggle_hot_corner(),
                        checked=lambda _: config_repo.get_config().hot_corner_enabled,
                    ),
                    pystray.MenuItem(
                        AppConfig.KEY_TASKBAR_SCROLL,
                        lambda: config_repo.toggle_taskbar_scroll(),
                        checked=lambda _: config_repo.get_config().taskbar_scroll_enabled,
                    ),
                    pystray.MenuItem(
                        AppConfig.KEY_KEEP_WINDOWS,
                        lambda: config_repo.toggle_keep_secondary_windows(),
                        checked=lambda _: config_repo.get_config().keep_secondary_windows,
                    ),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(
                        "📐 Configure Hot Corners...",
                        lambda: open_hot_corner_settings_window(),
                    ),
                ),
            ),
            pystray.MenuItem(
                "📐 Hot Corners Settings",
                lambda: open_hot_corner_settings_window(),
            ),
            pystray.MenuItem(
                "❎ Exit",
                self._on_exit,
            ),
        ]

    def _on_exit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._mouse_listener.stop()
        self._ctx.stop()
        if self._icon:
            self._icon.stop()

    def _check_updates_worker(self) -> None:
        has_update, latest_tag = UpdateChecker.check_for_updates()
        if has_update and self._icon:
            update_item = pystray.MenuItem(
                f"⚠️ Update Available ({latest_tag})",
                self._on_click_update,
            )
            self._menu_items.insert(0, update_item)

            update_icon_img = self._load_image("assets/icon-update.ico")
            self._icon.icon = update_icon_img
            self._icon.menu = pystray.Menu(*self._menu_items)

    def _on_click_update(self) -> None:
        win32api.ShellExecute(0, "open", UpdateChecker.RELEASES_URL, None, None, 1)
