"""Small standard-library HTTP helper; no secrets are logged."""
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
def post_json(url, payload, headers=None, timeout=30):
    body=json.dumps(payload).encode("utf-8")
    request=Request(url,data=body,method="POST",headers={"Content-Type":"application/json",**(headers or {})})
    try:
        with urlopen(request,timeout=timeout) as response: return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc: raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode('utf-8',errors='replace')[:500]}") from exc
    except URLError as exc: raise RuntimeError(f"Network error: {exc.reason}") from exc
def get_json(url, headers=None, timeout=30):
    request=Request(url,method="GET",headers=headers or {})
    try:
        with urlopen(request,timeout=timeout) as response: return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc: raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode('utf-8',errors='replace')[:500]}") from exc
    except URLError as exc: raise RuntimeError(f"Network error: {exc.reason}") from exc
