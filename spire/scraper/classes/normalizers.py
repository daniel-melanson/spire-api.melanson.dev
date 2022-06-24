from spire.scraper.classes.shared import re_override_factory

COURSE_CREDIT_NORMALIZER = re_override_factory(
    (r"\d+", "$0.00"),
    (r"^(\d+) - (\d+)$", "$1.00 - $2.00"),
    (r"^(\d+\.\d) - (\d+\.\d)$", "$10 - $20"),
    (r"^\d+\.\d$", "$00"),
)

NONE_STRING_TO_NONE_NORMALIZER = re_override_factory((r"^(None|\(None\))$", None))

SPLIT_NEWLINE = lambda x: [s.strip() for s in x.split("\n")]

STRIP_STR = lambda x: x.strip()

EMPTY_TO_NONE = lambda x: None if len(x) == 0 else x
