import json
import os
import threading

HOT_CORNER = "Hot Corner"
TASKBAR_SCROLL = "Taskbar Scroll"
KEEP_WINDOWS = "Keep secondary monitor windows"
HOT_CORNER_CONFIG = "Hot Corner Config"

DEFAULT_CORNERS = {
	"top_left": True,
	"top_right": False,
	"bottom_left": False,
	"bottom_right": False,
}

__features = {
	HOT_CORNER: True,
	TASKBAR_SCROLL: True,
	KEEP_WINDOWS: True,
	HOT_CORNER_CONFIG: {
		"0": DEFAULT_CORNERS
	},
}

settings_file = "settings.json"
__settings_cache = dict(__features)
__settings_lock = threading.Lock()
__last_settings_mtime = 0


def __get_settings():
	with open(settings_file, "r", encoding="utf-8") as f:
		return json.load(f)


def __save_settings(settings):
	global __last_settings_mtime
	try:
		with open(settings_file, "w", encoding="utf-8") as f:
			json.dump(settings, f, indent=4)
		if os.path.exists(settings_file):
			__last_settings_mtime = os.path.getmtime(settings_file)
	except Exception as err:
		print(f"Error saving settings: {err}")


def __load_settings():
	global __settings_cache, __last_settings_mtime

	with __settings_lock:
		if not os.path.exists(settings_file):
			__settings_cache = dict(__features)
			__save_settings(__settings_cache)
			return

		try:
			__last_settings_mtime = os.path.getmtime(settings_file)
			settings = __get_settings()
			if not isinstance(settings, dict):
				raise ValueError("Settings file corrupted")
		except Exception as err:
			print(f"Error loading settings ({err}), resetting defaults")
			__settings_cache = dict(__features)
			__save_settings(__settings_cache)
			return

		updated = False
		for feature in __features:
			if feature not in settings:
				settings[feature] = __features[feature]
				updated = True

		__settings_cache = settings
		if updated:
			__save_settings(__settings_cache)


def __check_reload_settings():
	global __last_settings_mtime
	try:
		if os.path.exists(settings_file):
			current_mtime = os.path.getmtime(settings_file)
			if current_mtime != __last_settings_mtime:
				__load_settings()
	except Exception:
		pass


# Initialize cache at module load
__load_settings()


def get_feature_state(feature: str) -> bool:
	__check_reload_settings()
	return __settings_cache.get(feature, __features.get(feature, True))


def change_feature_state(feature: str):
	with __settings_lock:
		__check_reload_settings()
		current_state = __settings_cache.get(feature, __features.get(feature, True))
		__settings_cache[feature] = not current_state
		__save_settings(__settings_cache)


def get_hot_corner_config() -> dict:
	__check_reload_settings()
	config = __settings_cache.get(HOT_CORNER_CONFIG)
	if not isinstance(config, dict):
		old_corners = __settings_cache.get("Hot Corner Corners")
		if isinstance(old_corners, dict):
			return {"0": old_corners}
		return {"0": dict(DEFAULT_CORNERS)}
	return config


def set_hot_corner_config(config: dict):
	with __settings_lock:
		__settings_cache[HOT_CORNER_CONFIG] = config
		__save_settings(__settings_cache)


def get_monitor_corners(monitor_index: int) -> dict:
	config = get_hot_corner_config()
	key = str(monitor_index)
	if key in config and isinstance(config[key], dict):
		res = dict(DEFAULT_CORNERS)
		res.update(config[key])
		return res
	return dict(DEFAULT_CORNERS)
