select
    route_id,
    origin_name,
    destination_name,
    route_type,
    train_category_focus,
    distance_km
from {{ ref('routes') }}

