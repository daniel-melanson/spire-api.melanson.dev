_VALID_TEXT = r"[\x00-\x7F]"

SUBJECT_ID_REGEXP = r"(?P<subject_id>[A-Z\-@]{2,9}[A-Z])"
SUBJECT_TITLE_REGEXP = r"(?P<subject_title>[\x00-\x7F]{3,99})"

COURSE_ID_NUM_REGEXP = r"(?P<course_number>.{1,9}[A-Za-z0-9])".replace(".", _VALID_TEXT)
COURSE_ID_REGEXP = SUBJECT_ID_REGEXP + r" " + COURSE_ID_NUM_REGEXP

COURSE_TITLE_REGEXP = r"(?P<course_title>.{3,256})".replace(".", _VALID_TEXT)

SECTION_ID_REGEXP = r"(?P<section_id>(\d{2,4})?([A-Z]{1,4})?-[A-Z]{1,4}\(\d{3,10}\))"

TERM_REGEXP = r"(Spring|Summer|Winter|Fall) (20\d{2})"

_COMPONENTS = r"(Lecture|Practicum|Discussion|Laboratory)"
COURSE_DETAIL_COMPONENT_REGEXP = f"({_COMPONENTS}, )" + r"{0,4}" + _COMPONENTS
