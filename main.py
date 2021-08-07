from pathlib import Path
from typing import List, Set

import streamlit as st

from data_loading import BibtexData
from searching import Searcher


@st.cache
def load_event_set(path: str) -> Set[str]:
    data = BibtexData.load(Path(path))
    return set([p.get_conference_code() for p in data.papers])


@st.cache
def load_texts(path: str, year: int, event_set: Set[str]) -> List[str]:
    data = BibtexData.load(Path(path))
    texts = []
    for p in data.papers:
        if p.year >= year and p.get_conference_code() in event_set:
            origin = f"{p.year} {p.get_conference_code().upper()}"
            url = p.url.strip('"')
            texts.append(f"[{origin}]({url}) {p.title}")
    return texts


def main(
    path_data: str = "data/anthology+abstracts.bib.gz",
    query: str = "intrinsic dimensionality",
    events: List[str] = ("acl", "emnlp", "naacl", "coling", "eacl", "findings", "lrec"),
):
    st.header("ReSearch: Find NLP conference papers easily")
    event_set = load_event_set(path_data)

    query = st.text_input("What paper are you looking for?", value=query)
    limit = st.number_input("How many results to show?", value=16)
    year = st.number_input("Earliest publication year?", value=2018)
    events = st.multiselect(
        "Which conferences to consider?",
        options=sorted(event_set),
        default=sorted(events),
    )

    texts = load_texts(path_data, year, event_set=set(events))
    st.write(f"Papers found: {len(texts)}")
    searcher = Searcher(x=texts, y=texts)
    results: List[str] = searcher.run(query)

    for r in results[: int(limit)]:
        st.markdown(r)


if __name__ == "__main__":
    main()
