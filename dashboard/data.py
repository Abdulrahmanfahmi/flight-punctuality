import os

import pandas as pd
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_STREAMLIT_USER"],
        password=os.environ["SNOWFLAKE_STREAMLIT_PASSWORD"],
        role=os.environ["SNOWFLAKE_STREAMLIT_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="MARTS",
    )


@st.cache_data(ttl=600)
def run_query(sql: str) -> pd.DataFrame:
    cursor = get_connection().cursor()
    cursor.execute(sql)
    columns = [col[0].lower() for col in cursor.description]
    return pd.DataFrame(cursor.fetchall(), columns=columns)


def load_flights() -> pd.DataFrame:
    df = run_query("""
        select
            f.flight_key,
            f.flight_date,
            f.flight_type,
            f.flight_id,
            f.status_code,
            f.delay_minutes,
            f.is_completed,
            f.is_delayed,
            f.is_cancelled,
            a.airport_iata,
            a.city          as airport_city,
            l.airline_icao,
            l.airline_name,
            l.country       as airline_country,
            d.day_name,
            d.is_weekend
        from fct_flights f
        join dim_airport a      on f.airport_iata = a.airport_iata
        left join dim_airline l on f.airline_icao = l.airline_icao
        join dim_date d         on f.flight_date  = d.date_day
    """)
    df["delay_minutes"] = pd.to_numeric(df["delay_minutes"])   
    return df                                                    


if __name__ == "__main__":
    df = load_flights()
    print("Rader:", len(df))
    print("Kolumner:", list(df.columns))
    print(df.head())