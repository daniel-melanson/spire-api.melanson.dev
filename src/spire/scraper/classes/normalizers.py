from typing import Any, Callable, Optional

from spire.scraper.classes.shared import re_override_factory

COURSE_CREDIT_NORMALIZER = re_override_factory(
    (r"\d+", "$0.00"),
    (r"^(\d+) - (\d+)$", "$1.00 - $2.00"),
    (r"^(\d+\.\d) - (\d+\.\d)$", "$10 - $20"),
    (r"^\d+\.\d$", "$00"),
)


def REPLACE_DOUBLE_SPACE(s: str):
    while "  " in s:
        s = s.replace("  ", " ")

    return s


def DICT_KEY_NORMALIZER(table: dict[str, str]) -> Callable[[str], str]:
    return lambda k: table[k] if k in table else k


NONE_STRING_TO_NONE_NORMALIZER = re_override_factory((r"^(None|\(None\))$", None))

SPLIT_NEWLINE: Callable[[str], list[str]] = lambda x: [s.strip() for s in x.split("\n")]

STRIP_STR: Callable[[Any], Any] = lambda x: x.strip() if isinstance(x, str) else x

EMPTY_TO_NONE: Callable[[Any], Optional[Any]] = lambda x: None if len(x) == 0 else x

_BAD_DESCRIPTIONS = (
    "not available at this time",
    "description not available",
    "not available at this time.",
    "this is not available at this time",
    "description not available at this time",
    "description not available at this time.",
    "description - Not available at this time",
    "course description not available at this time",
    "course desctiption not available at this time.",
    "course description not available at this time.",
)

DESCRIPTION_NOT_AVAILABLE_TO_NONE: Callable[[str], Optional[str]] = (
    lambda x: None if x.lower() in _BAD_DESCRIPTIONS else x
)


def NORMALIZER_FOR_DICT(normalizer: Callable[[Any], Any]) -> Callable[[dict[Any, Any]], dict[Any, Any]]:
    def f(x: dict[Any, Any]):
        for (k, v) in x.items():
            x[k] = normalizer(v)

        return x

    return f


DICT_STRIP_STR = NORMALIZER_FOR_DICT(STRIP_STR)
