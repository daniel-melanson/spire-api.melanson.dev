import logging
from logging import DEBUG
from typing import Optional, TypedDict

from selenium.webdriver.common.by import By

from scraper import SpireDriver
from scraper.shared import assert_match, scrape_spire_tables

log = logging.getLogger(__name__)
log.setLevel(DEBUG)


class SpireSubject(TypedDict):
    id: str
    name: str
    courses: list[str]


class SpireCourse(TypedDict):
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
        r"((?P<subject>[A-Za-z\-&]{2,20})\s+(?P<number>[\w\d\-]{2,50}))\s+-\s+(?P<title>.{3,100})",
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
        enrollment_information=tables["Enrollment Information"] if "Enrollment Information" in tables else None,
    )


def scrape_catalog(driver: SpireDriver):
    log.info("Scraping course catalog...")

    driver.navigate_to("catalog")

    subjects = []
    courses = []

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

            subject_match = assert_match(r"(?P<id>[A-Z\-&]{3,20}) - (?P<name>[A-Za-z\- :]{3,100})", subject_title)

            subject = SpireSubject(
                id=subject_match.group("id").upper(),
                name=subject_match.group("name"),
                courses=[],
            )

            log.debug("Initialized subject: %s.", subject)
            log.debug("Scraping subject: %s...", subject["name"])

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
                subject["courses"].append(course["id"])
                courses.append(course)

                log.debug("Scraped course, returning...")
                driver.click("DERIVED_SAA_CRS_RETURN_PB")
                log.debug("Returned.")

            log.info("Scraped subject: %s.", subject)
            subjects.append(subject)
            log.debug("Collapsing subject...")
            driver.click(subject_link_id)
            log.debug("Subject collapsed.")

    log.info("Scraped course catalog.")
    return (subjects, courses)
