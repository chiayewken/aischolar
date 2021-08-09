import json
import time
from collections import Counter
from typing import Optional, Set

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
    path_out: str = "data/dblp-2021-08-01.jsonl",
):
    with Timer(name=str(dict(parse=path_in))):
        parser = etree.XMLParser(load_dtd=True)
        tree = etree.parse(path_in, parser=parser)

    with open(path_out, "w") as f:
        for child in tqdm(tree.getroot(), desc=str(dict(write=path_out))):
            record = dict((sub.tag, sub.text) for sub in child)
            f.write(json.dumps(record) + "\n")


class Paper(BaseModel):
    title: Optional[str]
    ee: Optional[str]
    url: Optional[str]
    year: Optional[int]

    def get_conference(self) -> Optional[str]:
        url = self.url or ""
        prefix = "db/conf/"
        if url.startswith(prefix):
            name = url[len(prefix) :].split("/")[0]
            return name

    @classmethod
    def check_valid_line(cls, text: str, conferences: Set[str] = None) -> bool:
        prefix = "db/conf/"
        keys = ["title", "ee", "url", "year", prefix]
        if not all([k in text for k in keys]):
            return False

        if conferences:
            name = text.split(prefix)[-1].split("/")[0]
            return name in conferences
        return True

    def is_valid(self) -> bool:
        values = [self.title, self.ee, self.get_conference(), self.year]
        return all([x is not None for x in values])

    def as_text(self) -> str:
        assert self.is_valid()
        return f"{self.year} {self.get_conference()} {self.ee} {self.title}"


def test_paper():
    record = {
        "author": "Jianbo Tang",
        "title": "LICHEE: Improving Language Model Pre-training with Multi-grained Tokenization.",
        "pages": "1383-1392",
        "year": "2021",
        "booktitle": "ACL/IJCNLP (Findings)",
        "ee": "https://aclanthology.org/2021.findings-acl.119",
        "crossref": "conf/acl/2021f",
        "url": "db/conf/acl/acl2021f.html#GuoZZNLLLT21",
    }
    paper = Paper(**record)
    print(paper.as_text())


def test_dblp(path: str = "data/dblp-2021-08-01.jsonl"):
    events = []
    with open(path) as f:
        for line in tqdm(f.readlines()):
            if Paper.check_valid_line(line):
                record = json.loads(line)
                url = record.get("url", "")
                prefix = "db/conf/"
                name = url[len(prefix) :].split("/")[0]
                events.append(name)

    print(Counter(events))


def write_results(
    path_in: str = "data/dblp-2021-08-01.jsonl",
    path_out: str = "data/results.txt",
    path_conference_list: str = "data/conferences.txt",
):
    with open(path_conference_list) as f:
        name_to_paper = {line.strip(): [] for line in f}
        conferences = set(name_to_paper.keys())

    texts = []
    with open(path_in) as f:
        progress = tqdm(f.readlines(), desc=str(dict(write_results=path_in)))
        for line in progress:
            if Paper.check_valid_line(line, conferences):
                progress.set_postfix(success=len(texts))
                record = json.loads(line)
                paper = Paper(**record)
                if paper.is_valid():
                    texts.append(paper.as_text())

    with open(path_out, "w") as f:
        f.write("\n".join(texts))


def test_results(path: str = "data/results.txt"):
    with Timer(name=str(dict(load=path))):
        with open(path) as f:
            lines = f.readlines()
            print(dict(lines=len(lines)))


if __name__ == "__main__":
    Fire()
