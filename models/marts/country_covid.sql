{{ config(materialized='table') }}

with country_daily as (
    select
        observation_date,
        country,
        sum(confirmed_cases) as confirmed_cases,
        sum(death_cases) as death_cases,
        sum(recovered_cases) as recovered_cases,
        sum(active_cases) as active_cases
    from {{ ref('fact_covid') }}
    group by 1, 2
),

latest_date as (
    select max(observation_date) as max_observation_date
    from country_daily
)

select
    c.country,
    l.max_observation_date as latest_observation_date,
    max(case when c.observation_date = l.max_observation_date then c.confirmed_cases end) as latest_confirmed_cases,
    max(case when c.observation_date = l.max_observation_date then c.death_cases end) as latest_death_cases,
    max(case when c.observation_date = l.max_observation_date then c.recovered_cases end) as latest_recovered_cases,
    max(case when c.observation_date = l.max_observation_date then c.active_cases end) as latest_active_cases,
    max(c.confirmed_cases) as peak_confirmed_cases,
    max(c.death_cases) as peak_death_cases,
    avg(c.confirmed_cases) as avg_confirmed_cases,
    avg(c.death_cases) as avg_death_cases
from country_daily c
cross join latest_date l
group by 1, 2
