#!/usr/bin/env bash
set -e

if [[ ! -f data/raw.jsonl ]]; then
  cd data
  curl -O https://dblp.org/xml/release/dblp-2021-08-01.xml.gz
  curl -O https://dblp.org/xml/release/dblp-2019-11-22.dtd
  cd ..
  python data_loading.py convert_dblp_to_jsonl --path_in data/dblp-2021-08-01.xml.gz --path_out data/raw.jsonl
fi

python data_loading.py filter_papers --path_in data/raw.jsonl --path_out data/filtered.jsonl
python searching.py save_searcher --path_in data/filtered.jsonl --path_out data/searcher.pkl
