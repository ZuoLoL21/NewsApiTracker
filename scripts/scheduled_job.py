import logging
import sys

import schedule
import time

from dotenv import load_dotenv

from consts import LOGGING_LOCATION
from scripts.full_job import job

logger = logging.getLogger(__name__)


def run_schedule():
    schedule.every().day.at("00:05").do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)  # wait one minute


if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M",
            handlers=[
                logging.FileHandler(LOGGING_LOCATION, mode='a'),
                logging.StreamHandler(sys.stdout)
            ]
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    run_schedule()