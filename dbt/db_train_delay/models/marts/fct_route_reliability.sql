select
    r.route_id,
    r.origin_name,
    r.destination_name,
    r.route_type,
    r.train_category_focus,
    r.distance_km,
    sum(m.event_count) as event_count,
    avg(m.avg_delay_minutes) as avg_delay_minutes,
    avg(m.median_delay_minutes) as median_delay_minutes,
    sum(m.delayed_events) as delayed_events,
    sum(m.cancellations) as cancellations,
    sum(m.platform_changes) as platform_changes,
    round(sum(m.delayed_events) * 100.0 / nullif(sum(m.event_count), 0), 2) as delay_frequency_pct,
    round(sum(m.cancellations) * 100.0 / nullif(sum(m.event_count), 0), 2) as cancellation_rate_pct,
    round(sum(m.platform_changes) * 100.0 / nullif(sum(m.event_count), 0), 2) as platform_change_rate_pct,
    round(
        greatest(0, sum(m.event_count) - sum(m.delayed_events) - sum(m.cancellations))
        * 100.0 / nullif(sum(m.event_count), 0),
        2
    ) as on_time_rate_pct,
    round(avg(m.avg_delay_minutes) / nullif(r.distance_km, 0) * 100, 2) as delay_per_100_km,
    round(
        100
        - (sum(m.delayed_events) * 100.0 / nullif(sum(m.event_count), 0)) * 0.45
        - (sum(m.cancellations) * 100.0 / nullif(sum(m.event_count), 0)) * 0.40
        - (sum(m.platform_changes) * 100.0 / nullif(sum(m.event_count), 0)) * 0.15,
        2
    ) as reliability_score
from {{ ref('int_route_event_metrics') }} m
left join {{ ref('dim_routes') }} r
    on m.route_id = r.route_id
group by 1, 2, 3, 4, 5, 6
