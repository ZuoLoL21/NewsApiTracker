import os
from datetime import datetime
import psycopg2
from libs.models import Article
from libs.sentiment_analysis.base import Sentiment
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    """Get a connection to the PostgreSQL/TimescaleDB database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def add_to_db(article: Article, sentiment: Sentiment, topic: str) -> None:
    """
    Add an article with its sentiment to the TimescaleDB warehouse.

    Args:
        article: The article to store
        sentiment: The sentiment analysis result
        topic: The topic this article relates to
    """
    try:
        # Parse the published date
        published_at = datetime.fromisoformat(article.publishedAt.replace('Z', '+00:00'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert article with sentiment (ON CONFLICT to handle duplicates by URL)
        insert_query = """
            INSERT INTO articles (
                topic, published_at, source_name, author,
                title, description, url, url_to_image, content, sentiment
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (url) DO UPDATE SET
                sentiment = EXCLUDED.sentiment,
                created_at = NOW()
        """

        cursor.execute(insert_query, (
            topic,
            published_at,
            article.source.name,
            article.author,
            article.title,
            article.description,
            article.url,
            article.urlToImage,
            article.content,
            sentiment.value
        ))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Added article to DB: {article.title} with sentiment: {sentiment.value}")

    except Exception as e:
        logger.error(f"Error adding article to database: {e}")
        raise