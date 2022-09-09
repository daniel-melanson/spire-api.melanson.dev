import logging
import re
from datetime import date
from typing import NamedTuple

from django.db import transaction
from scraper.shared import fetch_soup, get_tag_text

from spire.models import Term, TermEvent

log = logging.getLogger(__name__)


class Event(NamedTuple):
    term: Term
    date: date
    description: str


SEASON_LIST = ["Spring", "Summer", "Winter", "Fall"]


def get_or_create_term(season, year):
    log.debug("Making or finding term: %s %s", season, year)

    year = int(year)

    assert type(season) is str and season in SEASON_LIST
    assert 2000 <= year <= 2100

    return Term.objects.get_or_create(
        season=season, year=year, defaults={ordinal: int(str(year) + str(SEASON_LIST.index(season)))}
    )

def clean_text(s):
    s = s.strip()

    while (match := re.search(r"\s{2,}", s)):
        span = match.span(0)

        s = s[: span[0]] + " " + s[span[1] :]

    return s

def get_tag_text(tag, decode):
    text = clean_text(tag.text)

    return decode(text) if decode else text


def scrape_academic_schedule():
    log.info("Scraping academic schedule...")
    soup = fetch_soup("https://www.umass.edu/registrar/calendars/academic-calendar")

    for header in soup.select(".field-item h3"):
        semester_title = get_tag_text(header, decode=True)

        log.debug("Scraping term events: %s", semester_title)
        match = re.match(r"^(University )?(Spring|Summer|Fall|Winter) (\d{4})", semester_title)
        if not match:
            log.debug("Header '%s' does not match, skipping.", semester_title)
            continue

        year = match.group(3)
        season = match.group(2)

        term = get_or_create_term(season, year)

        event_list = []
        log.debug("Scraping events for: %s", term)

        table = header.find_next("table")
        for event_element in table.select("tr"):
            event_text = get_tag_text(event_element, decode=True)

            log.debug("Got event: %s", event_text)
            event_match = re.match(
                r"^(.+) (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})$",
                event_text,
                re.I,
            )
            assert event_match

            event_desc = event_match.group(1)
            event_month = event_match.group(3)
            event_day = event_match.group(4)

            log.debug("Scraped event: %s %s - %s", event_month, event_day, event_desc)

            adjusted_year = year
            if season == "winter" and event_month in ("January", "February"):
                adjusted_year = str(int(year) + 1)
                log.info("Adjusted year to %s", adjusted_year)

            event_date = date(adjusted_year, event_month, event_day)

            if re.match(event_desc, "First day of classes", re.I):
                log.debug("Selecting event as start date.")
                term.start_date = event_date
                term.save()
            elif re.match(event_desc, "Last day of classes", re.I):
                log.debug("Selecting event as end date.")
                term.end_date = event_date
                term.save()

            event = Event(term, event_date, event_desc)

            log.debug("Adding event: %s", event)
            event_list.append(event)

        with transaction.atomic():
            dropped, _ = TermEvent.objects.filter(term=term).delete()
            log.debug("Dropped %s TermEvents in preparation to push %s new ones.", dropped, len(event_list))

            pushed_list = TermEvent.objects.bulk_create(event_list)
            log.info("Pushed %s new events.", len(pushed_list))

    log.info("Scraped academic schedule.")
