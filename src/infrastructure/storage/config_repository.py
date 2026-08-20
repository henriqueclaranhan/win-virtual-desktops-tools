from __future__ import annotations
import json
import os
import threading
from typing import Callable, List, Optional
from src.core.models.config import AppConfig, CornerSettings
from src.infrastructure.storage.path_resolver import PathResolver


class ConfigRepository:
    """Thread-safe configuration repository with automatic disk synchronization and change notifications."""

    def __init__(self, file_path: Optional[str] = None):
        self._file_path = file_path or PathResolver.get_settings_path()
        self._lock = threading.RLock()
        self._config: AppConfig = AppConfig()
        self._last_mtime: float = 0.0
        self._listeners: List[Callable[[AppConfig], None]] = []

        self.reload()

    @property
    def file_path(self) -> str:
        return self._file_path

    def add_listener(self, listener: Callable[[AppConfig], None]) -> None:
        """Register a callback to be called whenever config is modified."""
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[AppConfig], None]) -> None:
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def _notify_listeners(self) -> None:
        for listener in list(self._listeners):
            try:
                listener(self._config)
            except Exception as err:
                print(f"[ConfigRepository] Error in listener: {err}")

    def get_config(self) -> AppConfig:
        self._check_external_reload()
        with self._lock:
            return self._config

    def save_config(self, config: AppConfig) -> None:
        with self._lock:
            self._config = config
            self._write_to_disk()
            self._notify_listeners()

    def reload(self) -> None:
        with self._lock:
            if not os.path.exists(self._file_path):
                self._config = AppConfig()
                self._write_to_disk()
                return

            try:
                self._last_mtime = os.path.getmtime(self._file_path)
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._config = AppConfig.from_dict(data)
            except Exception as err:
                print(f"[ConfigRepository] Error loading config ({err}), preserving current config")

    def _check_external_reload(self) -> None:
        try:
            if os.path.exists(self._file_path):
                current_mtime = os.path.getmtime(self._file_path)
                if current_mtime != self._last_mtime:
                    self.reload()
                    self._notify_listeners()
        except Exception:
            pass

    def _write_to_disk(self) -> None:
        try:
            parent_dir = os.path.dirname(self._file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self._config.to_dict(), f, indent=4)

            if os.path.exists(self._file_path):
                self._last_mtime = os.path.getmtime(self._file_path)
        except Exception as err:
            print(f"[ConfigRepository] Error saving config: {err}")

    def toggle_hot_corner(self) -> bool:
        with self._lock:
            self.get_config()
            self._config.hot_corner_enabled = not self._config.hot_corner_enabled
            self._write_to_disk()
            self._notify_listeners()
            return self._config.hot_corner_enabled

    def toggle_taskbar_scroll(self) -> bool:
        with self._lock:
            self.get_config()
            self._config.taskbar_scroll_enabled = not self._config.taskbar_scroll_enabled
            self._write_to_disk()
            self._notify_listeners()
            return self._config.taskbar_scroll_enabled

    def toggle_keep_secondary_windows(self) -> bool:
        with self._lock:
            self.get_config()
            self._config.keep_secondary_windows = not self._config.keep_secondary_windows
            self._write_to_disk()
            self._notify_listeners()
            return self._config.keep_secondary_windows

    def set_monitor_corners(self, monitor_index: int, corners: CornerSettings) -> None:
        with self._lock:
            self.get_config()
            self._config.hot_corner_config[str(monitor_index)] = corners
            self._write_to_disk()
            self._notify_listeners()
