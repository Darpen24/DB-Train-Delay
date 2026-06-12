select
    route_id,
    train_category,
    service_date,
    weekday,
    is_weekend,
    day_part,
    count(*) as event_count,
    avg(delay_minutes) as avg_delay_minutes,
    approx_percentile(delay_minutes, 0.5) as median_delay_minutes,
    sum(case when is_delayed then 1 else 0 end) as delayed_events,
    sum(case when cancelled then 1 else 0 end) as cancellations,
    sum(case when platform_changed then 1 else 0 end) as platform_changes
from {{ ref('stg_train_events') }}
group by 1, 2, 3, 4, 5, 6

