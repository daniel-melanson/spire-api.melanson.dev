class Stats:
    def __init__(self):
        self._stats = {}

    def get(self, key: str):
        return self._stats.get(key, 0)

    def increment(self, key: str, by=1):
        if key not in self._stats:
            self._stats[key] = 0

        self._stats[key] += by
