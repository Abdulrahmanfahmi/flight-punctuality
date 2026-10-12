import time 
from datetime import datetime, timezone 
from dlt.sources.helpers import requests
from dlt_pipeline.config import SWEDAVIA_BASE_URL
from dlt_pipeline.config import REQUEST_PAUSE_SECONDS, SWEDAVIA_BASE_URL

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

if __name__ == "__main__":
    from dlt_pipeline.config import get_extraction_dates, get_swedavia_api_key

    today = get_extraction_dates()[:1]
    records = list(get_flights("departures", ["ARN", "VBY"], today, get_swedavia_api_key()))
    print("Totalt:", len(records), "avgångar")
    print("Exempel:", records[0]["flight_key"])