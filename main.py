import pickle
import time
from typing import List

import streamlit as st

from searching import Searcher


@st.cache
def cache_searcher(path_data: str) -> bytes:
    texts = []
    with open(path_data) as f:
        for line in f:
            year, conference, url, title = line.strip().split(maxsplit=3)
            texts.append(f"[{year} {conference.upper()}]({url}) {title}")

    searcher = Searcher()
    searcher.fit(x=texts, y=texts)
    return pickle.dumps(searcher)


def main(
    path_data: str = "data/results.txt",
    query: str = "optimal vocabulary",
    max_results: int = 100,
):
    start = time.time()
    st.header("ReSearch: Find NLP conference papers easily")

    query = st.text_input("What paper are you looking for?", value=query)
    min_year = st.number_input("Earliest publication year?", value=2018)
    searcher = pickle.loads(cache_searcher(path_data))

    results: List[str] = searcher.run(query)
    results = [text for text in results if int(text[1:].split()[0]) >= min_year]
    duration = round(time.time() - start, 3)
    st.write(f"About {len(results)} results ({duration} seconds)")

    for r in results[:max_results]:
        st.markdown(r)


if __name__ == "__main__":
    main()
