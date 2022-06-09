import root.settings
from spire.scraper import ScrapeCoverage, scrape_data


def main():
    scrape_data(ScrapeCoverage.TOTAL)


if __name__ == "__main__":
    main()
