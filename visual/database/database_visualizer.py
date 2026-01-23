"""
Streamlit-based dashboard for visualizing sentiment analysis data from TimescaleDB.
Displays approval rates over time, sentiment distribution, topic comparison, and more.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from libs.db_helpers import get_db_connection
from consts import TOPICS

# Page Configuration
st.set_page_config(
    page_title="News Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
SENTIMENT_COLORS = {
    'positive': '#28a745',
    'negative': '#dc3545',
    'neutral': '#6c757d',
    'unknown': '#ffc107',
    'invalid': '#e83e8c'
}

TIME_BUCKETS = {
    'Day': '1 day',
    'Week': '1 week',
    'Month': '1 month'
}


# Database Query Functions (with caching)

@st.cache_data(ttl=300)
def get_date_range():
    """Get the min and max dates from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                MIN(published_at) AS min_date,
                MAX(published_at) AS max_date
            FROM articles
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result and result[0] and result[1]:
            return result[0].date(), result[1].date()
        else:
            # Return default date range if no data
            today = datetime.now().date()
            return today - timedelta(days=30), today

    except Exception as e:
        st.error(f"Error fetching date range: {e}")
        today = datetime.now().date()
        return today - timedelta(days=30), today


@st.cache_data(ttl=300)
def fetch_approval_rate_over_time(start_date, end_date, topics, time_bucket):
    """
    Fetch approval rate over time.
    Approval rate = positive / (positive + negative + neutral) * 100
    Excludes 'unknown' and 'invalid' sentiments.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                time_bucket(%s, published_at) AS time_bucket,
                COUNT(*) AS total_articles,
                SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) AS positive_articles,
                ROUND(100.0 * SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) /
                      NULLIF(SUM(CASE WHEN sentiment IN ('positive', 'negative', 'neutral') THEN 1 ELSE 0 END), 0), 2) AS approval_rate
            FROM articles
            WHERE published_at BETWEEN %s AND %s
                AND topic = ANY(%s)
                AND sentiment IN ('positive', 'negative', 'neutral')
            GROUP BY time_bucket
            ORDER BY time_bucket
        """

        cursor.execute(query, (time_bucket, start_date, end_date, topics))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        if results:
            df = pd.DataFrame(results, columns=['time_bucket', 'total_articles', 'positive_articles', 'approval_rate'])
            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching approval rate data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_sentiment_distribution(start_date, end_date, topics):
    """Fetch sentiment distribution for all sentiment types."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                sentiment,
                COUNT(*) AS count
            FROM articles
            WHERE published_at BETWEEN %s AND %s
                AND topic = ANY(%s)
            GROUP BY sentiment
            ORDER BY count DESC
        """

        cursor.execute(query, (start_date, end_date, topics))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        if results:
            df = pd.DataFrame(results, columns=['sentiment', 'count'])
            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching sentiment distribution: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_topic_comparison(start_date, end_date):
    """Compare approval rates across topics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                topic,
                COUNT(*) AS total_articles,
                SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) AS positive_articles,
                ROUND(100.0 * SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) /
                      NULLIF(SUM(CASE WHEN sentiment IN ('positive', 'negative', 'neutral') THEN 1 ELSE 0 END), 0), 2) AS approval_rate
            FROM articles
            WHERE published_at BETWEEN %s AND %s
                AND sentiment IN ('positive', 'negative', 'neutral')
            GROUP BY topic
            ORDER BY approval_rate DESC
        """

        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        if results:
            df = pd.DataFrame(results, columns=['topic', 'total_articles', 'positive_articles', 'approval_rate'])
            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching topic comparison: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_article_volume_over_time(start_date, end_date, topics, time_bucket):
    """Fetch article volume over time."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                time_bucket(%s, published_at) AS time_bucket,
                COUNT(*) AS article_count
            FROM articles
            WHERE published_at BETWEEN %s AND %s
                AND topic = ANY(%s)
            GROUP BY time_bucket
            ORDER BY time_bucket
        """

        cursor.execute(query, (time_bucket, start_date, end_date, topics))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        if results:
            df = pd.DataFrame(results, columns=['time_bucket', 'article_count'])
            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching article volume: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_source_analysis(start_date, end_date, topics, limit):
    """Fetch top N sources with sentiment breakdown."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                source_name,
                sentiment,
                COUNT(*) AS count
            FROM articles
            WHERE published_at BETWEEN %s AND %s
                AND topic = ANY(%s)
                AND source_name IS NOT NULL
            GROUP BY source_name, sentiment
            HAVING COUNT(*) >= 5
            ORDER BY source_name, sentiment
        """

        cursor.execute(query, (start_date, end_date, topics))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        if results:
            df = pd.DataFrame(results, columns=['source_name', 'sentiment', 'count'])

            # Get top N sources by total article count
            source_totals = df.groupby('source_name')['count'].sum().sort_values(ascending=False).head(limit)
            top_sources = source_totals.index.tolist()

            # Filter to only top sources
            df = df[df['source_name'].isin(top_sources)]

            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching source analysis: {e}")
        return pd.DataFrame()


# Chart Creation Functions

def create_approval_rate_chart(df, time_bucket):
    """Create line chart for approval rate over time."""
    if df.empty:
        st.info("No data available for the selected filters.")
        return None

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['time_bucket'],
        y=df['approval_rate'],
        mode='lines+markers',
        name='Approval Rate',
        line=dict(color='#007bff', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>' +
                      'Approval Rate: %{y:.2f}%<br>' +
                      'Articles: %{customdata[0]}<br>' +
                      '<extra></extra>',
        customdata=df[['total_articles']].values
    ))

    fig.update_layout(
        title=f'Approval Rate Over Time (by {time_bucket})',
        xaxis_title='Date',
        yaxis_title='Approval Rate (%)',
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )

    return fig


def create_sentiment_distribution_chart(df, chart_type):
    """Create pie or bar chart for sentiment distribution."""
    if df.empty:
        st.info("No data available for the selected filters.")
        return None

    # Add colors to dataframe
    df['color'] = df['sentiment'].map(SENTIMENT_COLORS)

    if chart_type == 'Pie':
        fig = px.pie(
            df,
            values='count',
            names='sentiment',
            title='Sentiment Distribution',
            color='sentiment',
            color_discrete_map=SENTIMENT_COLORS,
            hole=0.3
        )
    else:  # Bar
        fig = px.bar(
            df,
            x='sentiment',
            y='count',
            title='Sentiment Distribution',
            color='sentiment',
            color_discrete_map=SENTIMENT_COLORS,
            text='count'
        )
        fig.update_traces(textposition='outside')

    fig.update_layout(height=400, template='plotly_white')

    return fig


def create_topic_comparison_chart(df):
    """Create horizontal bar chart for topic comparison."""
    if df.empty:
        st.info("No data available for topic comparison.")
        return None

    fig = px.bar(
        df,
        x='approval_rate',
        y='topic',
        orientation='h',
        title='Approval Rate by Topic',
        text='approval_rate',
        color='approval_rate',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100]
    )

    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(
        xaxis_title='Approval Rate (%)',
        yaxis_title='Topic',
        height=max(300, len(df) * 50),
        template='plotly_white'
    )

    return fig


def create_volume_chart(df, time_bucket):
    """Create bar chart for article volume over time."""
    if df.empty:
        st.info("No data available for the selected filters.")
        return None

    fig = px.bar(
        df,
        x='time_bucket',
        y='article_count',
        title=f'Article Volume Over Time (by {time_bucket})',
        color='article_count',
        color_continuous_scale='Blues',
        text='article_count'
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Articles',
        height=400,
        template='plotly_white',
        showlegend=False
    )

    return fig


def create_source_analysis_chart(df):
    """Create stacked bar chart for source analysis."""
    if df.empty:
        st.info("No data available for source analysis.")
        return None

    # Pivot data for stacked bar chart
    df_pivot = df.pivot(index='source_name', columns='sentiment', values='count').fillna(0)

    fig = go.Figure()

    for sentiment in df_pivot.columns:
        if sentiment in SENTIMENT_COLORS:
            fig.add_trace(go.Bar(
                name=sentiment.capitalize(),
                x=df_pivot.index,
                y=df_pivot[sentiment],
                marker_color=SENTIMENT_COLORS[sentiment],
                hovertemplate='<b>%{x}</b><br>' +
                              f'{sentiment.capitalize()}: %{{y}}<br>' +
                              '<extra></extra>'
            ))

    fig.update_layout(
        title='Source Analysis (Sentiment Breakdown)',
        xaxis_title='Source',
        yaxis_title='Number of Articles',
        barmode='stack',
        height=400,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


# UI Functions

def render_sidebar():
    """Render sidebar with filters and return selected values."""
    st.sidebar.header("Filters")

    # Get date range from database
    min_date, max_date = get_date_range()

    # Date range selector
    st.sidebar.subheader("Date Range")
    date_range = st.sidebar.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_range"
    )

    # Handle single date selection
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range if not isinstance(date_range, tuple) else date_range[0]

    # Topic multi-select
    st.sidebar.subheader("Topics")
    selected_topics = st.sidebar.multiselect(
        "Select topics",
        options=TOPICS,
        default=TOPICS,
        key="topics"
    )

    # Time bucket selector
    st.sidebar.subheader("Time Bucket")
    time_bucket_label = st.sidebar.selectbox(
        "Select aggregation period",
        options=list(TIME_BUCKETS.keys()),
        index=0,
        key="time_bucket"
    )
    time_bucket = TIME_BUCKETS[time_bucket_label]

    # Chart type toggle for sentiment distribution
    st.sidebar.subheader("Chart Options")
    chart_type = st.sidebar.radio(
        "Sentiment distribution chart type",
        options=['Pie', 'Bar'],
        index=0,
        key="chart_type"
    )

    # Top N sources slider
    top_n_sources = st.sidebar.slider(
        "Top N sources to display",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
        key="top_n_sources"
    )

    return {
        'start_date': start_date,
        'end_date': end_date,
        'topics': selected_topics,
        'time_bucket': time_bucket,
        'time_bucket_label': time_bucket_label,
        'chart_type': chart_type,
        'top_n_sources': top_n_sources
    }


def render_metrics_row(df_sentiment, df_volume):
    """Render key metrics at the top of the dashboard."""
    col1, col2, col3 = st.columns(3)

    with col1:
        if not df_sentiment.empty:
            total_articles = df_sentiment['count'].sum()
            st.metric("Total Articles", f"{total_articles:,}")
        else:
            st.metric("Total Articles", "0")

    with col2:
        if not df_sentiment.empty:
            # Calculate overall approval rate
            valid_sentiments = df_sentiment[df_sentiment['sentiment'].isin(['positive', 'negative', 'neutral'])]
            if not valid_sentiments.empty:
                positive_count = valid_sentiments[valid_sentiments['sentiment'] == 'positive']['count'].sum()
                total_valid = valid_sentiments['count'].sum()
                approval_rate = (positive_count / total_valid * 100) if total_valid > 0 else 0
                st.metric("Overall Approval Rate", f"{approval_rate:.2f}%")
            else:
                st.metric("Overall Approval Rate", "N/A")
        else:
            st.metric("Overall Approval Rate", "N/A")

    with col3:
        if not df_volume.empty and len(df_volume) >= 2:
            # Calculate trend (comparing last two periods)
            recent_volume = df_volume.iloc[-1]['article_count']
            previous_volume = df_volume.iloc[-2]['article_count']
            trend = recent_volume - previous_volume
            st.metric("Volume Trend", f"{recent_volume:,}", delta=f"{trend:+,}")
        else:
            st.metric("Volume Trend", "N/A")


def render_main_dashboard():
    """Render the main dashboard with all visualizations."""
    # Title and description
    st.title("📊 News Sentiment Dashboard")
    st.markdown("Visualize sentiment analysis data from news articles tracked in TimescaleDB.")

    # Render sidebar and get filter values
    filters = render_sidebar()

    # Validate topic selection
    if not filters['topics']:
        st.warning("Please select at least one topic from the sidebar.")
        return

    # Fetch data
    df_sentiment = fetch_sentiment_distribution(
        filters['start_date'],
        filters['end_date'],
        filters['topics']
    )

    df_volume = fetch_article_volume_over_time(
        filters['start_date'],
        filters['end_date'],
        filters['topics'],
        filters['time_bucket']
    )

    df_approval = fetch_approval_rate_over_time(
        filters['start_date'],
        filters['end_date'],
        filters['topics'],
        filters['time_bucket']
    )

    # Render metrics row
    st.markdown("---")
    render_metrics_row(df_sentiment, df_volume)
    st.markdown("---")

    # Primary visualization: Approval Rate Over Time
    st.header("Approval Rate Over Time")
    st.markdown("*Approval rate = positive / (positive + negative + neutral) × 100*")

    fig_approval = create_approval_rate_chart(df_approval, filters['time_bucket_label'])
    if fig_approval:
        st.plotly_chart(fig_approval, width='stretch')

    st.markdown("---")

    # Two column layout for sentiment and topic comparison
    col1, col2 = st.columns(2)

    with col1:
        st.header("Sentiment Distribution")
        fig_sentiment = create_sentiment_distribution_chart(df_sentiment, filters['chart_type'])
        if fig_sentiment:
            st.plotly_chart(fig_sentiment, width='stretch')

    with col2:
        st.header("Topic Comparison")
        df_topics = fetch_topic_comparison(filters['start_date'], filters['end_date'])
        fig_topics = create_topic_comparison_chart(df_topics)
        if fig_topics:
            st.plotly_chart(fig_topics, width='stretch')

    st.markdown("---")

    # Article Volume Over Time
    st.header("Article Volume Over Time")
    fig_volume = create_volume_chart(df_volume, filters['time_bucket_label'])
    if fig_volume:
        st.plotly_chart(fig_volume, width='stretch')

    st.markdown("---")

    # Source Analysis (collapsible)
    with st.expander("Source Analysis", expanded=False):
        st.markdown(f"Showing top {filters['top_n_sources']} sources with at least 5 articles.")
        df_sources = fetch_source_analysis(
            filters['start_date'],
            filters['end_date'],
            filters['topics'],
            filters['top_n_sources']
        )
        fig_sources = create_source_analysis_chart(df_sources)
        if fig_sources:
            st.plotly_chart(fig_sources, width='stretch')


# Main Execution

if __name__ == "__main__":
    try:
        render_main_dashboard()
    except Exception as e:
        st.error(f"An error occurred while rendering the dashboard: {e}")
        st.exception(e)
