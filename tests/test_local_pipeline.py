import pandas as pd
from db_train_delay.pipelines.local_pipeline import (
    build_gold_route_reliability,
    build_silver_events,
)


def test_silver_events_calculates_delay_and_flags_platform_change():
    raw = pd.DataFrame(
        [
            {
                "route_id": "mannheim_heidelberg",
                "station_id": "8000244",
                "station_name": "Mannheim Hbf",
                "destination_name": "Heidelberg Hbf",
                "train_name": "RE 73",
                "train_category": "RE",
                "planned_departure": "2026-06-01T07:05:00+02:00",
                "actual_departure": "2026-06-01T07:12:00+02:00",
                "planned_platform": "9",
                "actual_platform": "10",
                "cancelled": False,
            }
        ]
    )

    silver = build_silver_events(raw)

    assert silver.loc[0, "delay_minutes"] == 7
    assert bool(silver.loc[0, "is_delayed"]) is True
    assert bool(silver.loc[0, "platform_changed"]) is True


def test_gold_route_reliability_contains_expected_metrics():
    raw = pd.DataFrame(
        [
            {
                "route_id": "mannheim_heidelberg",
                "station_id": "8000244",
                "station_name": "Mannheim Hbf",
                "destination_name": "Heidelberg Hbf",
                "train_name": "RE 73",
                "train_category": "RE",
                "planned_departure": "2026-06-01T07:05:00+02:00",
                "actual_departure": "2026-06-01T07:10:00+02:00",
                "planned_platform": "9",
                "actual_platform": "9",
                "cancelled": False,
            }
        ]
    )

    gold = build_gold_route_reliability(build_silver_events(raw))

    assert gold.loc[0, "route_id"] == "mannheim_heidelberg"
    assert gold.loc[0, "delay_frequency_pct"] == 100
    assert "reliability_score" in gold.columns

