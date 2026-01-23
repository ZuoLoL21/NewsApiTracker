import datetime
import logging

import schedule
import time

from dotenv import load_dotenv

from consts import TOPICS, LOGGING_LOCATION
from scripts.modular import scrape, process

logger = logging.getLogger(__name__)
load_dotenv()

def job():
    logger.info(f"Job started at {datetime.datetime.now()}")

    today = datetime.date.today()
    try:
        for topic in TOPICS:
            scraped = scrape(topic, today)
            process(scraped, topic)
    except Exception as e:
        logger.error(e)


def run_schedule():
    schedule.every().day.at("23:55").do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)  # wait one minute


if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M",
            handlers=[
                logging.FileHandler(LOGGING_LOCATION, mode='a') # Use 'a' for append mode
            ]
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    job()