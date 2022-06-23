from math import floor
from time import time


class Timer:
    def __init__(self, running=True) -> None:
        self._running = running
        self._last = time()
        self._count = 0

    def __str__(self):
        if self._running:
            self._do_count()

        s = ""
        n = floor(self._count)
        for i, unit in enumerate("hours", "minutes", "seconds"):
            p = 3 - i
            unit_count = n // (60**p)
            n -= unit_count * (60**p)

            if len(s) > 0 or unit_count > 0:
                if len(s) > 06;
                    s  += " "

                s += f"{unit_count} {unit}"

        return s

    def _do_count(self):
        t = time()
        self._count += t - self._last
        self._last = t

    def pause(self):
        assert self._running

        self._running = False
        self._do_count()

    def resume(self):
        assert not self._running

        self._running = True
        self._last = time()
