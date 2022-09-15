from typing import Any, Optional


class VersionedCache:
    def __init__(self, t: str, head: Optional[dict[str, Any]] = None) -> None:
        self._head = head

        self._cache: dict[str, Any] = {}
        self._type = t
        self._skipped_keys: set[str] = set()

    def __str__(self) -> str:
        return f"VersionedCache('{self._type}',{str(self._head)})"

    @property
    def is_empty(self) -> bool:
        return self._head is None

    @property
    def type(self) -> str:
        return self._type

    def push(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def commit(self) -> None:
        self._head = self._cache
        self._cache = {}
        self._skipped_keys = set()

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        if self.is_empty or not self._head or key not in self._head:
            return default if default else None

        return self._head[key]

    def skip_once(self, lst: list[Any], key: str) -> list[Any]:
        if (v := self.get(key)) is None or key in self._skipped_keys:
            return lst

        self._skipped_keys.add(key)

        l: list[Any] = []
        found = False
        for x in lst:
            if not found and x == v:
                found = True

            if found:
                l.append(x)

        return l
