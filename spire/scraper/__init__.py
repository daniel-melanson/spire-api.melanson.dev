import logging
from datetime import datetime
from enum import Enum
from typing import Union

from spire.scraper.spire_catalog import scrape_catalog
from spire.scraper.spire_search import scrape_sections
from spire.scraper.SpireDriver import SpireDriver

log = logging.getLogger(__name__)


class ScrapeCoverage(Enum):
    Total = 0
    SubjectsAndCourses = 1
    Sections = 2


def scrape_data(coverage: ScrapeCoverage):
    for handler in log.handlers:
        if handler.baseFilename.endswith("scrape-results.log"):
            handler.doRollover()
            break

    log.info("Scraping data from spire...")
    log.info("Scrape coverage: %s", coverage)

    start = datetime.now()

    driver = SpireDriver()

    if coverage == ScrapeCoverage.Total or coverage == ScrapeCoverage.SubjectsAndCourses:
        try:
            scrape_catalog(driver)
        except Exception as e:
            log.exception("Failed while scraping course catalog: %s", e)
            driver.close()
            raise e

    if coverage == ScrapeCoverage.Total or coverage == ScrapeCoverage.Sections:
        try:
            scrape_sections(driver, coverage.section_terms)
        except Exception as e:
            log.exception("Failed while scraping sections: %s", e)
            driver.close()
            raise e

    driver.close()

    diff = datetime.now() - start

    hours = diff.total_seconds() // 60 // 60
    minutes = (diff.total_seconds() - (hours * 60 * 60)) // 60

    log.info("Scraped data from spire in %s hours and %s minutes.", hours, minutes)
