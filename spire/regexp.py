SUBJECT_ID_REGEXP = r"(?P<subject_id>[A-Z\-]{2,9}[A-Z])"
SUBJECT_TITLE_REGEXP = r"(?P<subject_title>[A-Za-z\- :&]{2,99}[a-z])"

COURSE_ID_NUM_REGEXP = r"(?P<course_number>[A-Za-z0-9\-]{1,9}[A-Za-z0-9])"
COURSE_ID_REGEXP = SUBJECT_ID_REGEXP + r" " + COURSE_ID_NUM_REGEXP

COURSE_TITLE_REGEXP = r"(?P<course_title>.{3,256})"
