import datetime
import logging
import os
from enum import Enum
from textwrap import dedent
from time import sleep

from django.conf import settings
from google.cloud.run_v2 import JobsClient
from google.cloud.run_v2.types import RunJobRequest

from spire.scraper.academic_calendar import scrape_academic_schedule
from spire.scraper.spire_driver import SpireDriver
from spire.scraper.spire_search import (
    ScrapeContext,
    scrape_all_terms,
    scrape_live_terms,
    scrape_single_term,
)
from spire.scraper.stats import Stats
from spire.scraper.subject_groups import SUBJECT_GROUPS
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


def _dump_page_source(driver: SpireDriver, name: str):
    sel_driver = driver.root_driver
    if not os.path.isdir("./logs/dump"):
        os.mkdir("./logs/dump")

    html_dump_path = os.path.join("./logs/dump", name)
    with open(html_dump_path, "wb") as f:
        f.write(sel_driver.page_source.encode("utf-8"))


def _dump_cache(cache):
    with open("./src/spire/scraper/debug_cache.py", "w+") as f:
        f.write(
            dedent(
                f"""
                from .versioned_cache import VersionedCache
            
                debug_versioned_cache = {cache}"""
            ).strip()
            + "\n"
        )


def _scrape(s, func, **kwargs):
    stats = Stats()
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

            driver.switch()
            func(ScrapeContext(driver, cache, stats), **kwargs)
        except Exception as e:
            driver.close()

            retries += 1
            if retries >= MAX_RETRIES:
                raise e

            log.exception(
                "Encountered an unexpected exception while scraping %s: %s", s, e
            )

            if settings.SCRAPER["DEBUG"]:
                _dump_page_source(
                    driver, f"scrape-html-dump-{retries}-{start_date}.html"
                )

            cache.commit()
            log.debug("Cache updated to: %s", cache)

            _dump_cache(cache)

            log.info("Sleeping...")
            sleep(5 * 60)
            for h in LOG_HANDLERS:
                h.doRollover()  # type: ignore

            driver = SpireDriver()


def _dispatch_scrape_job(term, subject_group):
    [season, year] = term.split(" ")
    run_client = JobsClient()

    request = RunJobRequest(
        name="projects/spire-api/locations/us-east1/jobs/spire-api-scrape-job",
        overrides=RunJobRequest.Overrides(
            container_overrides=RunJobRequest.Overrides.ContainerOverride(
                args=[
                    "python",
                    "manage.py",
                    "job",
                    "--term",
                    season,
                    year,
                    "--group",
                    subject_group,
                ],
                clear_args=True,
            )
        ),
    )

    result = run_client.run_job(request=request)
    log.info("Dispatched scrape job: %s", result)


def handle_scrape_dispatch():
    log.info("Handling scrape trigger...")
    driver = SpireDriver()

    log.info("Fetching live terms")
    for term in scrape_live_terms(driver):
        log.info("Dispatcing scrape for term: %s", term)

        for i in range(len(SUBJECT_GROUPS)):
            _dispatch_scrape_job(term, i)


def handle_scrape_job(term, group):
    _scrape(
        "course sections",
        scrape_single_term,
        season=term[0],
        year=term[1],
        subjects=SUBJECT_GROUPS[group],
        quick=True,
    )


def handle_scrape(coverage: ScrapeCoverage, **kwargs):
    quick = kwargs.get("quick", False)
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
            quick=quick,
        )

    log.info("Scraped data in %s", scrape_timer)
