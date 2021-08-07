import re
from gzip import GzipFile
from pathlib import Path
from typing import List, Optional, Tuple

from fire import Fire
from pydantic import BaseModel
from tqdm import tqdm


def parse_gzip_lines(path: Path) -> List[str]:
    with GzipFile(str(path)) as f:
        return [line.decode() for line in f]


class Paper(BaseModel):
    title: Optional[str]
    author: Optional[str]
    booktitle: Optional[str]
    month: Optional[str]
    year: int
    url: str
    publisher: Optional[str]
    abstract: Optional[str]

    def get_authors(self) -> List[str]:
        # Eg "Yao, Yiqun  and\n      Papakostas, Michalis  and\n      Burzo, Mihai"
        return [name.strip() for name in self.author.split("and\n")]

    @classmethod
    def parse_line(cls, line: str) -> Tuple[str, str]:
        line = line.strip().strip(",")
        key, value = line.split(" = ")[-2:]
        key = key.strip()
        value = value.strip("'").strip('"')
        return key, value

    @classmethod
    def fix_lines(cls, lines_raw: List[str]) -> List[str]:
        new = []
        for line in lines_raw:
            if " = " in line:
                new.append(line)
            else:
                new[-1] += line
        return new

    @classmethod
    def from_lines(cls, lines_raw: List[str]):
        lines_fixed = cls.fix_lines(lines_raw)
        record = {}
        for line in lines_fixed:
            key, value = cls.parse_line(line)
            record[key] = value
        return cls(**record)


class BibtexData(BaseModel):
    papers: List[Paper]

    @classmethod
    def load(cls, path: Path):
        # Tried https://github.com/sciunto-org/python-bibtexparser but too slow
        if path.suffix == ".gz":
            lines_raw = parse_gzip_lines(path)
        else:
            with open(path) as f:
                lines_raw = f.readlines()

        splits = cls.split_lines(lines_raw)
        papers = [
            Paper.from_lines(lst)
            for lst in tqdm(splits, desc=str(dict(Bibtex_load=path)))
        ]
        return cls(papers=papers)

    @classmethod
    def split_lines(cls, lines_raw: List[str]) -> List[List[str]]:
        splits = []
        temp = []
        pattern_start = re.compile("@\\w*{")

        for line in lines_raw:
            if line.strip() == "}":
                temp.append(line)
                splits.append(temp)
                temp = []
                continue

            matches = pattern_start.findall(line)
            if not matches:
                temp.append(line)
        return splits


def test_data(path: str = "anthology+abstracts.bib.gz"):
    data = BibtexData.load(Path(path))
    paper = data.papers[1000]
    print(paper.json(indent=2))
    print(paper.get_authors())


if __name__ == "__main__":
    Fire(test_data)
