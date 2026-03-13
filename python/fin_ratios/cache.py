"""
Caching layer for fin-ratios fetchers.

Prevents redundant network calls and respects API rate limits.
Supports in-memory, disk (JSON), and Redis backends.

Usage:
    from fin_ratios.cache import set_cache, clear_cache

    set_cache('disk', ttl_hours=24)         # persist across sessions
    set_cache('memory', ttl_hours=1)        # in-process only
    set_cache('redis', ttl_hours=6, url='redis://localhost:6379')
    set_cache('none')                       # disable caching

    # All fetcher calls are now cached automatically
    data = fetch_yahoo('AAPL')    # first call: network
    data = fetch_yahoo('AAPL')    # subsequent calls: instant
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable, Literal, Optional

# ── Global cache state ────────────────────────────────────────────────────────

_BACKEND: Literal["none", "memory", "disk", "redis"] = "none"
_TTL_SECONDS: int = 3600 * 24  # 24 hours default
_CACHE_DIR: Path = Path.home() / ".fin-ratios-cache"
_REDIS_CLIENT: Any = None
_MEMORY_STORE: dict[str, tuple[float, Any]] = {}  # key → (expiry_ts, value)


def set_cache(
    backend: Literal["none", "memory", "disk", "redis"] = "disk",
    ttl_hours: float = 24,
    cache_dir: Optional[str] = None,
    redis_url: str = "redis://localhost:6379",
    redis_db: int = 0,
) -> None:
    """
    Configure the global cache backend.

    Args:
        backend:    'none' | 'memory' | 'disk' | 'redis'
        ttl_hours:  How long to cache responses (default: 24h)
        cache_dir:  Override disk cache location (default: ~/.fin-ratios-cache)
        redis_url:  Redis connection string (only used with backend='redis')
        redis_db:   Redis database index

    Example:
        set_cache('disk', ttl_hours=24)
        set_cache('memory', ttl_hours=1)
        set_cache('none')   # disable
    """
    global _BACKEND, _TTL_SECONDS, _CACHE_DIR, _REDIS_CLIENT

    _BACKEND = backend
    _TTL_SECONDS = int(ttl_hours * 3600)

    if cache_dir:
        _CACHE_DIR = Path(cache_dir)

    if backend == "disk":
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if backend == "redis":
        try:
            import redis as _redis  # type: ignore

            _REDIS_CLIENT = _redis.from_url(redis_url, db=redis_db, decode_responses=True)
            _REDIS_CLIENT.ping()
        except ImportError:
            raise ImportError("Redis backend requires: pip install redis")
        except Exception as e:
            raise ConnectionError(f"Could not connect to Redis at {redis_url}: {e}")


def _cache_key(namespace: str, *args: Any, **kwargs: Any) -> str:
    payload = json.dumps(
        {"ns": namespace, "a": args, "k": sorted(kwargs.items())}, sort_keys=True, default=str
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _get(key: str) -> tuple[bool, Any]:
    """Returns (hit, value)."""
    now = time.time()

    if _BACKEND == "memory":
        entry = _MEMORY_STORE.get(key)
        if entry and entry[0] > now:
            return True, entry[1]
        return False, None

    if _BACKEND == "disk":
        path = _CACHE_DIR / f"{key}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if data.get("exp", 0) > now:
                    return True, data["val"]
            except Exception:
                pass
        return False, None

    if _BACKEND == "redis" and _REDIS_CLIENT:
        raw = _REDIS_CLIENT.get(f"fin-ratios:{key}")
        if raw:
            try:
                return True, json.loads(raw)
            except Exception:
                pass
        return False, None

    return False, None


def _set(key: str, value: Any) -> None:
    exp = time.time() + _TTL_SECONDS

    if _BACKEND == "memory":
        _MEMORY_STORE[key] = (exp, value)

    elif _BACKEND == "disk":
        path = _CACHE_DIR / f"{key}.json"
        try:
            path.write_text(json.dumps({"exp": exp, "val": value}, default=str))
        except Exception:
            pass  # cache write failure is non-fatal

    elif _BACKEND == "redis" and _REDIS_CLIENT:
        try:
            _REDIS_CLIENT.setex(f"fin-ratios:{key}", _TTL_SECONDS, json.dumps(value, default=str))
        except Exception:
            pass


def cached(namespace: str) -> Callable:
    """
    Decorator for fetcher functions. Caches based on all arguments.

    Example:
        @cached("yahoo")
        def fetch_yahoo(ticker: str, ...): ...
    """

    def decorator(fn: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _BACKEND == "none":
                return fn(*args, **kwargs)
            key = _cache_key(namespace, *args, **kwargs)
            hit, val = _get(key)
            if hit:
                return val
            result = fn(*args, **kwargs)
            _set(key, result)
            return result

        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper

    return decorator


def invalidate(ticker: str) -> int:
    """
    Remove all cached entries for a ticker (case-insensitive).
    Returns number of entries removed.
    """
    ticker_lower = ticker.lower()
    removed = 0

    if _BACKEND == "disk":
        for path in _CACHE_DIR.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                val = data.get("val")
                if isinstance(val, dict) and val.get("ticker", "").lower() == ticker_lower:
                    path.unlink()
                    removed += 1
            except Exception:
                pass

    elif _BACKEND == "memory":
        keys_to_del = [
            k
            for k, (_, v) in _MEMORY_STORE.items()
            if isinstance(v, dict) and v.get("ticker", "").lower() == ticker_lower
        ]
        for k in keys_to_del:
            del _MEMORY_STORE[k]
            removed += len(keys_to_del)

    return removed


def clear_cache() -> None:
    """Remove all cached entries."""
    global _MEMORY_STORE

    if _BACKEND == "disk":
        for path in _CACHE_DIR.glob("*.json"):
            path.unlink(missing_ok=True)

    elif _BACKEND == "memory":
        _MEMORY_STORE = {}

    elif _BACKEND == "redis" and _REDIS_CLIENT:
        keys = _REDIS_CLIENT.keys("fin-ratios:*")
        if keys:
            _REDIS_CLIENT.delete(*keys)


def cache_stats() -> dict:
    """Return cache statistics."""
    now = time.time()

    if _BACKEND == "disk":
        paths = list(_CACHE_DIR.glob("*.json"))
        valid = sum(1 for p in paths if _safe_read_exp(p) > now)
        return {
            "backend": "disk",
            "total": len(paths),
            "valid": valid,
            "dir": str(_CACHE_DIR),
            "ttl_hours": _TTL_SECONDS / 3600,
        }

    if _BACKEND == "memory":
        valid = sum(1 for exp, _ in _MEMORY_STORE.values() if exp > now)
        return {
            "backend": "memory",
            "total": len(_MEMORY_STORE),
            "valid": valid,
            "ttl_hours": _TTL_SECONDS / 3600,
        }

    return {"backend": _BACKEND}


def _safe_read_exp(path: Path) -> float:
    try:
        return json.loads(path.read_text()).get("exp", 0)
    except Exception:
        return 0
