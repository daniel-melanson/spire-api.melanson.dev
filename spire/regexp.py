SUBJECT_ID_REGEXP = r"(?P<subject_id>[A-Z\-&]{3,20})"
SUBJECT_TITLE_REGEXP = r"(?P<subject_title>[A-Za-z\- :]{3,100})"

COURSE_ID_NUM_REGEXP = r"(?P<course_number>[\w\d\-]{2,50}))"
COURSE_ID_REGEXP = SUBJECT_ID_REGEXP + r" " + COURSE_ID_NUM_REGEXP

COURSE_TITLE_REGEXP = r"(?P<course_title>.{3,100})"
