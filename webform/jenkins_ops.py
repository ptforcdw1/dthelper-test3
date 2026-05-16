"""Trigger a Jenkins parameterised build via REST API.

Handles both CSRF-protected and CSRF-disabled Jenkins setups. Returns the
build URL once the queued item has been picked up by an executor (or the
queue URL immediately if you'd rather poll later).
"""

import time
from typing import Optional, Tuple

import requests


class JenkinsError(RuntimeError):
    pass


def _auth(user: str, token: str) -> requests.auth.HTTPBasicAuth:
    return requests.auth.HTTPBasicAuth(user, token)


def _get_crumb(base_url: str, auth) -> Optional[Tuple[str, str]]:
    """Return (header_name, crumb_value) or None if CSRF is off."""
    r = requests.get(f"{base_url}/crumbIssuer/api/json", auth=auth, timeout=10)
    if r.status_code == 404:
        return None  # CSRF disabled
    r.raise_for_status()
    data = r.json()
    return data["crumbRequestField"], data["crumb"]


def trigger_build(
    base_url: str,
    job: str,
    user: str,
    token: str,
    params: dict,
) -> str:
    """POST to /buildWithParameters. Return the queue item URL."""
    base_url = base_url.rstrip("/")
    auth = _auth(user, token)
    headers = {}
    crumb = _get_crumb(base_url, auth)
    if crumb is not None:
        headers[crumb[0]] = crumb[1]
    r = requests.post(
        f"{base_url}/job/{job}/buildWithParameters",
        params=params,
        headers=headers,
        auth=auth,
        timeout=15,
    )
    if r.status_code not in (200, 201):
        raise JenkinsError(
            f"Jenkins build request failed: HTTP {r.status_code}\n{r.text}"
        )
    queue_url = r.headers.get("Location")
    if not queue_url:
        raise JenkinsError("Jenkins did not return a queue URL in Location header.")
    return queue_url


def wait_for_build_url(
    queue_url: str,
    user: str,
    token: str,
    timeout_s: int = 30,
) -> Optional[str]:
    """Poll the queue item until Jenkins assigns it a build URL.

    Returns the executable URL (the actual build page) or None if it
    didn't start within timeout_s. Either outcome is OK for the form:
    we can just show the queue URL if the build hasn't been picked up yet.
    """
    auth = _auth(user, token)
    deadline = time.time() + timeout_s
    api_url = queue_url.rstrip("/") + "/api/json"
    while time.time() < deadline:
        r = requests.get(api_url, auth=auth, timeout=10)
        if r.status_code == 200:
            data = r.json()
            executable = data.get("executable")
            if executable and "url" in executable:
                return executable["url"]
        time.sleep(2)
    return None
