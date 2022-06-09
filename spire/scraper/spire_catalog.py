import logging
from turtle import title
from typing import NamedTuple, Optional

from selenium.webdriver.common.by import By

from spire.models import Course, Subject
from spire.regexp import COURSE_ID_NUM_REGEXP, COURSE_TITLE_REGEXP, SUBJECT_ID_REGEXP, SUBJECT_TITLE_REGEXP
from spire.scraper import SpireDriver
from spire.scraper.shared import assert_match, scrape_spire_tables

log = logging.getLogger(__name__)

SUBJECT_OVERRIDES = {
    "BMED-ENG": ("BME", "Biomedical Engineering"),
    "CE-ENGIN": ("CEE", "Civil and Environmental Engineering"),
    "CHEM-ENG": ("CHE", "Chemical Engineering"),
    "EC-ENG": ("ECE", "Electrical & Computer Engineering"),
    "HM&FN": ("HFA", "Humanities and Fine Arts"),
    "HT-MGT": ("HTM", "Hospitality & Tourism Management"),
    "MI-ENG": ("MIE", "Mechanical & Industrial Engineering"),
    "NEUROS&B": ("NSB", "Neuroscience & Behavior"),
    "ORG&EVBI": ("OEB", "Organismic & Evolutionary Biology"),
}


class SpireSubject:
    id: str
    title: str

    def __init__(self, id=None, title=None) -> None:
        assert id is not None and title is not None

        if id in SUBJECT_OVERRIDES:
            override = SUBJECT_OVERRIDES[id]
            self.id = override[0]
            self.title = override[1]
        else:
            self.id = id
            self.title = title

        assert_match(SUBJECT_ID_REGEXP, self.id)
        assert_match(SUBJECT_TITLE_REGEXP, self.title)


class SpireCourse(NamedTuple):
    id: str
    subject: str
    number: str
    title: str
    details: dict[str, str]
    enrollment_information: Optional[dict[str, str]]
    description: Optional[str]


def scrape_course_page(driver: SpireDriver) -> SpireCourse:
    title_element = driver.wait_for_presence(By.ID, "DERIVED_CRSECAT_DESCR200")

    raw_title = title_element.text

    title_match = assert_match(
        SUBJECT_ID_REGEXP + r"\s+" + COURSE_ID_NUM_REGEXP + r"\s+-\s+" + COURSE_TITLE_REGEXP,
        raw_title,
    )

    tables = scrape_spire_tables(driver, "table.PSGROUPBOXNBO")

    assert "Course Detail" in tables

    number = title_match.group("number").upper()
    subject = title_match.group("subject").upper()

    return SpireCourse(
        id=f"{subject} {number}",
        subject=subject,
        number=number,
        title=title_match.group("title"),
        details=tables["Course Detail"],
        description=tables["Description"] if "Description" in tables else None,
        enrollment_information=tables["Enrollment Information"]
        if "Enrollment Information" in tables
        else None,
    )


def scrape_catalog(driver: SpireDriver):
    log.info("Scraping course catalog...")

    driver.navigate_to("catalog")

    # For each uppercase letter
    for ascii_code in range(65, 90):
        letter = chr(ascii_code)
        if letter in ("Q", "V", "X", "Z"):
            continue

        # Click letters grouping
        driver.click(f"DERIVED_SSS_BCC_SSR_ALPHANUM_{letter}")

        # For each subject in group
        for subject_link_id in driver.find_all_ids("a[id^=DERIVED_SSS_BCC_GROUP_BOX_]"):
            subject_link = driver.find(subject_link_id)
            assert subject_link

            subject_title = subject_link.text

            subject_match = assert_match(r"(?P<id>\S+) - (?P<title>.+)", subject_title)

            scraped_subject = SpireSubject(
                id=subject_match.group("id").upper(),
                title=subject_match.group("title"),
            )

            log.debug("Initialized scraped subject: %s.", scraped_subject)

            subject, created = Subject.objects.update_or_create(
                id=scraped_subject.id, title=scraped_subject.title
            )

            if created:
                log.info("Created new subject: %s", subject)

            log.debug("Scraping subject: %s...", subject.title)

            log.debug("Expanding subject list...")
            subject_link.click()
            driver.wait_for_spire()
            log.debug("Expanded subject list.")

            # For each course in subject
            for link_id in driver.find_all_ids("a[id^=CRSE_NBR]"):
                log.debug("Following next course link...")
                driver.click(link_id)

                course = scrape_course_page(driver)

                if course["subject"] != subject["id"]:
                    log.warning("Mismatched course subjects: %s != %s.", course["subject"], subject["id"])

                log.info("Scraped course: %s.", course)

                log.debug("Scraped course, returning...")
                driver.click("DERIVED_SAA_CRS_RETURN_PB")
                log.debug("Returned.")

            log.info("Scraped subject: %s.", subject)
            log.debug("Collapsing subject...")
            driver.click(subject_link_id)
            log.debug("Subject collapsed.")

    log.info("Scraped course catalog.")
