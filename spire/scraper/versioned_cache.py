class VersionedCache:
    def __init__(self):
        self._head = None

        self._cache = {}

    def __str__(self):
        return f"VersionedCache({str(self._head)})"

    @property
    def is_empty(self):
        return self._head is None

    def push(self, key: str, value):
        self._cache[key] = value

    def commit(self):
        self._head = self._cache
        self._cache = {}

    def get(self, key, default=None):
        if self.is_empty or key not in self._head:
            return default if default else None

        return self._head[key]
