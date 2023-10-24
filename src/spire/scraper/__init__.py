import datetime
import logging
import os
from enum import Enum
from textwrap import dedent
from time import sleep

from django.conf import settings

from spire.scraper.academic_calendar import scrape_academic_schedule
from spire.scraper.spire_catalog import scrape_catalog
from spire.scraper.spire_driver import SpireDriver
from spire.scraper.spire_search import scrape_all_sections
from spire.scraper.timer import Timer
from spire.scraper.versioned_cache import VersionedCache

try:
    from .debug_cache import debug_versioned_cache
except ImportError:
    debug_versioned_cache = None

log = logging.getLogger(__name__)

MAX_RETRIES = 10

LOG_HANDLERS = [x for x in log.handlers if x.get_name().startswith("scrape")]


class ScrapeCoverage(Enum):
    Total = 0
    SubjectsAndCourses = 1
    Sections = 2
    Calendar = 3


def scrape(s, func, **kwargs):
    start_date = datetime.datetime.now().replace(microsecond=0).isoformat()
    driver = SpireDriver()
    if (
        debug_versioned_cache is not None
        and settings.SCRAPER["DEBUG"]
        and debug_versioned_cache.type == s
    ):
        cache = debug_versioned_cache
    else:
        cache = VersionedCache(s)

    retries = 0
    while True:
        try:
            if not cache.is_empty:
                log.info("Scraping %s with cache: %s", s, cache)

            func(driver, cache, **kwargs)
            return
        except Exception as e:
            log.exception(
                "Encountered an unexpected exception while scraping %s: %s", s, e
            )
            retries += 1

            if settings.SCRAPER["DEBUG"]:
                sel_driver = driver.root_driver
                if not os.path.isdir("./logs/dump"):
                    os.mkdir("./logs/dump")

                html_dump_path = os.path.join(
                    "./logs/dump", f"scrape-html-dump-{retries}-{start_date}.html"
                )
                with open(html_dump_path, "wb") as f:
                    f.write(sel_driver.page_source.encode("utf-8"))

            cache.commit()
            log.debug("Cache updated to: %s", cache)
            with open("./src/spire/scraper/debug_cache.py", "w") as f:
                f.write(
                    dedent(
                        f"""
                        from .versioned_cache import VersionedCache
                    
                        debug_versioned_cache = {cache}"""
                    ).strip()
                    + "\n"
                )

            if retries >= MAX_RETRIES:
                driver.close()
                raise e

            log.info("Closing driver and sleeping...")
            driver = driver.close()
            sleep(5 * 60)
            for h in LOG_HANDLERS:
                h.doRollover()  # type: ignore

            driver = SpireDriver()


def scrape_data(coverage: ScrapeCoverage, quick=False):
    log.info("Scraping data from spire...")
    log.info("Scrape coverage: %s", coverage)

    scrape_timer = Timer()

    if coverage == ScrapeCoverage.Total or coverage == ScrapeCoverage.Calendar:
        scrape_academic_schedule()

    # if (
    #     coverage == ScrapeCoverage.Total
    #     or coverage == ScrapeCoverage.SubjectsAndCourses
    # ):
    #     scrape("course catalog", scrape_catalog)

    if coverage == ScrapeCoverage.Total or coverage == ScrapeCoverage.Sections:
        scrape("course sections", scrape_all_sections, quick=quick)

    log.info("Scraped data from spire in %s", scrape_timer)