import calendar
import logging
import re
from datetime import date

from bs4 import Tag
from django.db import transaction

from spire.models import Term, TermEvent
from spire.scraper.shared import SEASON_LIST, get_or_create_term
from spire.scraper.web import fetch_soup, get_tag_text

log = logging.getLogger(__name__)

MONTH_NUMBERS = {name: i for i, name in enumerate(calendar.month_name)}


def scrape_academic_schedule():
    log.info("Scraping academic schedule...")
    soup = fetch_soup("https://www.umass.edu/registrar/calendars/academic-calendar")

    for header in soup.select("p > strong"):
        assert header.parent
        semester_title = get_tag_text(header.parent, decode=True)

        log.debug("Scraping term events: %s", semester_title)
        match = re.match(
            r"((University|UWW) )?(Spring|Summer|Fall|Winter) (\d{4})",
            semester_title,
        )
        if not match:
            log.debug("Header '%s' does not match, skipping.", semester_title)
            continue

        year = match.group(4)
        season = match.group(3)

        is_uww = "uww" in semester_title.lower()
        if is_uww:
            assert season == "Summer"
            season = "UWW Summer"

        term = get_or_create_term(season, year)

        event_list = []
        log.debug("Scraping events for: %s", term)

        table = header.find_next("table")
        assert type(table) is Tag

        for event_element in table.select("tr"):
            event_text = get_tag_text(event_element, decode=True)

            log.debug("Got event: %s", event_text)
            event_match = re.match(
                r"^(.+)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})$",
                event_text,
                re.I,
            )
            assert event_match

            event_desc = event_match.group(1)
            event_month = event_match.group(3)
            event_day = event_match.group(4)

            log.debug("Scraped event: %s %s - %s", event_month, event_day, event_desc)

            adjusted_year = int(year)
            if season == "winter" and event_month in ("January", "February"):
                adjusted_year += 1
                log.info("Adjusted year to %s", adjusted_year)

            event_date = date(adjusted_year, MONTH_NUMBERS[event_month], int(event_day))

            if re.match(
                (
                    "First day of classes - Session One"
                    if is_uww
                    else "First day of classes"
                ),
                event_desc,
                re.I,
            ):
                log.debug("Selecting event as start date.")
                term.start_date = event_date
                term.save()
            elif re.search(
                "Summer Term Ends" if is_uww else "Last day of classes",
                event_desc,
                re.I,
            ):
                log.debug("Selecting event as end date.")
                term.end_date = event_date
                term.save()

            event = TermEvent(term=term, date=event_date, description=event_desc)

            log.debug("Adding event: %s", event)
            event_list.append(event)

        with transaction.atomic():
            dropped, _ = TermEvent.objects.filter(term=term).delete()
            log.debug(
                "Dropped %s TermEvents in preparation to push %s new ones.",
                dropped,
                len(event_list),
            )

            pushed_list = TermEvent.objects.bulk_create(event_list)
            log.info("Pushed %s new events.", len(pushed_list))

    log.info("Scraped academic schedule.")
