import streamlit as st
from services.paper_service import PaperService


def render_dashboard():
    st.header("📚 Paper Library")

    papers = PaperService.fetch_all()

    if not papers:
        st.info("📂 No research papers uploaded yet.")
        st.markdown("""
        **To get started:**
        1. Go to **Load Papers**
        2. Upload a PDF
        3. Click **Process & Embed**
        """)
        return

    years = sorted(
        {p.get("year") for p in papers if p.get("year") is not None}
    )

    filtered = papers  

    if not years:
        st.info("No year information available.")

    elif len(years) == 1:
        year = years[0]
        st.info(f"Showing papers from year {year}")
        filtered = [p for p in papers if p.get("year") == year]

    else:
        min_year = min(years)
        max_year = max(years)

        year_range = st.slider(
            "Filter by year",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )

        filtered = [
            p for p in papers
            if p.get("year") is not None
            and year_range[0] <= p["year"] <= year_range[1]
        ]

    keyword = st.text_input("Filter by keyword")

    if keyword:
        kw = keyword.lower()
        filtered = [
            p for p in filtered
            if (
                kw in p.get("title", "").lower()
                or kw in p.get("summary", "").lower()
                or kw in " ".join(p.get("keywords", [])).lower()
            )
        ]

    if not filtered:
        st.warning("No papers match the current filters.")
        return

    titles = [p["title"] for p in filtered]

    selected = st.selectbox("Select a paper", titles)

    paper_map = {p["title"]: p for p in filtered}
    paper = paper_map.get(selected)

    if not paper:
        st.warning("Paper not found.")
        return

    st.subheader("📄 Paper Details")

    st.write(f"**Title:** {paper.get('title')}")
    st.write(f"**Authors:** {', '.join(paper.get('authors', []))}")
    st.write(f"**Year:** {paper.get('year')}")
    st.write(f"**Venue:** {paper.get('venue')}")

    st.subheader("🧠 Summary")
    st.write(paper.get("summary"))
