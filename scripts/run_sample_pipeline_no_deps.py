from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from statistics import mean, median

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_SAMPLE = PROJECT_ROOT / "data" / "samples" / "raw_transport_rest_departures.json"
ROUTES_CSV = PROJECT_ROOT / "dbt" / "db_train_delay" / "seeds" / "routes.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "local" / "gold" / "route_reliability.csv"


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def main() -> None:
    events = json.loads(RAW_SAMPLE.read_text(encoding="utf-8"))
    routes = {}
    with ROUTES_CSV.open("r", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            row["distance_km"] = float(row["distance_km"])
            routes[row["route_id"]] = row

    enriched = []
    for event in events:
        planned = parse_ts(event["planned_departure"])
        actual = parse_ts(event["actual_departure"])
        delay = (
            None
            if event["cancelled"] or not actual
            else (actual - planned).total_seconds() / 60
        )
        enriched.append(
            {
                **event,
                "delay_minutes": delay,
                "is_delayed": bool(delay is not None and delay >= 5),
                "platform_changed": (
                    event.get("planned_platform") != event.get("actual_platform")
                    and not event["cancelled"]
                ),
            }
        )

    rows = []
    for route_id, route in routes.items():
        route_events = [event for event in enriched if event["route_id"] == route_id]
        if not route_events:
            continue
        delays = [
            event["delay_minutes"]
            for event in route_events
            if event["delay_minutes"] is not None
        ]
        event_count = len(route_events)
        delayed_events = sum(event["is_delayed"] for event in route_events)
        cancellations = sum(event["cancelled"] for event in route_events)
        platform_changes = sum(event["platform_changed"] for event in route_events)
        avg_delay = mean(delays) if delays else 0
        delay_frequency = delayed_events / event_count * 100
        cancellation_rate = cancellations / event_count * 100
        platform_change_rate = platform_changes / event_count * 100
        rows.append(
            {
                "route_id": route_id,
                "origin_name": route["origin_name"],
                "destination_name": route["destination_name"],
                "route_type": route["route_type"],
                "train_category_focus": route["train_category_focus"],
                "distance_km": route["distance_km"],
                "event_count": event_count,
                "avg_delay_minutes": round(avg_delay, 2),
                "median_delay_minutes": round(median(delays), 2) if delays else 0,
                "delayed_events": delayed_events,
                "cancellations": cancellations,
                "platform_changes": platform_changes,
                "delay_frequency_pct": round(delay_frequency, 2),
                "cancellation_rate_pct": round(cancellation_rate, 2),
                "platform_change_rate_pct": round(platform_change_rate, 2),
                "delay_per_100_km": round(avg_delay / route["distance_km"] * 100, 2),
                "reliability_score": round(
                    100
                    - delay_frequency * 0.45
                    - cancellation_rate * 0.40
                    - platform_change_rate * 0.15,
                    2,
                ),
            }
        )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} route reliability rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
