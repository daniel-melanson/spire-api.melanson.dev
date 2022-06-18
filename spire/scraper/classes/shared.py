import logging
from functools import reduce
from typing import NamedTuple

from django.db.models import Model
from django.utils import timezone

from spire.scraper.shared import assert_match

log = logging.getLogger(__name__)


def key_override_factory(table):
    for k in list(table.keys()):
        if isinstance(k, tuple):
            value = table[k]
            del table[k]

            for sub_k in k:
                table[sub_k] = value

    return table


def clean_id(*args: str) -> list[str]:
    cleaned = []

    for s in args:
        cleaned.append(s.strip().upper())

    return cleaned[0] if len(args) == 1 else cleaned


class RawField(NamedTuple):
    k: str
    normalizers: list = None
    assertions: list = None
    re: str = None


class RawObject:
    def __init__(self, model: Model, *args: RawField) -> None:
        self._model = model

        for field in args:
            v = getattr(self, field.k, None)
            if v is None:
                continue

            if field.normalizers:
                v = reduce(lambda a, f: f(a), field.normalizers, v)

            if field.re:
                assert_match(field.re, v)

            if field.assertions:
                reduce(lambda a, f: f(a), field.assertions, v)

            setattr(self, field.k, v)

        self._model_keys = set(
            [k for k in dir(self) if not k.startswith("_") and k != "id" and not callable(getattr(self, k))]
        )

    def __str__(self) -> str:
        values = ""
        for k in self._model_keys:
            if values != "":
                values += ", "

            values += f"{k}={getattr(self, k)}"

        return f"{self._name}[{getattr(self, 'id')}]({values})"

    def _as_model_default(self, time=False) -> dict:
        default = {}

        for k in self._model_keys:
            v = getattr(self, k)

            if isinstance(v, ScrapedObject):
                v = v.push()

            default[k] = v

        if time:
            default["_updated_at"] = timezone.now()

        return default

    def push(self):
        model, created = self._model.objects.update_or_create(
            id=self.id, defaults=self._as_model_default(self._time_aware)
        )

        log.info("%s %s: %s", "Created" if created else "Updated", self._model.__name__, self)
        return model
