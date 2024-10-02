import http.client
import json

__version_info__ = ("1", "1", "0")
__version__ = "v" + ".".join(__version_info__)

__releases_url__ = "https://github.com/henriqueclaranhan/win-virtual-desktops-tools/releases"
__releases_api_url__ = "api.github.com"
__releases_api_path__ = "/repos/henriqueclaranhan/win-virtual-desktops-tools/releases/latest"


def check_updates():
	headers = {
		"User-Agent": "win-virtual-desktops-tools"
	}

	conn = http.client.HTTPSConnection(__releases_api_url__)
	conn.request("GET", __releases_api_path__, headers=headers)
	response = conn.getresponse()
	data = json.loads(response.read().decode('utf-8'))
	conn.close()

	if __version__ != data["tag_name"]:
		return True

	return False
