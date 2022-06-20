import logging
import re
from typing import Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .spire_driver import SpireDriver

log = logging.getLogger(__name__)


def assert_match(r, s):
    log.debug("Full matching: %s against %s", s, r)
    str_match = re.fullmatch(r, s)
    assert str_match
    return str_match


def assert_dict_keys_subset(d: dict, keys: list[str]):
    assert set(d.keys()).issubset(set(keys))


def skip_until(lst, cache, key):
    value = cache.get(key)
    if not value:
        return lst

    itr = iter(lst)

    try:
        while next(itr) != value:
            pass
    finally:
        return itr


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


def scrape_description(_, table):
    return "\n".join([e.text for e in table.find_elements(By.CSS_SELECTOR, "span")])


def scrape_spire_field_value_table(driver: SpireDriver, table: WebElement) -> list[Tuple[str, str]]:
    log.debug("Scraping field-value pairs for table...")

    details = {}

    detail_fields = []
    detail_values = {}

    field_count = 0
    value_count = 0

    matched_ids = set()

    table_id = table.get_property("id").replace("$", "\$")
    for e in driver.find_all(f"#{table_id} > tbody > tr > td > div[id^=win0div]"):
        element_id = e.get_property("id")

        try:
            child = e.find_element(By.CSS_SELECTOR, "span[class$='LABEL']")
        except:
            child = None

        if element_id in ("win0divSSR_CLS_DTL_WRK_SSR_STATUS_LONG"):
            log.debug("Skipping element id: %s.", element_id)
        elif element_id == "win0div$ICField247$0":
            log.debug("Found RAP/TAP/HCL. Scraping...")

            details["RAP/TAP/HLC"] = e.find_element(By.ID, "win0divUM_RAPTAP_CLSDT_UM_RAP_TAP$0").text

            log.debug("Adding detail: %s.", ("RAP/TAP/HLC", details["RAP/TAP/HLC"]))
        elif child:
            log.debug("Found detail field element: %s.", element_id)
            detail_fields.append((element_id, child.text))
            assert "lbl" in element_id

            field_count += 1
        else:
            log.debug("Found detail value element: %s.", element_id)
            detail_values[element_id] = e
            value_count += 1

    assert value_count == field_count
    log.debug("Scraped ids. Matching...")

    for (field_id, field_title) in detail_fields:
        if field_id in FIELD_VALUE_IDS:
            value_id = FIELD_VALUE_IDS[field_id]

            assert value_id[:-1] + "1" not in detail_values
        elif field_id.endswith("lbl$0"):
            value_id = field_id[: -len("lbl$0")] + "$0"
        elif field_id.endswith("lbl"):
            value_id = field_id[: -len("lbl")]

        if value_id in detail_values:
            assert value_id not in matched_ids
            matched_ids.add(value_id)

            log.debug("Matched %s with %s.", field_id, value_id)
            element = detail_values[value_id]
            text = element.text.strip()
            if len(text) > 0:
                log.debug("Adding detail: %s.", (field_title, element.text))
                details[field_title] = text
            else:
                log.debug("Ignoring, empty value text.")
        else:
            log.warning("Unable to find a match for %s(%s).", field_id, field_title)

    log.debug("Scraped detail for table.")
    return details


def scrape_spire_class_availability(driver, table):
    try:
        combined_table = table.find_element(By.ID, "SCTN_CMBND$scroll$0")
    except:
        combined_table = None

    if combined_table:

        def get(id):
            return driver.wait_for_presence(By.ID, id).text

        combined_sections = []
        for section in combined_table.find_elements(By.CSS_SELECTOR, "tr[id^=trSCTN_CMBND\$0_row]"):
            combined_sections.append(section.text)

        return {
            "combined_sections": combined_sections,
            "availability": {
                "individual": {
                    "capacity": get("UM_DERIVED_SR_ENRL_CAP"),
                    "enrollment_total": get("UM_DERIVED_SR_ENRL_TOT"),
                    "available_seats": get("UM_DERIVED_SR_AVAILABLE_SEATS"),
                    "wait_list_capacity": get("UM_DERIVED_SR_WAIT_CAP"),
                    "wait_list_total": get("UM_DERIVED_SR_WAIT_TOT"),
                },
                "combined": {
                    "capacity": get("SSR_CLS_DTL_WRK_ENRL_CAP"),
                    "enrollment_total": get("SSR_CLS_DTL_WRK_ENRL_TOT"),
                    "available_seats": get("SSR_CLS_DTL_WRK_AVAILABLE_SEATS"),
                    "wait_list_capacity": get("SSR_CLS_DTL_WRK_WAIT_CAP"),
                    "wait_list_total": get("SSR_CLS_DTL_WRK_WAIT_TOT"),
                },
            },
        }
    else:
        return scrape_spire_field_value_table(driver, table)


TABLE_SCRAPERS = {
    "Course Detail": scrape_spire_field_value_table,
    "Enrollment Information": scrape_spire_field_value_table,
    "Description": scrape_description,
    "Class Details": scrape_spire_field_value_table,
    "RESTRICTIONS & NOTES": scrape_spire_field_value_table,
    "Class Overview": scrape_description,
    "Class Availability": scrape_spire_class_availability,
}

TABLE_CONTENT_SELECTORS = {"Class Details": "table[id^=ACE_\$ICField][class=PABACKGROUNDINVISIBLE]"}


def scrape_spire_tables(driver: SpireDriver, table_selector: str):
    log.debug("Scraping tables...")

    scraped_table_names = set()
    table_results = {}

    for table in driver.find_all(table_selector):
        table_label = table.find_element(By.CSS_SELECTOR, "tbody > tr:first-child > td[class*=LABEL]")
        assert table_label

        table_name = table_label.text
        if table_name in ("Textbooks/Materials", "Get Help"):
            log.debug("Skipping table: %s.", table_name)
            continue
        else:
            log.debug("Scraping table: %s.", table_name)

        assert table_name not in scraped_table_names
        scraped_table_names.add(table_name)

        table_content_selector = (
            TABLE_CONTENT_SELECTORS[table_name]
            if table_name in TABLE_CONTENT_SELECTORS
            else "table.PSGROUPBOX"
        )
        if table_name in TABLE_SCRAPERS:
            for table_content in table.find_elements(By.CSS_SELECTOR, table_content_selector):
                if table_name not in table_results:
                    table_results[table_name] = TABLE_SCRAPERS[table_name](driver, table_content)
                else:
                    additional_content = TABLE_SCRAPERS[table_name](driver, table_content)

                    if isinstance(additional_content, dict):
                        for k, v in additional_content.items():
                            assert k not in table_results[table_name]
                            table_results[table_name][k] = v
                    else:
                        table_results[table_name] += "\\n" + additional_content

            log.debug("Scraped table: %s(%s)", table_label.text, table_results[table_name])
        else:
            log.error("No handler for table: %s(%s)", table_name, table_label.get_property("id"))

    log.debug("Scraped tables.")
    return table_results
