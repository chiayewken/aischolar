#!/usr/bin/env bash
set -e

cd data
curl -O https://dblp.org/xml/release/dblp-2021-08-01.xml.gz
curl -O https://dblp.org/xml/release/dblp-2019-11-22.dtd
cd ..
python data_loading.py convert_dblp_to_jsonl
python data_loading.py write_results
