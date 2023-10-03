import logging
import re
from functools import reduce
from typing import Any, Callable, Iterable, NamedTuple, Optional, Union

from django.db.models import Model
from django.utils import timezone

from spire.scraper.shared import assert_match

log = logging.getLogger(__name__)


def assert_dict_keys_subset(d: dict[str, Any], keys: Iterable[str]):
    a = set(d.keys())
    b = set(keys)

    log.debug("Asserting %s is subset of %s", a, b)
    assert a.issubset(b)


def re_override_factory(*args: tuple[str, Any]) -> Callable[[str], str]:
    def f(x: str):
        for pattern, replace in args:
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
                        replace = (
                            replace[: offset + low]
                            + inserting_text
                            + replace[offset + high :]
                        )
                        offset += len(replace) - old

                    x = replace

        return x

    return f


def key_override_factory(*args: Any) -> dict[str, Any]:
    d: dict[str, Any] = {}

    for key, value in args:
        if isinstance(key, tuple):
            for sub_k in key:
                d[sub_k] = value
        else:
            d[key] = value

    return d


def clean_id(s: str) -> str:
    return s.strip().upper()


def to_camel_case(s: str) -> str:
    return s.lower().replace("/", "_").replace(" ", "_")


def serialize(v: Any):
    if isinstance(v, str):
        return f"'{v}'"
    if isinstance(v, list):
        if len(v) == 0:
            return "[]"

        return f"[{', '.join([serialize(x) for x in v])}]"

    return str(v)


class RawField(NamedTuple):
    k: str
    optional = True
    normalizers: list[Callable[[Any], Any]] = []
    re: Optional[str] = None
    min_len: Optional[int] = None
    len: Optional[tuple[int, int]] = None
    assertions: list[Callable[[Any], bool]] = []
    choices: Optional[tuple[str, ...]] = None


class RawObject:
    def __init__(
        self,
        model: Any,
        id: Union[str, None] = None,
        fields: list[RawField] = [],
        update_time: bool = False,
    ) -> None:
        self._name: str = "Raw" + model.__name__  # type: ignore
        self._model = model
        self.id = id
        self._update_time = update_time

        for field in fields:
            k = to_camel_case(field.k)
            v = getattr(self, k, None)
            log.debug(
                "Normalizing and asserting %s into field %s.%s", v, model.__name__, k
            )
            if v is None:
                assert field.optional
                log.debug("Field not present, skipping.")
                continue

            if field.normalizers:
                v = reduce(
                    lambda a, f: f(a) if a is not None else None, field.normalizers, v
                )

            if v is None:
                log.debug("Field normalized to none, skipping.")
                assert field.optional
            else:
                if field.re:
                    assert_match(field.re, v)

                if field.min_len:
                    assert field.min_len <= len(v)

                if field.len:
                    assert field.len[0] <= len(v) <= field.len[1]

                if field.assertions:
                    for f in field.assertions:
                        assert f(v)

                if field.choices:
                    assert v in field.choices

            setattr(self, k, v)
            log.debug("%s.%s set to %s", self._name, k, v)

        self._model_keys = [to_camel_case(f.k) for f in fields]

    def __str__(self) -> str:
        values = ""
        for k in self._model_keys:
            v = serialize(getattr(self, k))

            if len(self._model_keys) > 2:
                if len(values) > 0:
                    values += ",\n\t"

                values += f"{k}={v}"
            else:
                if len(values) > 0:
                    values += ", "

                values += f"{k}={v}"

        s = f"{self._name}[{self.id}]("
        if len(self._model_keys) > 2:
            s += f"\n\t{values}\n)"
        else:
            s += f"{values})"

        return s

    def get_model_defaults(self) -> dict[str, str]:
        default = {k: getattr(self, k) for k in self._model_keys if k != "id"}

        if self._update_time:
            default["_updated_at"] = timezone.now()

        return default

    def push(self, defaults: Optional[dict[str, Any]] = None, **kwargs: Any):
        if defaults is None:
            defaults = self.get_model_defaults()

        if len(kwargs) == 0:
            assert self.id is not None
            kwargs["id"] = self.id

        object, created = self._model.objects.update_or_create(
            **kwargs, defaults=defaults
        )

        log.info("%s %s: %s", "Created" if created else "Updated", self._model.__name__, object)  # type: ignore

        return object


class RawDictionary(RawObject):
    def __init__(
        self, model: Any, id: str, table: dict[str, str], fields: list[RawField]
    ) -> None:
        assert_dict_keys_subset(table, map(lambda d: d.k, fields))

        for f in fields:
            s_k = to_camel_case(f.k)

            if f.k in table:
                setattr(self, s_k, table[f.k])
            else:
                setattr(self, s_k, None)

        super().__init__(model, id, fields)
