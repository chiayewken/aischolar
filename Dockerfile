FROM python:3.8-slim

RUN pip install -U pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY data_loading.py data_loading.py
COPY searching.py searching.py
COPY data/venues.json data/venues.json
COPY data/searcher.pkl data/searcher.pkl
COPY main.py main.py

ENTRYPOINT "streamlit run main.py --server.port $PORT --server.address 0.0.0.0"
