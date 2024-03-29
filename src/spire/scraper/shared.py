import logging
import re
from typing import Any, Callable, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from spire.models import Term

from .spire_driver import SpireDriver

log = logging.getLogger(__name__)


def assert_match(r: str, s: str, search: bool = False):
    log.debug("%s: %s against %s", "Searching" if search else "Full matching", s, r)
    str_match = re.fullmatch(r, s) if not search else re.search(r, s)
    assert str_match
    return str_match


SEASON_LIST = ["Winter", "Spring", "Summer", "UWW Summer", "Fall"]


def get_or_create_term(season: str, year: str):
    log.debug("Making or finding term: %s %s", season, year)

    assert isinstance(season, str) and season in SEASON_LIST
    assert isinstance(year, str) and 2000 <= int(year) <= 2100

    term_id = f"{season} {year}"

    term, _ = Term.objects.get_or_create(
        id=term_id,
        defaults={
            "ordinal": int(str(year) + str(SEASON_LIST.index(season))),
            "season": season,
            "year": year,
        },
    )

    return term


FIELD_VALUE_IDS = {
    "win0divSSR_CRSE_OFF_VW_ACAD_GROUPlbl$0": "win0divACAD_GROUP_TBL_DESCR$0",
    "win0divSSR_CRSE_OFF_VW_ACAD_ORGlbl$0": "win0divACAD_ORG_TBL_DESCR$0",
    "win0divSR_LBL_WRK_CRSE_COMPONENT_LBLlbl$0": "win0divSSR_DUMMY_RECVW$0",
    "win0divSSR_CRSE_OFF_VW_RQRMNT_GROUPlbl$0": "win0divDERIVED_CRSECAT_DESCR254A$0",
    "win0divSSR_CRSE_OFF_VW_CAMPUSlbl$0": "win0divCAMPUS_TBL_DESCR$0",
    "win0divSSR_CLS_DTL_WRK_SESSION_CODElbl": "win0divPSXLATITEM_XLATLONGNAME",
    "win0divSR_LBL_WRK_CRSE_COMPONENT_LBLlbl": "win0divSSR_DUMMY_RECVW$0",
    "win0divSSR_CLS_DTL_WRK_ACAD_CAREERlbl": "win0divPSXLATITEM_XLATLONGNAME$33$",
    "win0divSSR_CLS_DTL_WRK_GRADING_BASISlbl": "win0divGRADE_BASIS_TBL_DESCRFORMAL",
    "win0divSSR_CLS_DTL_WRK_CONSENTlbl": "win0divPSXLATITEM_XLATLONGNAME$209$",
    "win0divSSR_CLS_DTL_WRK_SSR_DROP_CONSENTlbl": "win0divPSXLATITEM_XLATLONGNAME$229$",
    "win0divSSR_CLS_DTL_WRK_CRS_TOPIC_IDlbl": "win0divCRSE_TOPICS_DESCR",
}


def scrape_description(_, table: WebElement):
    return "\n".join(
        [e.text for e in table.find_elements(By.CSS_SELECTOR, "span")]
    ).strip()


def scrape_course_overview(driver: SpireDriver, _):
    text_area = driver.find("UM_DERIVED_SR_UM_CLASS_GOALS")

    return text_area.text if text_area else "None"


def scrape_spire_field_value_table(
    driver: SpireDriver, table: WebElement
) -> dict[str, str]:
    log.debug("Scraping field-value pairs for table...")

    details: dict[str, str] = {}

    detail_fields = []
    detail_values = {}

    field_count = 0
    value_count = 0

    matched_ids: set[str] = set()

    table_id: str = table.get_property("id").replace("$", "\\$")  # type: ignore
    for e in driver.find_all(f"#{table_id} > tbody > tr > td > div[id^=win0div]"):
        element_id: str = e.get_property("id")  # type: ignore

        try:
            child = e.find_element(By.CSS_SELECTOR, "span[class$='LABEL']")
        except:
            child = None

        if element_id in ("win0divSSR_CLS_DTL_WRK_SSR_STATUS_LONG"):
            log.debug("Skipping element id: %s", element_id)
        elif element_id == "win0div$ICField247$0":
            log.debug("Found RAP/TAP/HCL. Scraping...")

            details["RAP/TAP/HLC"] = e.find_element(
                By.ID, "win0divUM_RAPTAP_CLSDT_UM_RAP_TAP$0"
            ).text

            log.debug("Adding detail: %s", ("RAP/TAP/HLC", details["RAP/TAP/HLC"]))
        elif element_id == "win0divUM_CAPS_WRK_UM_ENRL_CAP_CUR":
            log.debug("Found detail field element: %s", element_id)
            detail_fields.append((element_id, "NSO Enroll Cap"))

            field_count += 1
        elif child:
            log.debug("Found detail field element: %s", element_id)
            detail_fields.append((element_id, child.text))
            assert "lbl" in element_id

            field_count += 1
        else:
            log.debug("Found detail value element: %s", element_id)
            detail_values[element_id] = e
            value_count += 1

    assert value_count == field_count
    log.debug("Scraped ids. Matching...")

    for field_id, field_title in detail_fields:
        value_id: str

        if field_id in FIELD_VALUE_IDS:
            value_id = FIELD_VALUE_IDS[field_id]

            assert value_id[:-1] + "1" not in detail_values
        elif field_id.endswith("lbl$0"):
            value_id = field_id[: -len("lbl$0")] + "$0"
        elif field_id.endswith("lbl"):
            value_id = field_id[: -len("lbl")]
        elif field_id == "win0divUM_CAPS_WRK_UM_ENRL_CAP_CUR":
            value_id = "win0divUM_CAPS_WRK_UM_ENRL_CAP_CUR$333$"
        else:
            assert False

        if value_id in detail_values:
            assert value_id not in matched_ids
            matched_ids.add(value_id)

            log.debug("Matched %s with %s.", field_id, value_id)
            element = detail_values[value_id]
            text = element.text.strip()
            if len(text) > 0:
                log.debug("Adding detail: %s", (field_title, element.text))
                details[field_title] = text
            else:
                log.debug("Ignoring, empty value text.")
        else:
            log.warning("Unable to find a match for %s(%s).", field_id, field_title)
            assert False

    log.debug("Scraped detail for table.")
    return details


def scrape_spire_class_availability(driver: SpireDriver, table: WebElement):
    try:
        combined_table = table.find_element(By.ID, "SCTN_CMBND$scroll$0")
    except:
        combined_table = None

    if combined_table:

        def get(id: str) -> str:
            return driver.wait_for_presence(By.ID, id).text

        combined_sections = []
        for section in combined_table.find_elements(
            By.CSS_SELECTOR, "tr[id^=trSCTN_CMBND\\$0_row]"
        ):
            combined_sections.append(section.text.strip())

        return {
            "Individual Availability": {
                "Capacity": get("UM_DERIVED_SR_ENRL_CAP"),
                "Enrollment Total": get("UM_DERIVED_SR_ENRL_TOT"),
                "Available Seats": get("UM_DERIVED_SR_AVAILABLE_SEATS"),
                "Wait List Capacity": get("UM_DERIVED_SR_WAIT_CAP"),
                "Wait List Total": get("UM_DERIVED_SR_WAIT_TOT"),
            },
            "Combined Availability": {
                "Sections": combined_sections,
                "Capacity": get("SSR_CLS_DTL_WRK_ENRL_CAP"),
                "Enrollment Total": get("SSR_CLS_DTL_WRK_ENRL_TOT"),
                "Available Seats": get("SSR_CLS_DTL_WRK_AVAILABLE_SEATS"),
                "Wait List Capacity": get("SSR_CLS_DTL_WRK_WAIT_CAP"),
                "Wait List Total": get("SSR_CLS_DTL_WRK_WAIT_TOT"),
            },
        }
    else:
        return scrape_spire_field_value_table(driver, table)


TABLE_SCRAPERS: dict[str, Callable[[SpireDriver, WebElement], Any]] = {
    "Course Detail": scrape_spire_field_value_table,
    "Enrollment Information": scrape_spire_field_value_table,
    "Description": scrape_description,
    "Class Details": scrape_spire_field_value_table,
    "RESTRICTIONS & NOTES": scrape_spire_field_value_table,
    "Class Overview": scrape_course_overview,
    "Class Availability": scrape_spire_class_availability,
}

TABLE_CONTENT_SELECTORS = {
    "Class Details": "table[id^=ACE_\\$ICField][class=PABACKGROUNDINVISIBLE]"
}


def scrape_spire_tables(driver: SpireDriver, table_selector: str):
    log.debug("Scraping tables...")

    scraped_table_names: set[str] = set()
    table_results: dict[str, Any] = {}

    for table in driver.find_all(table_selector):
        table_label = table.find_element(By.CSS_SELECTOR, "tbody > tr:first-child > td[class*=LABEL]")  # type: ignore
        assert table_label

        table_name = table_label.text
        if table_name in ("Textbooks/Materials", "Get Help"):
            log.debug("Skipping table: %s", table_name)
            continue
        else:
            log.debug("Scraping table: %s", table_name)

        assert table_name not in scraped_table_names
        scraped_table_names.add(table_name)

        table_content_selector = TABLE_CONTENT_SELECTORS.get(
            table_name, "table.PSGROUPBOX"
        )
        if table_name in TABLE_SCRAPERS:
            for table_content in table.find_elements(By.CSS_SELECTOR, table_content_selector):  # type: ignore
                if table_name not in table_results:
                    table_results[table_name] = TABLE_SCRAPERS[table_name](
                        driver, table_content
                    )
                else:
                    additional_content = TABLE_SCRAPERS[table_name](
                        driver, table_content
                    )

                    if isinstance(additional_content, dict):
                        for k, v in additional_content.items():
                            assert k not in table_results[table_name]
                            table_results[table_name][k] = v
                    elif additional_content is not None:
                        table_results[table_name] += "\n" + additional_content

            log.debug(
                "Scraped table: %s(%s)", table_label.text, table_results[table_name]
            )
        else:
            log.error(
                "No handler for table: %s(%s)",
                table_name,
                table_label.get_property("id"),  # type: ignore
            )

    log.debug("Scraped tables: %s", table_results)
    return table_results
