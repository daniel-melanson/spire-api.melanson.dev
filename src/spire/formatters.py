import logging
from datetime import datetime


class ProcessTimeFormatter(logging.Formatter):
    def __init__(self):
        super().__init__("%(levelname)s %(asctime)s %(module)s - %(message)s")

        self.start_time = datetime.now()

    def formatTime(self, *_):
        elapsed = datetime.now() - self.start_time

        seconds, _ = divmod(elapsed.total_seconds() * 1000, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
