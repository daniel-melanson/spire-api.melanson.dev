import logging
from datetime import datetime

from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from spire.models import Section, SectionCoverage, Staff
from spire.regexp import TERM_REGEXP
from spire.scraper.shared import assert_match, scrape_spire_tables, skip_until
from spire.scraper.spire_driver import SpireDriver
from spire.scraper.versioned_cache import VersionedCache

log = logging.getLogger(__name__)


def scrape_search_results(driver: SpireDriver, term: str):
    """
    log.debug("Scraping search results...")
    sections = []

    course_title_span_ids = driver.find_all_ids("span[id^=DERIVED_CLSRCH_DESCR200]")
    for span_id in course_title_span_ids:
        span = driver.find(span_id)

        title_match = assert_match(
            r"(?P<subject_id>\S+)\s+(?P<course_number>\S+)\s+(?P<course_title>.+)",
            span.text,
        )
        course_id = SpireCourse.get_course_id(
            title_match.group("subject_id"), title_match.group("course_number")
        )

        log.debug("Scraping sections for course: %s.", course_id)

        sections_table = driver.find(
            "ACE_DERIVED_CLSRCH_GROUPBOX1$133$" + span_id[len("DERIVED_CLSRCH_DESCR200") :]
        )
        assert sections_table

        log.debug("Scraping emails for course...")
        course_staff_emails = {}
        for a in sections_table.find_elements(By.CSS_SELECTOR, "a[href^=mailto\:]"):
            href = a.get_property("href")

            email = href[len("mailto:") :]

            course_staff_emails[a.text] = email

        log.debug("Scraped emails: %s.", course_staff_emails)

        link_ids = [
            e.get_property("id")
            for e in sections_table.find_elements(
                By.CSS_SELECTOR, "a[id^=DERIVED_CLSRCH_SSR_CLASSNAME_LONG\$]"
            )
        ]
        for link_id in link_ids:
            link = driver.find(link_id)
            section_id = link.text

            driver.click(link_id)

            table_results = scrape_spire_tables(driver, "table.PSGROUPBOXWBO")

            meeting_info_table = driver.find("SSR_CLSRCH_MTG$scroll$0")

            instructors = []
            for raw_name in meeting_info_table.find_element(
                By.CSS_SELECTOR, "span[id^=MTG_INSTR]"
            ).text.split("\\n"):
                name = raw_name[:-1] if raw_name.endswith(",") else raw_name

                scraped_staff = SpireStaff(
                    name=name, email=course_staff_emails[name] if name in course_staff_emails else None
                )

                log.info("Scraped staff: %s", staff)
                if scraped_staff.email:
                    staff, created = Staff.objects.update_or_create(
                        email=scraped_staff.email, defaults={"name": scraped_staff.name}
                    )

                instructors.append(staff)

            section = SpireSection(
                course_id=course_id,
                term=term,
                id=section_id,
                details=table_results["Class Details"],
                meeting_information=SpireMeetingInformation(
                    days_and_times=meeting_info_table.find_element(
                        By.CSS_SELECTOR, "span[id^=MTG_SCHED]"
                    ).text,
                    instructors=instructors,
                    room=meeting_info_table.find_element(By.CSS_SELECTOR, "span[id^=MTG_LOC]").text,
                    meeting_dates=meeting_info_table.find_element(By.CSS_SELECTOR, "span[id^=MTG_DATE]").text,
                ),
                availability=table_results["Class Availability"],
                description=table_results["Description"] if "Description" in table_results else None,
                overview=table_results["Class Overview"] if "Class Overview" in table_results else None,
                restrictions=table_results["RESTRICTIONS & NOTES"]
                if "RESTRICTIONS & NOTES" in table_results
                else None,
            )
            log.info("Scraped section: %s", section)

            section, created = Section.objects.update_or_create(
                id=section.id, defaults=section.as_model_default(True)
            )

            log.info("%s section: %s", "Created" if created else "Updated", section)

            for instructor in instructors:
                if isinstance(instructor, Staff):
                    section.instructors.add(instructor)

            driver.click("CLASS_SRCH_WRK2_SSR_PB_BACK")

    log.debug("Scraped search results.")
    return sections
    """
    pass


def get_option_values(select):
    return [
        e.text for e in select.find_elements(By.CSS_SELECTOR, "option") if len(e.get_property("value")) > 0
    ]


def scrape_sections(driver: SpireDriver, cache: VersionedCache):
    pass
    """
    log.info("Scraping sections...")
    driver.navigate_to("search")

    subject_select = driver.wait_for_interaction(By.ID, "CLASS_SRCH_WRK2_SUBJECT\$108\$")
    assert subject_select
    subject_values = get_option_values(subject_select)

    term_select = driver.wait_for_interaction(By.ID, "UM_DERIVED_SA_UM_TERM_DESCR")
    assert term_select
    term_values = get_option_values(term_select)

    has_skipped = False
    for term_offset in range(cache.get("term_offset", 4 * 5), -1, -1):
        cache.push("term_offset", term_offset)

        flipped_term = term_values[term_offset]
        [year, season] = flipped_term.split(" ")
        term = f"{season} {year}"
        assert_match(TERM_REGEXP, term)

        coverage, _ = SectionCoverage.objects.get_or_create(
            term=term, defaults={"completed": False, "start_time": timezone.now()}
        )

        if coverage.completed:
            year = int(year)
            match season:
                case "Fall":
                    end_date = datetime(year=year + 1, month=1, day=1)
                case "Winter":
                    end_date = datetime(year=year + 1, month=3, day=1)
                case "Spring":
                    end_date = datetime(year=year, month=6, day=1)
                case "Summer":
                    end_date = datetime(year=year, month=9, day=1)

            if end_date < datetime.now():
                log.info("Skipping the %s semester, as information is static.", term)
                continue

        for subject in subject_values if has_skipped else skip_until(subject_values, cache, "subject"):
            has_skipped = True
            cache.push("subject", subject)

            log.info("Searching for sections in subject: %s.", subject)
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

            log.info("Searching for %s courses in during the %s term...", subject, term_values[term_offset])
            driver.click("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")

            return_button = driver.find("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")

            if return_button:
                scrape_search_results(driver, term_values[term_offset])

                log.debug("Returning...")
                driver.click("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")
            else:
                log.debug("No search results found, skipping...")

        coverage.completed = True
        coverage.end_time = timezone.now()
        coverage.save()

    log.info("Scraped sections.")
    """
