class VersionedCache:
    def __init__(self, t, head=None):
        self._head = head

        self._cache = {}
        self._type = t
        self._skipped_keys = set()

    def __str__(self):
        return f"VersionedCache('{self._type}',{str(self._head)})"

    @property
    def is_empty(self):
        return self._head is None

    @property
    def type(self):
        return self._type

    def push(self, key: str, value):
        self._cache[key] = value

    def commit(self):
        self._head = self._cache
        self._cache = {}
        self._skipped_keys = set()

    def get(self, key, default=None):
        if self.is_empty or key not in self._head:
            return default if default else None

        return self._head[key]

    def skip_once(self, lst, key):
        if (v := self.get(key)) is None or key in self._skipped_keys:
            return lst

        self._skipped_keys.add(key)

        l = []
        found = False
        for x in lst:
            if not found and x == v:
                found = True

            if found:
                l.append(x)

        return l
