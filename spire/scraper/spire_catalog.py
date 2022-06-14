import logging
import numbers
from typing import Optional

from django.utils import timezone
from selenium.webdriver.common.by import By

from spire.models import Course, Subject
from spire.scraper import SpireDriver
from spire.scraper.normalizers.SpireCourse import SpireCourse
from spire.scraper.normalizers.SpireSubject import SpireSubject
from spire.scraper.shared import assert_dict_keys_subset, assert_match, scrape_spire_tables, skip_until
from spire.scraper.VersionedCache import VersionedCache

log = logging.getLogger(__name__)


def _scrape_course_page(driver: SpireDriver) -> SpireCourse:
    title_element = driver.wait_for_presence(By.ID, "DERIVED_CRSECAT_DESCR200")

    raw_title = title_element.text

    title_match = assert_match(
        r"(?P<subject>\S+)\s+(?P<number>\S+)\s+-\s+(?P<title>.+)",
        raw_title,
    )

    tables = scrape_spire_tables(driver, "table.PSGROUPBOXNBO")

    assert "Course Detail" in tables
    assert_dict_keys_subset(tables, ["Course Detail", "Description", "Enrollment Information"])

    return SpireCourse(
        subject=title_match.group("subject"),
        number=title_match.group("number"),
        title=title_match.group("title"),
        details=tables["Course Detail"],
        description=tables["Description"] if "Description" in tables else None,
        enrollment_information=tables["Enrollment Information"]
        if "Enrollment Information" in tables
        else None,
    )


def _scrape_subject_list(driver: SpireDriver, cache: VersionedCache, subject: Subject):
    course_link_ids = skip_until(driver.find_all_ids("a[id^=CRSE_NBR]"), cache, "course_link_id")

    # For each course in the subject
    for link_id in course_link_ids:
        log.debug("Following next course link...")
        driver.click(link_id)
        log.debug("Arrived at course page.")

        scraped_course = _scrape_course_page(driver)
        assert scraped_course.subject == subject

        log.info("Scraped course: %s", scraped_course)

        course, created = Course.objects.update_or_create(
            course_id=scraped_course.course_id,
            defaults=scraped_course.as_model_default(True),
        )

        log.info("%s course: %s", "Created" if created else "Updated", course)

        cache.push("course_link_id", link_id)

        log.debug("Returning to course catalog...")
        driver.click("DERIVED_SAA_CRS_RETURN_PB")
        log.debug("Returned.")


def scrape_catalog(driver: SpireDriver, cache: VersionedCache):
    log.info("Scraping course catalog...")

    driver.navigate_to("catalog")

    if not cache.is_empty:
        log.info("Scraping course catalog with cache: %s", cache)

    # For each uppercase letter; start at 65 (A) or cached value
    for ascii_code in range(cache.get("subject_group_ascii", ord("A")), ord("Z") + 1):
        letter = chr(ascii_code)
        if letter in ("Q", "V", "X", "Z"):
            continue

        log.info("Scraping subject letter group: %s", letter)
        cache.push("subject_group_ascii", ascii_code)

        # Click letters grouping
        driver.click(f"DERIVED_SSS_BCC_SSR_ALPHANUM_{letter}")

        # Skip all subjects that were already successfully scraped
        subject_link_ids = skip_until(
            driver.find_all_ids("a[id^=DERIVED_SSS_BCC_GROUP_BOX_]"), cache, "subject_link_id"
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
                subject_id=subject_match.group("id"),
                title=subject_match.group("title"),
            )

            log.debug("Initialized scraped subject: %s", scraped_subject)

            if scraped_subject.subject_id in ("LLEIP"):
                """
                Spire Documents LLIEP and LLEIP, both with the same title "LL: Intensive English Program
                At the time of writing, neither even had documented courses, so I kept LLIEP because it
                was the correct acronym and I didn't want to drop the unique key constraint on Subject.title
                """
                continue

            # Push results to database
            subject, created = Subject.objects.update_or_create(
                subject_id=scraped_subject.subject_id, defaults=scraped_subject.as_model_default()
            )

            log.info("%s new subject: %s", "Created" if created else "Updated", subject)

            # Expand subject list
            driver.click(subject_link_id)

            _scrape_subject_list(driver, cache, subject)

            # Cache the subject; as it successfully fully scraped
            cache.push("subject_link_id", subject_link_id)

            # Collapse subject list
            driver.click(subject_link_id)

    log.info("Scraped course catalog.")
