import logging
from curses.ascii import isspace
from datetime import datetime

from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from spire.models import (
    Course,
    CourseOffering,
    Section,
    SectionCombinedAvailability,
    SectionCoverage,
    Subject,
)
from spire.patterns import TERM_REGEXP
from spire.scraper.classes.normalizers import REPLACE_DOUBLE_SPACE
from spire.scraper.classes.raw_course import RawCourse
from spire.scraper.classes.raw_meeting_information import RawInstructor
from spire.scraper.classes.raw_section import RawSection
from spire.scraper.classes.raw_subject import RawSubject
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


def _scrape_meeting_instructor_list(sections_table, link_number):
    log.debug("Scraping meeting instructors...")
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
            found_names = set()

            for email_link in instructor_column.find_elements(By.CSS_SELECTOR, "a[href^='mailto:']"):
                href = email_link.get_property("href")
                staff_name = email_link.text.strip()
                if staff_name.endswith(","):
                    staff_name = staff_name[:-1]

                staff_email = href[len("mailto:") :]
                instructor_list.append(RawInstructor(name=staff_name, email=staff_email))
                found_names.add(staff_name)

            log.debug("Scraping raw text...")
            possible_names = raw_instructor_text.split(", ")
            skip = False

            for i in range(len(possible_names)):
                if skip:
                    skip = False
                    continue

                if i < len(possible_names) - 1 and possible_names[i + 1] in ("Jr"):
                    name = f"{possible_names[i]}, {possible_names[i + 1]}"
                    skip = True
                else:
                    name = possible_names[i]

                if name not in found_names:
                    instructor_list.append(RawInstructor(name=name, email=None))

            scraped_names = ", ".join(map(lambda x: x.name, instructor_list))
            log.debug("Comparing name characters between '%s' and '%s'", scraped_names, raw_instructor_text)

            assert (
                abs(_count_name_characters(scraped_names) - _count_name_characters(raw_instructor_text)) == 0
            )

        meeting_instructor_list.append(instructor_list)

    log.debug("Scraped meeting instructors: %s", [[str(r) for r in l] for l in meeting_instructor_list])
    return meeting_instructor_list


def can_skip(driver: SpireDriver, course: Course, section_id: str, link_number: str):
    try:
        section = Section.objects.get(id=section_id)

        if section.course != course:
            return False, "mismatched section course and current course"

        if SectionCombinedAvailability.objects.filter(individual_availability_id=section.id).first():
            return False, "section is combined"

        status_icon = driver.find(
            f"#win0divDERIVED_CLSRCH_SSR_STATUS_LONG\${link_number} > div > img", By.CSS_SELECTOR
        )

        src = status_icon.get_attribute("src")
        if src.endswith("PS_CS_STATUS_WAITLIST_ICN_1.gif"):
            current_status = "Wait List"
        elif src.endswith("PS_CS_STATUS_OPEN_ICN_1.gif"):
            current_status = "Open"
        elif src.endswith("PS_CS_STATUS_CLOSED_ICN_1.gif"):
            current_status = "Closed"
        else:
            log.debug(
                "Uncaught image src: %s",
            )
            assert False

        current_enrollment = int(driver.find("UM_DERIVED_SR_ENRL_TOT$" + link_number).text)
        current_capacity = int(driver.find("UM_DERIVED_SR_ENRL_TOT$" + link_number).text)

        if section.details.status != current_status:
            return False, "mismatched status"

        if section.availability.enrollment_total != current_enrollment:
            return False, "mismatched enrollment total"

        if section.availability.capacity == current_capacity:
            return False, "mismatched capacity"

        return True, "OK"
    except Section.DoesNotExist:
        return False, "does not exist"


# Extremely rare cases
COURSE_GROUP_OVERRIDES = {"FILM-ST  391SF": "FILM-ST  391SF   S-International SciFi Cinema"}

SECTION_ID_OVERRIDES = {
    "-(62798)": "01-DIS(62798)",
    "-(62799)": "01AA-DIS(62799)",
    "-(62800)": "01AB-DIS(62800)",
    "-(62801)": "01AC-DIS(62801)",
    "`01-PRA(52104)": "01-PRA(52104)",
    "`01-PRA(72927)": "01-PRA(72927)",
}


def _scrape_search_results(
    driver: SpireDriver, cache: VersionedCache, quick: bool, term: str, subject: Subject
):
    section_count = 0

    for span_id in cache.skip_once(
        driver.find_all_ids("span[id^=DERIVED_CLSRCH_DESCR200]"), "course_span_id"
    ):
        cache.push("course_span_id", span_id)

        span = driver.find(span_id)

        title_match = assert_match(
            r"(?P<subject_id>\S+)\s+(?P<course_number>\S+)\s+(?P<course_title>.+)",
            COURSE_GROUP_OVERRIDES.get(span.text, span.text),
        )

        course_id, _, number = RawCourse.get_course_id(
            title_match.group("subject_id"), title_match.group("course_number")
        )

        course_title = REPLACE_DOUBLE_SPACE(title_match.group("course_title").strip())

        course, created = Course.objects.get_or_create(
            id=course_id,
            defaults={
                "subject": subject,
                "number": number,
                "title": course_title,
                "description": None,
                "_updated_at": timezone.now(),
            },
        )

        log.debug("Scraping sections for %s course: %s", "new" if created else "found", course)

        offering, created = CourseOffering.objects.get_or_create(
            course=course,
            term=term,
            defaults={
                "subject": subject,
                "alternative_title": course_title if course_title != course.title else None,
            },
        )

        log.debug("%s course offering: %s", "Created" if created else "Got", offering)

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
            t = link.text.strip()
            section_id = SECTION_ID_OVERRIDES.get(t, t)

            log.debug("Scraping section %s...", section_id)

            link_number = link_id[len("DERIVED_CLSRCH_SSR_CLASSNAME_LONG$") :]
            meeting_instructor_list = _scrape_meeting_instructor_list(
                driver.find(section_table_id), link_number
            )
            log.debug("Scraped meeting instructor list: %s", meeting_instructor_list)

            if quick:
                can_skip_section, reason = can_skip(driver, course, section_id, link_number)
                if can_skip_section:
                    log.info("Skipping section: %s", section_id)
                    scraped_section_ids_for_course.add(section_id)
                    continue
                else:
                    log.info("Not skipping section: %s - %s", section_id, reason)

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
                id=section_id,
                details=table_results["Class Details"],
                meeting_information=meeting_info_list,
                restrictions=table_results.get("RESTRICTIONS & NOTES", None),
                availability=table_results["Class Availability"],
                description=table_results.get("Description", None),
                overview=table_results.get("Class Overview", None),
            )

            log.info("Scraped section:\n%s", section)
            scraped_section_ids_for_course.add(section.id)

            section_count += 1

            log.info("Clicking return then pushing...")
            driver.click("CLASS_SRCH_WRK2_SSR_PB_BACK", wait=False)

            section.push(offering)

            driver.wait_for_spire()
            log.info("Returned to search results for %s durning %s.", subject, term)

        dropped, _ = (
            Section.objects.filter(course_id=course_id, term=term)
            .exclude(id__in=scraped_section_ids_for_course)
            .delete()
        )
        log.info("Dropped %s %s sections for course %s that are no longer listed.", dropped, term, course_id)

    return section_count


def _initialize_query(driver: SpireDriver, term_id: str, subject_id: str):
    term_select = driver.wait_for_interaction(By.ID, "UM_DERIVED_SA_UM_TERM_DESCR")
    driver.scroll_to(term_select)
    term_select = Select(term_select)
    term_select.select_by_value(term_id)
    driver.wait_for_spire()

    subject_select = driver.wait_for_interaction(By.ID, "CLASS_SRCH_WRK2_SUBJECT$108$")
    driver.scroll_to(subject_select)
    subject_select = Select(subject_select)
    subject_select.select_by_value(subject_id)
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


def scrape_sections(driver: SpireDriver, cache: VersionedCache, quick=False):
    log.info("Scraping sections...")

    driver.navigate_to("search")

    total_timer = Timer()
    scraped_terms = 0

    def get_option_values(select):
        return [
            (e.get_property("value"), e.text)
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

        (term_id, flipped_term) = term_values[term_offset]
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
        for (subject_id, subject_title) in cache.skip_once(subject_values, "subject"):
            cache.push("subject", (subject_id, subject_title))
            subject_timer = Timer()

            # Initialize and search for subject during term
            _initialize_query(driver, term_id, subject_id)

            raw_subject = RawSubject(subject_id, subject_title)
            subject, created = Subject.objects.get_or_create(
                id=raw_subject.id, defaults={"title": raw_subject.title}
            )

            log.info("%s subject: %s", "Created" if created else "Found", subject)

            log.info("Searching for sections in subject %s during %s...", subject.id, term)
            driver.click("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")

            assert driver.find("win0divDERIVED_CLSRCH_SSR_CLASS_LBLlbl")

            return_button = driver.find("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")

            if return_button:
                count = _scrape_search_results(driver, cache, quick, term, subject)

                log.info(
                    "Scraped %s %s sections during %s in %s. Returning...",
                    count,
                    subject,
                    term,
                    subject_timer,
                )
                driver.click("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")
            else:
                error_message_span = driver.find("DERIVED_CLSMSG_ERROR_TEXT")
                assert error_message_span
                warning = error_message_span.text
                if warning == "The search returns no results that match the criteria specified.":
                    log.info("There are no %s section during %s. Skipping.", subject, term)
                else:
                    log.warning("Failed while searching: %s", error_message_span.text)
                    raise Exception(f"Unexpected search error: {warning}")

        coverage.completed = True
        coverage.end_time = timezone.now()
        coverage.save()

        log.info("Scraped sections for the %s term in %s.", term, term_timer)

    log.info("Scraped %s terms in %s.", scraped_terms, total_timer)
