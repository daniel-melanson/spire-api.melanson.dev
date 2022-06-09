import logging
from logging import DEBUG
from typing import Optional, TypedDict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from spire.regexp import COURSE_ID_NUM_REGEXP, COURSE_TITLE_REGEXP, SUBJECT_ID_REGEXP
from spire.scraper.shared import assert_match, scrape_spire_tables
from spire.scraper.SpireDriver import SpireDriver

log = logging.getLogger(__name__)
log.setLevel(DEBUG)


class SpireStaff(TypedDict):
    name: str
    email: Optional[str]


class SpireMeetingInformation(TypedDict):
    days_and_times: str
    room: str
    instructors: list[SpireStaff]
    meeting_dates: str


class SpireSection(TypedDict):
    course_id: str
    term: str
    section_id: str
    details: dict[str, str]
    meeting_information: SpireMeetingInformation
    restrictions: Optional[dict[str, str]]
    availability: dict[str, str]
    description: Optional[str]
    overview: Optional[str]


def scrape_search_results(driver: SpireDriver, term: str):
    log.debug("Scraping search results...")
    sections = []

    course_title_span_ids = driver.find_all_ids("span[id^=DERIVED_CLSRCH_DESCR200]")
    for span_id in course_title_span_ids:
        span = driver.find(span_id)

        title_match = assert_match(
            SUBJECT_ID_REGEXP + r"\s+" + COURSE_ID_NUM_REGEXP + r"\s+" + COURSE_TITLE_REGEXP, span.text
        )
        course_id = f"{title_match.group('subject_id')} {title_match.group('course_number')}"

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

                instructors.append(
                    SpireStaff(
                        name=name, email=course_staff_emails[name] if name in course_staff_emails else None
                    )
                )

            section = SpireSection(
                course_id=course_id,
                term=term,
                section_id=section_id,
                details=table_results["Class Details"],
                meeting_information=SpireMeetingInformation(
                    days_and_times=meeting_info_table.find_element(
                        By.CSS_SELECTOR, "span[id^=MTG_SCHED]"
                    ).text,
                    room=meeting_info_table.find_element(By.CSS_SELECTOR, "span[id^=MTG_LOC]").text,
                    instructors=instructors,
                    meeting_dates=meeting_info_table.find_element(By.CSS_SELECTOR, "span[id^=MTG_DATE]").text,
                ),
                availability=table_results["Class Availability"],
                description=table_results["Description"] if "Description" in table_results else None,
                overview=table_results["Class Overview"] if "Class Overview" in table_results else None,
                restrictions=table_results["RESTRICTIONS & NOTES"]
                if "RESTRICTIONS & NOTES" in table_results
                else None,
            )
            log.info("Scraped section: %s.", section)
            sections.append(section)

            driver.click("CLASS_SRCH_WRK2_SSR_PB_BACK")

    log.debug("Scraped search results.")
    return sections


def get_option_values(select):
    return [
        e.text for e in select.find_elements(By.CSS_SELECTOR, "option") if len(e.get_property("value")) > 0
    ]


def scrape_sections(driver: SpireDriver):
    log.info("Scraping sections...")
    driver.navigate_to("search")

    subject_select = driver.wait_for_interaction(By.ID, "CLASS_SRCH_WRK2_SUBJECT\$108\$")
    assert subject_select
    subject_values = get_option_values(subject_select)

    term_select = driver.wait_for_interaction(By.ID, "UM_DERIVED_SA_UM_TERM_DESCR")
    assert term_select
    term_values = get_option_values(term_select)

    for term_offset in range(0, 4 * 5):
        for subject in subject_values:
            log.info("Searching for sections in subject: %s.", subject)

            log.debug("Setting-up search query...")
            term_select = driver.wait_for_interaction(By.ID, "UM_DERIVED_SA_UM_TERM_DESCR")
            driver.scroll_to(term_select)
            term_select = Select(term_select)
            term_select.select_by_visible_text(term_values[term_offset])

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

            log.debug("Searching for %s courses in during the %s term...", subject, term_values[term_offset])
            driver.click("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")

            return_button = driver.find("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")

            if return_button:
                course_sections = scrape_search_results(driver, term_values[term_offset])

                log.debug("Returning...")
                driver.click("CLASS_SRCH_WRK2_SSR_PB_NEW_SEARCH")
            else:
                log.debug("No search results found, skipping...")

    log.info("Scraped sections.")
