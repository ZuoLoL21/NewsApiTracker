import argparse
import logging

from consts import SCRAPING_END_DATE
from scripts.initialize_database import fill_database
from scripts.scheduled_job import run_schedule

parser = argparse.ArgumentParser(
        prog="News Tracker",
        description=""" 
        A tool that scrapes NewsAPI and stores the data within a timescale_db\n
        It also has a way to easily display (streamlit run visual/database_visualizer.py)
        """
)
parser.add_argument('-s', '--scrape', type=int, help="If entered, will scrape as many days as stated (enter -1 for all)")
parser.add_argument('-m', '--maintain', action='store_true', help="If entered, will maintain the database by running the tool everyday")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    args = parser.parse_args()

    if args.scrape:
        fill_database(SCRAPING_END_DATE, args.scrape if args.scrape != -1 else None)

    if args.maintain:
        run_schedule()
