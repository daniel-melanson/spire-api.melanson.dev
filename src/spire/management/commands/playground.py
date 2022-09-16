from django.core.management.base import BaseCommand

from spire.scraper.classes.buildings.raw_building import get_raw_building_room


class Command(BaseCommand):
    help = "Testing for queries."

    def handle(self, *args, **options):

        matched_out = open("./matched", "w")
        unmatched_out = open("./unmatched", "w")

        with open("./possible_rooms", "r") as f:
            matched = 0
            total = 0
            for line in f:
                line = line.strip()
                total += 1

                match = get_raw_building_room(line)
                if not match.endswith("None"):
                    matched += 1

                print(match, file=matched_out if not match.endswith("None") else unmatched_out)

        print(matched / total, file=matched_out)
        print((total - matched) / total, file=unmatched_out)
