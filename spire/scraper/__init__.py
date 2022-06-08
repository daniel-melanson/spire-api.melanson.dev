import logging
from datetime import datetime
from logging import DEBUG
from typing import Optional, TypedDict

from scraper.spire_catalog import SpireCourse, SpireSubject, scrape_catalog
from scraper.spire_search import SpireSection, scrape_sections
from scraper.SpireDriver import SpireDriver

log = logging.getLogger(__name__)
log.setLevel(DEBUG)

SCRAPE_RESULT_VERSION = 1


class ScrapeData(TypedDict):
    subjects: Optional[list[SpireSubject]]
    courses: Optional[list[SpireCourse]]
    sections: Optional[list[SpireSection]]


class ScrapeResult(TypedDict):
    version: int
    coverage: str
    date: datetime
    duration: int
    section_coverage: str
    data: ScrapeData


def scrape_data(coverage: str) -> ScrapeResult:
    log.info("Scraping data from spire...")

    start = datetime.now()

    driver = SpireDriver()

    subjects = None
    courses = None
    if coverage in ("TOTAL", "COURSES"):
        try:
            (subjects, courses) = scrape_catalog(driver)
        except Exception as e:
            log.exception("Failed while scraping course catalog: %s", e)
            driver.close()
            raise e

    sections = None
    first_scraped_term = None
    if coverage in ("TOTAL", "SECTIONS"):
        try:
            (sections, first_scraped_term) = scrape_sections(driver)
        except Exception as e:
            log.exception("Failed while scraping sections: %s", e)
            driver.close()
            raise e

    driver.close()

    diff = datetime.now() - start

    hours = diff.total_seconds() // 60 // 60
    minutes = (diff.total_seconds() - (hours * 60 * 60)) // 60

    log.info("Scraped data from spire in %s hours and %s minutes.", hours, minutes)
    return ScrapeResult(
        version=SCRAPE_RESULT_VERSION,
        coverage=coverage,
        date=start.isoformat(),
        duration=f"{hours} hour{'s' if hours > 1 else ''}, {minutes} minutes",
        section_coverage=first_scraped_term if first_scraped_term else "N/A",
        data=ScrapeData(subjects=subjects, courses=courses, sections=sections),
    )
