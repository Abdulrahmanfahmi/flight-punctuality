with flight_dates as (

    select flight_date from {{ ref('stg_arrivals') }}
    union all
    select flight_date from {{ ref('stg_departures') }}

),

bounds as (

    select
        min(flight_date) as start_date,
        max(flight_date) as end_date
    from flight_dates

),

spine as (

    select
        dateadd(day, row_number() over (order by seq4()) - 1, bounds.start_date) as date_day
    from table(generator(rowcount => 3650))
    cross join bounds

)

select
    date_day,
    year(date_day)                         as year,
    month(date_day)                        as month,
    monthname(date_day)                    as month_name,
    day(date_day)                          as day_of_month,
    weekiso(date_day)                      as week_of_year,
    dayofweekiso(date_day)                 as day_of_week,
    dayname(date_day)                      as day_name,
    dayofweekiso(date_day) in (6, 7)       as is_weekend

from spine
cross join bounds
where spine.date_day <= bounds.end_date