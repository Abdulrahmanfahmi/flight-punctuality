with source as (

    select * from {{ source('raw', 'departures') }}

),

renamed as (

    select
        -- identifierare
        flight_key,
        flight_id,
        airport_iata,
        'departure' as flight_type,

        -- flygbolag
        airline_operator__iata as airline_iata,
        airline_operator__icao as airline_icao,
        airline_operator__name as airline_name,

        -- tider i UTC
        convert_timezone('UTC', departure_time__scheduled_utc) as scheduled_at_utc,
        convert_timezone('UTC', departure_time__actual_utc)    as actual_at_utc,

        -- flygdatum i svensk tid
        convert_timezone('Europe/Stockholm', departure_time__scheduled_utc)::date as flight_date,

        -- status
        location_and_status__flight_leg_status         as status_code,
        location_and_status__flight_leg_status_english as status

    from source
    where location_and_status__flight_leg_status != 'DEL'

)

select * from renamed