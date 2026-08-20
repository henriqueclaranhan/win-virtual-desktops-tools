from __future__ import annotations
import http.client
import json
from typing import Tuple, Optional
from _version import (
    __version__,
    __releases_url__,
    __releases_api_url__,
    __releases_api_path__,
)


class UpdateChecker:
    """Checks for newer releases on GitHub based on project version metadata."""

    CURRENT_VERSION: str = __version__
    RELEASES_URL: str = __releases_url__
    GITHUB_API_HOST: str = __releases_api_url__
    GITHUB_API_PATH: str = __releases_api_path__

    @classmethod
    def check_for_updates(cls, timeout: int = 5) -> Tuple[bool, Optional[str]]:
        """
        Queries the GitHub Releases API for a newer tag.
        Returns: (has_update: bool, latest_tag: Optional[str])
        """
        headers = {
            "User-Agent": "win-virtual-desktops-tools"
        }

        try:
            conn = http.client.HTTPSConnection(cls.GITHUB_API_HOST, timeout=timeout)
            conn.request("GET", cls.GITHUB_API_PATH, headers=headers)
            response = conn.getresponse()
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                latest_tag = data.get("tag_name")
                if latest_tag and latest_tag != cls.CURRENT_VERSION:
                    return True, latest_tag
            conn.close()
        except Exception:
            pass

        return False, None
