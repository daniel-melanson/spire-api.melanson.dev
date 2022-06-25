import logging
from curses.ascii import isspace
from datetime import datetime
from os import link

from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from spire.models import Section, SectionCoverage
from spire.patterns import TERM_REGEXP
from spire.scraper.classes.raw_course import RawCourse
from spire.scraper.classes.raw_meeting_information import RawInstructor
from spire.scraper.classes.raw_section import RawSection
from spire.scraper.timer import Timer

from .shared import assert_match, scrape_spire_tables
from .spire_driver import SpireDriver
from .versioned_cache import VersionedCache

log = logging.getLogger(__name__)


def _count_name_characters(s: str):
    count = 0
    for c in s:
        if not isspace(c) and c != ",":
            count += 1

    return count


def _scrape_meeting_instructor_list(sections_table, link_id):
    log.debug("Scraping meeting instructors...")
    link_number = link_id[len("DERIVED_CLSRCH_SSR_CLASSNAME_LONG$") :]
    meeting_information_table = sections_table.find_element(By.ID, "SSR_CLSRCH_MTG1$scroll$" + link_number)

    meeting_instructor_list = []

    for meeting_row in meeting_information_table.find_elements(By.CSS_SELECTOR, "tr[id^=trSSR_CLSRCH_MTG]"):
        instructor_column = meeting_row.find_element(By.CSS_SELECTOR, "div[id^=win0divUM_DERIVED_SR_UM_HTML1")

        raw_instructor_text = instructor_column.text.strip()
        while "\n\n" in raw_instructor_text or "  " in raw_instructor_text:
            raw_instructor_text = raw_instructor_text.replace("\n\n", "\n").replace("  ", " ")

        log.debug("Scraping raw staff from %s", raw_instructor_text)

        instructor_list = []
        if len(raw_instructor_text) == 0 or raw_instructor_text in ("Staff", "TBD"):
            instructor_list.append(RawInstructor(name="Staff"))
        else:
            links = instructor_column.find_elements(By.CSS_SELECTOR, "a[href^='mailto:']")
            if len(links) > 0:
                log.debug("Email links found, scraping those...")
                for email_link in links:
                    href = email_link.get_property("href")
                    staff_name = email_link.text
                    staff_email = href[len("mailto:") :]
                    instructor_list.append(RawInstructor(name=staff_name, email=staff_email))
            else:
                log.debug("No emails found. Scraping from raw text.")
                for name in raw_instructor_text.split("\n"):
                    instructor_list.append(RawInstructor(name=name, email=None))

            scraped_names = ", ".join(map(lambda x: x.name, instructor_list))
            log.debug("Comparing name characters between '%s' and '%s'", scraped_names, raw_instructor_text)

            assert (
                abs(_count_name_characters(scraped_names) - _count_name_characters(raw_instructor_text)) < 2
            )

        meeting_instructor_list.append(instructor_list)

    log.debug("Scraped meeting instructors: %s", meeting_instructor_list)
    return meeting_instructor_list


def _scrape_search_results(driver: SpireDriver, term: str):
    section_count = 0

    for span_id in driver.find_all_ids("span[id^=DERIVED_CLSRCH_DESCR200]"):
        span = driver.find(span_id)

        title_match = assert_match(
            r"(?P<subject_id>\S+)\s+(?P<course_number>\S+)\s+(?P<course_title>.+)",
            span.text,
        )
        course_id, subject, _ = RawCourse.get_course_id(
            title_match.group("subject_id"), title_match.group("course_number")
        )

        log.debug("Scraping sections for course: %s", course_id)

        scraped_section_ids_for_course = set()

        section_table_id = "ACE_DERIVED_CLSRCH_GROUPBOX1$133$" + span_id[len("DERIVED_CLSRCH_DESCR200") :]
        sections_table = driver.find(section_table_id)
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

            log.debug("Scraping section %s...", section_id)

            meeting_instructor_list = _scrape_meeting_instructor_list(driver.find(section_table_id), link_id)
            log.debug("Scraped meeting instructor list: %s", meeting_instructor_list)

            log.info("Navigating to section page for %s section %s...", course_id, section_id)
            driver.click(link_id)

            table_results = scrape_spire_tables(driver, "table.PSGROUPBOXWBO")
            meeting_info_list = []
            for row in driver.find_all("tr[id^='trSSR_CLSRCH_MTG$0_row']"):
                meeting_info_list.append(
                    {
                        "days_and_times": row.find_element(By.CSS_SELECTOR, "span[id^=MTG_SCHED]").text,
                        "instructors": meeting_instructor_list.pop(),
                        "room": row.find_element(By.CSS_SELECTOR, "span[id^=MTG_LOC]").text,
                        "meeting_dates": row.find_element(By.CSS_SELECTOR, "span[id^=MTG_DATE]").text,
                    }
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
            scraped_section_ids_for_course.add(section.id)

            section_count += 1

            log.info("Clicking return then pushing...")
            driver.click("CLASS_SRCH_WRK2_SSR_PB_BACK", wait=False)

            section.push()

            driver.wait_for_spire()
            log.info("Returned to search results for %s durning %s.", subject, term)

        dropped, _ = (
            Section.objects.filter(course_id=course_id, term=term)
            .exclude(id__in=scraped_section_ids_for_course)
            .delete()
        )
        log.info("Dropped %s %s sections for course %s that are no longer listed.", dropped, term, course_id)

    return section_count


def _initialize_query(driver: SpireDriver, flipped_term: str, subject: str):
    log.debug("Setting-up a search query for %s during %s...", subject, flipped_term)
    term_select = driver.wait_for_interaction(By.ID, "UM_DERIVED_SA_UM_TERM_DESCR")
    driver.scroll_to(term_select)
    term_select = Select(term_select)
    term_select.select_by_visible_text(flipped_term)
    driver.wait_for_spire()

    subject_select = driver.wait_for_interaction(By.ID, "CLASS_SRCH_WRK2_SUBJECT$108$")
    driver.scroll_to(subject_select)
    subject_select = Select(subject_select)
    subject_select.select_by_visible_text(subject)
    driver.wait_for_spire()

    number_select = Select(driver.find("CLASS_SRCH_WRK2_SSR_EXACT_MATCH1"))
    number_select.select_by_visible_text("greater than or equal to")
    driver.wait_for_spire()

    number_input = driver.find("CLASS_SRCH_WRK2_CATALOG_NBR$8$")
    number_input.clear()
    number_input.send_keys("0")
    driver.wait_for_spire()

    open_input = driver.find("CLASS_SRCH_WRK2_SSR_OPEN_ONLY")
    if open_input.is_selected():
        open_input.click()
        driver.wait_for_spire()


def scrape_sections(driver: SpireDriver, cache: VersionedCache):
    log.info("Scraping sections...")

    driver.navigate_to("search")

    total_timer = Timer()
    scraped_terms = 0

    def get_option_values(select):
        return [
            e.text
            for e in select.find_elements(By.CSS_SELECTOR, "option")
            if len(e.get_property("value")) > 0
        ]

    # Fetch subject option values
    subject_select = driver.wait_for_interaction(By.ID, "CLASS_SRCH_WRK2_SUBJECT\$108\$")
    assert subject_select
    subject_values = get_option_values(subject_select)

    # Fetch term option values
    term_select = driver.wait_for_interaction(By.ID, "UM_DERIVED_SA_UM_TERM_DESCR")
    assert term_select
    term_values = get_option_values(term_select)

    # For each term, 5 academic years from the most recently posted year
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
                    end_date = datetime(year=year + 1, month=1, day=1)
                case "Winter":
                    end_date = datetime(year=year + 1, month=2, day=15)
                case "Spring":
                    end_date = datetime(year=year, month=6, day=1)
                case "Summer":
                    end_date = datetime(year=year, month=9, day=15)

            if timezone.make_aware(end_date) < timezone.now():
                log.info("Skipping the %s term, as information is static.", term)
                continue

        log.info("Scraping sections during %s...", term)
        term_timer = Timer()

        # For each subject
        for subject in cache.skip_once(subject_values, "subject"):
            cache.push("subject", subject)
            subject_timer = Timer()

            # Initialize and search for subject during term
            _initialize_query(driver, flipped_term, subject)

            log.info("Searching for sections in subject %s during %s...", subject, term)
            driver.click("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")

            return_button = driver.find("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")

            # return button -> search results
            if return_button:
                count = _scrape_search_results(driver, term)

                log.info(
                    "Scraped %s %s sections during %s in %s. Returning...",
                    count,
                    subject,
                    term,
                    subject_timer,
                )
                driver.click("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")
            else:
                log.info("No return button found. Assuming no results found.")

                warning = driver.find("win0divDERIVED_CLSMSG_GROUP2")
                if warning:
                    log.warn("Warning found: %s", warning.text)
                else:
                    log.warn("No warning found.")

        coverage.completed = True
        coverage.end_time = timezone.now()
        coverage.save()

        log.info("Scraped sections for the %s term in %s.", term, term_timer)

    log.info("Scraped %s terms in %s.", scraped_terms, total_timer)
