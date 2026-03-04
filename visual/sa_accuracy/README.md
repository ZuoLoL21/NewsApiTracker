# Sentiment Analyzer Accuracy Testing

This directory contains tools for generating test datasets and comparing the accuracy of different sentiment analyzers across multiple topics.

## Files

- `tests/` - Directory containing topic-specific test datasets (one JSON file per topic)
- `topic_helpers.py` - Utilities for managing multi-topic test datasets
- `generate_tests.py` - Interactive UI for scraping articles and manually classifying them
- `compare_accuracy.py` - Streamlit UI for comparing analyzer performance with confusion matrices and metrics
- `tests.json.backup` - Backup of legacy test data (auto-created during migration)

## Multi-Topic Support

The accuracy testing tools now support multiple topics, allowing you to:
- Create separate test datasets for different domains (e.g., "Cloud Computing", "Healthcare", "Finance")
- Compare how sentiment analyzers perform across different subject matter
- Evaluate analyzers on aggregated metrics across all topics
- Build comprehensive test coverage for production use

### File Structure

Each topic's test data is stored in a separate file:
```
visual/sa_accuracy/
├── tests/
│   ├── cloud-computing.json      # Topic: "Cloud Computing"
│   ├── artificial-intelligence.json  # Topic: "Artificial Intelligence"
│   └── healthcare.json           # Topic: "Healthcare"
├── generate_tests.py
├── compare_accuracy.py
└── topic_helpers.py
```

**File naming**: Topic names are converted to filesystem-safe slugs (e.g., "AI & Machine Learning" → `ai-machine-learning.json`)

### Migration from Legacy `tests.json`

If you have an existing `tests.json` file, it will be **automatically migrated** the first time you run either tool:
1. The test data is loaded and saved to `tests/<topic-slug>.json`
2. The original `tests.json` is renamed to `tests.json.backup`
3. A success message is displayed in the sidebar

No manual intervention required!

## Quick Start

### Step 1: Generate Test Data

Run the test data generator to scrape and classify articles:

```bash
streamlit run visual/sa_accuracy/generate_tests.py
```

**Workflow:**

1. **Select Topic Mode** (in sidebar):
   - **Use Existing Topic**: Add more tests to an existing topic
   - **Create New Topic**: Start a new topic test dataset

2. **Choose/Enter Topic**:
   - For existing: Select from dropdown (shows test count)
   - For new: Enter a unique topic name (e.g., "Cloud Computing", "Healthcare", "Cybersecurity")

3. **Scrape Articles**:
   - Click "Scrape Articles" to fetch recent news articles
   - Articles already classified for this topic are automatically filtered out

4. **Classify Sentiment**:
   - Review each article and classify its sentiment:
     - **Positive**: Article portrays the topic favorably
     - **Negative**: Article portrays the topic unfavorably
     - **Neutral**: Article is objective/factual about the topic
     - **Unknown**: Cannot determine sentiment or article is not relevant
   - Classifications are automatically saved to `tests/<topic-slug>.json`

**Features:**
- Multi-topic support with topic selection/creation UI
- Shows all available topics with test counts
- Automatically filters out already-classified articles per topic
- Shows progress and statistics
- Displays article images, descriptions, and full content
- Links to original article for verification
- Can skip articles you're unsure about

### Step 2: Compare Analyzer Accuracy

Once you have test cases for one or more topics, run the comparison tool:

```bash
streamlit run visual/sa_accuracy/compare_accuracy.py
```

**Workflow:**

1. **Select Topics** (in sidebar):
   - Use the multiselect widget to choose one or more topics to evaluate
   - Shows test count for each available topic
   - Default: First available topic

2. **Run Evaluation**:
   - Click outside the multiselect to trigger analysis
   - Sentiment analyzers run on each topic separately
   - Results are aggregated across all selected topics

**What You'll See:**

- **Overall Performance Metrics** (weighted aggregated across topics):
  - Accuracy, precision, recall, and F1 score for each analyzer
  - Total test count across all selected topics

- **Per-Topic Breakdown** (if multiple topics selected):
  - Individual metrics for each topic
  - Shows which topics are harder/easier for each analyzer

- **Confusion Matrices**:
  - Overall aggregated confusion matrix
  - Per-topic confusion matrices (if multiple topics)
  - Visual representation showing where predictions are correct/incorrect

- **Classification Reports**:
  - Detailed per-class performance metrics (aggregated)

- **Prediction Comparison**:
  - Side-by-side view of both analyzers' predictions vs. ground truth
  - Includes topic column for multi-topic evaluations
  - ✓/✗ indicators for correct/incorrect predictions

- **Agreement Analysis**:
  - How often the analyzers agree with each other across all tests

## Understanding the Results

### Confusion Matrix

The confusion matrix is a table that shows prediction accuracy:

```
              Predicted
           Pos  Neg  Neu  Unk
Actual Pos  15   2    3    0
       Neg   1  18    1    0
       Neu   2   1   25    2
       Unk   0   0    1    9
```

- **Diagonal** (Pos→Pos, Neg→Neg, etc.): Correct predictions
- **Off-diagonal**: Misclassifications
- **Dark colors**: Higher counts

### Metrics Explained

- **Accuracy**: `(Correct Predictions) / (Total Predictions)`
  - Overall percentage of correct predictions

- **Precision**: `(True Positives) / (True Positives + False Positives)`
  - Of all positive predictions, how many were actually positive?
  - High precision = few false alarms

- **Recall**: `(True Positives) / (True Positives + False Negatives)`
  - Of all actual positives, how many were correctly identified?
  - High recall = few missed positives

- **F1 Score**: `2 * (Precision * Recall) / (Precision + Recall)`
  - Harmonic mean of precision and recall
  - Balanced measure of performance

### Agreement Rate

Shows how often both analyzers make the same prediction (regardless of correctness):
- **High agreement + high accuracy**: Both analyzers are working well
- **High agreement + low accuracy**: Systematic bias (both making the same mistakes)
- **Low agreement**: Analyzers use different approaches or have different failure modes

### Aggregated Metrics (Multi-Topic)

When evaluating multiple topics, overall metrics are **weighted by test count**:

```
Overall Accuracy = Σ(Topic Accuracy × Topic Test Count) / Total Test Count
```

**Example**:
- Topic A: 80% accuracy, 100 tests → contributes 80.0%
- Topic B: 60% accuracy, 50 tests → contributes 20.0%
- **Overall**: (80×100 + 60×50) / 150 = **73.3%**

This ensures topics with more test cases have proportionally more influence on the overall score, which is fairer than a simple average.

## Test Dataset Recommendations

For meaningful accuracy metrics:

### Minimum Requirements (Per Topic)
- **At least 20-30 test cases** for basic evaluation
- **50+ test cases** for reliable metrics
- **100+ test cases** for statistical significance

### Multi-Topic Strategy
- **Start with 2-3 diverse topics** to understand analyzer behavior across domains
- **Add more topics** as you identify performance gaps
- **Maintain similar test counts** across topics for balanced evaluation
- **Choose topics relevant to your use case** (e.g., if analyzing tech news, focus on tech-related topics)

### Balanced Dataset
Try to have roughly equal numbers of each sentiment class:
- 25% Positive
- 25% Negative
- 40% Neutral (most common in news)
- 10% Unknown/Invalid

### Diverse Coverage
Include articles that are:
- From different news sources
- Different writing styles (formal news, opinion pieces, technical blogs)
- Various subtopics within your main topic
- Edge cases (sarcasm, mixed sentiment, off-topic)

### Quality Guidelines
- **Clear sentiment**: You should be confident in your classification
- **Topic relevance**: Article should meaningfully discuss the topic
- **Full content**: Prefer articles with complete content, not just headlines
- **Consistency**: Use the same criteria for all classifications

## Currently Tested Analyzers

1. **ABSA Sentiment Analyzer** (`ABSASentimentAnalyzer`)
   - Aspect-Based Sentiment Analysis
   - Uses transformer models to analyze sentiment

2. **LLM Sentiment Analyzer** (`LLMSentimentAnalyzer`)
   - Large Language Model based analysis
   - Uses language models for contextual understanding

## Troubleshooting

### "No test topics found"
- Run `generate_tests.py` first to create test data
- Check that `tests/` directory exists with `.json` files
- If you have a legacy `tests.json`, it will be auto-migrated on first run

### "No test cases found for selected topics"
- Ensure the selected topics have test data
- Check the test files in `tests/` directory to verify they contain test cases

### Scraping fails or returns 0 articles
- Check that `NEWS_API_KEY` is set in your `.env` file
- Try a different topic or time range
- News API has rate limits and result caps

### Analyzer errors during comparison
- Ensure both analyzers are properly configured
- Check that required models are downloaded
- Review logs for specific error messages

## Adding More Test Cases

You can run `generate_tests.py` multiple times:
- **For existing topics**: Select "Use Existing Topic" and choose the topic
- **For new topics**: Select "Create New Topic" and enter a unique name
- Tests are appended to the topic's JSON file
- Already-classified articles are automatically skipped per topic
- You can work on multiple topics in the same session by switching between modes

## Manual Test Editing

You can manually edit topic test files in `tests/` if needed:

**File**: `tests/cloud-computing.json`
```json
{
  "topic": "Cloud Computing",
  "tests": [
    {
      "input": {
        "source": {"id": null, "name": "Source Name"},
        "author": "Author Name",
        "title": "Article Title",
        "description": "Article description",
        "url": "https://example.com",
        "urlToImage": "https://example.com/image.jpg",
        "publishedAt": "2026-01-19T00:00:00Z",
        "content": "Full article content"
      },
      "output": "positive"
    }
  ]
}
```

**Important**: The `topic` field must match the topic name (not the slug). Valid sentiment values: `"positive"`, `"negative"`, `"neutral"`, `"unknown"`, `"invalid"`

### Managing Topics

**List available topics**:
```python
from topic_helpers import list_available_topics

topics = list_available_topics()
for topic in topics:
    print(f"{topic.topic}: {topic.test_count} tests ({topic.file_path})")
```

**Load a specific topic**:
```python
from topic_helpers import load_topic_tests

tests = load_topic_tests("Cloud Computing")
print(f"Loaded {len(tests.tests)} tests for {tests.topic}")
```

**Save tests for a topic**:
```python
from topic_helpers import save_topic_tests, Tests

tests = Tests(topic="New Topic", tests=[])
save_topic_tests(tests)
```

## Dependencies

Required Python packages (should be in `pyproject.toml`):
- `streamlit` - Web UI framework
- `scikit-learn` - Metrics and confusion matrix
- `matplotlib` - Plotting
- `seaborn` - Enhanced visualizations
- `pandas` - Data manipulation
- `pydantic` - Data validation

Install with:
```bash
pip install -e .
```
