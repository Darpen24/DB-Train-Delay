import pandas as pd
from db_train_delay.pipelines.local_pipeline import (
    build_gold_route_reliability,
    build_silver_events,
    compute_reliability_score,
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
                "ingested_at": "2026-06-01T07:13:00+02:00",
                "source": "transport.rest",
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
                "ingested_at": "2026-06-01T07:11:00+02:00",
                "source": "transport.rest",
            }
        ]
    )

    gold = build_gold_route_reliability(build_silver_events(raw))

    assert gold.loc[0, "route_id"] == "mannheim_heidelberg"
    assert gold.loc[0, "delay_frequency_pct"] == 100
    assert "reliability_score" in gold.columns


def test_reliability_score_formula_is_weighted_correctly():
    score = compute_reliability_score(50, 25, 10)

    assert score == 66.0


def test_gold_route_reliability_contains_on_time_rate():
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
                "ingested_at": "2026-06-01T07:11:00+02:00",
                "source": "transport.rest",
            },
            {
                "route_id": "mannheim_heidelberg",
                "station_id": "8000244",
                "station_name": "Mannheim Hbf",
                "destination_name": "Heidelberg Hbf",
                "train_name": "RE 75",
                "train_category": "RE",
                "planned_departure": "2026-06-01T08:05:00+02:00",
                "actual_departure": "2026-06-01T08:05:00+02:00",
                "planned_platform": "9",
                "actual_platform": "9",
                "cancelled": False,
                "ingested_at": "2026-06-01T08:06:00+02:00",
                "source": "transport.rest",
            },
        ]
    )

    gold = build_gold_route_reliability(build_silver_events(raw))

    assert gold.loc[0, "on_time_rate_pct"] == 50.0


def test_cancelled_event_keeps_delay_minutes_null():
    raw = pd.DataFrame(
        [
            {
                "route_id": "munich_hamburg",
                "station_id": "8000261",
                "station_name": "Munich Hbf",
                "destination_name": "Hamburg Hbf",
                "train_name": "ICE 588",
                "train_category": "ICE",
                "planned_departure": "2026-06-04T06:18:00+02:00",
                "actual_departure": None,
                "planned_platform": "19",
                "actual_platform": None,
                "cancelled": True,
                "ingested_at": "2026-06-04T06:20:00+02:00",
                "source": "transport.rest",
            }
        ]
    )

    silver = build_silver_events(raw)

    assert pd.isna(silver.loc[0, "delay_minutes"])
