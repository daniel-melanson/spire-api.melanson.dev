from math import floor
from time import sleep, time


class Timer:
    def __init__(self, running: bool = True) -> None:
        self._running = running
        self._last = time()
        self._count = 0

    def __str__(self):
        if self._running:
            self._do_count()

        s = ""
        n = self._count
        for i, unit in enumerate(["hour", "minute", "second"]):
            p = 60 ** (3 - i - 1)
            unit_count = n // p if p > 1 else floor(n * 1000) / 1000
            n -= unit_count * p

            if len(s) > 0 or unit_count > 0:
                if len(s) > 0:
                    s += " "

                s += f"{unit_count} {unit}"
                if unit_count > 0:
                    s += "s"

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


if __name__ == "__main__":
    t = Timer()
    sleep(5.5)
    print(t)
