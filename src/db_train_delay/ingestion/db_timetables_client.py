from __future__ import annotations


class DbTimetablesClient:
    """Placeholder for the official DB Timetables API client.

    Add DB API Marketplace credentials through environment variables and map planned,
    recent, and full changes into the same event contract used by transport.rest.
    """

    base_url = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret

    def planned_timetable(self, eva_station_id: str, date: str, hour: str) -> list[dict]:
        raise NotImplementedError("Implement after DB API Marketplace access is available.")

