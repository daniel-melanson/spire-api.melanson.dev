import logging
from datetime import datetime
from logging import DEBUG
from logging.handlers import RotatingFileHandler
from typing import NamedTuple

from scraper.spire_catalog import scrape_catalog
from scraper.spire_search import scrape_sections
from scraper.SpireDriver import SpireDriver

log = logging.getLogger(__name__)


class ScrapeCoverage(NamedTuple):
    subjects_and_courses: bool
    section_terms: tuple[str]


def scrape_data(coverage: ScrapeCoverage):
    for handler in log.handlers:
        if handler.baseFilename.endswith("scrape-results.log"):
            handler.doRollover()
            break

    log.info("Scraping data from spire...")
    log.info("Scrape coverage: %s", coverage)

    start = datetime.now()

    driver = SpireDriver()

    if coverage.subjects_and_courses:
        try:
            scrape_catalog(driver)
        except Exception as e:
            log.exception("Failed while scraping course catalog: %s", e)
            driver.close()
            raise e

    if len(coverage.section_terms) > 0:
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
