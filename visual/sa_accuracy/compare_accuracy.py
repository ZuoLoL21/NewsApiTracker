import json
from typing import List, Dict, Any
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support, classification_report

from pydantic import BaseModel

from libs.models import Article
from libs.sentiment_analysis import ABSASentimentAnalyzer, LLMSentimentAnalyzer
from libs.sentiment_analysis.base import Sentiment

ALL_CLASSES = [
    ("ABSA Sentiment Analyzer", ABSASentimentAnalyzer),
    ("LLM Sentiment Analyzer", LLMSentimentAnalyzer)
]

class Test(BaseModel):
    input: Article
    output: Sentiment

class Tests(BaseModel):
    tests: List[Test]
    topic: str


def load_tests(filepath: str = "tests/tests.json") -> Tests:
    """Load and validate test data from JSON file."""
    with open(filepath) as f:
        tests = json.load(f)
    return Tests.model_validate(tests)


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


def calculate_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """Calculate accuracy, precision, recall, and F1 score."""
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }


def main():
    st.set_page_config(page_title="Sentiment Analyzer Comparison", layout="wide")

    st.title("🎯 Sentiment Analyzer Accuracy Comparison")
    st.markdown("---")

    # Load tests
    try:
        validated_tests = load_tests()
        topic = validated_tests.topic
        true_tests = validated_tests.tests

        st.sidebar.header("Test Configuration")
        st.sidebar.metric("Topic", topic)
        st.sidebar.metric("Number of Test Cases", len(true_tests))

        if len(true_tests) == 0:
            st.warning("No test cases found in tests.json")
            return

    except Exception as e:
        st.error(f"Error loading tests: {e}")
        return

    # Extract true labels
    y_true = [test.output.value for test in true_tests]

    # All possible sentiment labels
    all_labels = [s.value for s in Sentiment]

    # Run analysis for each analyzer
    results = {}
    predictions = {}

    with st.spinner("Running sentiment analysis..."):
        for name, analyzer_class in ALL_CLASSES:
            predictions[name] = run_sentiment_analysis(analyzer_class, topic, true_tests)
            results[name] = calculate_metrics(y_true, [p.value for p in predictions[name]])

    # Display overall metrics comparison
    st.header("📊 Overall Performance Metrics")

    col1, col2 = st.columns(2)

    for idx, (name, metrics) in enumerate(results.items()):
        with [col1, col2][idx]:
            st.subheader(name)
            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:
                st.metric("Accuracy", f"{metrics['accuracy']:.2%}")
                st.metric("Precision", f"{metrics['precision']:.2%}")

            with metric_col2:
                st.metric("Recall", f"{metrics['recall']:.2%}")
                st.metric("F1 Score", f"{metrics['f1_score']:.2%}")

    st.markdown("---")

    # Display confusion matrices
    st.header("🔍 Confusion Matrices")

    col1, col2 = st.columns(2)

    for idx, (name, preds) in enumerate(predictions.items()):
        with [col1, col2][idx]:
            st.subheader(name)
            fig = plot_confusion_matrix(
                y_true,
                [p.value for p in preds],
                all_labels,
                f"Confusion Matrix: {name}"
            )
            st.pyplot(fig)
            plt.close()

    st.markdown("---")

    # Detailed classification reports
    st.header("📋 Detailed Classification Reports")

    for name, preds in predictions.items():
        with st.expander(f"{name} - Classification Report"):
            report = classification_report(
                y_true,
                [p.value for p in preds],
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
    for idx, test in enumerate(true_tests):
        row = {
            "Article Title": test.input.title[:50] + "..." if len(test.input.title) > 50 else test.input.title,
            "True Label": y_true[idx],
        }

        for name, preds in predictions.items():
            pred_value = preds[idx].value
            # Add checkmark if prediction matches true label
            match_indicator = "✓" if pred_value == y_true[idx] else "✗"
            row[name] = f"{pred_value} {match_indicator}"

        comparison_data.append(row)

    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)

    # Agreement analysis
    st.markdown("---")
    st.header("🤝 Analyzer Agreement")

    if len(ALL_CLASSES) == 2:
        preds1 = [p.value for p in predictions[ALL_CLASSES[0][0]]]
        preds2 = [p.value for p in predictions[ALL_CLASSES[1][0]]]

        agreement = sum(1 for p1, p2 in zip(preds1, preds2) if p1 == p2)
        agreement_rate = agreement / len(preds1) if len(preds1) > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cases", len(preds1))
        with col2:
            st.metric("Cases Where Analyzers Agree", agreement)
        with col3:
            st.metric("Agreement Rate", f"{agreement_rate:.2%}")


if __name__ == "__main__":
    main()
