import datetime
import logging
import sys

from consts import LOGGING_LOCATION
from scripts.full_job import job

logger = logging.getLogger(__name__)


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

    date_to_use = datetime.date.today()
    try:
        while True:
            job(date_to_use=date_to_use)
            date_to_use -= datetime.timedelta(days=1)

    except Exception as e:
        logger.error(e)
