import logging
from datetime import datetime
from enum import Enum
from time import sleep

from spire.scraper.spire_catalog import scrape_catalog
from spire.scraper.spire_search import scrape_sections
from spire.scraper.SpireDriver import SpireDriver
from spire.scraper.VersionedCache import VersionedCache

log = logging.getLogger(__name__)

MAX_RETRIES = 3


class ScrapeCoverage(Enum):
    Total = 0
    SubjectsAndCourses = 1
    Sections = 2


def scrape(s, func):
    driver = SpireDriver()
    cache = VersionedCache()

    retries = 0
    while True:
        try:
            func(driver, cache)
            return
        except Exception as e:
            retries += 1
            log.exception("Encountered an unexpected exception while scraping %s: %s", s, e)

            if retries < MAX_RETRIES:
                cache.commit()
                log.info("Closing driver and sleeping...")
                driver = driver.close()
                sleep(5 * 60)

                driver = SpireDriver()
                continue
            else:
                driver.close()
                raise e


def scrape_data(coverage: ScrapeCoverage):
    for handler in log.handlers:
        if handler.baseFilename.endswith("scrape-results.log"):
            handler.doRollover()
            break

    log.info("Scraping data from spire...")
    log.info("Scrape coverage: %s", coverage)

    start = datetime.now()

    if coverage == ScrapeCoverage.Total or coverage == ScrapeCoverage.SubjectsAndCourses:
        scrape("course catalog", scrape_catalog)

    if coverage == ScrapeCoverage.Total or coverage == ScrapeCoverage.Sections:
        scrape("course sections", scrape_sections)

    diff = datetime.now() - start

    hours = diff.total_seconds() // 60 // 60
    minutes = (diff.total_seconds() - (hours * 60 * 60)) // 60

    log.info("Scraped data from spire in %s hours and %s minutes.", hours, minutes)
