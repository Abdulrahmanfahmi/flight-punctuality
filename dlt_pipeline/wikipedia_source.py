import io
import re

import pandas as pd
from dlt.sources.helpers import requests

from dlt_pipeline.config import (
    WIKIPEDIA_AIRLINES_URL,
    WIKIPEDIA_AIRPORTS_URL,
    WIKIPEDIA_HEADERS,
)


def read_wikipedia_table(url: str, table_index: int = 0) -> pd.DataFrame:
    response = requests.get(url, headers=WIKIPEDIA_HEADERS, timeout=30)
    response.raise_for_status()
    return pd.read_html(io.StringIO(response.text))[table_index]


def clean_column_name(name: str) -> str:
    name = re.sub(r"\[.*?\]", "", str(name))
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    return name.strip("_").lower()


if __name__ == "__main__":
    df = read_wikipedia_table(WIKIPEDIA_AIRPORTS_URL)
    print("Rader och kolumner:", df.shape)
    print("Före:", list(df.columns))
    print("Efter:", [clean_column_name(c) for c in df.columns])