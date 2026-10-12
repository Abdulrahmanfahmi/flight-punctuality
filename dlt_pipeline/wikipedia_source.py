import io
import re
import dlt
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

def to_records(df: pd.DataFrame) -> list[dict]:
    df = df.rename(columns=clean_column_name)
    df = df.astype(object).where(pd.notna(df), None)
    return df.to_dict(orient="records")


@dlt.source(name="wikipedia")
def wikipedia_source():
    @dlt.resource(name="airlines", write_disposition="replace")
    def airlines():
        yield to_records(read_wikipedia_table(WIKIPEDIA_AIRLINES_URL))

    @dlt.resource(name="airports", write_disposition="replace")
    def airports():
        yield to_records(read_wikipedia_table(WIKIPEDIA_AIRPORTS_URL))

    return airlines, airports


if __name__ == "__main__":
    source = wikipedia_source()
    print("Tabeller:", list(source.resources.keys()))

    records = list(source.resources["airports"])
    print("Antal flygplatser:", len(records))
    arlanda = [r for r in records if r["iata"] == "ARN"][0]
    print("Arlanda:", arlanda)