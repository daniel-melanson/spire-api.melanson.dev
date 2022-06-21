from functools import reduce


NO_EMPTY_STRS_ASSERTION = lambda x: reduce(lambda a, x: a and len(x) > 0, x, True)
