import logging

from spire.models import SectionDetail
from spire.scraper.classes.assertions import NO_EMPTY_STRS_ASSERTION
from spire.scraper.classes.courses.raw_course_detail import RawUnits
from spire.scraper.classes.normalizers import (
    DICT_KEY_NORMALIZER,
    NONE_STRING_TO_NONE_NORMALIZER,
    STRIP_STR,
)
from spire.scraper.classes.shared import RawDictionary, RawField

log = logging.getLogger(__name__)


def class_component_norm(x: str) -> list[str]:
    l = []
    for s in x.split("\n"):
        if s in ("Required", "Optional"):
            # Prior to Summer 2024, all components were required
            # After Summer 2024, some components are optional
            # FUCK!!!!!
            pass
        elif s == "Studio / Skills":
            l.append("Studio/Skills")
        else:
            l.append(s)

    return l


gened_set = set(
    [
        "AL",
        "AT",
        "BS",
        "CW",
        "DG",
        "DU",
        "G",
        "HS",
        "I",
        "PS",
        "R1",
        "R2",
        "SB",
        "SI",
        "U",
    ]
)

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
        "Flex Option",
    ]
)


class RawSectionDetail(RawDictionary):
    def __init__(self, spire_id: str, table: dict[str, str]) -> None:
        if "Units" in table:
            self.units = RawUnits(table["Units"])
            log.debug("Scraped units: %s", self.units)
            del table["Units"]

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
                        DICT_KEY_NORMALIZER(
                            {
                                "*University": "University",
                                "UWW": "University Without Walls",
                                "*University Eligible/UWW": "University Eligible/UWW",
                                "*University Non-standard Dates": "University Non-standard Dates",
                                "Univ+ Non-Stand. (UWW)": "University Without Walls Non-standard Dates",
                                "Univ+ Summer Session 1 (UWW)": "University Without Walls Summer Session 1",
                            }
                        )
                    ],
                    min_len=1,
                ),
                RawField(
                    k="Class Components",
                    normalizers=[class_component_norm],
                    assertions=[
                        NO_EMPTY_STRS_ASSERTION,
                        lambda x: set(x).issubset(class_component_set),
                    ],
                ),
                RawField(
                    k="Career", choices=("Undergraduate", "Graduate", "Non-Credit")
                ),
                RawField(k="Grading", min_len=1),
                RawField(k="Topic", min_len=1),
                RawField(
                    k="Gened",
                    normalizers=[
                        NONE_STRING_TO_NONE_NORMALIZER,
                        STRIP_STR,
                        lambda x: x.split(" "),
                    ],
                    assertions=[lambda x: set(x).issubset(gened_set)],
                ),
                RawField(k="RAP/TAP/HLC", normalizers=[NONE_STRING_TO_NONE_NORMALIZER]),
            ],
        )

    def push(self, **kwargs):
        sd, created = super().push(**kwargs)

        if hasattr(self, "units"):
            sd.units, _ = self.units.push()
            sd.save()

        return sd, created
