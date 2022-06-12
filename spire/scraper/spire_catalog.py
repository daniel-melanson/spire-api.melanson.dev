import logging
from typing import Optional

from django.utils import timezone
from selenium.webdriver.common.by import By

from spire.models import Course, Subject
from spire.regexp import (
    COURSE_ID_NUM_REGEXP,
    COURSE_ID_REGEXP,
    COURSE_TITLE_REGEXP,
    SUBJECT_ID_REGEXP,
    SUBJECT_TITLE_REGEXP,
)
from spire.scraper import SpireDriver
from spire.scraper.ScrapeMemento import ScrapeMemento
from spire.scraper.shared import (
    assert_dict_keys_subset,
    assert_match,
    key_normalizer_factory,
    scrape_spire_tables,
)

log = logging.getLogger(__name__)


SUBJECT_NORMALIZER = key_normalizer_factory(
    {
        "BMED-ENG": ("BME", "Biomedical Engineering"),
        "CE-ENGIN": ("CEE", "Civil and Environmental Engineering"),
        "CHEM-ENG": ("CHE", "Chemical Engineering"),
        ("EC-ENG", "E&C-ENG"): ("ECE", "Electrical & Computer Engineering"),
        ("HM&FN", "HMFNART"): ("HFA", "Humanities and Fine Arts"),
        "HT-MGT": ("HTM", "Hospitality & Tourism Management"),
        ("MI-ENG", "M&I-ENG"): ("MIE", "Mechanical & Industrial Engineering"),
        ("NEUROS&B", "NEUROSB"): ("NSB", "Neuroscience & Behavior"),
        ("ORG&EVBI", "ORGEVBI"): ("OEB", "Organismic & Evolutionary Biology"),
    }
)


class SpireSubject:
    subject_id: str
    title: str

    def __init__(self, subject_id: str, title: str) -> None:
        if (override := SUBJECT_NORMALIZER(subject_id)) != subject_id:
            self.subject_id = override[0]
            self.title = override[1]
        else:
            self.subject_id = subject_id
            self.title = title

        assert_match(SUBJECT_ID_REGEXP, self.subject_id)
        assert_match(SUBJECT_TITLE_REGEXP, self.title)


DETAIL_NORMALIZERS = {
    "Academic Group": key_normalizer_factory(
        {
            "College of Humanities&Fine Art": "College of Humanities & Fine Art",
            "Stockbridge School": "Stockbridge School of Agriculture",
            "College of Social & Behav. Sci": "College of Social & Behavioral Sciences",
        }
    ),
    "Academic Organization": key_normalizer_factory(
        {
            "Bldg &Construction Technology": "Building & Construction Technology",
            "Civil & Environmental Engin.": "Civil & Environmental Engineering",
            "College of Info & Computer Sci": "Manning College of Information & Computer Sciences",
        }
    ),
    "Grading Basis": key_normalizer_factory(
        {"Grad Ltr Grading, with options": "Graduate Letter Grading, with options"}
    ),
}


DETAIL_KEYS = [
    "Career",
    "Units",
    "Grading Basis",
    "Course Components",
    "Academic Group",
    "Academic Organization",
    "Campus",
]


class SpireCourse:
    course_id: str
    subject: str
    number: str
    title: str
    details: dict[str, str]
    enrollment_information: Optional[dict[str, str]]
    description: Optional[str]

    def __init__(
        self,
        course_id: str,
        subject: str,
        number: str,
        title: str,
        details: dict[str, str],
        enrollment_information: Optional[dict[str, str]],
        description: Optional[str],
    ):
        if (override := SUBJECT_NORMALIZER(subject)) != subject:
            subject = override[0]
            course_id = f"{subject} {number}"

        assert_match(COURSE_ID_REGEXP, course_id)
        self.course_id = course_id

        assert_match(SUBJECT_ID_REGEXP, subject)
        self.subject = subject

        assert_match(COURSE_ID_NUM_REGEXP, number)
        self.number = number

        assert_match(COURSE_TITLE_REGEXP, title)
        self.title = title

        assert_dict_keys_subset(
            details,
            DETAIL_KEYS,
        )

        for key in DETAIL_KEYS:
            if key in details:
                if key in DETAIL_NORMALIZERS:
                    x = DETAIL_NORMALIZERS[key](details[key])
                    details[key] = x
                else:
                    x = details[key]

        self.details = details

        self.enrollment_information = enrollment_information

        self.description = description

    def __str__(self):
        return (
            "SpireCourse("
            + str(
                {
                    "course_id": self.course_id,
                    "subject": self.subject,
                    "number": self.number,
                    "title": self.title,
                    "details": str(self.details),
                    "enrollment_information": str(self.enrollment_information),
                    "description": str(self.description),
                }
            )
            + ")"
        )


def _scrape_course_page(driver: SpireDriver) -> SpireCourse:
    title_element = driver.wait_for_presence(By.ID, "DERIVED_CRSECAT_DESCR200")

    raw_title = title_element.text

    title_match = assert_match(
        r"(?P<subject>\S+)\s+(?P<number>\S+) - (?P<title>.+)",
        raw_title,
    )

    tables = scrape_spire_tables(driver, "table.PSGROUPBOXNBO")

    assert "Course Detail" in tables
    assert_dict_keys_subset(tables, ["Course Detail", "Description", "Enrollment Information"])

    number = title_match.group("number").upper()
    subject = title_match.group("subject").upper()

    return SpireCourse(
        course_id=f"{subject} {number}",
        subject=subject,
        number=number,
        title=title_match.group("title"),
        details=tables["Course Detail"],
        description=tables["Description"] if "Description" in tables else None,
        enrollment_information=tables["Enrollment Information"]
        if "Enrollment Information" in tables
        else None,
    )


def _scrape_subject_list(driver: SpireDriver, memento: ScrapeMemento, subject: Subject):
    course_link_ids = memento.skip_until(driver.find_all_ids("a[id^=CRSE_NBR]"), "course_link_id")

    # For each course in the subject
    for link_id in course_link_ids:
        log.debug("Following next course link...")
        driver.click(link_id)
        log.debug("Arrived at course page.")

        scraped_course = _scrape_course_page(driver)
        assert scraped_course.subject == subject.subject_id

        log.info("Scraped course: %s", scraped_course)

        course, created = Course.objects.update_or_create(
            course_id=scraped_course.course_id,
            defaults={
                "subject": subject,
                "number": scraped_course.number,
                "title": scraped_course.title,
                "description": scraped_course.description,
                "details": scraped_course.details,
                "enrollment_information": scraped_course.enrollment_information,
                "_updated_at": timezone.now(),
            },
        )

        log.info("%s course: %s", "Created" if created else "Updated", course)

        memento.push("course_link_id", link_id)

        log.debug("Returning to course catalog...")
        driver.click("DERIVED_SAA_CRS_RETURN_PB")
        log.debug("Returned.")


def scrape_catalog(driver: SpireDriver, memento: ScrapeMemento):
    log.info("Scraping course catalog...")

    driver.navigate_to("catalog")

    if not memento.is_empty:
        log.info("Scraping course catalog with memento: %s", memento)

    # For each uppercase letter; start at 65 (A) or cached value
    for ascii_code in range(memento.get("subject_group_ascii", 65), 90):
        letter = chr(ascii_code)
        if letter in ("Q", "V", "X", "Z"):
            continue

        log.info("Scraping subject letter group: %s", letter)

        # Click letters grouping
        driver.click(f"DERIVED_SSS_BCC_SSR_ALPHANUM_{letter}")

        # Skip all subjects that were already successfully scraped
        subject_link_ids = memento.skip_until(
            driver.find_all_ids("a[id^=DERIVED_SSS_BCC_GROUP_BOX_]"), "subject_link_id"
        )

        # For each subject in group
        for subject_link_id in subject_link_ids:
            # Get link
            subject_link = driver.find(subject_link_id)
            assert subject_link

            # Match title
            subject_title = subject_link.text
            subject_match = assert_match(r"(?P<id>\S+) - (?P<title>.+)", subject_title)
            scraped_subject = SpireSubject(
                subject_id=subject_match.group("id").upper(),
                title=subject_match.group("title"),
            )

            log.debug("Initialized scraped subject: %s", scraped_subject)

            # Push results to database
            subject, created = Subject.objects.update_or_create(
                subject_id=scraped_subject.subject_id, defaults={"title": scraped_subject.title}
            )

            log.info("%s new subject: %s", "Created" if created else "Updated", subject)

            # Expand subject list
            driver.click(subject_link_id)

            _scrape_subject_list(driver, memento, subject)

            # Cache the subject; as it successfully fully scraped
            memento.push("subject_link_id", subject_link_id)

            # Collapse subject list
            driver.click(subject_link_id)

    log.info("Scraped course catalog.")
