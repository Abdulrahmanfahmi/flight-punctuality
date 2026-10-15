with swedavia_airports as (

    select airport_iata from {{ ref('stg_arrivals') }}
    union
    select airport_iata from {{ ref('stg_departures') }}

),

wikipedia as (

    select * from {{ ref('stg_airports') }}

)

select
    s.airport_iata,
    w.airport_icao,
    w.airport_name,
    w.city,
    w.usage,
    w.passengers_2023

from swedavia_airports s
left join wikipedia w
    on s.airport_iata = w.airport_iata