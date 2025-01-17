from typing import List

from .alert_type import AlertType
from .geo_point import GeoPoint


class Alert:
    def __init__(
        self,
        alertType: AlertType,
        event: str,
        area: str,
        boundary: List[List[GeoPoint]],
        headline: str,
        description: str,
    ):
        self.alertType = alertType
        self.event = event
        self.area = area
        self.boundary = boundary
        self.headline = headline
        self.description = description

    def center(self) -> GeoPoint:
        minLat = 1000.0
        maxLat = -1000.0
        minLon = 1000.0
        maxLon = -1000.0

        for ring in self.boundary:
            for point in ring:
                minLat = min(minLat, point.lat)
                maxLat = max(maxLat, point.lat)
                minLon = min(minLon, point.lon)
                maxLon = max(maxLon, point.lon)

        return GeoPoint((minLat + maxLat) / 2, (minLon + maxLon) / 2)
