with arrivals as (

    select * from {{ ref('stg_arrivals') }}

),

departures as (

    select * from {{ ref('stg_departures') }}

),

flights as (

    select * from arrivals
    union all
    select * from departures

),

with_delay as (

    select
        *,
        actual_at_utc is not null as is_completed,
        case
            when actual_at_utc is not null
            then round(datediff(second, scheduled_at_utc, actual_at_utc) / 60, 1)
        end as delay_minutes
    from flights

)

select
    -- nycklar
    flight_key,
    airport_iata,
    airline_icao,
    flight_date,

    -- beskrivning
    flight_id,
    flight_type,
    status_code,

    -- tider
    scheduled_at_utc,
    actual_at_utc,

    -- mått
    delay_minutes,
    is_completed,
    case when is_completed then delay_minutes > 15 end as is_delayed,
    status_code = 'CAN' as is_cancelled

from with_delay