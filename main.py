import json
import pickle
import time
from typing import List, Dict

import streamlit as st

from data_loading import Paper
from searching import Searcher, YearReranker, AuthorReranker, VenueReranker


@st.cache
def cache_searcher(path_data: str) -> bytes:
    with open(path_data) as f:
        y = f.readlines()
    papers = [Paper(**json.loads(line)) for line in y]
    x = [" ".join([p.title, " ".join(p.authors)]) for p in papers]

    searcher = Searcher()
    searcher.fit(x=x, y=y)
    return pickle.dumps(searcher)


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


def main(
    path_data: str = "data/filtered.jsonl",
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
    query = st.text_input("Search by Title, Author, Year or Venue", value=query)
    min_year, max_year = st.slider("Year Range", 2012, 2021, value=(2018, 2021))
    searcher = pickle.loads(cache_searcher(path_data))

    venue_set = set(venues)
    results: List[str] = searcher.run(query)
    papers = []
    for r in results:
        p = Paper(**json.loads(r))
        if min_year <= p.year <= max_year:
            if p.venue in venue_set:
                papers.append(p)

    for reranker in [YearReranker(), VenueReranker(), AuthorReranker()]:
        papers = reranker.run(query, papers)

    duration = round(time.time() - start, 3)
    max_results = min(max_results, len(papers))
    st.write(f"Showing {max_results} of {len(papers)} results ({duration} seconds)")

    for p in papers[:max_results]:
        text = f"[{p.year} {p.venue.upper()}]({p.url}) {p.title}"
        text = highlight(query, text)
        st.markdown(text, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
