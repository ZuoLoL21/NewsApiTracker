# Sentiment Analyzer Accuracy Testing

This directory contains tools for generating test datasets and comparing the accuracy of different sentiment analyzers.

## Files

- `tests.json` - Test dataset containing articles with manually classified sentiment labels
- `generate_tests.py` - Interactive UI for scraping articles and manually classifying them
- `compare_accuracy.py` - Streamlit UI for comparing analyzer performance with confusion matrices and metrics

## Quick Start

### Step 1: Generate Test Data

Run the test data generator to scrape and classify articles:

```bash
streamlit run visual/sa_accuracy/generate_tests.py
```

**Workflow:**
1. Enter a topic to scrape (e.g., "Cloud Computing", "Artificial Intelligence")
2. Click "Scrape Articles" to fetch recent news articles
3. Review each article and classify its sentiment:
   - **Positive**: Article portrays the topic favorably
   - **Negative**: Article portrays the topic unfavorably
   - **Neutral**: Article is objective/factual about the topic
   - **Unknown**: Cannot determine sentiment or article is not relevant
4. Classifications are automatically saved to `tests.json`

**Features:**
- Automatically filters out already-classified articles
- Shows progress and statistics
- Displays article images, descriptions, and full content
- Links to original article for verification
- Can skip articles you're unsure about

### Step 2: Compare Analyzer Accuracy

Once you have test cases in `tests.json`, run the comparison tool:

```bash
streamlit run visual/sa_accuracy/compare_accuracy.py
```

**What You'll See:**
- **Overall Performance Metrics**: Accuracy, precision, recall, and F1 score for each analyzer
- **Confusion Matrices**: Visual representation showing where predictions are correct/incorrect
- **Classification Reports**: Detailed per-class performance metrics
- **Prediction Comparison**: Side-by-side view of both analyzers' predictions vs. ground truth
- **Agreement Analysis**: How often the analyzers agree with each other

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

## Test Dataset Recommendations

For meaningful accuracy metrics:

### Minimum Requirements
- **At least 20-30 test cases** for basic evaluation
- **50+ test cases** for reliable metrics
- **100+ test cases** for statistical significance

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

### "No test cases found in tests.json"
- Run `generate_tests.py` first to create test data
- Ensure `tests.json` exists in this directory

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
- Tests are appended to existing `tests.json`
- Already-classified articles are automatically skipped
- You can change topics between runs (topic in file will be from last session)

## Manual Test Editing

You can also manually edit `tests.json` if needed:

```json
{
  "topic": "Your Topic",
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

Valid sentiment values: `"positive"`, `"negative"`, `"neutral"`, `"unknown"`, `"invalid"`

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
