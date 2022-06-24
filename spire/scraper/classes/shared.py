import logging
import re
from functools import reduce
from typing import Any, Iterable, NamedTuple

from django.db.models import Model
from django.utils import timezone

from spire.scraper.shared import assert_match

log = logging.getLogger(__name__)


def assert_dict_keys_subset(d: dict, keys: Iterable[str]):
    assert set(d.keys()).issubset(set(keys))


def re_override_factory(*args: tuple[str, Any]):
    def f(x):
        for (pattern, replace) in args:
            if match := re.match(pattern, x):
                if not isinstance(replace, str):
                    x = replace
                    break
                else:
                    offset = 0
                    for replace_match in re.finditer(r"\$(\d+)", replace):
                        group_number = replace_match.group(1)
                        inserting_text = match.group(int(group_number))

                        (low, high) = replace_match.span(0)
                        old = len(replace)
                        replace = replace[: offset + low] + inserting_text + replace[offset + high :]
                        offset += len(replace) - old

                    x = replace

        return x

    return f


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
    return s.lower().replace("/", "_").replace(" ", "_")


class RawField(NamedTuple):
    k: str
    normalizers: list = None
    assertions: list = None
    re: str = None
    choices: tuple[str, ...] = None
    len: tuple[int, int] = None
    optional = True


class RawObject:
    def __init__(self, model: Model, *args: RawField, pk="id", update_time=False) -> None:
        self._name = "Raw" + model.__name__
        self._model = model
        self._pk = pk
        self._update_time = update_time

        for field in args:
            k = to_camel_case(field.k)
            v = getattr(self, k, None)
            log.debug("Normalizing and asserting %s into field %s.%s", v, Model.__name__, k)
            if v is None:
                assert field.optional
                log.debug("Field not present, skipping")
                continue

            if field.normalizers:
                v = reduce(lambda a, f: f(a) if a is not None else None, field.normalizers, v)

            if field.re:
                assert_match(field.re, v)

            if field.len:
                assert field.len[0] <= len(v) <= field.len[1]

            if field.assertions:
                for f in field.assertions:
                    assert f(v)

            if field.choices:
                assert v in field.choices

            setattr(self, k, v)
            log.debug("%s.%s set to %s", self._name, k, v)

        self._model_keys = [to_camel_case(f.k) for f in args]

    def __str__(self) -> str:
        values = ""
        for k in self._model_keys:
            v = getattr(self, k)

            if isinstance(v, str):
                v = f"'{v}'"
            elif isinstance(v, list):
                v = f"[{', '.join([str(x) for x in v])}]"

            if len(self._model_keys) > 2:
                if len(values) > 0:
                    values += ",\n\t"

                values += f"{k}={v}"
            else:
                if len(values) > 0:
                    values += ", "

                values += f"{k}={v}"

        s = f"{self._name}[{getattr(self, self._pk, None)}]("
        if len(self._model_keys) > 2:
            s += f"\n\t{values}\n)"
        else:
            s += f"{values})"

        return s

    def get_model_defaults(self) -> dict:
        default = {k: getattr(self, k) for k in self._model_keys if k != self._pk}

        if self._update_time:
            default["_updated_at"] = timezone.now()

        return default

    def push(self, defaults=None, **kwargs):
        if defaults is None:
            defaults = self.get_model_defaults()

        if len(kwargs) == 0:
            kwargs["id"] = self.id

        object, created = self._model.objects.update_or_create(**kwargs, defaults=defaults)

        log.info("%s %s: %s", "Created" if created else "Updated", self._model.__name__, object)

        return object


class RawDictionary(RawObject):
    def __init__(self, model: Model, table: dict[str, str], *args: RawField, pk="id") -> None:
        assert_dict_keys_subset(table, map(lambda d: d.k, args))

        for f in args:
            s_k = to_camel_case(f.k)

            if f.k in table:
                setattr(self, s_k, table[f.k])
            else:
                setattr(self, s_k, None)

        super().__init__(model, *args, pk=pk)
