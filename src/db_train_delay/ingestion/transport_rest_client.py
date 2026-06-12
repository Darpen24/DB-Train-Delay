from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass(frozen=True)
class TransportRestClient:
    base_url: str = "https://v6.db.transport.rest"
    request_delay_seconds: float = 0.7
    timeout_seconds: int = 30
    max_retries: int = 3

    def _session(self) -> requests.Session:
        retry = Retry(
            total=self.max_retries,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def departures(self, station_id: str, limit: int = 20) -> list[dict[str, Any]]:
        url = f"{self.base_url}/stops/{station_id}/departures"
        params = {"duration": 60, "results": limit, "remarks": "true"}
        response = self._session().get(url, params=params, timeout=self.timeout_seconds)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise requests.HTTPError(
                f"transport.rest request failed for station {station_id} with status "
                f"{response.status_code}: {response.text[:200]}"
            ) from exc
        time.sleep(self.request_delay_seconds)
        payload = response.json()
        return payload.get("departures", payload if isinstance(payload, list) else [])

    def normalize_departure(
        self, station_id: str, station_name: str, event: dict[str, Any]
    ) -> dict[str, Any]:
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
