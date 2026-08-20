from __future__ import annotations
from typing import Optional
from pynput.mouse import Listener
from src.core.app_context import AppContext


class MouseListenerController:
    """Manages low-level global mouse hooks via pynput."""

    def __init__(self, app_context: AppContext):
        self._ctx = app_context
        self._listener: Optional[Listener] = None

    def start(self) -> None:
        if self._listener is not None and self._listener.is_alive():
            return

        self._listener = Listener(
            on_move=self._on_move,
            on_scroll=self._on_scroll,
        )
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _on_move(self, x: int, y: int) -> None:
        try:
            self._ctx.hot_corner_service.handle_mouse_move(x, y)
        except Exception as err:
            print(f"[MouseListener] Error in on_move: {err}")

    def _on_scroll(self, x: int, y: int, _dx: int, dy: int) -> None:
        try:
            self._ctx.desktop_scroll_service.handle_scroll(x, y, dy)
        except Exception as err:
            print(f"[MouseListener] Error in on_scroll: {err}")
