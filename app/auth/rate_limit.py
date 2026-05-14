from time import monotonic


class LoginRateLimiter:
    def __init__(self, max_attempts: int, lock_seconds: int) -> None:
        self.max_attempts = max_attempts
        self.lock_seconds = lock_seconds
        self._attempts: dict[str, tuple[int, float]] = {}

    def is_locked(self, key: str) -> bool:
        count, locked_until = self._attempts.get(key, (0, 0.0))
        if locked_until <= monotonic():
            return False
        return count >= self.max_attempts

    def record_failure(self, key: str) -> None:
        count, locked_until = self._attempts.get(key, (0, 0.0))
        if locked_until <= monotonic():
            count = 0
        count += 1
        locked_until = monotonic() + self.lock_seconds if count >= self.max_attempts else 0.0
        self._attempts[key] = (count, locked_until)

    def record_success(self, key: str) -> None:
        self._attempts.pop(key, None)
