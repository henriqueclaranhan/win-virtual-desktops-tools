import unittest
from unittest.mock import MagicMock
from src.core.models.config import AppConfig
from src.core.services.desktop_scroll_service import DesktopScrollService


class TestDesktopScrollService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.config = AppConfig(taskbar_scroll_enabled=True, keep_secondary_windows=True)
        self.mock_repo.get_config.return_value = self.config

        self.mock_win = MagicMock()
        self.mock_win.is_overview_foreground.return_value = False
        self.mock_win.is_point_over_taskbar.return_value = True

        self.mock_vda = MagicMock()
        self.mock_vda.get_current_desktop_number.return_value = 0
        self.mock_vda.get_desktop_count.return_value = 3

        self.mock_window_mgr = MagicMock()

        self.service = DesktopScrollService(
            config_repo=self.mock_repo,
            window_mgr_service=self.mock_window_mgr,
            win_adapter=self.mock_win,
            vda_adapter=self.mock_vda,
        )

    def test_scroll_down_switches_next_desktop(self):
        handled = self.service.handle_scroll(x=100, y=100, dy=-1)
        self.assertTrue(handled)
        self.mock_win.trigger_desktop_switch_shortcut.assert_called_once_with(1)
        self.mock_window_mgr.move_secondary_windows_to_desktop.assert_called_once_with(1)

    def test_scroll_up_at_boundary_does_not_switch(self):
        handled = self.service.handle_scroll(x=100, y=100, dy=1)
        self.assertFalse(handled)
        self.mock_win.trigger_desktop_switch_shortcut.assert_not_called()

    def test_scroll_outside_taskbar_ignored(self):
        self.mock_win.is_point_over_taskbar.return_value = False
        self.mock_win.is_overview_foreground.return_value = False

        handled = self.service.handle_scroll(x=100, y=100, dy=-1)
        self.assertFalse(handled)
        self.mock_win.trigger_desktop_switch_shortcut.assert_not_called()


if __name__ == "__main__":
    unittest.main()
