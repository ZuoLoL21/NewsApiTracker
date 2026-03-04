"""
Utilities for managing multi-topic sentiment analysis test datasets.

This module provides functions for:
- Converting topic names to filesystem-safe slugs
- Managing topic-specific test file paths
- Discovering available topics
- Migrating legacy test data
"""

import re
import sys
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.libs.local_helpers.pydantic_helpers import save_model, load_model
from src.libs.models import Article
from src.libs.sentiment_analysis.base import Sentiment


class Test(BaseModel):
    """A single test case with input article and expected sentiment."""
    input: Article
    output: Sentiment


class Tests(BaseModel):
    """Collection of test cases for a specific topic."""
    topic: str
    tests: List[Test]


class TopicTestMetadata(BaseModel):
    """Metadata about a topic's test dataset."""
    topic: str
    file_path: Path
    test_count: int
    slug: str


def topic_to_slug(topic: str) -> str:
    """
    Convert a topic name to a filesystem-safe slug.

    Examples:
        "Cloud Computing" -> "cloud-computing"
        "AI & Machine Learning" -> "ai-machine-learning"
        "IoT/Edge Computing" -> "iot-edge-computing"

    Args:
        topic: The topic name to convert

    Returns:
        A lowercase, hyphenated slug safe for use in filenames
    """
    # Replace special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', topic.lower())
    # Replace whitespace with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Strip leading/trailing hyphens
    slug = slug.strip('-')

    return slug


def get_tests_directory() -> Path:
    """Get the path to the tests directory, creating it if needed."""
    tests_dir = Path(__file__).parent / "tests"
    tests_dir.mkdir(exist_ok=True)
    return tests_dir


def get_topic_file_path(topic: str) -> Path:
    """
    Get the file path for a topic's test data.

    Args:
        topic: The topic name

    Returns:
        Path to the topic's JSON test file
    """
    slug = topic_to_slug(topic)
    return get_tests_directory() / f"{slug}.json"


def list_available_topics() -> List[TopicTestMetadata]:
    """
    Discover all available topic test files.

    Returns:
        List of metadata for each available topic, sorted by topic name
    """
    tests_dir = get_tests_directory()

    if not tests_dir.exists():
        return []

    topics = []

    for test_file in tests_dir.glob("*.json"):
        try:
            # Load the test file to get metadata
            tests_data = load_model(Tests, test_file)

            metadata = TopicTestMetadata(
                topic=tests_data.topic,
                file_path=test_file,
                test_count=len(tests_data.tests),
                slug=test_file.stem
            )
            topics.append(metadata)

        except Exception as e:
            # Skip files that can't be loaded
            print(f"Warning: Could not load {test_file}: {e}")
            continue

    # Sort by topic name
    topics.sort(key=lambda t: t.topic.lower())

    return topics


def migrate_legacy_tests() -> Optional[str]:
    """
    Migrate legacy tests.json to the new tests/ directory structure.

    If tests.json exists and contains data:
    1. Load the test data
    2. Save to tests/<topic-slug>.json
    3. Rename tests.json to tests.json.backup

    Returns:
        Success message if migration occurred, None if no migration needed
    """
    legacy_file = Path(__file__).parent / "tests.json"

    if not legacy_file.exists():
        return None

    try:
        # Check if it's already a backup
        if legacy_file.name == "tests.json.backup":
            return None

        # Load legacy data
        tests_data = load_model(Tests, legacy_file)

        if not tests_data.tests:
            # Empty test file, no need to migrate
            return None

        # Get the new file path
        new_file = get_topic_file_path(tests_data.topic)

        # Check if the new file already exists
        if new_file.exists():
            # Load existing data to check if it's the same
            existing_data = load_model(Tests, new_file)
            if len(existing_data.tests) >= len(tests_data.tests):
                # New file has same or more tests, safe to backup old one
                backup_file = legacy_file.parent / "tests.json.backup"
                legacy_file.rename(backup_file)
                return f"Legacy tests.json backed up to tests.json.backup (data already migrated)"

        # Save to new location
        save_model(tests_data, new_file)

        # Backup the old file
        backup_file = legacy_file.parent / "tests.json.backup"
        legacy_file.rename(backup_file)

        return f"Migrated {len(tests_data.tests)} test cases for topic '{tests_data.topic}' to {new_file.name}"

    except Exception as e:
        raise Exception(f"Failed to migrate legacy tests.json: {e}")


def load_topic_tests(topic: str) -> Tests:
    """
    Load test cases for a specific topic.

    Args:
        topic: The topic name

    Returns:
        Tests object containing the topic and test cases

    Raises:
        FileNotFoundError: If the topic's test file doesn't exist
    """
    file_path = get_topic_file_path(topic)

    if not file_path.exists():
        # Return empty Tests object
        return Tests(topic=topic, tests=[])

    return load_model(Tests, file_path)


def save_topic_tests(tests_data: Tests) -> None:
    """
    Save test cases for a specific topic.

    Args:
        tests_data: The Tests object to save
    """
    file_path = get_topic_file_path(tests_data.topic)
    save_model(tests_data, file_path)
