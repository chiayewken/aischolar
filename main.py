import json
import pickle
import time
from collections import Counter
from typing import Dict, List

import streamlit as st

from data_loading import Paper
from searching import AuthorReranker, Searcher, VenueReranker, YearReranker


def highlight(query: str, text: str, color: str = "lightyellow") -> str:
    words = []
    query_set = set(query.lower().split())
    for w in text.split():
        for q in query_set:
            if q in w.lower():
                w = f'<mark style="background-color: {color}">{w}</mark>'
                break
        words.append(w)
    return " ".join(words)

def get_top_k_authors(papers, k=7):
    author_list = Counter([a for p in papers for a in p.authors]).most_common(5)
    return [a[0] for a in author_list]

def get_query(label: str, default: str) -> str:
    # Support input via url parameters
    params = st.experimental_get_query_params()
    query = params.get("query", default)
    query = query[0] if isinstance(query, list) else query
    query = st.text_input(label, value=query)
    st.experimental_set_query_params(query=query)
    return query


def main(
    path_searcher: str = "data/searcher.pkl",
    path_venues: str = "data/venues.json",
    query: str = "optimal vocabulary",
    max_results: int = 100,
    title: str = "AI Scholar",
):
    start = time.time()
    st.set_page_config(page_title=title, initial_sidebar_state="collapsed")
    with open(path_venues) as f:
        type_to_venues: Dict[str, List[str]] = json.load(f)
        type_to_venues["All"] = [v for lst in type_to_venues.values() for v in lst]

    venue_type = st.sidebar.radio("Research Category", sorted(type_to_venues.keys()))
    venues = type_to_venues[venue_type]
    venues = st.sidebar.multiselect("Paper Venue", venues, default=venues)
    query = get_query("Search by Title, Author, Year or Venue", default=query)
    min_year, max_year = st.slider("Year Range", 2012, 2021, value=(2018, 2021))
    with open(path_searcher, "rb") as f:
        searcher = pickle.load(f)
        assert isinstance(searcher, Searcher)

    venue_set = set(venues)
    results: List[str] = searcher.run(query)
    papers = []
    for r in results:
        p = Paper(**json.loads(r))
        if min_year <= p.year <= max_year:
            if p.venue in venue_set:
                papers.append(p)

    duration = round(time.time() - start, 3)
    max_results = min(max_results, len(papers))
    st.write(f"Showing {max_results} of {len(papers)} results ({duration} seconds)")

    vip_authors = get_top_k_authors(papers)
    select_author = st.multiselect("Top Authors related to search", vip_authors)
    query = query + ' '.join(select_author)
    
    for reranker in [YearReranker(), VenueReranker(), AuthorReranker()]:
        papers = reranker.run(query, papers)


    for p in papers[:max_results]:
        text = f"[{p.year} {p.venue.upper()}]({p.url}) {p.title}"
        text = highlight(query, text)
        st.markdown(text, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
