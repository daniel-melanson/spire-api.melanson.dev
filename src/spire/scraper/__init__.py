import datetime
import logging
import os
import subprocess
from enum import Enum
from textwrap import dedent
from time import sleep

from django.conf import settings

from spire.scraper.academic_calendar import scrape_academic_schedule
from spire.scraper.spire_driver import SpireDriver
from spire.scraper.spire_search import (
    ScrapeContext,
    scrape_all_terms,
    scrape_live_terms,
    scrape_single_term,
)
from spire.scraper.stats import Stats
from spire.scraper.subject_groups import SUBJECT_LETTER_GROUPS
from spire.scraper.timer import Timer
from spire.scraper.versioned_cache import VersionedCache

try:
    from .debug_cache import debug_versioned_cache
except ImportError:
    debug_versioned_cache = None

log = logging.getLogger(__name__)

BASE_DIR = settings.BASE_DIR

MAX_RETRIES = 10

LOG_HANDLERS = [x for x in log.handlers if x.get_name().startswith("scrape")]


class ScrapeCoverage(Enum):
    Total = 0
    SubjectsAndCourses = 1
    Sections = 2
    Calendar = 3


def _dump_page_source(driver: SpireDriver, name: str):
    dump_path = "/tmp/spire-api/dump"

    sel_driver = driver.root_driver
    if not os.path.isdir(dump_path):
        os.mkdir(dump_path)

    html_dump_path = os.path.join(dump_path, name)
    with open(html_dump_path, "wb") as f:
        f.write(sel_driver.page_source.encode("utf-8"))


def _dump_cache(cache):
    file_path = os.path.join(BASE_DIR, "spire", "scraper", "debug_cache.py")

    with open(file_path, "w+") as f:
        f.write(
            dedent(
                f"""
                from .versioned_cache import VersionedCache
            
                debug_versioned_cache = {cache}"""
            ).strip()
            + "\n"
        )


def _scrape(s, func, **kwargs):
    start_date = datetime.datetime.now().replace(microsecond=0).isoformat()

    stats = Stats()

    if (
        debug_versioned_cache is not None
        and settings.SCRAPER["DEBUG"]
        and debug_versioned_cache.type == s
    ):
        cache = debug_versioned_cache
    else:
        cache = VersionedCache(s)

    for round in range(MAX_RETRIES):
        driver = SpireDriver()

        try:
            if not cache.is_empty:
                log.info("Scraping %s with cache: %s", s, cache)

            func(ScrapeContext(driver, cache, stats), **kwargs)

            driver.close()
            break
        except Exception as e:
            if round == MAX_RETRIES - 1:
                raise e

            log.exception(
                "Encountered an unexpected exception while scraping %s: %s", s, e
            )

            if settings.SCRAPER["DEBUG"]:
                _dump_page_source(driver, f"scrape-html-dump-{round}-{start_date}.html")

            driver.close()

            cache.commit()
            log.debug("Cache updated to: %s", cache)

            _dump_cache(cache)

            log.info("Sleeping...")
            sleep(5 * 60)
            for h in LOG_HANDLERS:
                h.doRollover()  # type: ignore


def _dispatch_scrape_job(*args):
    ARGS = [str(x) for x in args]

    log.info("Dispatching job: %s", ARGS)

    command = f"gcloud run jobs execute spire-api-scrape-job --project spire-api --region us-east1 --args={','.join(ARGS)}"
    subprocess.check_output(command, shell=True, universal_newlines=True)

    log.info("Dispatched job.")


def _dispatch_section_scrape_job(term, subject_group):
    [season, year] = term.id.split(" ")

    _dispatch_scrape_job("--term", season, year, "--group", subject_group, "job")


def _dispatch_calendar_scrape_job():
    _dispatch_scrape_job("calendar")


def handle_scrape_dispatch():
    log.info("Handling scrape trigger...")

    log.info("Dispatching calendar scrape job...")
    _dispatch_calendar_scrape_job()

    log.info("Fetching live terms...")
    driver = SpireDriver()
    live_terms = scrape_live_terms(driver)
    driver.close()
    log.info("Fetched live terms %s", live_terms)

    for term in live_terms:
        log.info("Dispatching scrape for %s", term)

        for i in range(len(SUBJECT_LETTER_GROUPS)):
            _dispatch_section_scrape_job(term, i)


def handle_scrape_job(term, group):
    _scrape(
        "course sections",
        scrape_single_term,
        season=term[0],
        year=term[1],
        subject_letters=SUBJECT_LETTER_GROUPS[group],
    )


def handle_scrape(coverage: ScrapeCoverage, **kwargs):
    term = kwargs.get("term", None)

    log.info("Scraping data...")
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
        _scrape(
            "course sections",
            scrape_single_term if term else scrape_all_terms,
            season=term[0] if term else None,
            year=term[1] if term else None,
        )

    log.info("Scraped data in %s", scrape_timer)
