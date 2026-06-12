from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db_train_delay.ingestion.transport_rest_client import TransportRestClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest departures from transport.rest")
    parser.add_argument("--station", required=True, help="DB EVA station ID, for example 8000244")
    parser.add_argument("--station-name", default="Unknown")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", default="data/raw/transport_rest_departures.json")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    client = TransportRestClient()
    raw_events = client.departures(args.station, limit=args.limit)
    normalized = [
        client.normalize_departure(args.station, args.station_name, event) for event in raw_events
    ]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(normalized)} events to {output_path}")
