import os
import sys
from pathlib import Path


class PathResolver:
    """Provides reliable path resolution for frozen PyInstaller builds and development environments."""

    @staticmethod
    def get_project_root() -> Path:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return Path(__file__).resolve().parent.parent.parent.parent

    @classmethod
    def get_resource_path(cls, relative_path: str) -> str:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = Path(sys._MEIPASS)
        else:
            base = cls.get_project_root()
        return str(base / relative_path)

    @classmethod
    def get_dll_path(cls, dll_name: str = "VirtualDesktopAccessor.dll") -> str:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            candidate = Path(sys._MEIPASS) / dll_name
            if candidate.exists():
                return str(candidate)

        root = cls.get_project_root()
        dev_path = root / "dll" / dll_name
        if dev_path.exists():
            return str(dev_path)

        return str(root / dll_name)

    @classmethod
    def get_settings_path(cls) -> str:
        root = cls.get_project_root()
        local_settings = root / "settings.json"
        if local_settings.exists():
            return str(local_settings)

        app_data = os.getenv("APPDATA")
        if app_data:
            target_dir = Path(app_data) / "WinVirtualDesktopsTools"
            target_dir.mkdir(parents=True, exist_ok=True)
            return str(target_dir / "settings.json")

        return str(local_settings)
