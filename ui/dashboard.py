import streamlit as st
from services.paper_service import PaperService
from ui.chat import render_chat


def render_dashboard():
    """
    Renders the main dashboard interface for browsing, filtering, and interacting with research papers

    Args:
           No arguments
    Returns:
           None
    """
    st.header("📚 Paper Library")
    st.markdown(
            """
            <style>
            .vertical-divider {
                border-left: 2px solid #DDD;
                height: 100vh;
                margin: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    papers = PaperService.fetch_all()

    if not papers:
        st.info("📂 No research papers available yet.")
        st.markdown("""
        Papers are added by the admin via the ingestion pipeline.
        
        Once papers are processed, they will appear here automatically.
        """)
        return


    left_col, divider_col, right_col = st.columns([1, 0.03, 1])

    with divider_col:
            st.markdown(
                '<div class="vertical-divider"></div>',
                unsafe_allow_html=True
            )

    with divider_col:
        st.markdown(
            '<div class="vertical-divider"></div>',
            unsafe_allow_html=True
        )



    with left_col:
        years = sorted(
            {p.get("year") for p in papers if p.get("year") is not None}
        )

        filtered = papers

        if years:
            if len(years) == 1:
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
        else:
            st.info("No year information available.")

        all_keywords = sorted({
            kw
            for p in papers
            for kw in p.get("keywords", [])
        })

        selected_keywords = st.multiselect(
            "Filter by keyword (optional)",
            options=all_keywords
        )

        if selected_keywords:
            filtered = [
                p for p in filtered
                if any(
                    kw.lower() in " ".join(p.get("keywords", [])).lower()
                    for kw in selected_keywords
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
        st.write(" ".join(paper.get("summary", [])))


    with right_col:
        if st.button("💬 Ask about this paper"):
                    st.session_state.focus_chat = True
                    st.session_state.active_paper_title = paper["title"]
        if st.session_state.get("focus_chat"):
            st.subheader(
                f"💬 Chat — {st.session_state.active_paper_title}"
            )
            render_chat(scoped=True)

            if st.button("❌ Close chat"):
                st.session_state.focus_chat = False
                st.session_state.pop("active_paper_title", None)
                st.rerun()
        else:
            st.info("👈 Select a paper and click **Ask about this paper** to start chatting.")