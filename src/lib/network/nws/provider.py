import concurrent.futures
import json
from typing import Dict, List, Tuple

from lib.model.alert import Alert
from lib.model.alert_type import AlertType
from lib.model.radar_station import RadarStation

from ..util import makeRequest


class NWSProvider:
    HOST = "https://api.weather.gov"

    def getRadarStations(self) -> Dict[str, RadarStation] | None:
        response = makeRequest(
            self.HOST + "/radar/stations",
            params={"stationType": "WSR-88D"},
            timeout=10,
        )
        if not response:
            return None

        responseJson = response.json()

        stations = {}
        for station in responseJson["features"]:
            stationID = station["properties"]["id"]
            name = station["properties"]["name"]
            long = station["geometry"]["coordinates"][0]
            lat = station["geometry"]["coordinates"][1]
            stations[stationID] = RadarStation(stationID, name, lat, long)

        return stations

    def getAlerts(self) -> Dict[AlertType, List[Alert]] | None:
        alerts = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.getAlertsForType, alertType)
                for alertType in [
                    AlertType.TORNADO_WARNING,
                    AlertType.SEVERE_THUNDERSTORM_WARNING,
                ]
            }
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if not result:
                    return None

                alerts[result[0]] = result[1]

        return alerts

    def getAlertsForType(
        self, alertType: AlertType
    ) -> Tuple[AlertType, List[Alert]] | None:
        # response = makeRequest(
        #     self.HOST + "/alerts/active",
        #     params={
        #         "status": "actual",
        #         "limit": 500,
        #         "code": alertType.code(),
        #     },
        #     timeout=10,
        # )
        # if not response:
        #     return None

        # responseJson = response.json()

        # temporary testing stuff
        filename = "lib/network/nws/"
        if alertType == AlertType.TORNADO_WARNING:
            filename += "tornado_warning.json"
        else:
            filename += "severe_thunderstorm_warning.json"

        with open(filename, "r", encoding="utf-8") as f:
            responseJson = json.loads(f.read())
        # end temp stuff

        features = responseJson["features"]

        alerts = []

        for feature in features:
            alerts.append(Alert(alertType, feature["properties"]["event"]))

        return (alertType, alerts)
