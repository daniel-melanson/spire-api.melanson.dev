import logging
from functools import reduce
from typing import NamedTuple

from django.db.models import Model
from django.utils import timezone

from spire.scraper.shared import assert_match

log = logging.getLogger(__name__)


def key_override_factory(table, as_table=False):
    for k in list(table.keys()):
        if isinstance(k, tuple):
            value = table[k]
            del table[k]

            for sub_k in k:
                table[sub_k] = value

    if as_table:
        return table

    return lambda k: table[k] if k in table else k


def clean_id(*args: str) -> list[str]:
    cleaned = []

    for s in args:
        cleaned.append(s.strip().upper())

    return cleaned[0] if len(args) == 1 else cleaned


def to_camel_case(s: str) -> str:
    return s.lower().replace(" ", "_")


class RawField(NamedTuple):
    k: str
    normalizers: list = None
    assertions: list = None
    re: str = None
    len: tuple[int, int] = None


class RawObject:
    def __init__(self, model: Model, *args: RawField, pk="id") -> None:
        self._name = model.__name__
        self._pk = pk

        for field in args:
            k = to_camel_case(field.k)
            v = getattr(self, k, None)
            if v is None:
                continue

            if field.normalizers:
                v = reduce(lambda a, f: f(a), field.normalizers, v)

            if field.re:
                assert_match(field.re, v)

            if field.len:
                assert field.len[0] < len(v) < field.len[1]

            if field.assertions:
                reduce(lambda a, f: f(a), field.assertions, v)

            setattr(self, k, v)

        self._model_keys = set(
            [
                k
                for k in dir(self)
                if not k.startswith("_") and k != self._pk and not callable(getattr(self, k))
            ]
        )

    def __str__(self) -> str:
        values = ""
        for k in self._model_keys:
            if values != "":
                values += ", "

            values += f"{k}={getattr(self, k)}"

        return f"{self._name}[{getattr(self, self._pk)}]({values})"

    def get_model_default(self, time=False) -> dict:
        default = {k: getattr(self, k) for k in self._model_keys if k != "id"}

        if time:
            default["_updated_at"] = timezone.now()

        return default
