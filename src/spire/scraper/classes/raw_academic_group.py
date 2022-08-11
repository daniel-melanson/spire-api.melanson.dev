from spire.models import AcademicGroup
from spire.scraper.classes.normalizers import DICT_KEY_NORMALIZER
from spire.scraper.classes.shared import RawField, RawObject, key_override_factory

GROUP_OVERRIDES = key_override_factory(
    {
        "College of Humanities&Fine Art": "College of Humanities & Fine Art",
        "Stockbridge School": "Stockbridge School of Agriculture",
        "College of Social & Behav. Sci": "College of Social & Behavioral Sciences",
        "College of Info & Computer Sci": "Manning College of Information & Computer Sciences",
        "College of Natural Sci. & Math": "College of Natural Sciences",
        (
            "School of Pub Hlth & Hlth Sci",
            "Sch. of Public Health&Hlth Sci",
        ): "School of Public Health & Health Sciences",
        "School of Education": "College of Education",
        "School of Management": "Isenberg School of Management",
        "Commonwealth College": "Commonwealth Honors College",
    }
)

ACADEMIC_GROUP_NORMALIZER = DICT_KEY_NORMALIZER(GROUP_OVERRIDES)


class RawAcademicGroup(RawObject):
    title: str

    def __init__(self, title: str) -> None:
        self.title = title

        super().__init__(
            AcademicGroup,
            fields=[
                RawField(k="title", normalizers=[ACADEMIC_GROUP_NORMALIZER]),
            ],
        )

    def push(self):
        object, _ = AcademicGroup.objects.get_or_create(title=self.title)

        return object
