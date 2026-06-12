from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from db_train_delay.utils.paths import LOCAL_DATA_DIR, PROJECT_ROOT, SAMPLE_DATA_DIR

RELIABILITY_DELAY_WEIGHT = 0.45
RELIABILITY_CANCELLATION_WEIGHT = 0.40
RELIABILITY_PLATFORM_WEIGHT = 0.15


def load_raw_events(path: Path | None = None) -> pd.DataFrame:
    raw_path = path or SAMPLE_DATA_DIR / "raw_transport_rest_departures.json"
    with raw_path.open("r", encoding="utf-8") as file:
        return pd.DataFrame(json.load(file))


def build_silver_events(raw_events: pd.DataFrame) -> pd.DataFrame:
    events = raw_events.copy()
    events["planned_departure"] = pd.to_datetime(events["planned_departure"], utc=True)
    events["actual_departure"] = pd.to_datetime(events["actual_departure"], utc=True)
    events["ingested_at"] = pd.to_datetime(events["ingested_at"], utc=True)
    events["delay_minutes"] = (
        (events["actual_departure"] - events["planned_departure"]).dt.total_seconds() / 60
    ).fillna(0)
    events.loc[events["cancelled"], "delay_minutes"] = pd.NA
    events["is_delayed"] = events["delay_minutes"].fillna(0) >= 5
    events["platform_changed"] = (
        events["planned_platform"].fillna("") != events["actual_platform"].fillna("")
    ) & ~events["cancelled"]
    events["service_date"] = events["planned_departure"].dt.date.astype(str)
    events["weekday"] = events["planned_departure"].dt.day_name()
    events["is_weekend"] = events["planned_departure"].dt.dayofweek >= 5
    events["day_part"] = events["planned_departure"].dt.hour.map(classify_day_part)
    events["event_id"] = (
        events["route_id"].astype(str)
        + "|"
        + events["station_id"].astype(str)
        + "|"
        + events["train_name"].astype(str)
        + "|"
        + events["planned_departure"].astype(str)
    )
    return events


def classify_day_part(hour: int) -> str:
    if 5 <= hour < 10:
        return "morning"
    if 10 <= hour < 16:
        return "midday"
    if 16 <= hour < 20:
        return "evening"
    return "night"


def load_routes() -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / "dbt" / "db_train_delay" / "seeds" / "routes.csv")


def compute_reliability_score(
    delay_frequency_pct: float, cancellation_rate_pct: float, platform_change_rate_pct: float
) -> float:
    return round(
        100
        - delay_frequency_pct * RELIABILITY_DELAY_WEIGHT
        - cancellation_rate_pct * RELIABILITY_CANCELLATION_WEIGHT
        - platform_change_rate_pct * RELIABILITY_PLATFORM_WEIGHT,
        2,
    )


def build_gold_route_reliability(silver_events: pd.DataFrame) -> pd.DataFrame:
    routes = load_routes()
    events = silver_events.merge(routes, on="route_id", how="left")
    grouped = events.groupby(
        [
            "route_id",
            "origin_name",
            "destination_name_y",
            "route_type",
            "train_category_focus",
            "distance_km",
        ],
        dropna=False,
    )
    reliability = grouped.agg(
        event_count=("train_name", "count"),
        avg_delay_minutes=("delay_minutes", "mean"),
        median_delay_minutes=("delay_minutes", "median"),
        delayed_events=("is_delayed", "sum"),
        cancellations=("cancelled", "sum"),
        platform_changes=("platform_changed", "sum"),
    ).reset_index()
    reliability = reliability.rename(columns={"destination_name_y": "destination_name"})
    reliability["delay_frequency_pct"] = (
        reliability["delayed_events"] / reliability["event_count"] * 100
    ).round(2)
    reliability["cancellation_rate_pct"] = (
        reliability["cancellations"] / reliability["event_count"] * 100
    ).round(2)
    reliability["platform_change_rate_pct"] = (
        reliability["platform_changes"] / reliability["event_count"] * 100
    ).round(2)
    reliability["on_time_rate_pct"] = (
        (
            reliability["event_count"]
            - reliability["delayed_events"]
            - reliability["cancellations"]
        ).clip(lower=0)
        / reliability["event_count"]
        * 100
    ).round(2)
    reliability["delay_per_100_km"] = (
        reliability["avg_delay_minutes"].fillna(0) / reliability["distance_km"] * 100
    ).round(2)
    reliability["reliability_score"] = reliability.apply(
        lambda row: compute_reliability_score(
            row["delay_frequency_pct"],
            row["cancellation_rate_pct"],
            row["platform_change_rate_pct"],
        ),
        axis=1,
    )
    return reliability.sort_values("reliability_score", ascending=False)


def run_local_pipeline() -> dict[str, Path]:
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    bronze_dir = LOCAL_DATA_DIR / "bronze"
    silver_dir = LOCAL_DATA_DIR / "silver"
    gold_dir = LOCAL_DATA_DIR / "gold"
    for directory in [bronze_dir, silver_dir, gold_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    raw = load_raw_events()
    silver = build_silver_events(raw)
    gold = build_gold_route_reliability(silver)

    bronze_path = bronze_dir / "train_events.parquet"
    silver_path = silver_dir / "train_events.parquet"
    gold_path = gold_dir / "route_reliability.parquet"
    gold_csv_path = gold_dir / "route_reliability.csv"

    raw.to_parquet(bronze_path, index=False)
    silver.to_parquet(silver_path, index=False)
    gold.to_parquet(gold_path, index=False)
    gold.to_csv(gold_csv_path, index=False)

    return {
        "bronze": bronze_path,
        "silver": silver_path,
        "gold": gold_path,
        "gold_csv": gold_csv_path,
    }
