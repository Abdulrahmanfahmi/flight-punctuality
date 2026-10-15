with source as (

    select * from {{ source('raw', 'airports') }}

),

renamed as (

    select
        iata                            as airport_iata,
        icao                            as airport_icao,
        airport_name,
        city_served                     as city,
        usage,
        cast(passengers_2023 as integer) as passengers_2023

    from source
    where iata is not null

)

select * from renamed