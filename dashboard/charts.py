import pandas as pd
import plotly.express as px

FLIGHT_TYPE_LABELS = {"arrival": "Ankomster", "departure": "Avgångar"}
COLORS = {"Ankomster": "#2471A3", "Avgångar": "#E67E22"}
METRIC_LABELS = {
    "forsenade": "Antal försenade",
    "andel_forsenade": "Andel försenade (%)",
}
HOVER_LABELS = {
    "genomforda": "Genomförda",
    "forsenade": "Försenade",
    "andel_forsenade": "Andel (%)",
    "day_name": "Veckodag",
}


def summarize(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    summary = (
        df.assign(
            completed=df["is_completed"].eq(True),
            delayed=df["is_delayed"].eq(True),
        )
        .groupby(by, as_index=False)
        .agg(genomforda=("completed", "sum"), forsenade=("delayed", "sum"))
    )
    summary = summary[summary["genomforda"] > 0]
    summary["andel_forsenade"] = (100 * summary["forsenade"] / summary["genomforda"]).round(1)
    if "flight_type" in by:
        summary["typ"] = summary["flight_type"].map(FLIGHT_TYPE_LABELS)
    return summary


def delay_by_airport(df: pd.DataFrame, metric: str):
    data = summarize(df, ["airport_label", "flight_type"])
    fig = px.bar(
        data,
        x=metric,
        y="airport_label",
        color="typ",
        barmode="group",
        orientation="h",
        text_auto=True,
        color_discrete_map=COLORS,
        hover_data={"genomforda": True, "forsenade": True, "andel_forsenade": True},
        labels={metric: METRIC_LABELS[metric], "airport_label": "", "typ": "", **HOVER_LABELS},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    return fig


def delay_by_airline(df: pd.DataFrame, metric: str, min_flights: int = 20, top_n: int = 15):
    data = summarize(df, ["airline_name"])
    data = data[data["genomforda"] >= min_flights].nlargest(top_n, metric)
    fig = px.bar(
        data,
        x=metric,
        y="airline_name",
        orientation="h",
        text_auto=True,
        color_discrete_sequence=["#C0392B"],
        hover_data={"genomforda": True, "forsenade": True, "andel_forsenade": True},
        labels={metric: METRIC_LABELS[metric], "airline_name": "", **HOVER_LABELS},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    return fig


def delay_by_date(df: pd.DataFrame, metric: str, min_flights: int = 10):
    data = summarize(df, ["flight_date", "day_name", "flight_type"])
    data = data[data["genomforda"] >= min_flights]
    fig = px.line(
        data,
        x="flight_date",
        y=metric,
        color="typ",
        markers=True,
        color_discrete_map=COLORS,
        hover_data={"day_name": True, "genomforda": True, "forsenade": True},
        labels={metric: METRIC_LABELS[metric], "flight_date": "Datum", "typ": "", **HOVER_LABELS},
    )
    fig.update_xaxes(dtick="D1", tickformat="%a %d %b")
    fig.update_layout(height=400)
    return fig