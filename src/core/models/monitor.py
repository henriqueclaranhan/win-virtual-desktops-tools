from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class MonitorRect:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    def as_tuple(self) -> Tuple[int, int, int, int]:
        return (self.left, self.top, self.right, self.bottom)


@dataclass
class MonitorInfo:
    index: int
    device_name: str
    rect: MonitorRect
    is_primary: bool

    @property
    def resolution_str(self) -> str:
        return f"{self.rect.width}x{self.rect.height}"
