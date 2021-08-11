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
    filter_year = st.sidebar.slider("Filter by Year", 2000, 2021, (2019, 2021), 1)
    min_year, max_year = filter_year
    filter_conference = st.multiselect("Filter by Conference",
            ['None', 'NLP', 'ACL,EMNLP,NAACL', 'CV', 'ML', 'ACL', 'EMNLP', 'NAACL'],
            default='ACL,EMNLP,NAACL'
            )
    conference_list = []
    if 'None' not in filter_conference: 
        if 'NLP' in filter_conference:
            conference_list += ['ACL', 'EMNLP', 'EACL', 'COLING', 'IJNLP', 'NAACL', 'IJCAI', 'AAAI', 'LREC', 'SEMEVAL', 'SIGDIAL']
        if 'ACL,EMNLP,NAACL' in filter_conference:
            conference_list += ['ACL', 'EMNLP', 'NAACL']
        if 'CV' in filter_conference:
            conference_list += ['CVPR', 'ICCV', 'ECCV']
        if 'ML' in filter_conference:
            conference_list += ['ICLR', 'NIPS', 'ICML']
    else:
        conference_list = ['ICLR','NIPS', 'ICML', 'AAAI' ,'IJCAI' ,'ACL', 'EMNLP' ,'NAACL' ,'COLING' ,'LREC' ,'EACL' ,'SEMEVAL' ,'SIGDIAL' ,'IJCNLP' ,'INTERSPEECH' ,'ICASSP' ,'CVPR' ,'ICCV' ,'ECCV']



    searcher = pickle.loads(cache_searcher(path_data))

    results: List[str] = searcher.run(query)
    duration = round(time.time() - start, 3)
    st.write(f"About {len(results)} results ({duration} seconds)")

    num_result = 0
    for r in results:
        if min_year <= int(r[1:].split()[0]) <= max_year:
            if r.split()[1].split(']')[0].upper() in conference_list:
                st.markdown(r)
                num_result += 1
        if num_result >= max_results: break


if __name__ == "__main__":
    main()
