import unittest
from unittest.mock import MagicMock
from src.core.models.config import AppConfig, CornerSettings
from src.core.models.monitor import MonitorInfo, MonitorRect
from src.core.services.hot_corner_service import HotCornerService


class TestHotCornerService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.config = AppConfig(
            hot_corner_enabled=True,
            hot_corner_config={"0": CornerSettings(top_left=True, top_right=False)}
        )
        self.mock_repo.get_config.return_value = self.config

        self.mock_win = MagicMock()
        self.mock_win.get_connected_monitors.return_value = [
            MonitorInfo(
                index=0,
                device_name="Display 1",
                rect=MonitorRect(left=0, top=0, right=1920, bottom=1080),
                is_primary=True
            )
        ]
        self.mock_win.is_app_fullscreen.return_value = False

        self.service = HotCornerService(
            config_repo=self.mock_repo,
            win_adapter=self.mock_win
        )

    def test_triggers_in_top_left_corner(self):
        self.service.handle_mouse_move(2, 2)
        self.mock_win.trigger_task_view_shortcut.assert_called_once()

    def test_does_not_trigger_outside_corner(self):
        self.service.handle_mouse_move(500, 500)
        self.mock_win.trigger_task_view_shortcut.assert_not_called()

    def test_does_not_trigger_when_disabled(self):
        self.config.hot_corner_enabled = False
        self.service.handle_mouse_move(2, 2)
        self.mock_win.trigger_task_view_shortcut.assert_not_called()

    def test_does_not_trigger_when_fullscreen(self):
        self.mock_win.is_app_fullscreen.return_value = True
        self.service.handle_mouse_move(2, 2)
        self.mock_win.trigger_task_view_shortcut.assert_not_called()


if __name__ == "__main__":
    unittest.main()
