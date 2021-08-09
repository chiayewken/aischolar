import pickle
from typing import List, Any

import numpy as np
from fire import Fire
from pydantic import BaseModel
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_distances

from data_loading import Timer


class Searcher(BaseModel):
    encoder: CountVectorizer = TfidfVectorizer()
    matrix: csr_matrix = None
    results: List[str] = None

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    def fit(self, x: List[str], y: List[str]):
        self.matrix = self.encoder.fit_transform(x)
        self.results = y

    def run(self, query: str) -> List[Any]:
        assert self.matrix is not None and self.results is not None
        x = self.encoder.transform([query])
        dists: List[float] = list(cosine_distances(self.matrix, x).squeeze())
        y = [self.results[i] for i, d in enumerate(dists) if d < 1.0]
        dists = [d for d in dists if d < 1.0]
        results = [y[i] for i in np.argsort(dists)]
        return results


def test_searcher(path_data="data/results.txt", query="beyond accuracy"):
    with open(path_data) as f:
        texts = f.readlines()

    searcher = Searcher()
    searcher.fit(x=texts, y=texts)
    results: List[str] = searcher.run(query)
    for r in results[:3]:
        print(r)


def test_save(path_data="data/results.txt"):
    with open(path_data) as f:
        texts = f.readlines()
    searcher = Searcher()

    with Timer(name="fit_encoder"):
        searcher.fit(x=texts, y=texts)

    with Timer(name="save_encoder"):
        data = pickle.dumps(searcher)

    with Timer(name="load_encoder"):
        searcher = pickle.loads(data)

    with Timer(name="run_after_load"):
        results = searcher.run("causality")
        print(results[:3])


if __name__ == "__main__":
    Fire()
