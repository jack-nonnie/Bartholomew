"""Thin fal.ai wrapper: caching, cost logging, and data-URI file inputs.

- Every call is cached by (endpoint, arguments) so an approved result is never paid for twice.
- Local files are sent as data URIs (no separate upload host needed).
- Auth: FAL_KEY env var, or the network proxy injects the key (then FAL_KEY is a placeholder).
"""
import hashlib, json, os, time, urllib.request
from pathlib import Path

os.environ.setdefault("FAL_KEY", "proxy:injected")
import fal_client  # noqa: E402

from .config import ROOT

CACHE = ROOT / "output" / ".cache"
CACHE.mkdir(parents=True, exist_ok=True)


def file_uri(path: str | Path) -> str:
    return fal_client.encode_file(str(ROOT / path) if not Path(path).is_absolute() else str(path))


def _key(endpoint: str, args: dict) -> str:
    blob = json.dumps({"e": endpoint, "a": args}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:20]


def run(endpoint: str, args: dict, *, est_cost: float, log: Path, label: str) -> dict:
    """Call a fal endpoint (or return the cached result)."""
    k = _key(endpoint, args)
    cached = CACHE / f"{k}.json"
    if cached.exists():
        print(f"  [cache] {label}")
        return json.loads(cached.read_text())
    print(f"  [fal] {label}  -> {endpoint}  (est ${est_cost:.2f})", flush=True)
    t = time.time()
    result = fal_client.subscribe(endpoint, arguments=args, with_logs=False)
    cached.write_text(json.dumps(result))
    entry = {"label": label, "endpoint": endpoint, "est_cost": est_cost,
             "seconds": round(time.time() - t, 1), "cache_key": k, "at": time.strftime("%F %T")}
    entries = json.loads(log.read_text()) if log.exists() else []
    entries.append(entry)
    log.write_text(json.dumps(entries, indent=2))
    return result


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)  # always refresh: the prompt (and result) may have changed
    return dest


def first_url(result: dict, *keys: str) -> str:
    """Pull the first media URL out of a fal result, whatever its shape."""
    for k in keys:
        v = result.get(k)
        if isinstance(v, list) and v:
            v = v[0]
        if isinstance(v, dict) and "url" in v:
            return v["url"]
        if isinstance(v, str) and v.startswith("http"):
            return v
    raise ValueError(f"no media url in result keys {list(result)}")
