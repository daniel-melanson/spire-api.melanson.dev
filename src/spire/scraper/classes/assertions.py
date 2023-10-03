from typing import Callable, Sized

NO_EMPTY_STRS_ASSERTION: Callable[[list[Sized]], bool] = lambda lst: all(
    map(lambda x: len(x) > 0, lst)
)
