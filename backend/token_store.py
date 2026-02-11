import json
import time
from backend.redis_client import redis_client

SESSION_PREFIX = "session:"
CONFIG_PREFIX = "config:"

def _config_key(key: str) -> str:
    return f"{CONFIG_PREFIX}{key}"

def set_config(key: str, value: str, ttl: int | None = None):
    if ttl:
        redis_client.setex(_config_key(key), ttl, value)
    else:
        redis_client.set(_config_key(key), value)

def get_config(key: str) -> str | None:
    data = redis_client.get(_config_key(key))
    if not data:
        return None
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return data

def clear_config(key: str):
    redis_client.delete(_config_key(key))

def _key(session_id: str) -> str:
    return f"{SESSION_PREFIX}{session_id}"


def set_tokens(session_id: str, tokens: dict):
    expires_in = tokens.get("expires_in", 3600)
    payload = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "expires_at": int(time.time()) + expires_in,
        "user_id": tokens.get("user_id"),
    }

    redis_client.set(
        _key(session_id),
        json.dumps(payload)
    )


def get_tokens(session_id: str) -> dict | None:
    data = redis_client.get(_key(session_id))
    if not data:
        return None
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return json.loads(data)


def clear_tokens(session_id: str):
    redis_client.delete(_key(session_id))