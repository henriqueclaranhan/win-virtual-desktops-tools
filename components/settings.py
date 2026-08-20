import json
import os
import threading

HOT_CORNER = "Hot Corner"
TASKBAR_SCROLL = "Taskbar Scroll"
KEEP_WINDOWS = "Keep secondary monitor windows"

__features = {
	HOT_CORNER: True,
	TASKBAR_SCROLL: True,
	KEEP_WINDOWS: True
}

settings_file = "settings.json"
__settings_cache = dict(__features)
__settings_lock = threading.Lock()


def __get_settings():
	with open(settings_file, "r", encoding="utf-8") as f:
		return json.load(f)


def __save_settings(settings):
	try:
		with open(settings_file, "w", encoding="utf-8") as f:
			json.dump(settings, f, indent=4)
	except Exception as err:
		print(f"Error saving settings: {err}")


def __load_settings():
	global __settings_cache

	with __settings_lock:
		if not os.path.exists(settings_file):
			__settings_cache = dict(__features)
			__save_settings(__settings_cache)
			return

		try:
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


# Initialize cache at module load
__load_settings()


def get_feature_state(feature: str) -> bool:
	return __settings_cache.get(feature, __features.get(feature, True))


def change_feature_state(feature: str):
	with __settings_lock:
		current_state = __settings_cache.get(feature, __features.get(feature, True))
		__settings_cache[feature] = not current_state
		__save_settings(__settings_cache)

