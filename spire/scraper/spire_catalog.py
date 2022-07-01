import logging

from selenium.webdriver.common.by import By

from spire.models import Subject
from spire.scraper.timer import Timer

from .classes import RawCourse, RawSubject
from .shared import assert_match, scrape_spire_tables
from .spire_driver import SpireDriver
from .versioned_cache import VersionedCache

log = logging.getLogger(__name__)


def _scrape_course_page(driver: SpireDriver, subject: Subject) -> RawCourse:
    title_element = driver.wait_for_presence(By.ID, "DERIVED_CRSECAT_DESCR200")

    raw_title = title_element.text

    title_match = assert_match(
        r"(?P<subject>\S+)\s+(?P<number>\S+)\s+-\s+(?P<title>.+)",
        raw_title,
    )

    tables = scrape_spire_tables(driver, "table.PSGROUPBOXNBO")

    return RawCourse(
        subject=subject,
        number=title_match.group("number"),
        title=title_match.group("title"),
        details=tables["Course Detail"],
        description=tables.get("Description", None),
        enrollment_information=tables.get("Enrollment Information", None),
    )


def _scrape_subject_list(driver: SpireDriver, cache: VersionedCache, subject: Subject):
    log.info("Scraping subject list for: %s", subject)
    subject_timer = Timer()

    # For each course in the subject list
    for link_id in cache.skip_once(driver.find_all_ids("a[id^=CRSE_NBR]"), "course_link_id"):
        log.debug("Clicking course page link: %s...", link_id)
        driver.click(link_id)
        log.debug("Arrived at course page.")

        scraped_course = _scrape_course_page(driver, subject)

        log.info("Scraped course:\n%s", scraped_course)

        cache.push("course_link_id", link_id)

        log.debug("Returning to course catalog...")
        driver.click("DERIVED_SAA_CRS_RETURN_PB", wait=False)
        scraped_course.push()

        driver.wait_for_spire()
        log.debug("Returned to course catalog.")

    log.info("Scraped subject list for %s in %s", subject, subject_timer)


def scrape_catalog(driver: SpireDriver, cache: VersionedCache):
    log.info("Scraping course catalog...")

    driver.navigate_to("catalog")

    scraped_subject_id_set = set()

    # For each uppercase letter; start at 65 (A) or cached value
    total_timer = Timer()
    for ascii_code in range(cache.get("subject_group_ascii", ord("A")), ord("Z") + 1):
        letter = chr(ascii_code)
        if letter in ("Q", "V", "X", "Z"):
            continue

        log.info("Scraping subject letter group: %s", letter)
        cache.push("subject_group_ascii", ascii_code)

        subject_group_timer = Timer()

        # Click letters grouping
        driver.click(f"DERIVED_SSS_BCC_SSR_ALPHANUM_{letter}")

        # For each subject in group
        for subject_link_id in cache.skip_once(
            driver.find_all_ids("a[id^=DERIVED_SSS_BCC_GROUP_BOX_]"),
            "subject_link_id",
        ):
            # Get link
            subject_link = driver.find(subject_link_id)
            assert subject_link

            # Match title
            subject_title = subject_link.text
            subject_match = assert_match(r"(?P<id>\S+)\s+-\s+(?P<title>.+)", subject_title)
            scraped_subject = RawSubject(
                id=subject_match.group("id"),
                title=subject_match.group("title"),
            )

            log.debug("Initialized scraped subject: %s", scraped_subject)

            if scraped_subject.id in ("LLEIP"):
                # Spire Documents LLIEP and LLEIP, both with the same title "LL: Intensive English Program
                # At the time of writing, neither even had documented courses, so I kept LLIEP because it
                # was the correct acronym and I didn't want to drop the unique key constraint on Subject.title
                continue

            scraped_subject_id_set.add(scraped_subject.id)

            # Expand subject list
            driver.click(subject_link_id, wait=False)

            # Push results to database
            subject = scraped_subject.push()

            # Wait for spire to expand the list
            driver.wait_for_spire()

            _scrape_subject_list(driver, cache, subject)

            # Cache the subject; as it successfully fully scraped
            cache.push("subject_link_id", subject_link_id)

            # Collapse subject list
            driver.click(subject_link_id)

        log.info("Scraped subject letter group %s in %s", letter, subject_group_timer)

    dropped, _ = Subject.objects.exclude(id__in=scraped_subject_id_set).delete()
    log.info("Dropped %s subjects that are no longer listed on spire.", dropped)

    log.info("Scraped course catalog in %s", total_timer)
