from spire.scraper.classes.shared import RawField, RawObject, key_override_factory

DETAIL_KEYS = [
    "Career",
    "Units",
    "Grading Basis",
    "Course Components",
    "Academic Group",
    "Academic Organization",
    "Campus",
]

DETAIL_OVERRIDES = {
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


class ScrapedCourseDetail(RawObject):
    def __init__(self, table: dict[str, str]) -> None:
        super().__init__("SpireCourseDetail")
