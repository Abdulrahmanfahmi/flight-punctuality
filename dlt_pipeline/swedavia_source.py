from datetime import datetime, timezone 
from dlt.sources.helpers import requests

from dlt_pipeline.config import SWEDAVIA_BASE_URL


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