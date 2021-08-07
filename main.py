from pathlib import Path
from typing import List

import streamlit as st

from data_loading import BibtexData, Paper
from searching import Searcher


def main(path_data="data/anthology+abstracts.bib.gz", query="intrinsic dimensionality"):
    data = BibtexData.load(Path(path_data))
    searcher = Searcher(x=[p.title or "" for p in data.papers], y=data.papers)
    events = sorted(set([p.booktitle for p in data.papers if p.booktitle is not None]))

    query = st.text_input("What paper are you looking for?", value=query)
    limit = st.number_input("How many results to show?", value=5)
    year = st.number_input("After which year did the paper come out?", value=2018)
    events = st.multiselect("Which conferences to filter?", options=events)
    event_set = set(events)

    results: List[Paper] = searcher.run(query)
    results = [r for r in results if r.year > year]
    if event_set:
        results = [r for r in results if r.booktitle in event_set]

    for r in results[:limit]:
        st.json(r.dict())


if __name__ == "__main__":
    main()
