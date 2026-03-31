{{ config(materialized='table') }}

with daily_location as (
    select
        observation_date,
        country,
        province,
        max(last_update_ts) as last_update_ts,
        sum(confirmed) as confirmed_cases,
        sum(deaths) as death_cases,
        sum(recovered) as recovered_cases,
        sum(active_cases) as active_cases
    from {{ ref('stg_covid_data') }}
    group by 1, 2, 3
)

select
    observation_date,
    country,
    province,
    last_update_ts,
    confirmed_cases,
    death_cases,
    recovered_cases,
    active_cases,
    confirmed_cases - lag(confirmed_cases) over (
        partition by country, province
        order by observation_date
    ) as confirmed_cases_daily_change,
    death_cases - lag(death_cases) over (
        partition by country, province
        order by observation_date
    ) as death_cases_daily_change,
    recovered_cases - lag(recovered_cases) over (
        partition by country, province
        order by observation_date
    ) as recovered_cases_daily_change
from daily_location
