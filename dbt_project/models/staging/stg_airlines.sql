with source as (

    select * from {{ source('raw', 'airlines') }}

),

cleaned as (

    select
        nullif(trim(icao), 'n/a')               as airline_icao,
        nullif(trim(iata), 'n/a')               as airline_iata,
        airline                                 as airline_name,
        nullif(trim(telephony_designator), 'n/a') as callsign,
        country_region                          as country,
        comments,
        coalesce(comments ilike '%defunct%', false) as is_defunct

    from source

),

deduplicated as (

    select *
    from cleaned
    where airline_icao is not null
    qualify row_number() over (
        partition by airline_icao
        order by is_defunct, airline_name
    ) = 1

)

select * from deduplicated