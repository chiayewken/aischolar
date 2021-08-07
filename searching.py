from pathlib import Path
from typing import List, Any

import numpy as np
from fire import Fire
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances

from data_loading import BibtexData, Paper


class Searcher(BaseModel):
    x: List[str]
    y: List[Any]

    def run(self, query: str) -> List[Any]:
        encoder = TfidfVectorizer()
        x = encoder.fit_transform(self.x)
        x_query = encoder.transform([query])
        print(dict(x=x.shape, x_query=x_query.shape))
        dists: np.ndarray = cosine_distances(x, x_query)
        rank: np.ndarray = np.argsort(dists, axis=0).squeeze()
        return [self.y[i] for i in rank]


def test_searcher(path_data="data/anthology+abstracts.bib.gz", query="beyond accuracy"):
    data = BibtexData.load(Path(path_data))
    searcher = Searcher(x=[p.title or "" for p in data.papers], y=data.papers)
    results: List[Paper] = searcher.run(query)
    for r in results[:3]:
        print(r.json(indent=2))
        print()


if __name__ == "__main__":
    Fire(test_searcher)
