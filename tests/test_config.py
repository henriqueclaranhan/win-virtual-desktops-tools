import unittest
import os
import tempfile
from src.core.models.config import AppConfig, CornerSettings
from src.infrastructure.storage.config_repository import ConfigRepository


class TestConfig(unittest.TestCase):
    def test_corner_settings(self):
        corner = CornerSettings(top_left=True, bottom_right=True)
        d = corner.to_dict()
        self.assertTrue(d["top_left"])
        self.assertFalse(d["top_right"])
        self.assertTrue(d["bottom_right"])

        restored = CornerSettings.from_dict(d)
        self.assertEqual(restored.top_left, corner.top_left)
        self.assertEqual(restored.bottom_right, corner.bottom_right)

    def test_default_config(self):
        config = AppConfig()
        self.assertTrue(config.hot_corner_enabled)
        self.assertTrue(config.taskbar_scroll_enabled)
        self.assertTrue(config.keep_secondary_windows)
        self.assertTrue(config.get_monitor_corners(0).top_left)
        self.assertFalse(config.get_monitor_corners(0).top_right)
        self.assertFalse(config.get_monitor_corners(1).top_left)

    def test_legacy_dict_migration(self):
        legacy_data = {
            "Hot Corner": False,
            "Taskbar Scroll": True,
            "Keep secondary monitor windows": False,
            "Hot Corner Config": {
                "0": {
                    "top_left": False,
                    "top_right": True,
                    "bottom_left": False,
                    "bottom_right": True,
                }
            }
        }
        config = AppConfig.from_dict(legacy_data)
        self.assertFalse(config.hot_corner_enabled)
        self.assertTrue(config.taskbar_scroll_enabled)
        self.assertFalse(config.keep_secondary_windows)

        corners_0 = config.get_monitor_corners(0)
        self.assertFalse(corners_0.top_left)
        self.assertTrue(corners_0.top_right)
        self.assertTrue(corners_0.bottom_right)

    def test_config_repository_persistence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_file = os.path.join(tmpdir, "test_settings.json")
            repo = ConfigRepository(file_path=cfg_file)

            self.assertTrue(os.path.exists(cfg_file))
            self.assertTrue(repo.get_config().hot_corner_enabled)

            new_state = repo.toggle_hot_corner()
            self.assertFalse(new_state)
            self.assertFalse(repo.get_config().hot_corner_enabled)

            repo2 = ConfigRepository(file_path=cfg_file)
            self.assertFalse(repo2.get_config().hot_corner_enabled)


if __name__ == "__main__":
    unittest.main()
