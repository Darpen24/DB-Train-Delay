from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests


@dataclass(frozen=True)
class TransportRestClient:
    base_url: str = "https://v6.db.transport.rest"
    request_delay_seconds: float = 0.7
    timeout_seconds: int = 30

    def departures(self, station_id: str, limit: int = 20) -> list[dict[str, Any]]:
        url = f"{self.base_url}/stops/{station_id}/departures"
        params = {"duration": 60, "results": limit, "remarks": "true"}
        response = requests.get(url, params=params, timeout=self.timeout_seconds)
        response.raise_for_status()
        time.sleep(self.request_delay_seconds)
        payload = response.json()
        return payload.get("departures", payload if isinstance(payload, list) else [])

    def normalize_departure(self, station_id: str, station_name: str, event: dict[str, Any]) -> dict[str, Any]:
        line = event.get("line") or {}
        planned = event.get("plannedWhen")
        actual = event.get("when")
        return {
            "route_id": None,
            "station_id": station_id,
            "station_name": station_name,
            "destination_name": (event.get("destination") or {}).get("name"),
            "train_name": line.get("name"),
            "train_category": line.get("productName") or line.get("mode"),
            "planned_departure": planned,
            "actual_departure": actual,
            "planned_platform": event.get("plannedPlatform"),
            "actual_platform": event.get("platform"),
            "cancelled": bool(event.get("cancelled", False)),
            "ingested_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "source": "transport.rest",
        }

