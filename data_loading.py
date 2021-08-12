import json
import re
import time
from collections import Counter
from typing import Set, List, Dict

from fire import Fire
from lxml import etree
from pydantic import BaseModel
from tqdm import tqdm


class Timer(BaseModel):
    name: str
    start: float = None

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start
        print(dict(timer=self.name, duration=round(duration, 3)))


def convert_dblp_to_jsonl(
    path_in: str = "data/dblp-2021-08-01.xml.gz",
    path_out: str = "data/raw.jsonl",
):
    with Timer(name=str(dict(parse=path_in))):
        parser = etree.XMLParser(load_dtd=True)
        tree = etree.parse(path_in, parser=parser)

    with open(path_out, "w") as f:
        for child in tqdm(tree.getroot(), desc=str(dict(write=path_out))):
            record = {}
            for sub in child:
                record.setdefault(sub.tag, []).append(sub.text)
            f.write(json.dumps(record) + "\n")


class RawPaper(BaseModel):
    title: List[str]
    author: List[str]
    year: List[int]
    ee: List[str]
    url: List[str]

    @classmethod
    def parse_venue(cls, text: str) -> str:
        # Eg db/journals/jmlr, db/conf/acl
        for match in re.findall(pattern="db/\\w*/\\w*", string=text):
            return match.split("/")[-1]
        return ""

    @classmethod
    def check_valid_line(cls, text: str, venues: Set[str] = None) -> bool:
        keys = ["title", "author", "year", "ee", "url"]
        if not all([f'"{k}"' in text for k in keys]):
            return False

        if venues:
            return cls.parse_venue(text) in venues
        return True


def test_raw_paper():
    record = {
        "author": ["Matt Garley", "Julia Hockenmaier"],
        "title": [
            "Beefmoves: Dissemination, Diversity, and Dynamics of English Borrowings in a German Hip Hop Forum."
        ],
        "pages": ["135-139"],
        "year": ["2012"],
        "booktitle": ["ACL (2)"],
        "ee": ["https://www.aclweb.org/anthology/P12-2027/"],
        "crossref": ["conf/acl/2012-2"],
        "url": ["db/conf/acl/acl2012-2.html#GarleyH12"],
    }
    paper = RawPaper(**record)
    assert paper.check_valid_line(json.dumps(record))
    assert paper.check_valid_line(json.dumps(record), venues={"acl"})
    assert not paper.check_valid_line(json.dumps(record), venues={"emnlp"})
    record.pop("ee")
    assert not paper.check_valid_line(json.dumps(record))
    return paper


def test_raw_data(path: str = "data/raw.jsonl", path_venues="data/venues.json"):
    with open(path_venues) as f:
        venues = [x for lst in json.load(f).values() for x in lst]

    outputs = []

    with open(path) as f:
        for line in tqdm(f.readlines()):
            o = RawPaper.parse_venue(line)
            outputs.append(o)

    output_set = set(outputs)
    for v in venues:
        assert v in output_set
    print(Counter(outputs).most_common(256))


class Paper(BaseModel):
    title: str
    authors: List[str]
    year: int
    venue: str
    url: str

    @classmethod
    def from_raw(cls, raw: RawPaper):
        return cls(
            title=raw.title[0],
            authors=raw.author,
            year=raw.year[0],
            venue=raw.parse_venue(raw.url[0]),
            url=raw.ee[0],
        )


def test_paper():
    raw = test_raw_paper()
    paper = Paper.from_raw(raw)
    print(paper.json(indent=2))


def filter_papers(
    path_in: str = "data/raw.jsonl",
    path_out: str = "data/filtered.jsonl",
    path_venues: str = "data/venues.json",
):
    with open(path_venues) as f:
        label_to_papers: Dict[str, List[Paper]] = {
            x: [] for lst in json.load(f).values() for x in lst
        }
    labels = set(label_to_papers.keys())

    lines = []
    with open(path_in) as f:
        for text in tqdm(f.readlines(), desc="Check valid"):
            if RawPaper.check_valid_line(text, venues=labels):
                lines.append(text)

    for text in tqdm(lines, desc="Parse papers"):
        try:
            paper = Paper.from_raw(RawPaper(**json.loads(text)))
            assert paper.venue in label_to_papers.keys()
            label_to_papers[paper.venue].append(paper)
        except Exception as e:
            print(e)

    with open(path_out, "w") as f:
        for k, lst in label_to_papers.items():
            assert lst
            for paper in lst:
                f.write(paper.json() + "\n")


if __name__ == "__main__":
    Fire()
