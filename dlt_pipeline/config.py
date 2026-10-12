import os
from datetime import datetime, timedelta 
from zoneinfo import ZoneInfo 
from dotenv import load_dotenv

load_dotenv()


SWEDAVIA_BASE_URL = "https://api.swedavia.se/flightinfo/v2"

SWEDAVIA_AIRPORTS = ["ARN", "GOT", "MMX", "BMA", "LLA", "UME", "OSD", "VBY", "KRN", "RNB"]

FLIGHT_TYPES = ["arrivals", "departures"]

DAYS_TO_EXTRACT = 3


WIKIPEDIA_AIRLINES_URL = "https://en.wikipedia.org/wiki/List_of_airline_codes"
WIKIPEDIA_AIRPORTS_URL = "https://en.wikipedia.org/wiki/List_of_airports_in_Sweden"
WIKIPEDIA_HEADERS = {"User-Agent": "flight-punctuality-student-project"}

TIMEZONE = ZoneInfo("Europe/Stockholm")

REQUEST_PAUSE_SECONDS = 0.5

def get_extraction_dates(days: int = DAYS_TO_EXTRACT) -> list[str]:
    today = datetime.now(TIMEZONE).date()
    return [(today - timedelta(days=i)).isoformat() for i in range(days)]


def get_swedavia_api_key() -> str:
    api_key = os.getenv("SWEDAVIA_API_KEY")
    if not api_key:
        raise ValueError("SWEDAVIA_API_KEY saknas i .env")
    return api_key


def get_snowflake_credentials() -> dict:
    return {
        "host": os.environ["SNOWFLAKE_ACCOUNT"],
        "database": os.environ["SNOWFLAKE_DATABASE"],
        "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        "username": os.environ["SNOWFLAKE_DLT_USER"],
        "password": os.environ["SNOWFLAKE_DLT_PASSWORD"],
        "role": os.environ["SNOWFLAKE_DLT_ROLE"],
    }