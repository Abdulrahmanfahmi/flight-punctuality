import streamlit as st

from charts import delay_by_airline, delay_by_airport, delay_by_date
from data import load_flights

FLIGHT_TYPE_LABELS = {"arrival": "Ankomster", "departure": "Avgångar"}
METRIC_OPTIONS = {"Andel försenade (%)": "andel_forsenade", "Antal försenade": "forsenade"}


def filter_flights(df, date_range, airports, flight_types):
    filtered = df[df["flight_type"].isin(flight_types)]
    if len(date_range) == 2:
        start, end = date_range
        filtered = filtered[(filtered["flight_date"] >= start) & (filtered["flight_date"] <= end)]
    if airports:
        filtered = filtered[filtered["airport_label"].isin(airports)]
    return filtered


def show_kpis(df):
    completed = df["is_completed"].eq(True).sum()
    delayed = df["is_delayed"].eq(True).sum()
    cancelled = df["is_cancelled"].eq(True).sum()
    share_delayed = 100 * delayed / completed if completed else 0
    avg_delay = df.loc[df["is_completed"].eq(True), "delay_minutes"].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Genomförda flyg", f"{completed:,}".replace(",", " "))
    col2.metric("Försenade (>15 min)", f"{delayed:,}".replace(",", " "))
    col3.metric("Andel försenade", f"{share_delayed:.1f} %")
    col4.metric("Snittavvikelse", f"{avg_delay:.1f} min" if completed else "–")
    col5.metric("Inställda", f"{cancelled}")


st.set_page_config(page_title="Flygpunktlighet", page_icon="", layout="wide")
st.title(" Punktlighet vid Swedavias flygplatser")
st.caption(
    "Ett flyg räknas som försenat om det är mer än 15 minuter efter tidtabell. "
    "Andelen räknas på genomförda flyg."
)

flights = load_flights()
flights["airport_label"] = flights["airport_city"] + " (" + flights["airport_iata"] + ")"

# --- Filter ---
st.sidebar.header("Filter")
min_date, max_date = flights["flight_date"].min(), flights["flight_date"].max()
date_range = st.sidebar.date_input(
    "Datum", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
airports = st.sidebar.multiselect(
    "Flygplats", sorted(flights["airport_label"].unique()), placeholder="Alla flygplatser"
)
flight_types = st.sidebar.multiselect(
    "Typ av flyg",
    options=list(FLIGHT_TYPE_LABELS),
    default=list(FLIGHT_TYPE_LABELS),
    format_func=FLIGHT_TYPE_LABELS.get,
)
metric_label = st.sidebar.radio("Visa i diagrammen", list(METRIC_OPTIONS))
metric = METRIC_OPTIONS[metric_label]

filtered = filter_flights(flights, date_range, airports, flight_types)

# --- Nyckeltal ---
show_kpis(filtered)
st.divider()

# --- Per flygplats ---
st.subheader("Förseningar per flygplats")
st.plotly_chart(delay_by_airport(filtered, metric))
st.caption(
    "Beslutsstöd: vilka flygplatser behöver extra resurser, till exempel mer "
    "markpersonal eller bättre planering av gater och säkerhetskontroll?"
)

# --- Per flygbolag ---
st.subheader("Flygbolag med flest förseningar")
st.plotly_chart(delay_by_airline(filtered, metric))
st.caption(
    "Beslutsstöd: vilka flygbolag ska flygplatsen följa upp med? "
    "Bara flygbolag med minst 20 genomförda flyg visas, eftersom få flyg ger osäkra procent."
)

# --- Per datum ---
st.subheader("Förseningar per dag")
st.plotly_chart(delay_by_date(filtered, metric))
st.caption(
    "Beslutsstöd: blir punktligheten bättre eller sämre, och finns det mönster "
    "som helger eller enskilda dagar med störningar? Dagar med färre än 10 "
    "genomförda flyg visas inte, eftersom få flyg ger missvisande procent."
)