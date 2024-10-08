import json
import os

HOT_CORNER = "Hot Corner"
TASKBAR_SCROLL = "Taskbar Scroll"
KEEP_WINDOWS = "Keep secondary monitor windows"

__features = {
	HOT_CORNER: True,
	TASKBAR_SCROLL: True,
	KEEP_WINDOWS: True
}

settings_file = "settings.json"


def __get_settings():
	f = open(settings_file)
	settings = json.load(f)

	return settings


def __save_settings(settings):
	with open(settings_file, "w") as f:
		json.dump(settings, f, indent=4)


def __create_settings():
	default_settings = {feature: True for feature in __features}

	__save_settings(default_settings)


def __sync_settings():
	if not os.path.exists(settings_file):
		__create_settings()

	settings = None

	try:
		settings = __get_settings()

	except Exception as err:
		print(f"Unexpected {err=}, {type(err)=}")

		__create_settings()

		settings = __get_settings()

	if not settings:
		return False

	updated = False

	for feature in __features:
		if feature not in settings:
			settings[feature] = True
			updated = True

	if updated:
		__save_settings(settings)


def get_feature_state(feature: str):
	__sync_settings()

	settings = __get_settings()

	return settings[feature]


def change_feature_state(feature: str):
	__sync_settings()

	settings = __get_settings()

	settings[feature] = not settings[feature]

	__save_settings(settings)
