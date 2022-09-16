from spire.models import SectionDetail
from spire.patterns import UNITS_REGEXP
from spire.scraper.classes.assertions import NO_EMPTY_STRS_ASSERTION
from spire.scraper.classes.normalizers import (
    COURSE_CREDIT_NORMALIZER,
    DICT_KEY_NORMALIZER,
    NONE_STRING_TO_NONE_NORMALIZER,
    STRIP_STR,
)
from spire.scraper.classes.shared import RawDictionary, RawField


def class_component_norm(x: str) -> list[str]:
    l = []
    for s in x.split("\n"):
        if s == "Required":
            # l[-1] = l[-1] + " (Required)"
            # After scraping 65000 sections, every class component
            # was listed as required... Nice!
            pass
        elif s == "Studio / Skills":
            l.append("Studio/Skills")
        else:
            l.append(s)

    return l


gened_set = set(["AL", "AT", "BS", "CW", "DG", "DU", "G", "HS", "I", "PS", "R1", "R2", "SB", "SI", "U"])

class_component_set = set(
    [
        "Colloquium",
        "Discussion",
        "Dissertation/Thesis",
        "Individualized Study",
        "Laboratory",
        "Lecture",
        "Practicum",
        "Seminar",
        "Studio/Skills",
        "Online",
    ]
)


class RawSectionDetail(RawDictionary):
    def __init__(self, spire_id: str, table: dict[str, str]) -> None:
        super().__init__(
            SectionDetail,
            spire_id,
            table,
            [
                RawField(k="Status", choices=("Open", "Closed", "Wait List")),
                RawField(k="Class Number", re=r"^\d{3,15}$"),
                RawField(
                    k="Session",
                    normalizers=[
                        DICT_KEY_NORMALIZER({"*University": "University", "UWW": "University Without Walls"})
                    ],
                    min_len=1,
                ),
                RawField(
                    k="Units",
                    normalizers=[COURSE_CREDIT_NORMALIZER],
                    re=UNITS_REGEXP,
                ),
                RawField(
                    k="Class Components",
                    normalizers=[class_component_norm],
                    assertions=[NO_EMPTY_STRS_ASSERTION, lambda x: set(x).issubset(class_component_set)],
                ),
                RawField(k="Career", choices=("Undergraduate", "Graduate", "Non-Credit")),
                RawField(k="Grading", min_len=1),
                RawField(k="Topic", min_len=1),
                RawField(
                    k="Gened",
                    normalizers=[NONE_STRING_TO_NONE_NORMALIZER, STRIP_STR, lambda x: x.split(" ")],
                    assertions=[lambda x: set(x).issubset(gened_set)],
                ),
                RawField(k="RAP/TAP/HLC", normalizers=[NONE_STRING_TO_NONE_NORMALIZER]),
            ],
        )