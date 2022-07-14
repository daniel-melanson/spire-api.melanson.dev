from django.core.management.base import BaseCommand, CommandError

from spire.scraper import ScrapeCoverage, scrape_data


class Command(BaseCommand):
    help = "Does a clean scrape of all courses from the Spire course catalog."

    def add_arguments(self, parser):
        parser.add_argument("coverage", nargs=1, type=str, choices=("total", "sections", "courses"))

        parser.add_argument("--quick", action="store_true")

    def handle(self, *args, **options):
        match options["coverage"][0]:
            case "total":
                enum = ScrapeCoverage.Total
            case "sections":
                enum = ScrapeCoverage.Sections
            case "courses":
                enum = ScrapeCoverage.SubjectsAndCourses
            case _:
                raise CommandError("Unexpected coverage option.")

        scrape_data(enum, quick=options["quick"])
