from celery import shared_task

from spire.scraper import scrape_data


@shared_task
def scrape(coverage, quick):
    scrape_data(coverage, quick)
