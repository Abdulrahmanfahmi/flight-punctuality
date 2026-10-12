import time
from datetime import datetime, timezone

import dlt  
from dlt.sources.helpers import requests

from dlt_pipeline.config import ( 
    FLIGHT_TYPES,
    REQUEST_PAUSE_SECONDS,
    SWEDAVIA_AIRPORTS,
    SWEDAVIA_BASE_URL,
    get_extraction_dates,
    get_swedavia_api_key,
)


def fetch_flights(airport: str, flight_type: str, date: str, api_key: str) -> list[dict]:
    url = f"{SWEDAVIA_BASE_URL}/{airport}/{flight_type}/{date}"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json().get("flights", [])


def add_metadata(flight: dict, airport: str, flight_type: str, date: str) -> dict:
    time_field = "arrivalTime" if flight_type == "arrivals" else "departureTime"
    scheduled_utc = flight.get(time_field, {}).get("scheduledUtc")

    return {
        "flight_key": f"{airport}_{flight.get('flightId')}_{scheduled_utc}",
        "airport_iata": airport,
        "flight_type": flight_type.rstrip("s"),
        "query_date": date,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        **flight,
    }


def get_flights(flight_type: str, airports: list[str], dates: list[str], api_key: str):
    seen_keys = set()
    for airport in airports:
        for date in dates:
            flights = fetch_flights(airport, flight_type, date, api_key)
            print(f"  {flight_type:<10} {airport} {date}: {len(flights)} flyg")

            for flight in flights:
                record = add_metadata(flight, airport, flight_type, date)
                if record["flight_key"] in seen_keys:
                    continue
                seen_keys.add(record["flight_key"])
                yield record

            time.sleep(REQUEST_PAUSE_SECONDS)


@dlt.source(name="swedavia", max_table_nesting=1)
def swedavia_source(airports: list[str] | None = None, dates: list[str] | None = None):
    """Ger två tabeller: arrivals och departures."""
    api_key = get_swedavia_api_key()
    airports = airports or SWEDAVIA_AIRPORTS
    dates = dates or get_extraction_dates()

    for flight_type in FLIGHT_TYPES:
        yield dlt.resource(
            get_flights(flight_type, airports, dates, api_key),
            name=flight_type,
            write_disposition="merge",
            primary_key="flight_key",
        )



if __name__ == "__main__":
    today = get_extraction_dates()[:1]
    source = swedavia_source(airports=["VBY"], dates=today)

    print("Tabeller:", list(source.resources.keys()))
    for name, resource in source.resources.items():
        print(f"  {name}: write_disposition={resource.write_disposition}")

    records = list(source)
    print("Rader totalt:", len(records))