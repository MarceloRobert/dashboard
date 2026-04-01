from collections.abc import Callable
from typing import Any

from django.conf import settings

import requests

from kernelCI_app.helpers.logger import log_message

MONITORING_ID_PARAM_HELP_TEXT = (
    "Monitoring ID configured in settings for healthcheck.io pings "
    "(optional, used for monitoring the command execution)"
)

HEALTHCHECK_BASE_URL = "https://hc-ping.com"


def _resolve_monitoring_url(monitoring_id: str) -> str | None:
    monitoring_urls = getattr(settings, "HEALTHCHECK_MONITORING_URLS", {})
    monitoring_path = monitoring_urls.get(monitoring_id)
    if not monitoring_path:
        return None

    monitoring_path = monitoring_path.rstrip("/")
    if monitoring_path.startswith("http://") or monitoring_path.startswith("https://"):
        return monitoring_path

    return f"{HEALTHCHECK_BASE_URL.rstrip('/')}/{monitoring_path.lstrip('/')}"


def _ping_healthcheck(monitoring_id: str, status: str) -> None:
    monitoring_url = _resolve_monitoring_url(monitoring_id)
    if not monitoring_url:
        log_message(
            f"No healthcheck URL configured for monitoring_id='{monitoring_id}', skipping ping."
        )
        return

    try:
        response = requests.get(f"{monitoring_url}/{status}", timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        log_message(
            f"Failed to ping healthcheck for monitoring_id='{monitoring_id}' and status='{status}': {e}"
        )


def run_with_healthcheck_monitoring(
    *, monitoring_id: str | None, action: Callable[[], Any]
) -> Any:
    if not monitoring_id:
        return action()

    _ping_healthcheck(monitoring_id, "start")

    try:
        result = action()
    except Exception:
        _ping_healthcheck(monitoring_id, "fail")
        raise

    _ping_healthcheck(monitoring_id, "success")
    return result
