with source_data as (
    select *
    from {{ source('raw', 'covid_data') }}
),

cleaned as (
    select
        cast(sno as number) as source_row_id,
        try_to_date(observation_date, 'MM/DD/YYYY') as observation_date,
        coalesce(nullif(trim(province), ''), 'Unknown') as province,
        case
            when trim(country) = 'Mainland China' then 'China'
            else trim(country)
        end as country,
        coalesce(
            try_to_timestamp_ntz(last_update, 'MM/DD/YYYY HH24:MI'),
            try_to_timestamp_ntz(last_update, 'MM/DD/YYYY HH24:MI:SS'),
            try_to_timestamp_ntz(last_update, 'M/D/YYYY HH24:MI'),
            try_to_timestamp_ntz(last_update, 'M/D/YYYY HH24:MI:SS'),
            try_to_timestamp_ntz(last_update)
        ) as last_update_ts,
        greatest(coalesce(cast(confirmed as number), 0), 0) as confirmed,
        greatest(coalesce(cast(deaths as number), 0), 0) as deaths,
        greatest(coalesce(cast(recovered as number), 0), 0) as recovered,
        greatest(
            coalesce(cast(confirmed as number), 0)
            - coalesce(cast(deaths as number), 0)
            - coalesce(cast(recovered as number), 0),
            0
        ) as active_cases
    from source_data
)

select *
from cleaned
where observation_date is not null
  and country is not null
