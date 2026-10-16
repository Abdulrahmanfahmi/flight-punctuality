from pathlib import Path

import dagster as dg
import dlt
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dagster_dlt.translator import DltResourceTranslatorData
from dotenv import load_dotenv

from dlt_pipeline.config import get_snowflake_credentials
from dlt_pipeline.swedavia_source import swedavia_source
from dlt_pipeline.wikipedia_source import wikipedia_source

load_dotenv()

DBT_PROJECT_DIR = Path(__file__).parent.parent / "dbt_project"


# ---------- dlt: laddning till FLIGHT_DB.RAW ----------

class RawTableTranslator(DagsterDltTranslator):
    """Döper dlt-tabellerna till raw/<tabell>, samma namn som dbt:s sources."""

    def get_asset_spec(self, data: DltResourceTranslatorData) -> dg.AssetSpec:
        default_spec = super().get_asset_spec(data)
        return default_spec.replace_attributes(key=dg.AssetKey(["raw", data.resource.name]))


def create_dlt_pipeline(name: str) -> dlt.Pipeline:
    """En dlt-pipeline per källa, så att de kan köras samtidigt utan att krocka."""
    return dlt.pipeline(
        pipeline_name=name,
        destination=dlt.destinations.snowflake(credentials=get_snowflake_credentials()),
        dataset_name="raw",
    )


@dlt_assets(
    dlt_source=swedavia_source(),
    dlt_pipeline=create_dlt_pipeline("swedavia"),
    name="swedavia",
    group_name="raw",
    dagster_dlt_translator=RawTableTranslator(),
)
def swedavia_assets(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    """Ankomster och avgångar från Swedavia. Datumen räknas ut när körningen startar."""
    yield from dlt.run(context=context, dlt_source=swedavia_source())


@dlt_assets(
    dlt_source=wikipedia_source(),
    dlt_pipeline=create_dlt_pipeline("wikipedia"),
    name="wikipedia",
    group_name="raw",
    dagster_dlt_translator=RawTableTranslator(),
)
def wikipedia_assets(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    """Flygbolag och flygplatser från Wikipedia."""
    yield from dlt.run(context=context)


# ---------- dbt: transformation till STAGING och MARTS ----------

dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROJECT_DIR)
dbt_project.prepare_if_dev()


@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    """Alla dbt-modeller och tester som Dagster-assets."""
    yield from dbt.cli(["build"], context=context).stream()


# ---------- Job och schema ----------

flight_pipeline_job = dg.define_asset_job(
    name="flight_pipeline",
    selection=dg.AssetSelection.all(),
    description="Hela pipelinen: dlt laddar RAW, sedan bygger dbt STAGING och MARTS.",
)

daily_schedule = dg.ScheduleDefinition(
    job=flight_pipeline_job,
    cron_schedule="0 6 * * *",
    execution_timezone="Europe/Stockholm",
    default_status=dg.DefaultScheduleStatus.RUNNING,
)


# ---------- Allt samlat ----------

defs = dg.Definitions(
    assets=[swedavia_assets, wikipedia_assets, dbt_models],
    jobs=[flight_pipeline_job],
    schedules=[daily_schedule],
    resources={
        "dlt": DagsterDltResource(),
        "dbt": DbtCliResource(project_dir=dbt_project),
    },
)