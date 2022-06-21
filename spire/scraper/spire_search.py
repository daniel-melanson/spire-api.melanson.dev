import logging
import re

from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from spire.models import Section, SectionCoverage, Staff
from spire.patterns import TERM_REGEXP
from spire.scraper.classes.raw_course import RawCourse
from spire.scraper.classes.raw_section import RawMeetingInformation, RawSection, RawStaff
from spire.scraper.timer import Timer

from .shared import assert_match, scrape_spire_tables, skip_until
from .spire_driver import SpireDriver
from .versioned_cache import VersionedCache

log = logging.getLogger(__name__)


def _scrape_section_emails(driver: SpireDriver) -> dict[str, str]:
    log.debug("Scraping emails for course...")
    course_staff_emails = {}
    for a in sections_table.find_elements(By.CSS_SELECTOR, "a[href^=mailto\:]"):
        href = a.get_property("href")
        log.debug("Scraped href: %s", href)

    email = href[len("mailto:") :]

    if re.fullmatch(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        course_staff_emails[a.text] = email
    else:
        log.debug("Not an email, skipping: %s", email)

    log.debug("Scraped emails: %s.", course_staff_emails)


def _scrape_section_page(driver: SpireDriver, section_id, course_id, term):
    table_results = scrape_spire_tables(driver, "table.PSGROUPBOXWBO")

    meeting_info_list = []
    for row in driver.find_all("tr[id^='trSSR_CLSRCH_MTG$0_row'"):
        instructors = []
        for raw_name in row.find_element(By.CSS_SELECTOR, "span[id^=MTG_INSTR]").text.split("\\n"):
            name = raw_name[:-1] if raw_name.endswith(",") else raw_name

            instructors.append(RawStaff(name=name, email=course_staff_emails.get(name, None)))

        meeting_info_list.append(
            RawMeetingInformation(
                days_and_times=row.find_element(By.CSS_SELECTOR, "span[id^=MTG_SCHED]").text,
                instructors=instructors,
                room=row.find_element(By.CSS_SELECTOR, "span[id^=MTG_LOC]").text,
                meeting_dates=row.find_element(By.CSS_SELECTOR, "span[id^=MTG_DATE]").text,
            )
        )

    section = RawSection(
        course_id=course_id,
        term=term,
        id=section_id,
        details=table_results["Class Details"],
        meeting_information=meeting_info_list,
        restrictions=table_results.get("RESTRICTIONS & NOTES", None),
        availability=table_results["Class Availability"],
        description=table_results.get("Description", None),
        overview=table_results.get("Class Overview", None),
    )
    log.info("Scraped section: %s", section)

    section.push()


def _scrape_search_results(driver: SpireDriver, term: str):
    log.info("Scraping search results...")
    t = Timer()

    course_title_span_ids = driver.find_all_ids("span[id^=DERIVED_CLSRCH_DESCR200]")
    for span_id in course_title_span_ids:
        span = driver.find(span_id)

        title_match = assert_match(
            r"(?P<subject_id>\S+)\s+(?P<course_number>\S+)\s+(?P<course_title>.+)",
            span.text,
        )
        course_id, _, _ = RawCourse.get_course_id(
            title_match.group("subject_id"), title_match.group("course_number")
        )

        log.debug("Scraping sections for course: %s.", course_id)

        sections_table = driver.find(
            "ACE_DERIVED_CLSRCH_GROUPBOX1$133$" + span_id[len("DERIVED_CLSRCH_DESCR200") :]
        )
        assert sections_table

        link_ids = [
            e.get_property("id")
            for e in sections_table.find_elements(
                By.CSS_SELECTOR, "a[id^=DERIVED_CLSRCH_SSR_CLASSNAME_LONG\$]"
            )
        ]

        for link_id in link_ids:
            link = driver.find(link_id)
            section_id = link.text.strip()

            driver.click(link_id)

            _scrape_section_page(
                driver,
                section_id,
                term,
            )

            driver.click("CLASS_SRCH_WRK2_SSR_PB_BACK")

    t.end()
    log.info("Scraped search results in %s.", t)


def get_option_values(select):
    return [
        e.text for e in select.find_elements(By.CSS_SELECTOR, "option") if len(e.get_property("value")) > 0
    ]


def _initialize_query(driver: SpireDriver, flipped_term: str, subject: str):
    log.debug("Setting-up search query...")
    term_select = driver.wait_for_interaction(By.ID, "UM_DERIVED_SA_UM_TERM_DESCR")
    driver.scroll_to(term_select)
    term_select = Select(term_select)
    term_select.select_by_visible_text(flipped_term)

    subject_select = driver.wait_for_interaction(By.ID, "CLASS_SRCH_WRK2_SUBJECT$108$")
    driver.scroll_to(subject_select)
    subject_select = Select(subject_select)
    subject_select.select_by_visible_text(subject)

    number_select = Select(driver.find("CLASS_SRCH_WRK2_SSR_EXACT_MATCH1"))
    number_select.select_by_visible_text("greater than or equal to")

    number_input = driver.find("CLASS_SRCH_WRK2_CATALOG_NBR$8$")
    number_input.clear()
    number_input.send_keys("0")

    open_input = driver.find("CLASS_SRCH_WRK2_SSR_OPEN_ONLY")
    if open_input.is_selected():
        open_input.click()


def scrape_sections(driver: SpireDriver, cache: VersionedCache):
    log.info("Scraping sections...")

    driver.navigate_to("search")

    total_timer = Timer()

    # Fetch subject option values
    subject_select = driver.wait_for_interaction(By.ID, "CLASS_SRCH_WRK2_SUBJECT\$108\$")
    assert subject_select
    subject_values = get_option_values(subject_select)

    # Fetch term option values
    term_select = driver.wait_for_interaction(By.ID, "UM_DERIVED_SA_UM_TERM_DESCR")
    assert term_select
    term_values = get_option_values(term_select)

    has_skipped = False

    # For each term, 5 year from the most recently posted year
    for term_offset in range(cache.get("term_offset", 4 * 5 - 1), -1, -1):
        cache.push("term_offset", term_offset)

        flipped_term = term_values[term_offset]
        [year, season] = flipped_term.split(" ")
        term = f"{season} {year}"
        assert_match(TERM_REGEXP, term)

        # Establish coverage entry
        coverage, _ = SectionCoverage.objects.get_or_create(
            term=term, defaults={"completed": False, "start_time": timezone.now()}
        )

        if coverage.completed:
            year = int(year)
            match season:
                case "Fall":
                    end_date = timezone(year=year + 1, month=1, day=1)
                case "Winter":
                    end_date = timezone(year=year + 1, month=2, day=15)
                case "Spring":
                    end_date = timezone(year=year, month=6, day=1)
                case "Summer":
                    end_date = timezone(year=year, month=9, day=15)

            if end_date < timezone.now():
                log.info("Skipping the %s semester, as information is static.", term)
                continue

        log.info("Searching for sections during the term: %s", term)
        # For each subject
        for subject in subject_values if has_skipped else skip_until(subject_values, cache, "subject"):
            has_skipped = True
            cache.push("subject", subject)

            # Initialize and search for subject during term
            log.info("Searching for sections in subject %s during %s", subject, term)
            _initialize_query(driver, flipped_term, subject)
            log.info("Submitting query...")
            driver.click("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")

            return_button = driver.find("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")

            # return button -> search results
            if return_button:
                _scrape_search_results(driver, term)

                log.debug("Returning...")
                driver.click("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")
            else:
                log.info("No search results found, skipping...")

        coverage.completed = True
        coverage.end_time = timezone.now()
        coverage.save()

    total_timer.end()
    log.info("Scraped sections in %s.", total_timer)
