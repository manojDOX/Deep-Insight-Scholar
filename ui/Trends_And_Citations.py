# ui/pages/2_Trends_And_Citations.py

import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

from config.settings import Settings
from tools.tavily_search import TavilySearchTool


METADATA_PATH = Path(Settings.METADATA_FILE)


@st.cache_data
def load_metadata() -> pd.DataFrame:
    """
    Loads and caches metadata from the JSON file into a pandas DataFrame

    Args:
          No arguments
    Returns:
          pandas DataFrame containing the metadata
    """
    if not METADATA_PATH.exists():
        st.error("metadata.json not found. Run prepare_pdf.py first.")
        st.stop()

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return pd.DataFrame(data)


def build_keyword_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the metadata DataFrame to create a row for each keyword-paper combination

    Args:
          df: pandas DataFrame containing paper metadata
    Returns:
          pandas DataFrame with columns year, keyword, and venue
    """
    rows = []
    for _, row in df.iterrows():
        for kw in row.get("keywords", []):
            rows.append({
                "year": row["year"],
                "keyword": kw,
                "venue": row["venue"]
            })
    return pd.DataFrame(rows)


def detect_emerging_topics(trend_df: pd.DataFrame, recent_years: int = 2):
    """
    Identifies keywords with the highest growth in frequency over the specified recent years

    Args:
          trend_df: DataFrame containing keyword trends
          recent_years: Number of recent years to consider for growth calculation (default=2)
    Returns:
          pandas Series containing growth scores for emerging topics, sorted descending
    """
    pivot = (
        trend_df
        .groupby(["year", "keyword"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )

    growth = pivot.diff().tail(recent_years).sum()
    return growth[growth > 0].sort_values(ascending=False)


def compute_influence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates an influence score for papers based on keyword count and venue popularity

    Args:
          df: pandas DataFrame containing paper metadata
    Returns:
          pandas DataFrame sorted by influence score
    """
    df = df.copy()
    df["keyword_count"] = df.keywords.apply(len)
    df["influence_score"] = (
        df["keyword_count"] +
        df.groupby("venue")["venue"].transform("count")
    )
    return df.sort_values("influence_score", ascending=False)


def render_trends_and_citations():
    """
    Renders the Trends & Citations page, including filters, charts, and emerging topic analysis

    Args:
          No arguments
    Returns:
          None
    """
    st.header("📈 Research Trends & Citations")

    df = load_metadata()
    trend_df = build_keyword_trends(df)

    with st.expander("🔍 Filters", expanded=True):
        year_min, year_max = int(df.year.min()), int(df.year.max())
        year_range = st.slider(
            "Year Range",
            year_min,
            year_max,
            (year_min, year_max)
        )

        venue_filter = st.multiselect(
            "Venue",
            sorted(df.venue.unique()),
            default=list(df.venue.unique())
        )

    filtered_trend = trend_df[
        (trend_df.year >= year_range[0]) &
        (trend_df.year <= year_range[1]) &
        (trend_df.venue.isin(venue_filter))
    ]

    st.subheader("📊 Keyword Trends Over Time")

    fig = px.histogram(
        filtered_trend,
        x="year",
        color="keyword",
        title="Keyword Frequency by Year"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔥 Emerging Topics")

    emerging = detect_emerging_topics(filtered_trend)
    tavily = TavilySearchTool(max_results=2)

    if emerging.empty:
        st.info("No emerging topics detected for selected range.")
    else:
        for topic, score in emerging.head(5).items():
            with st.expander(f"{topic} (growth score: {int(score)})"):
                st.write(
                    tavily.search(
                        f"recent research trend and importance of {topic}"
                    )
                )

    st.subheader("🔗 Influential Papers (Proxy View)")

    influential = compute_influence(df)

    st.dataframe(
        influential[
            ["title", "authors", "year", "venue", "influence_score"]
        ].head(15),
        use_container_width=True
    )

    st.caption(
        "Influence is approximated using keyword reuse, venue concentration, and recency."
    )