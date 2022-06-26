import datetime
import logging
import os
from enum import Enum
from time import sleep

from root.settings import DEBUG_SCRAPER
from spire.scraper.timer import Timer

from .spire_catalog import scrape_catalog
from .spire_driver import SpireDriver
from .spire_search import scrape_sections
from .versioned_cache import VersionedCache

try:
    from .debug_cache import debug_cache
except ImportError:
    debug_cache = None

log = logging.getLogger(__name__)

MAX_RETRIES = 10

LOG_HANDLERS = [x for x in log.handlers if x.baseFilename.startswith("scrape-")]


class ScrapeCoverage(Enum):
    Total = 0
    SubjectsAndCourses = 1
    Sections = 2


def scrape(s, func):
    start_time = datetime.datetime.now().replace(microsecond=0).isoformat()
    driver = SpireDriver()
    cache = VersionedCache() if not DEBUG_SCRAPER or debug_cache is None else debug_cache

    retries = 0
    while True:
        try:
            if not cache.is_empty:
                log.info("Scraping %s with cache: %s", s, cache)

            func(driver, cache)
            return
        except Exception as e:
            sel_driver = driver.root_driver

            if not os.path.isdir("./dump"):
                os.mkdir("./dump")

            html_dump_path = os.path.join("./dump", f"scrape-html-dump-{retries}-{start_time}.html")
            with open(html_dump_path, "w") as f:
                f.write(sel_driver.page_source.encode("utf-8"))

            retries += 1
            log.exception("Encountered an unexpected exception while scraping %s: %s", s, e)
            for handler in LOG_HANDLERS:
                handler.doRollover()

            cache.commit()
            log.debug("Cache updated to: %s", cache)
            if retries < MAX_RETRIES:
                log.info("Closing driver and sleeping...")
                driver = driver.close()
                sleep(5 * 60)

                driver = SpireDriver()
                continue
            else:
                driver.close()
                raise e


def scrape_data(coverage: ScrapeCoverage):
    log.info("Scraping data from spire...")
    log.info("Scrape coverage: %s", coverage)

    scrape_timer = Timer()

    if coverage == ScrapeCoverage.Total or coverage == ScrapeCoverage.SubjectsAndCourses:
        scrape("course catalog", scrape_catalog)

    if coverage == ScrapeCoverage.Total or coverage == ScrapeCoverage.Sections:
        scrape("course sections", scrape_sections)

    log.info("Scraped data from spire in %s", scrape_timer)
