import json
import logging
import sys
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libs.models import Article
from libs.sentiment_analysis.base import Sentiment
from scripts.modular.generate_one_time_data import scrape

logger = logging.getLogger(__name__)
load_dotenv()

TESTS_FILE = Path(__file__).parent / "tests.json"


def load_existing_tests():
    """Load existing test cases from tests.json."""
    if TESTS_FILE.exists():
        with open(TESTS_FILE, 'r') as f:
            return json.load(f)
    return {"topic": "", "tests": []}


def save_tests(tests_data):
    """Save test cases to tests.json."""
    with open(TESTS_FILE, 'w') as f:
        json.dump(tests_data, f, indent=2)


def article_already_classified(article: Article, existing_tests: dict) -> bool:
    """Check if article URL is already in the test set."""
    for test in existing_tests.get("tests", []):
        if test["input"].get("url") == article.url:
            return True
    return False


def main():
    st.set_page_config(page_title="Test Data Generator", layout="wide")

    st.title("🏷️ Sentiment Test Data Generator")
    st.markdown("Scrape articles and manually classify them for testing sentiment analyzers")
    st.markdown("---")

    # Initialize session state
    if "scraped_articles" not in st.session_state:
        st.session_state.scraped_articles = None
        st.session_state.current_index = 0
        st.session_state.classified_count = 0
        st.session_state.skipped_count = 0
        st.session_state.topic = ""

    # Sidebar configuration
    st.sidebar.header("Configuration")

    # Load existing tests
    existing_tests = load_existing_tests()

    st.sidebar.metric("Existing Test Cases", len(existing_tests.get("tests", [])))
    st.sidebar.metric("Current Topic", existing_tests.get("topic", "Not set"))

    # Topic input
    topic = st.sidebar.text_input(
        "Topic to scrape",
        value=existing_tests.get("topic", "Cloud Computing"),
        help="Enter the topic you want to scrape articles about"
    )

    # Days back input
    days_back = st.sidebar.number_input(
        "Days back to search",
        min_value=1,
        max_value=30,
        value=1,
        help="How many days back to search for articles"
    )

    # Scrape button
    if st.sidebar.button("🔍 Scrape Articles", type="primary"):
        with st.spinner(f"Scraping articles about '{topic}'..."):
            try:
                scraped_data = scrape(topic, date.today())
                st.session_state.scraped_articles = scraped_data.articles
                st.session_state.current_index = 0
                st.session_state.classified_count = 0
                st.session_state.skipped_count = 0
                st.session_state.topic = topic

                # Filter out already classified articles
                unclassified = [
                    a for a in st.session_state.scraped_articles
                    if not article_already_classified(a, existing_tests)
                ]
                st.session_state.scraped_articles = unclassified

                st.sidebar.success(f"Found {len(unclassified)} new articles!")
            except Exception as e:
                st.sidebar.error(f"Error scraping: {e}")
                logger.error(f"Scraping error: {e}", exc_info=True)

    st.sidebar.markdown("---")

    # Show progress
    if st.session_state.scraped_articles:
        total = len(st.session_state.scraped_articles)
        current = st.session_state.current_index
        st.sidebar.progress(current / total if total > 0 else 0)
        st.sidebar.metric("Progress", f"{current} / {total}")
        st.sidebar.metric("Classified", st.session_state.classified_count)
        st.sidebar.metric("Skipped", st.session_state.skipped_count)

    # Main content area
    if st.session_state.scraped_articles is None:
        st.info("👈 Configure settings and click 'Scrape Articles' to begin")

        # Show existing tests
        if existing_tests.get("tests"):
            st.subheader("Existing Test Cases")
            st.write(f"**Topic:** {existing_tests['topic']}")

            for idx, test in enumerate(existing_tests["tests"][:5]):  # Show first 5
                with st.expander(f"Test {idx + 1}: {test['input']['title'][:60]}..."):
                    st.write(f"**Sentiment:** {test['output']}")
                    st.write(f"**Source:** {test['input']['source']['name']}")
                    st.write(f"**Published:** {test['input']['publishedAt']}")

            if len(existing_tests["tests"]) > 5:
                st.info(f"... and {len(existing_tests['tests']) - 5} more")

    elif st.session_state.current_index >= len(st.session_state.scraped_articles):
        st.success("🎉 All articles processed!")
        st.metric("Total Classified", st.session_state.classified_count)
        st.metric("Total Skipped", st.session_state.skipped_count)

        if st.button("Start Over"):
            st.session_state.scraped_articles = None
            st.session_state.current_index = 0
            st.rerun()

    else:
        # Show current article
        article = st.session_state.scraped_articles[st.session_state.current_index]

        st.subheader(f"Article {st.session_state.current_index + 1} of {len(st.session_state.scraped_articles)}")

        # Article details in columns
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### {article.title}")
            st.markdown(f"**Source:** {article.source.name}")
            st.markdown(f"**Author:** {article.author or 'Unknown'}")
            st.markdown(f"**Published:** {article.publishedAt}")

            if article.urlToImage:
                try:
                    st.image(article.urlToImage, width='stretch')
                except:
                    pass

            st.markdown("**Description:**")
            st.write(article.description or "No description available")

            if article.content:
                with st.expander("View Full Content"):
                    st.write(article.content)

            if article.url:
                st.markdown(f"[🔗 Read Full Article]({article.url})")

        with col2:
            st.markdown("### Classify Sentiment")
            st.markdown(f"**Context:** {st.session_state.topic}")
            st.info("Consider the article's sentiment specifically in relation to the topic")

            # Classification buttons
            st.markdown("**Select Sentiment:**")

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("✅ Positive", width='stretch', type="primary"):
                    save_classification(article, Sentiment.POSITIVE, st.session_state.topic)
                    st.session_state.classified_count += 1
                    st.session_state.current_index += 1
                    st.rerun()

                if st.button("❌ Negative", width='stretch', type="primary"):
                    save_classification(article, Sentiment.NEGATIVE, st.session_state.topic)
                    st.session_state.classified_count += 1
                    st.session_state.current_index += 1
                    st.rerun()

            with col_b:
                if st.button("➖ Neutral", width='stretch', type="primary"):
                    save_classification(article, Sentiment.NEUTRAL, st.session_state.topic)
                    st.session_state.classified_count += 1
                    st.session_state.current_index += 1
                    st.rerun()

                if st.button("❓ Unknown", width='stretch', type="primary"):
                    save_classification(article, Sentiment.UNKNOWN, st.session_state.topic)
                    st.session_state.classified_count += 1
                    st.session_state.current_index += 1
                    st.rerun()

            st.markdown("---")

            if st.button("⏭️ Skip Article", width='stretch'):
                st.session_state.skipped_count += 1
                st.session_state.current_index += 1
                st.rerun()

            st.markdown("---")
            st.markdown("**Sentiment Guidelines:**")
            st.caption("**Positive:** Article portrays the topic favorably")
            st.caption("**Negative:** Article portrays the topic unfavorably")
            st.caption("**Neutral:** Article is objective/factual about the topic")
            st.caption("**Unknown:** Cannot determine sentiment or not relevant")


def save_classification(article: Article, sentiment: Sentiment, topic: str):
    """Save a classified article to tests.json."""
    existing_tests = load_existing_tests()

    # Update topic if it's different
    if not existing_tests.get("topic"):
        existing_tests["topic"] = topic

    # Add the new test case
    test_case = {
        "input": article.model_dump(),
        "output": sentiment.value
    }

    existing_tests.setdefault("tests", []).append(test_case)

    # Save to file
    save_tests(existing_tests)

    logger.info(f"Classified article: {article.title[:50]}... as {sentiment.value}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s"
    )
    main()
