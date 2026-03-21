from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List


def validate_markdown_output_path(raw_path: str) -> Path:
    output_path = Path(raw_path)
    if output_path.is_absolute():
        raise ValueError("absolute output paths are not allowed")
    if ".." in output_path.parts:
        raise ValueError("parent directory traversal is not allowed")
    if output_path.suffix.lower() != ".md":
        raise ValueError("output file must end with .md")
    return output_path


@dataclass
class SlidingWindowRateLimiter:
    limit_per_minute: int
    windows: Dict[str, List[float]] = field(default_factory=dict)

    def check(self, client_id: str, now_ts: float) -> None:
        window_start = now_ts - 60.0
        history = self.windows.get(client_id, [])
        history = [ts for ts in history if ts >= window_start]
        if len(history) >= self.limit_per_minute:
            raise ValueError("rate limit exceeded")
        history.append(now_ts)
        self.windows[client_id] = history


def parse_api_keys(raw_multi: str | None, raw_single: str | None = None) -> set[str]:
    values: set[str] = set()
    if raw_multi:
        for item in raw_multi.split(","):
            token = item.strip()
            if token:
                values.add(token)
    if raw_single and raw_single.strip():
        values.add(raw_single.strip())
    return values


@dataclass
class RedisSlidingWindowRateLimiter:
    redis_client: object
    limit_per_minute: int
    key_prefix: str = "repohunter:ratelimit"

    def check(self, client_id: str, now_ts: float) -> None:
        key = f"{self.key_prefix}:{client_id}"
        window_start = now_ts - 60.0
        p = self.redis_client.pipeline(transaction=True)
        p.zremrangebyscore(key, 0, window_start)
        p.zcard(key)
        p.zadd(key, {str(now_ts): now_ts})
        p.expire(key, 120)
        results = p.execute()
        current_count = int(results[1])
        if current_count >= self.limit_per_minute:
            raise ValueError("rate limit exceeded")
