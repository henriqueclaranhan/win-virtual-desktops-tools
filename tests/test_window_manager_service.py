import unittest
from unittest.mock import MagicMock
from src.core.models.config import AppConfig
from src.core.models.monitor import MonitorInfo, MonitorRect
from src.core.services.window_manager_service import WindowManagerService


class TestWindowManagerService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.config = AppConfig(keep_secondary_windows=True)
        self.mock_repo.get_config.return_value = self.config

        self.mock_win = MagicMock()
        self.mock_win.get_primary_monitor_device.return_value = "\\\\.\\DISPLAY1"
        self.mock_win.get_connected_monitors.return_value = [
            MonitorInfo(index=0, device_name="\\\\.\\DISPLAY1", rect=MonitorRect(0, 0, 1920, 1080), is_primary=True),
            MonitorInfo(index=1, device_name="\\\\.\\DISPLAY2", rect=MonitorRect(1920, 0, 3840, 1080), is_primary=False),
        ]

        self.mock_vda = MagicMock()
        self.service = WindowManagerService(
            config_repo=self.mock_repo,
            win_adapter=self.mock_win,
            vda_adapter=self.mock_vda,
        )

    def test_sync_pins_secondary_and_unpins_primary(self):
        # Window 101 on DISPLAY2 (not pinned) -> should pin
        # Window 102 on DISPLAY2 (already pinned) -> no-op
        # Window 201 on DISPLAY1 (pinned) -> should unpin
        # Window 202 on DISPLAY1 (not pinned) -> no-op
        self.mock_win.get_all_visible_top_level_windows.return_value = [101, 102, 201, 202]

        def get_device(hwnd):
            if hwnd in (101, 102):
                return "\\\\.\\DISPLAY2"
            return "\\\\.\\DISPLAY1"

        self.mock_win.get_window_monitor_device.side_effect = get_device

        def is_pinned(hwnd):
            return hwnd in (102, 201)

        self.mock_vda.is_pinned_window.side_effect = is_pinned

        result = self.service.sync_secondary_windows()
        self.assertTrue(result)

        self.mock_vda.pin_window.assert_called_once_with(101)
        self.mock_vda.unpin_window.assert_called_once_with(201)

    def test_sync_disabled_when_config_false(self):
        self.config.keep_secondary_windows = False
        self.mock_win.get_all_visible_top_level_windows.return_value = [101]
        self.mock_vda.is_pinned_window.return_value = True

        result = self.service.sync_secondary_windows()
        self.assertFalse(result)
        self.mock_vda.unpin_window.assert_called_once_with(101)

    def test_sync_disabled_when_single_monitor(self):
        self.mock_win.get_connected_monitors.return_value = [
            MonitorInfo(index=0, device_name="\\\\.\\DISPLAY1", rect=MonitorRect(0, 0, 1920, 1080), is_primary=True)
        ]
        self.mock_win.get_all_visible_top_level_windows.return_value = [101]
        self.mock_vda.is_pinned_window.return_value = True

        result = self.service.sync_secondary_windows()
        self.assertFalse(result)
        self.mock_vda.unpin_window.assert_called_once_with(101)

    def test_unpin_all_secondary_windows(self):
        self.mock_win.get_all_visible_top_level_windows.return_value = [101, 102]
        self.mock_vda.is_pinned_window.side_effect = lambda hwnd: hwnd == 101

        self.service.unpin_all_secondary_windows()
        self.mock_vda.unpin_window.assert_called_once_with(101)


if __name__ == "__main__":
    unittest.main()
