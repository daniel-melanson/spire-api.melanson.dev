import logging
import re
from time import sleep

import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException
from unidecode import unidecode

log = logging.getLogger(__name__)


def clean_text(s: str) -> str:
    s = s.strip()

    while (match := re.search(r"\s{2,}", s)) is not None:
        span = match.span(0)

        s = s[: span[0]] + " " + s[span[1] :]

    return s


def fetch(url: str) -> requests.Response:
    log.debug("Fetching %s...", url)
    attempts = 0
    while True:
        try:
            res = requests.get(url)
            log.debug("Successfully fetched %s.", url)
            break
        except RequestException as exception:
            attempts += 1
            if attempts < 5:
                log.exception("Failed to fetch %s: %s.", url, exception)
                log.info("Sleeping...")
                sleep(5)
            else:
                raise exception

    return res


def get_soup(res: requests.Response) -> BeautifulSoup:
    return BeautifulSoup(res.content, "html5lib")


def fetch_soup(url: str) -> BeautifulSoup:
    return get_soup(fetch(url))


def get_tag_text(tag: Tag, decode=False):
    text = clean_text(tag.text)

    return unidecode(text) if decode else text
