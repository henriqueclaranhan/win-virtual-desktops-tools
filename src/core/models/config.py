from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any


@dataclass
class CornerSettings:
    top_left: bool = True
    top_right: bool = False
    bottom_left: bool = False
    bottom_right: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> CornerSettings:
        if not isinstance(data, dict):
            return cls()
        return cls(
            top_left=bool(data.get("top_left", False)),
            top_right=bool(data.get("top_right", False)),
            bottom_left=bool(data.get("bottom_left", False)),
            bottom_right=bool(data.get("bottom_right", False)),
        )

    def to_dict(self) -> Dict[str, bool]:
        return asdict(self)


@dataclass
class AppConfig:
    hot_corner_enabled: bool = True
    taskbar_scroll_enabled: bool = True
    keep_secondary_windows: bool = True
    hot_corner_config: Dict[str, CornerSettings] = field(
        default_factory=lambda: {"0": CornerSettings(top_left=True)}
    )

    KEY_HOT_CORNER = "Hot Corner"
    KEY_TASKBAR_SCROLL = "Taskbar Scroll"
    KEY_KEEP_WINDOWS = "Keep secondary monitor windows"
    KEY_HOT_CORNER_CONFIG = "Hot Corner Config"
    KEY_OLD_CORNERS = "Hot Corner Corners"

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> AppConfig:
        if not isinstance(data, dict):
            return cls()

        hot_corner = data.get(
            "hot_corner_enabled", data.get(cls.KEY_HOT_CORNER, True)
        )
        taskbar_scroll = data.get(
            "taskbar_scroll_enabled", data.get(cls.KEY_TASKBAR_SCROLL, True)
        )
        keep_windows = data.get(
            "keep_secondary_windows", data.get(cls.KEY_KEEP_WINDOWS, True)
        )

        corners_raw = data.get("hot_corner_config", data.get(cls.KEY_HOT_CORNER_CONFIG))
        corners_map: Dict[str, CornerSettings] = {}

        if isinstance(corners_raw, dict):
            for mon_id, mon_cfg in corners_raw.items():
                corners_map[str(mon_id)] = CornerSettings.from_dict(mon_cfg)
        else:
            old_corners = data.get(cls.KEY_OLD_CORNERS)
            if isinstance(old_corners, dict):
                corners_map["0"] = CornerSettings.from_dict(old_corners)
            else:
                corners_map["0"] = CornerSettings(top_left=True)

        if "0" not in corners_map:
            corners_map["0"] = CornerSettings(top_left=True)

        return cls(
            hot_corner_enabled=bool(hot_corner),
            taskbar_scroll_enabled=bool(taskbar_scroll),
            keep_secondary_windows=bool(keep_windows),
            hot_corner_config=corners_map,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.KEY_HOT_CORNER: self.hot_corner_enabled,
            self.KEY_TASKBAR_SCROLL: self.taskbar_scroll_enabled,
            self.KEY_KEEP_WINDOWS: self.keep_secondary_windows,
            self.KEY_HOT_CORNER_CONFIG: {
                mon_id: cfg.to_dict() for mon_id, cfg in self.hot_corner_config.items()
            },
        }

    def get_monitor_corners(self, monitor_index: int) -> CornerSettings:
        key = str(monitor_index)
        if key in self.hot_corner_config:
            return self.hot_corner_config[key]
        return CornerSettings(top_left=(monitor_index == 0))
