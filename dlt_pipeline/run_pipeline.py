
import dlt

from dlt_pipeline.config import get_extraction_dates, get_snowflake_credentials
from dlt_pipeline.swedavia_source import swedavia_source
from dlt_pipeline.wikipedia_source import wikipedia_source

PIPELINE_NAME = "flight_punctuality"
DATASET_NAME = "raw"


def create_pipeline() -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.snowflake(credentials=get_snowflake_credentials()),
        dataset_name=DATASET_NAME,
    )


def run() -> None:
    pipeline = create_pipeline()

    print(f"Hämtar Swedavia-data för: {get_extraction_dates()}")
    print(pipeline.run(swedavia_source()))

    print("Hämtar Wikipedia-data")
    print(pipeline.run(wikipedia_source()))


if __name__ == "__main__":
    run()