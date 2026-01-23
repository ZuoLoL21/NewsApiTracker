import datetime
import logging

from src.consts import TOPICS
from src.scripts.modular import scrape, process

logger = logging.getLogger(__name__)

def job(date_to_use:datetime.date|None = None):
    if date_to_use is None:
        date_to_use = datetime.date.today()

    logger.info(f"Job started at {datetime.datetime.now()} for {date_to_use}")
    try:
        for topic in TOPICS:
            scraped = scrape(topic, date_to_use)
            process(scraped, topic)
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M"
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    job()