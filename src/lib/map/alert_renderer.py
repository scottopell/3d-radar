from __future__ import annotations

import math
from typing import List

from panda3d.core import LineSegs, NodePath, PandaNode, Vec3, Vec4

from lib.app.state import AppState
from lib.model.alert import Alert
from lib.model.alert_type import AlertType
from lib.model.geo_point import GeoPoint
from lib.ui.core.colors import UIColors
from lib.util.events.listener import Listener


class AlertRenderer(Listener):
    def __init__(
        self,
        root: NodePath[PandaNode],
        state: AppState,
        alertType: AlertType,
    ) -> None:
        super().__init__()

        self.root = root
        self.state = state
        self.alertType = alertType

        self.alerts: List[NodePath[PandaNode]] = []

        self.renderAlerts()
        self.listen(state.alerts, lambda _: self.renderAlerts())

    def renderAlerts(self) -> None:
        for a in self.alerts:
            a.removeNode()

        payload = self.state.alerts.value
        alerts = payload.alerts[self.alertType]

        for alert in alerts:
            print(self.hashBoundary(alert.boundary))

            self.alerts.append(self.drawAlert(alert))

    def hashBoundary(self, boundary: List[List[GeoPoint]]) -> int:
        loopHashes = []

        for loop in boundary:
            loopHashes.append(hash(tuple(loop)))

        return hash(tuple(loopHashes))

    def drawAlert(self, alert: Alert) -> NodePath[PandaNode]:
        lineSegs = LineSegs()
        lineSegs.setColor(self.getColor())
        lineSegs.setThickness(2)

        for loop in alert.boundary:
            self.drawLoop(loop, lineSegs)

        np = NodePath(lineSegs.create())
        np.reparentTo(self.root)
        return np

    def drawLoop(self, loop: List[GeoPoint], lineSegs: LineSegs) -> None:
        if len(loop) < 4:
            return

        lineSegs.moveTo(self.toGlobe(loop[0]))
        for point in loop:
            lineSegs.drawTo(self.toGlobe(point))

    def toGlobe(self, point: GeoPoint) -> Vec3:
        az = math.radians(point.lon)
        el = math.radians(point.lat)

        x = math.cos(az) * math.cos(el)
        y = math.sin(az) * math.cos(el)
        z = math.sin(el)

        return Vec3(x, y, z)

    def getColor(self) -> Vec4:
        if self.alertType == AlertType.TORNADO_WARNING:
            return UIColors.RED
        if self.alertType == AlertType.SEVERE_THUNDERSTORM_WARNING:
            return UIColors.ORANGE

        return UIColors.WHITE

    def destroy(self) -> None:
        super().destroy()

        for alert in self.alerts:
            alert.removeNode()
