from django.core.management.base import BaseCommand, CommandError

from spire.scraper import ScrapeCoverage, scrape_data


class Command(BaseCommand):
    help = "Does a clean scrape of all courses from the Spire course catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--distributed",
            action="store_true",
            help="Whether the section scraper should run in distributed mode.",
        )

        parser.add_argument(
            "--term", type=str, nargs=2, help="A specific term of sections to scrape."
        )

        parser.add_argument("--quick", action="store_true")

        parser.add_argument(
            "coverage",
            nargs=1,
            type=str,
            default="all",
            choices=("all", "sections", "courses", "calendar"),
            help="The data the scraper should scrape.",
        )

    def handle(self, *args, **options):
        match options["coverage"][0]:
            case "all":
                enum = ScrapeCoverage.Total
            case "sections":
                enum = ScrapeCoverage.Sections
            case "courses":
                enum = ScrapeCoverage.SubjectsAndCourses
            case "calendar":
                enum = ScrapeCoverage.Calendar
            case _:
                raise CommandError("Unexpected coverage option.")

        del options["coverage"]
        scrape_data(enum, **options)
