import logging
from typing import Optional

from spire.models import CourseDetail, CourseUnits
from spire.scraper.classes.assertions import NO_EMPTY_STRS_ASSERTION
from spire.scraper.classes.groups.raw_academic_group import (
    ACADEMIC_GROUP_NORMALIZER,
    GROUP_OVERRIDES,
)
from spire.scraper.classes.normalizers import (
    COURSE_CREDIT_NORMALIZER,
    DICT_KEY_NORMALIZER,
    SPLIT_NEWLINE,
)
from spire.scraper.classes.shared import RawDictionary, RawField, RawObject

log = logging.getLogger(__name__)

ACADEMIC_ORG_NORMALIZER = DICT_KEY_NORMALIZER(
    {
        **GROUP_OVERRIDES,
        "Bldg &Construction Technology": "Building & Construction Technology",
        "Civil & Environmental Engin.": "Civil & Environmental Engineering",
        "College of Info & Computer Sci": "Manning College of Information & Computer Sciences",
        "Organismic&EvolutionaryBiology": "Organismic & Evolutionary Biology",
        "BA/BS w. Individual Concentra.": "BA/BS with Individual Concentration",
        "LL: Career & Personal Develop.": "LL: Career & Personal Development",
        "Data Analytcs & Comput. SocSci": "Data Analytics and Computational Social Science",
        "Univ. of Massachusetts Amherst": "University of Massachusetts Amherst",
        "Languages,Literature & Culture": "Languages, Literature & Culture",
        "Sustainable Community Develop": "Sustainable Community Development",
        "Electrical & Computer Engin.": "Electrical & Computer Engineering",
        "Mechanical&IndustrialEngineerg": "Mechanical & Industrial Engineering",
        "Five Coll Ctr: World Languages": "Five College Center: World Languages",
        "Social Thought &Political Econ": "Social Thought & Political Economy",
        "Hospitality & Tourism Managmnt": "Hospitality & Tourism Management",
        "Info. and Computer Sciences": "Informatics and Computer Sciences",
    }
)


class RawUnits(RawObject):
    def __init__(self, units: str) -> None:
        credits = COURSE_CREDIT_NORMALIZER(units)

        if " - " in credits:
            [min_s, max_s] = credits.split(" - ")
            self.min = float(min_s)
            self.max = float(max_s)
            self.base = None
        else:
            self.min = None
            self.max = None
            self.base = float(credits)

        super().__init__(
            CourseUnits, None, [RawField("base"), RawField("min"), RawField("max")]
        )

    def push(self):
        if self.base is not None:
            u, _ = CourseUnits.objects.get_or_create(
                base=self.base, defaults={"min": None, "max": None}
            )
        else:
            u, _ = CourseUnits.objects.get_or_create(
                min=self.min, max=self.max, defaults={"base": None}
            )

        return u


class RawCourseDetail(RawDictionary):
    career: Optional[str]
    grading_basis: Optional[str]
    course_components: Optional[list[str]]
    academic_group: Optional[str]
    campus: Optional[str]

    def __init__(self, course_id: str, table: dict[str, str]) -> None:
        if "Units" in table:
            self.units = RawUnits(table["Units"])
            log.debug("Scraped units: %s", self.units)
            del table["Units"]

        super().__init__(
            CourseDetail,
            course_id,
            table,
            fields=[
                RawField(k="Career", min_len=1),
                RawField(
                    k="Grading Basis",
                    min_len=1,
                    normalizers=[
                        DICT_KEY_NORMALIZER(
                            {
                                "Grad Ltr Grading, with options": "Graduate Letter Grading, with options"
                            }
                        )
                    ],
                ),
                RawField(
                    k="Course Components",
                    len=(1, 4),
                    normalizers=[SPLIT_NEWLINE],
                    assertions=[NO_EMPTY_STRS_ASSERTION],
                ),
                RawField(
                    k="Campus",
                    min_len=3,
                    normalizers=[
                        DICT_KEY_NORMALIZER(
                            {
                                "University (not CE)": "University",
                                "Continuing Education": "Continuing Education",
                            }
                        )
                    ],
                ),
                RawField(
                    k="Academic Group",
                    min_len=1,
                    normalizers=[ACADEMIC_GROUP_NORMALIZER],
                ),
                RawField(
                    k="Academic Organization",
                    min_len=1,
                    normalizers=[ACADEMIC_ORG_NORMALIZER],
                ),
            ],
        )

    def push(self, **kwargs):
        cd = super().push(**kwargs)

        if hasattr(self, "units"):
            cd.units = self.units.push()
            cd.save()

        return cd
