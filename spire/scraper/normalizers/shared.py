from functools import reduce
from typing import NamedTuple

from django.utils import timezone

from spire.scraper.shared import assert_match


def key_override_factory(table):
    for k in list(table.keys()):
        if isinstance(k, tuple):
            value = table[k]
            del table[k]

            for sub_k in k:
                table[sub_k] = value

    def overrider(x):
        return table[x] if x in table else x

    return overrider


SUBJECT_OVERRIDES = key_override_factory(
    {
        "BDIC": ("BDIC", "Bachelors Degree with Individualized Concentration"),
        "BIOCHEM": ("BIOCHEM", "Biochemistry & Molecular Biology"),
        "BMED-ENG": ("BME", "Biomedical Engineering"),
        "CE-ENGIN": ("CEE", "Civil and Environmental Engineering"),
        "CHEM-ENG": ("CHE", "Chemical Engineering"),
        "CICS": ("CICS", "Manning College of Information & Computer Sciences"),
        ("EC-ENG", "E&C-ENG"): ("ECE", "Electrical & Computer Engineering"),
        ("HM&FN", "HMFNART"): ("HFA", "Humanities and Fine Arts"),
        "HT-MGT": ("HTM", "Hospitality & Tourism Management"),
        ("MI-ENG", "M&I-ENG"): ("MIE", "Mechanical & Industrial Engineering"),
        ("NEUROS&B", "NEUROSB"): ("NSB", "Neuroscience & Behavior"),
        ("ORG&EVBI", "ORGEVBI"): ("OEB", "Organismic & Evolutionary Biology"),
        "SPHH": ("SPHH", "School of Public Health & Health Sciences"),
        "STOCKSCH": ("STOCKSCH", "Stockbridge School of Agriculture"),
    }
)


_DETAIL_OVERRIDES = {
    "Academic Group": key_override_factory(
        {
            "College of Humanities&Fine Art": "College of Humanities & Fine Art",
            "Stockbridge School": "Stockbridge School of Agriculture",
            "College of Social & Behav. Sci": "College of Social & Behavioral Sciences",
            "College of Info & Computer Sci": "Manning College of Information & Computer Sciences",
        }
    ),
    "Academic Organization": key_override_factory(
        {
            "Bldg &Construction Technology": "Building & Construction Technology",
            "Civil & Environmental Engin.": "Civil & Environmental Engineering",
            "College of Info & Computer Sci": "Manning College of Information & Computer Sciences",
        }
    ),
    "Grading Basis": key_override_factory(
        {"Grad Ltr Grading, with options": "Graduate Letter Grading, with options"}
    ),
}


def description_normalizer(desc: str) -> str:
    desc = desc.replace("\\n", " ").replace("\\\\\\n", " ")

    while "  " in desc:
        desc = desc.replace("  ", " ")

    while "\n\n" in desc:
        desc = desc.replace("\n\n", "\n")

    return desc


def detail_override_normalizer(detail: dict) -> dict:
    for (k, f) in _DETAIL_OVERRIDES.items():
        if k in detail:
            detail[k] = f(detail[k])

    return detail


def clean_id(*args: str) -> list[str]:
    cleaned = []

    for s in args:
        cleaned.append(s.strip().upper())

    return cleaned[0] if len(args) == 1 else cleaned


class SpireField(NamedTuple):
    k: str
    normalizers: list = None
    assertions: list = None
    re: str = None


def _reduce_assertions(a, f):
    if isinstance(f, str):
        assert_match(f, a)
    else:
        f(a)

    return a


class SpireObject:
    def __init__(self, name: str, *args: SpireField) -> None:
        self._name = name
        self._primary_key = "id"

        for field in args:
            v = getattr(self, field.k, None)
            if v is None:
                continue

            if field.normalizers:
                v = reduce(lambda a, f: f(a), field.normalizers, v)

            if field.re:
                assert_match(field.re, v)

            if field.assertions:
                reduce(_reduce_assertions, field.assertions, v)

            setattr(self, field.k, v)

        self._model_keys = set(
            [
                k
                for k in dir(self)
                if not k.startswith("_") and k != self._primary_key and not callable(getattr(self, k))
            ]
        )

    def __str__(self) -> str:
        values = ""
        for k in self._model_keys:
            if values != "":
                values += ", "

            values += f"{k}={getattr(self, k)}"

        return f"{self._name}[{getattr(self, self._primary_key)}]({values})"

    def as_model_default(self, time=False) -> dict:
        default = {k: getattr(self, k) for k in self._model_keys}

        if time:
            default["_updated_at"] = timezone.now()

        return default
