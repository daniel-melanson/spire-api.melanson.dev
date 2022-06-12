class ScrapeMemento:
    def __init__(self):
        self._state = None

        self._cache = {}

    def __str__(self):
        return f"ScrapeMemento({str(self._state)})"

    @property
    def is_empty(self):
        return self._state is None

    def push(self, key: str, value):
        self._cache[key] = value

    def commit(self):
        self._state = self._cache
        self._cache = {}

    def get(self, key, default=None):
        if self.is_empty or key not in self._state:
            return default if default else None

        return self._state[key]

    def skip_until(self, lst, key):
        value = self.get(key)
        if not value:
            return lst

        itr = iter(lst)

        while next(itr) != value:
            pass

        return itr
