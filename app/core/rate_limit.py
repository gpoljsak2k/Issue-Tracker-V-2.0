from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone


class LoginRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts: dict[str, deque[datetime]] = defaultdict(deque)

    def is_blocked(self, key: str) -> bool:
        now = datetime.now(timezone.utc)
        self._cleanup(key, now)
        return len(self.attempts[key]) >= self.max_attempts

    def add_attempt(self, key: str) -> None:
        now = datetime.now(timezone.utc)
        self._cleanup(key, now)
        self.attempts[key].append(now)

    def reset(self, key: str) -> None:
        if key in self.attempts:
            del self.attempts[key]

    def _cleanup(self, key: str, now: datetime) -> None:
        window_start = now - timedelta(seconds=self.window_seconds)
        while self.attempts[key] and self.attempts[key][0] < window_start:
            self.attempts[key].popleft()


login_rate_limiter = LoginRateLimiter(max_attempts=5, window_seconds=60)