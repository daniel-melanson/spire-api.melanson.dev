from django.core.management.base import BaseCommand, CommandError

from spire.scraper import (
    ScrapeCoverage,
    handle_scrape,
    handle_scrape_dispatch,
    handle_scrape_job,
)


class Command(BaseCommand):
    help = "Does a clean scrape of all courses from the Spire course catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--term", type=str, nargs=2, help="A specific term of sections to scrape."
        )

        parser.add_argument(
            "--group",
            type=int,
            help="The subject group to scrape.",
        )

        parser.add_argument("--quick", action="store_true")

        parser.add_argument(
            "mode",
            type=str,
            default="all",
            choices=("all", "dispatch", "job", "sections", "courses", "calendar"),
            help="The data the scraper should scrape.",
        )

    def handle(self, *args, **options):
        match options["mode"]:
            case "dispatch":
                return handle_scrape_dispatch()
            case "job":
                term = options["term"]
                assert term

                group = options["group"]
                assert group

                return handle_scrape_job(term, group)
            case "all":
                enum = ScrapeCoverage.Total
            case "sections":
                enum = ScrapeCoverage.Sections
            case "courses":
                enum = ScrapeCoverage.SubjectsAndCourses
            case "calendar":
                enum = ScrapeCoverage.Calendar
            case _:
                raise CommandError("Unexpected mode option.")

        handle_scrape(enum, **options)
