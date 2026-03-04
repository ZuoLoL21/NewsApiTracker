import logging
import sys
from datetime import date
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.libs.models import Article
from src.libs.sentiment_analysis import Sentiment
from src.scripts.modular.generate_one_time_data import scrape

# Import topic helpers from current directory
sys.path.insert(0, str(Path(__file__).parent))
from topic_helpers import (
    migrate_legacy_tests,
    list_available_topics,
    load_topic_tests,
    save_topic_tests,
    Tests
)

logger = logging.getLogger(__name__)
load_dotenv()


def article_already_classified(article: Article, existing_tests: Tests) -> bool:
    """Check if article URL is already in the test set."""
    for test in existing_tests.tests:
        if test.input.url == article.url:
            return True
    return False


def main():
    st.set_page_config(page_title="Test Data Generator", layout="wide")

    st.title("🏷️ Sentiment Test Data Generator")
    st.markdown("Scrape articles and manually classify them for testing sentiment analyzers")
    st.markdown("---")

    # Migrate legacy tests on first run
    try:
        migration_msg = migrate_legacy_tests()
        if migration_msg:
            st.sidebar.success(migration_msg)
    except Exception as e:
        st.sidebar.error(f"Migration error: {e}")

    # Initialize session state
    if "scraped_articles" not in st.session_state:
        st.session_state.scraped_articles = None
        st.session_state.current_index = 0
        st.session_state.classified_count = 0
        st.session_state.skipped_count = 0
        st.session_state.topic = ""

    # Sidebar configuration
    st.sidebar.header("Configuration")

    # Topic selection/creation
    st.sidebar.subheader("Topic Selection")

    # Get available topics
    available_topics = list_available_topics()

    # Display existing topics
    if available_topics:
        st.sidebar.markdown("**Available Topics:**")
        for topic_meta in available_topics:
            st.sidebar.caption(f"• {topic_meta.topic} ({topic_meta.test_count} tests)")

    # Topic mode selection
    topic_mode = st.sidebar.radio(
        "Select mode:",
        ["Use Existing Topic", "Create New Topic"],
        help="Choose whether to add tests to an existing topic or create a new one"
    )

    # Get topic based on mode
    if topic_mode == "Use Existing Topic":
        if available_topics:
            topic_names = [t.topic for t in available_topics]
            selected_topic = st.sidebar.selectbox(
                "Select topic:",
                topic_names,
                help="Choose an existing topic to add more test cases"
            )
            topic = selected_topic
        else:
            st.sidebar.warning("No existing topics found. Please create a new topic.")
            topic = st.sidebar.text_input(
                "New topic name:",
                value="Cloud Computing",
                help="Enter the name for your first topic"
            )
    else:  # Create New Topic
        topic = st.sidebar.text_input(
            "New topic name:",
            value="",
            help="Enter a unique name for the new topic"
        )

        # Validate new topic name
        if topic and any(t.topic.lower() == topic.lower() for t in available_topics):
            st.sidebar.error(f"Topic '{topic}' already exists. Please choose a different name or use 'Use Existing Topic' mode.")
            topic = ""

    # Load tests for selected topic
    if topic:
        existing_tests = load_topic_tests(topic)
        st.sidebar.metric("Test Cases for This Topic", len(existing_tests.tests))
        st.sidebar.metric("Current Topic", topic)
    else:
        existing_tests = Tests(topic="", tests=[])
        st.sidebar.metric("Test Cases for This Topic", 0)

    st.sidebar.markdown("---")

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
        if existing_tests.tests:
            st.subheader("Existing Test Cases")
            st.write(f"**Topic:** {existing_tests.topic}")

            for idx, test in enumerate(existing_tests.tests[:5]):  # Show first 5
                with st.expander(f"Test {idx + 1}: {test.input.title[:60]}..."):
                    st.write(f"**Sentiment:** {test.output.value}")
                    st.write(f"**Source:** {test.input.source.name}")
                    st.write(f"**Published:** {test.input.publishedAt}")

            if len(existing_tests.tests) > 5:
                st.info(f"... and {len(existing_tests.tests) - 5} more")
        elif available_topics:
            st.subheader("Available Topics")
            st.write("Select a topic from the sidebar or create a new one to get started.")

            for topic_meta in available_topics:
                with st.expander(f"{topic_meta.topic} ({topic_meta.test_count} tests)"):
                    st.write(f"**File:** {topic_meta.file_path.name}")
                    st.write(f"**Test count:** {topic_meta.test_count}")

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
    """Save a classified article to the topic's test file."""
    from topic_helpers import Test

    # Load existing tests for this topic
    existing_tests = load_topic_tests(topic)

    # Add the new test case
    test_case = Test(input=article, output=sentiment)
    existing_tests.tests.append(test_case)

    # Ensure topic is set
    if not existing_tests.topic:
        existing_tests.topic = topic

    # Save to file
    save_topic_tests(existing_tests)

    logger.info(f"Classified article: {article.title[:50]}... as {sentiment.value} for topic '{topic}'")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s"
    )
    main()
