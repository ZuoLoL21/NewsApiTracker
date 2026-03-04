import sys
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support, classification_report

from pydantic import BaseModel

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.libs.models import Article
from src.libs.sentiment_analysis import ABSASentimentAnalyzer, LLMSentimentAnalyzer
from src.libs.sentiment_analysis.base import Sentiment

# Import topic helpers from current directory
sys.path.insert(0, str(Path(__file__).parent))
from topic_helpers import (
    migrate_legacy_tests,
    list_available_topics,
    load_topic_tests,
    Test,
    Tests
)

ALL_CLASSES = [
    ("ABSA Sentiment Analyzer", ABSASentimentAnalyzer),
    ("LLM Sentiment Analyzer", LLMSentimentAnalyzer)
]


class MultiTopicTests(BaseModel):
    """Combined test data from multiple topics."""
    topics: List[str]
    all_tests: List[Test]
    per_topic_tests: Dict[str, List[Test]]


class TopicMetrics(BaseModel):
    """Performance metrics for a specific topic."""
    topic: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    test_count: int


class AggregatedMetrics(BaseModel):
    """Aggregated metrics across all topics."""
    overall: TopicMetrics
    per_topic: List[TopicMetrics]


def load_multi_topic_tests(topics: List[str]) -> MultiTopicTests:
    """Load and combine test data from multiple topics."""
    all_tests = []
    per_topic_tests = {}

    for topic in topics:
        topic_data = load_topic_tests(topic)
        all_tests.extend(topic_data.tests)
        per_topic_tests[topic] = topic_data.tests

    return MultiTopicTests(
        topics=topics,
        all_tests=all_tests,
        per_topic_tests=per_topic_tests
    )


def run_sentiment_analysis(analyzer_class, topic: str, tests: List[Test]) -> List[Sentiment]:
    """Run sentiment analysis on all test cases."""
    analyzer = analyzer_class(topic)
    predictions = []

    for test in tests:
        try:
            prediction = analyzer.sentiment_analysis(test.input.model_dump())
            predictions.append(prediction)
        except Exception as e:
            st.error(f"Error analyzing article: {e}")
            predictions.append(Sentiment.UNKNOWN)

    return predictions


def plot_confusion_matrix(y_true: List[str], y_pred: List[str], labels: List[str], title: str):
    """Plot confusion matrix using matplotlib and seaborn."""
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_ylabel('True Label', fontsize=12)
    ax.set_xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()

    return fig


def calculate_metrics(y_true: List[str], y_pred: List[str], test_count: int = None) -> Dict[str, Any]:
    """Calculate accuracy, precision, recall, and F1 score."""
    if test_count is None:
        test_count = len(y_true)

    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "test_count": test_count
    }


def calculate_aggregated_metrics(
    per_topic_results: Dict[str, Dict[str, Any]],
    topics: List[str]
) -> AggregatedMetrics:
    """
    Calculate weighted aggregated metrics across topics.

    Metrics are weighted by the number of test cases in each topic.
    """
    total_tests = sum(r["test_count"] for r in per_topic_results.values())

    if total_tests == 0:
        # Return zero metrics if no tests
        overall = TopicMetrics(
            topic="Overall",
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            test_count=0
        )
        return AggregatedMetrics(overall=overall, per_topic=[])

    # Calculate weighted average for each metric
    weighted_accuracy = sum(
        r["accuracy"] * r["test_count"] for r in per_topic_results.values()
    ) / total_tests

    weighted_precision = sum(
        r["precision"] * r["test_count"] for r in per_topic_results.values()
    ) / total_tests

    weighted_recall = sum(
        r["recall"] * r["test_count"] for r in per_topic_results.values()
    ) / total_tests

    weighted_f1 = sum(
        r["f1_score"] * r["test_count"] for r in per_topic_results.values()
    ) / total_tests

    # Create overall metrics
    overall = TopicMetrics(
        topic="Overall (Weighted Average)",
        accuracy=weighted_accuracy,
        precision=weighted_precision,
        recall=weighted_recall,
        f1_score=weighted_f1,
        test_count=total_tests
    )

    # Create per-topic metrics
    per_topic = [
        TopicMetrics(
            topic=topic,
            accuracy=per_topic_results[topic]["accuracy"],
            precision=per_topic_results[topic]["precision"],
            recall=per_topic_results[topic]["recall"],
            f1_score=per_topic_results[topic]["f1_score"],
            test_count=per_topic_results[topic]["test_count"]
        )
        for topic in topics
    ]

    return AggregatedMetrics(overall=overall, per_topic=per_topic)


def main():
    st.set_page_config(page_title="Sentiment Analyzer Comparison", layout="wide")

    st.title("🎯 Sentiment Analyzer Accuracy Comparison")
    st.markdown("---")

    # Migrate legacy tests on first run
    try:
        migration_msg = migrate_legacy_tests()
        if migration_msg:
            st.sidebar.success(migration_msg)
    except Exception as e:
        st.sidebar.error(f"Migration error: {e}")

    # Sidebar - Topic Selection
    st.sidebar.header("Topic Selection")

    # Get available topics
    available_topics = list_available_topics()

    if not available_topics:
        st.warning("No test topics found. Please use the Test Data Generator to create test cases first.")
        st.info("Run `streamlit run visual/sa_accuracy/generate_tests.py` to create test datasets.")
        return

    # Show available topics with metadata
    st.sidebar.markdown("**Available Topics:**")
    for topic_meta in available_topics:
        st.sidebar.caption(f"• {topic_meta.topic} ({topic_meta.test_count} tests)")

    # Multi-select for topics
    selected_topics = st.sidebar.multiselect(
        "Select topics to evaluate:",
        [t.topic for t in available_topics],
        default=[available_topics[0].topic],
        help="Choose one or more topics to evaluate. Metrics will be aggregated across all selected topics."
    )

    if not selected_topics:
        st.info("👈 Please select at least one topic from the sidebar to begin evaluation.")
        return

    # Load multi-topic tests
    try:
        multi_topic_data = load_multi_topic_tests(selected_topics)

        st.sidebar.markdown("---")
        st.sidebar.header("Test Configuration")
        st.sidebar.metric("Selected Topics", len(selected_topics))
        st.sidebar.metric("Total Test Cases", len(multi_topic_data.all_tests))

        for topic in selected_topics:
            st.sidebar.caption(f"• {topic}: {len(multi_topic_data.per_topic_tests[topic])} tests")

        if len(multi_topic_data.all_tests) == 0:
            st.warning("No test cases found for selected topics")
            return

    except Exception as e:
        st.error(f"Error loading tests: {e}")
        return

    # All possible sentiment labels
    all_labels = [s.value for s in Sentiment]

    # Run analysis for each analyzer on each topic
    results_by_analyzer = {}
    predictions_by_analyzer = {}
    per_topic_results = {name: {} for name, _ in ALL_CLASSES}

    with st.spinner("Running sentiment analysis on all topics..."):
        for name, analyzer_class in ALL_CLASSES:
            # Run analysis for each topic separately
            topic_predictions = {}
            topic_true_labels = {}

            for topic in selected_topics:
                topic_tests = multi_topic_data.per_topic_tests[topic]
                if not topic_tests:
                    continue

                # Run sentiment analysis for this topic
                preds = run_sentiment_analysis(analyzer_class, topic, topic_tests)
                topic_predictions[topic] = preds
                topic_true_labels[topic] = [test.output.value for test in topic_tests]

                # Calculate metrics for this topic
                per_topic_results[name][topic] = calculate_metrics(
                    topic_true_labels[topic],
                    [p.value for p in preds],
                    len(topic_tests)
                )

            # Combine all predictions and true labels
            all_predictions = []
            all_true_labels = []
            for topic in selected_topics:
                if topic in topic_predictions:
                    all_predictions.extend(topic_predictions[topic])
                    all_true_labels.extend(topic_true_labels[topic])

            predictions_by_analyzer[name] = {
                "all": all_predictions,
                "per_topic": topic_predictions
            }

            # Calculate aggregated metrics
            aggregated = calculate_aggregated_metrics(per_topic_results[name], selected_topics)
            results_by_analyzer[name] = aggregated

    # Display overall metrics comparison
    st.header("📊 Overall Performance Metrics")

    if len(selected_topics) > 1:
        st.caption(f"Aggregated across {len(selected_topics)} topics (weighted by test count)")

    col1, col2 = st.columns(2)

    for idx, (name, aggregated_metrics) in enumerate(results_by_analyzer.items()):
        metrics = aggregated_metrics.overall
        with [col1, col2][idx]:
            st.subheader(name)
            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:
                st.metric("Accuracy", f"{metrics.accuracy:.2%}")
                st.metric("Precision", f"{metrics.precision:.2%}")

            with metric_col2:
                st.metric("Recall", f"{metrics.recall:.2%}")
                st.metric("F1 Score", f"{metrics.f1_score:.2%}")

            st.caption(f"Based on {metrics.test_count} total test cases")

    st.markdown("---")

    # Display per-topic breakdown if multiple topics selected
    if len(selected_topics) > 1:
        st.header("📋 Per-Topic Performance Breakdown")

        for name, aggregated_metrics in results_by_analyzer.items():
            with st.expander(f"{name} - Topic Breakdown"):
                # Create DataFrame for per-topic metrics
                topic_data = []
                for topic_metric in aggregated_metrics.per_topic:
                    topic_data.append({
                        "Topic": topic_metric.topic,
                        "Test Count": topic_metric.test_count,
                        "Accuracy": f"{topic_metric.accuracy:.2%}",
                        "Precision": f"{topic_metric.precision:.2%}",
                        "Recall": f"{topic_metric.recall:.2%}",
                        "F1 Score": f"{topic_metric.f1_score:.2%}"
                    })

                df = pd.DataFrame(topic_data)
                st.dataframe(df, hide_index=True, use_container_width=True)

        st.markdown("---")

    # Display confusion matrices
    st.header("🔍 Confusion Matrices")

    if len(selected_topics) > 1:
        st.subheader("Aggregated Confusion Matrices")
        st.caption("Combined predictions across all selected topics")

    col1, col2 = st.columns(2)

    # Overall confusion matrices
    for idx, (name, pred_data) in enumerate(predictions_by_analyzer.items()):
        all_preds = pred_data["all"]
        all_true = []
        for topic in selected_topics:
            topic_tests = multi_topic_data.per_topic_tests[topic]
            all_true.extend([test.output.value for test in topic_tests])

        with [col1, col2][idx]:
            st.subheader(name)
            fig = plot_confusion_matrix(
                all_true,
                [p.value for p in all_preds],
                all_labels,
                f"Overall: {name}"
            )
            st.pyplot(fig)
            plt.close()

    # Per-topic confusion matrices (if multiple topics)
    if len(selected_topics) > 1:
        st.markdown("---")
        st.subheader("Per-Topic Confusion Matrices")

        for topic in selected_topics:
            with st.expander(f"Topic: {topic}"):
                col1, col2 = st.columns(2)

                for idx, (name, pred_data) in enumerate(predictions_by_analyzer.items()):
                    if topic not in pred_data["per_topic"]:
                        continue

                    topic_preds = pred_data["per_topic"][topic]
                    topic_tests = multi_topic_data.per_topic_tests[topic]
                    topic_true = [test.output.value for test in topic_tests]

                    with [col1, col2][idx]:
                        st.write(f"**{name}**")
                        fig = plot_confusion_matrix(
                            topic_true,
                            [p.value for p in topic_preds],
                            all_labels,
                            f"{topic}: {name}"
                        )
                        st.pyplot(fig)
                        plt.close()

    st.markdown("---")

    # Detailed classification reports
    st.header("📋 Detailed Classification Reports")

    for name, pred_data in predictions_by_analyzer.items():
        all_preds = pred_data["all"]
        all_true = []
        for topic in selected_topics:
            topic_tests = multi_topic_data.per_topic_tests[topic]
            all_true.extend([test.output.value for test in topic_tests])

        with st.expander(f"{name} - Overall Classification Report"):
            report = classification_report(
                all_true,
                [p.value for p in all_preds],
                labels=all_labels,
                zero_division=0,
                output_dict=True
            )

            # Convert to DataFrame for better display
            report_df = pd.DataFrame(report).transpose()
            st.dataframe(report_df.style.format("{:.2f}"))

    st.markdown("---")

    # Side-by-side comparison of predictions
    st.header("📝 Prediction Comparison")

    comparison_data = []
    idx_offset = 0

    for topic in selected_topics:
        topic_tests = multi_topic_data.per_topic_tests[topic]

        for test_idx, test in enumerate(topic_tests):
            true_label = test.output.value

            row = {
                "Topic": topic,
                "Article Title": test.input.title[:40] + "..." if len(test.input.title) > 40 else test.input.title,
                "True Label": true_label,
            }

            for name, pred_data in predictions_by_analyzer.items():
                if topic in pred_data["per_topic"]:
                    pred_value = pred_data["per_topic"][topic][test_idx].value
                    # Add checkmark if prediction matches true label
                    match_indicator = "✓" if pred_value == true_label else "✗"
                    row[name] = f"{pred_value} {match_indicator}"

            comparison_data.append(row)

        idx_offset += len(topic_tests)

    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Agreement analysis
    st.markdown("---")
    st.header("🤝 Analyzer Agreement")

    if len(ALL_CLASSES) == 2:
        all_preds1 = [p.value for p in predictions_by_analyzer[ALL_CLASSES[0][0]]["all"]]
        all_preds2 = [p.value for p in predictions_by_analyzer[ALL_CLASSES[1][0]]["all"]]

        agreement = sum(1 for p1, p2 in zip(all_preds1, all_preds2) if p1 == p2)
        agreement_rate = agreement / len(all_preds1) if len(all_preds1) > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cases", len(all_preds1))
        with col2:
            st.metric("Cases Where Analyzers Agree", agreement)
        with col3:
            st.metric("Agreement Rate", f"{agreement_rate:.2%}")


if __name__ == "__main__":
    main()
