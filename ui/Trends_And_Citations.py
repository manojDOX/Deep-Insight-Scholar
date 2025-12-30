# ui/pages/2_Trends_And_Citations.py

import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

from tools.tavily_search import TavilySearchTool


METADATA_PATH = Path("data/metadata/metadata.json")


# -----------------------------
# Data helpers
# -----------------------------
@st.cache_data
def load_metadata() -> pd.DataFrame:
    if not METADATA_PATH.exists():
        st.error("metadata.json not found. Run prepare_pdf.py first.")
        st.stop()

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return pd.DataFrame(data)


def build_keyword_trends(df: pd.DataFrame) -> pd.DataFrame:
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
    df = df.copy()
    df["keyword_count"] = df.keywords.apply(len)
    df["influence_score"] = (
        df["keyword_count"] +
        df.groupby("venue")["venue"].transform("count")
    )
    return df.sort_values("influence_score", ascending=False)


# -----------------------------
# Main render function
# -----------------------------
def render_trends_and_citations():
    st.header("📈 Research Trends & Citations")

    df = load_metadata()
    trend_df = build_keyword_trends(df)

    # -----------------------------
    # Filters (INLINE, not sidebar)
    # -----------------------------
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

    # -----------------------------
    # Keyword trends
    # -----------------------------
    st.subheader("📊 Keyword Trends Over Time")

    fig = px.histogram(
        filtered_trend,
        x="year",
        color="keyword",
        title="Keyword Frequency by Year"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Emerging topics (Tavily)
    # -----------------------------
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

    # -----------------------------
    # Citation / influence proxy
    # -----------------------------
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
