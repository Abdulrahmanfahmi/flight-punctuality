with flights as (

    select airline_icao, airline_iata, airline_name from {{ ref('stg_arrivals') }}
    union all
    select airline_icao, airline_iata, airline_name from {{ ref('stg_departures') }}

),

swedavia_airlines as (

    select
        airline_icao,
        airline_iata,
        airline_name,
        count(*) as number_of_flights
    from flights
    where airline_icao is not null
    group by airline_icao, airline_iata, airline_name
    qualify row_number() over (
        partition by airline_icao
        order by number_of_flights desc
    ) = 1

),

wikipedia as (

    select * from {{ ref('stg_airlines') }}

)

select
    s.airline_icao,
    s.airline_iata,
    s.airline_name,
    w.country,
    w.callsign,
    w.airline_icao is not null as has_wikipedia_match

from swedavia_airlines s
left join wikipedia w
    on s.airline_icao = w.airline_icao