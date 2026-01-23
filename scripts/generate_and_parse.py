import datetime
import logging

import schedule
import time

from dotenv import load_dotenv

from consts import TOPICS
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
        level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s"
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    job()