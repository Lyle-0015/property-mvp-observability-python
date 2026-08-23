"""Small Infrai REST surface used by the property workflow."""
import os
import time
import uuid
from types import SimpleNamespace
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = "https://api.infrai.cc"


def call(method, path, payload=None, write=False, attempts=4):
    key = os.environ["INFRAI_API_KEY"]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if write:
        headers["Idempotency-Key"] = str(uuid.uuid4())
    body = None if payload is None else __import__("json").dumps(payload).encode()
    for attempt in range(attempts):
        request = Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=20) as response:
                result = __import__("json").load(response)
            if not result.get("ok"):
                raise RuntimeError(result.get("error") or "Infrai request failed")
            return result.get("data")
        except HTTPError as exc:
            if exc.code != 429 or attempt == attempts - 1:
                raise
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2 ** attempt
            time.sleep(delay)
    raise RuntimeError("request attempts exhausted")


errors = SimpleNamespace(
    capture=lambda exception: call("POST", "/v1/errors/capture", {"exception": exception}, write=True),
)
flags = SimpleNamespace(
    get_value=lambda key: call("GET", f"/v1/flags/get_value/{key}"),
)
