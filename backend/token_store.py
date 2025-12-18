import json
import time
from backend.redis_client import redis_client

SESSION_PREFIX = "session:"


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

    redis_client.setex(
        _key(session_id),
        expires_in,
        json.dumps(payload)
    )


def get_tokens(session_id: str) -> dict | None:
    data = redis_client.get(_key(session_id))
    if not data:
        return None
    return json.loads(data)


def clear_tokens(session_id: str):
    redis_client.delete(_key(session_id))
