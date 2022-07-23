from spire.models import AcademicGroup
from spire.scraper.classes.shared import RawField, RawObject, key_override_factory

GROUP_OVERRIDES = key_override_factory(
    {
        "College of Natural Sci. & Math": "College of Natural Sciences",
        "Sch. of Public Health&Hlth Sci": "School of Public Health & Health Sciences",
        "School of Education": "College of Education",
    },
)


class RawAcademicGroup(RawObject):
    title: str

    def __init__(self, title: str) -> None:
        self.title = GROUP_OVERRIDES(title)

        super().__init__(
            AcademicGroup,
            fields=[
                RawField(k="title"),
            ],
        )

    def push(self):
        object, created = AcademicGroup.objects.get_or_create(title=self.title)

        return object
