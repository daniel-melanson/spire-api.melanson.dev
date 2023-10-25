import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from spire.models import (
    Course,
    CourseOffering,
    Section,
    SectionCombinedAvailability,
    SectionCoverage,
    Subject,
    Term,
)
from spire.scraper.classes import RawCourse, RawInstructor, RawSection, RawSubject
from spire.scraper.classes.normalizers import REPLACE_DOUBLE_SPACE
from spire.scraper.shared import assert_match, scrape_spire_tables, get_or_create_term
from spire.scraper.spire_driver import SpireDriver
from spire.scraper.timer import Timer
from spire.scraper.versioned_cache import VersionedCache
from typing import NamedTuple
from spire.scraper.stats import Stats

log = logging.getLogger(__name__)


class ScrapeContext(NamedTuple):
    driver: SpireDriver
    cache: VersionedCache
    stats: Stats


def _count_name_characters(s: str):
    count = 0
    for c in s:
        if not c.isspace() and c != ",":
            count += 1

    return count


def _scrape_meeting_instructor_list(sections_table, link_number: str):
    log.debug("Scraping meeting instructors...")
    meeting_information_table = sections_table.find_element(
        By.ID, "SSR_CLSRCH_MTG1$scroll$" + link_number
    )

    meeting_instructor_list = []

    for meeting_row in meeting_information_table.find_elements(
        By.CSS_SELECTOR, "tr[id^=trSSR_CLSRCH_MTG]"
    ):
        instructor_column = meeting_row.find_element(
            By.CSS_SELECTOR, "div[id^=win0divUM_DERIVED_SR_UM_HTML1"
        )

        raw_instructor_text = instructor_column.text.strip()
        while "\n\n" in raw_instructor_text or "  " in raw_instructor_text:
            raw_instructor_text = raw_instructor_text.replace("\n\n", "\n").replace(
                "  ", " "
            )

        log.debug("Scraping raw staff from %s", raw_instructor_text)

        instructor_list = []
        if len(raw_instructor_text) == 0 or raw_instructor_text in ("Staff", "TBD"):
            instructor_list.append(RawInstructor(name="Staff"))
        else:
            found_names = set()

            for email_link in instructor_column.find_elements(
                By.CSS_SELECTOR, "a[href^='mailto:']"
            ):
                href = email_link.get_property("href")
                staff_name = email_link.text.strip()
                if staff_name.endswith(","):
                    staff_name = staff_name[:-1]

                staff_email = href[len("mailto:") :]
                instructor_list.append(
                    RawInstructor(name=staff_name, email=staff_email)
                )
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
            log.debug(
                "Comparing name characters between '%s' and '%s'",
                scraped_names,
                raw_instructor_text,
            )

            assert (
                abs(
                    _count_name_characters(scraped_names)
                    - _count_name_characters(raw_instructor_text)
                )
                == 0
            )

        meeting_instructor_list.append(instructor_list)

    log.debug(
        "Scraped meeting instructors: %s",
        [[str(r) for r in l] for l in meeting_instructor_list],
    )
    return meeting_instructor_list


def _can_skip(
    driver: SpireDriver, offering: CourseOffering, spire_id: str, link_number: str
):
    try:
        section = Section.objects.get(spire_id=spire_id, offering=offering)  # type: ignore

        if SectionCombinedAvailability.objects.filter(  # type: ignore
            individual_availability_id=section.id
        ).first():
            return False, "section is combined"

        status_icon = driver.find(
            f"#win0divDERIVED_CLSRCH_SSR_STATUS_LONG\\${link_number} > div > img",
            By.CSS_SELECTOR,
        )

        src: str = status_icon.get_attribute("src")  # type: ignore
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

        if section.details.status != current_status:
            return False, "mismatched status"

        ce_elem = driver.find("UM_DERIVED_SR_ENRL_TOT$" + link_number)
        assert ce_elem
        current_enrollment = int(ce_elem.text)

        if section.availability.enrollment_total != current_enrollment:
            return False, "mismatched enrollment total"

        cc_elem = driver.find("UM_DERIVED_SR_ENRL_CAP$" + link_number)
        assert cc_elem
        current_capacity = int(cc_elem.text)

        if section.availability.capacity != current_capacity:
            return (
                False,
                f"mismatched capacity, {section.availability.capacity} != {current_capacity}",
            )

        return True, "OK"
    except Section.DoesNotExist:  # type: ignore
        return False, "does not exist"


# Extremely rare cases
COURSE_GROUP_OVERRIDES = {
    "FILM-ST  391SF": "FILM-ST  391SF   S-International SciFi Cinema"
}

SPIRE_ID_OVERRIDES = {
    "-(62798)": "01-DIS(62798)",
    "-(62799)": "01AA-DIS(62799)",
    "-(62800)": "01AB-DIS(62800)",
    "-(62801)": "01AC-DIS(62801)",
    "`01-PRA(52104)": "01-PRA(52104)",
    "`01-PRA(72927)": "01-PRA(72927)",
}


def _scrape_search_results(
    context: ScrapeContext,
    term: Term,
    subject: Subject,
    quick=False,
):
    driver = context.driver
    cache = context.cache

    scraped_course_ids = set()
    for span_id in cache.skip_once(
        driver.find_all_ids("span[id^=DERIVED_CLSRCH_DESCR200]"), "course_span_id"
    ):
        cache.push("course_span_id", span_id)

        span = driver.find(span_id)
        assert span

        title_match = assert_match(
            r"(?P<subject_id>\S+)\s+(?P<course_number>\S+)\s+(?P<course_title>.+)",
            COURSE_GROUP_OVERRIDES.get(span.text, span.text),
        )

        course_id, _, number = RawCourse.get_course_id(
            title_match.group("subject_id"), title_match.group("course_number")
        )
        scraped_course_ids.add(course_id)
        course_title = REPLACE_DOUBLE_SPACE(title_match.group("course_title").strip())

        course, created = Course.objects.get_or_create(  # type: ignore
            id=course_id,
            defaults={
                "subject": subject,
                "number": number,
                "title": course_title,
                "description": None,
                "_updated_at": timezone.now(),
            },
        )

        log.debug(
            "Scraping sections for %s course: %s", "new" if created else "found", course
        )

        offering, created = CourseOffering.objects.get_or_create(  # type: ignore
            course=course,
            term=term,
            defaults={
                "subject": subject,
                "alternative_title": course_title
                if course_title != course.title
                else None,
            },
        )

        log.debug("%s course offering: %s", "Created" if created else "Got", offering)

        scraped_spire_ids_for_course = set()

        section_table_id = (
            "ACE_DERIVED_CLSRCH_GROUPBOX1$133$"
            + span_id[len("DERIVED_CLSRCH_DESCR200") :]
        )
        sections_table = driver.find(section_table_id)
        assert sections_table

        link_ids: list[str] = [
            e.get_property("id")
            for e in sections_table.find_elements(
                By.CSS_SELECTOR, "a[id^='DERIVED_CLSRCH_SSR_CLASSNAME_LONG\\$']"
            )
        ]  # type: ignore

        context.stats.increment("sections_found", len(link_ids))

        for link_id in link_ids:
            link = driver.find(link_id)
            assert link

            t = link.text.strip()
            spire_id = SPIRE_ID_OVERRIDES.get(t, t)

            scraped_spire_ids_for_course.add(spire_id)

            log.debug("Scraping section %s during %s...", spire_id, term.id)

            link_number = link_id[len("DERIVED_CLSRCH_SSR_CLASSNAME_LONG$") :]
            meeting_instructor_list = _scrape_meeting_instructor_list(
                driver.find(section_table_id), link_number
            )
            log.debug("Scraped meeting instructor list: %s", meeting_instructor_list)

            if quick:
                can_skip_section, reason = _can_skip(
                    driver, offering, spire_id, link_number
                )
                if can_skip_section:
                    log.debug("Skipping section: %s", spire_id)
                    continue
                else:
                    log.debug("Not skipping section: %s - %s", spire_id, reason)

            context.stats.increment("sections_scraped")

            log.debug(
                "Navigating to section page for %s section %s...", course_id, spire_id
            )
            driver.click(link_id)

            table_results = scrape_spire_tables(driver, "table.PSGROUPBOXWBO")

            meeting_info_list = []
            for row in driver.find_all("tr[id^='trSSR_CLSRCH_MTG$0_row']"):
                meeting_info_list.append(
                    {
                        "days_and_times": row.find_element(
                            By.CSS_SELECTOR, "span[id^=MTG_SCHED]"
                        ).text,
                        "instructors": meeting_instructor_list.pop(),
                        "room": row.find_element(
                            By.CSS_SELECTOR, "span[id^=MTG_LOC]"
                        ).text,
                        "meeting_dates": row.find_element(
                            By.CSS_SELECTOR, "span[id^=MTG_DATE]"
                        ).text,
                    }
                )

            section = RawSection(
                spire_id=spire_id,
                details=table_results["Class Details"],
                meeting_information=meeting_info_list,
                restrictions=table_results.get("RESTRICTIONS & NOTES", None),
                availability=table_results["Class Availability"],
                description=table_results.get("Description", None),
                overview=table_results.get("Class Overview", None),
            )

            log.info("Scraped section:\n%s", section)

            log.debug("Clicking return then pushing...")
            driver.click("CLASS_SRCH_WRK2_SSR_PB_BACK", wait=False)

            section.push(offering)

            driver.wait_for_spire()
            log.debug("Returned to search results for %s durning %s.", subject, term)

        dropped, _ = (
            Section.objects.filter(offering__course=course, offering__term=term)  # type: ignore
            .exclude(spire_id__in=scraped_spire_ids_for_course)
            .delete()
        )
        if dropped > 0:
            log.info(
                "Dropped %s %s sections during %s that are no longer listed.",
                dropped,
                course_id,
                term,
            )

    dropped, _ = (
        CourseOffering.objects.filter(subject=subject, term=term)  # type: ignore
        .exclude(course__id__in=scraped_course_ids)
        .delete()
    )

    if dropped > 0:
        log.info(
            "Dropped %s %s course offerings during %s that are no longer listed.",
            dropped,
            subject.id,
            term,
        )


def _initialize_query(driver: SpireDriver, term_id: str, subject_id: str):
    for select_id, value in [
        ("UM_DERIVED_SA_UM_TERM_DESCR", term_id),
        ("CLASS_SRCH_WRK2_SUBJECT$108$", subject_id),
    ]:
        element: WebElement = driver.wait_for_interaction(By.ID, select_id)
        assert element

        driver.scroll_to(element)

        select = Select(element)
        select.select_by_value(value)

        driver.wait_for_spire()

    select_element = driver.find("CLASS_SRCH_WRK2_SSR_EXACT_MATCH1")
    assert select_element

    number_select = Select(select_element)
    number_select.select_by_visible_text("greater than or equal to")
    driver.wait_for_spire()

    number_input = driver.find("CLASS_SRCH_WRK2_CATALOG_NBR$8$")
    assert number_input
    number_input.clear()
    number_input.send_keys("A")
    driver.wait_for_spire()

    open_input = driver.find("CLASS_SRCH_WRK2_SSR_OPEN_ONLY")
    assert open_input

    if open_input.is_selected():
        open_input.click()
        driver.wait_for_spire()


def _get_select_options(driver: SpireDriver):
    def get_option_values(select: WebElement, f=None) -> list[tuple[str, str]]:
        return [
            (e.get_property("value"), f(e.text) if f else e.text)
            for e in select.find_elements(By.CSS_SELECTOR, "option")
            if len(e.get_property("value")) > 0  # type: ignore
        ]

    # Fetch subject option values
    subject_select: WebElement = driver.wait_for_interaction(
        By.ID, "CLASS_SRCH_WRK2_SUBJECT$108$"
    )
    assert subject_select
    subject_options: list[tuple[str, str]] = get_option_values(subject_select)

    # Fetch term option values
    term_select: WebElement = driver.wait_for_interaction(
        By.ID, "UM_DERIVED_SA_UM_TERM_DESCR"
    )
    assert term_select

    def swap(s: str):
        [year, season] = s.split(" ")
        return f"{season} {year}"

    term_options: list[tuple[str, str]] = get_option_values(term_select, f=swap)

    return (term_options, subject_options)


def _should_skip_term(coverage):
    if coverage.completed and settings.SCRAPER["SKIP_OLD_TERMS"]:
        year = coverage.term.year
        season = coverage.term.season

        match season:
            case "Fall":
                end_date = datetime(year=year + 1, month=1, day=1)
            case "Winter":
                end_date = datetime(year=year + 1, month=2, day=15)
            case "Spring":
                end_date = datetime(year=year, month=6, day=1)
            case "Summer":
                end_date = datetime(year=year, month=9, day=15)
            case _:
                assert False

        if coverage.end_time and timezone.make_aware(end_date) < coverage.end_time:
            log.info(
                "Skipping the %s term, as information is static.", coverage.term.id
            )
            return True

    return False


def _search_query(context: ScrapeContext, term, subject, quick=False):
    driver = context.driver

    log.info("Searching for sections in subject %s during %s...", subject.id, term)
    subject_timer = Timer()
    driver.click("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")

    assert driver.find("win0divDERIVED_CLSRCH_SSR_CLASS_LBLlbl")
    return_button = driver.find("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")

    if not return_button:
        error_message_span = driver.find("DERIVED_CLSMSG_ERROR_TEXT")
        assert error_message_span
        warning = error_message_span.text
        if (
            warning
            == "The search returns no results that match the criteria specified."
        ):
            log.info("There are no %s section during %s. Skipping.", subject, term)
            return (0, 0)
        else:
            log.warning("Failed while searching: %s", error_message_span.text)
            raise Exception(f"Unexpected search error: {warning}")

    _scrape_search_results(context, term, subject, quick=quick)

    log.info(
        "Scraped %s %s sections during %s in %s. Returning...",
        context.stats.get("sections_scraped"),
        subject,
        term,
        subject_timer,
    )

    driver.click("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")


def _scrape_term(
    context: ScrapeContext,
    term,
    term_value,
    subject_options,
    quick=False,
):
    # Establish coverage entry
    coverage, _ = SectionCoverage.objects.get_or_create(  # type: ignore
        term=term,
        defaults={"completed": False, "start_time": timezone.now()},
    )

    if _should_skip_term(coverage):
        return

    log.info("Scraping sections during %s...", term)
    timer = Timer()

    # For each subject
    for subject_value, subject_title in context.cache.skip_once(
        subject_options, "subject"
    ):
        context.cache.push("subject", (subject_value, subject_title))

        # Initialize and search for subject durn/aing term
        _initialize_query(context.driver, term_value, subject_value)

        raw_subject = RawSubject(subject_value, subject_title)
        subject = raw_subject.push()

        # Execute search
        _search_query(context, term, subject, quick=quick)

        if quick:
            sections_scraped = context.stats.get("sections_scraped")
            sections_found = context.stats.get("sections_found")

            log.info(
                "Running skip percentage of: %.2f%% per term",
                (1 - (sections_scraped / sections_found)) * 100,
            )

    coverage.completed = True
    coverage.end_time = timezone.now()
    coverage.save()

    log.info("Scraped sections for the %s term in %s.", term, timer)


def scrape_single_term(context: ScrapeContext, season, year, **kwargs) -> None:
    term = get_or_create_term(season, year)
    log.info("Scraping sections for single term %s...", term.id)

    (term_options, subject_options) = _get_select_options(context.driver)

    term_value = [v for (v, id) in term_options if term.id == id][0]

    _scrape_term(context, term, term_value, subject_options, **kwargs)
    log.info("Scraped sections for single term %s...", term.id)


def scrape_all_terms(context: ScrapeContext, **options):
    log.info("Scraping sections for all terms...")

    total_timer = Timer()

    (term_options, subject_options) = _get_select_options(context.driver)

    # For each term, 5 academic years from the most recently posted year
    for term_offset in range(context.cache.get("term_offset", 4 * 2 - 1), -1, -1):  # type: ignore
        context.cache.push("term_offset", term_offset)

        (term_option, term_id) = term_options[term_offset]
        [season, year] = term_id.split(" ")
        term = get_or_create_term(season, year)

        _scrape_term(context, term, term_option, subject_options, **options)

        context.stats.increment("terms_scraped")

    log.info("Scraped %s terms in %s.", context.stats.get("terms_scraped"), total_timer)
