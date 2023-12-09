import json
from typing import Any, Dict, TypeVar

from lib.model.data_type import DataType
from lib.util.events.observable import Observable

T = TypeVar("T")


class AppState:
    def __init__(self) -> None:
        self.observables: Dict[str, Observable[Any]] = {}  # type: ignore

        self.uiScale = self.createField("uiScale", 1.0)

        self.volumeMin = self.createField("volumeMin", 0.04)
        self.volumeMax = self.createField("volumeMax", 1.0)
        self.volumeFalloff = self.createField("volumeFalloff", 0.7)

        self.station = self.createField("station", "KDMX")
        self.year = self.createField("year", 2023)
        self.month = self.createField("month", 11)
        self.day = self.createField("day", 27)
        self.time = self.createField("time", "11:24")

        self.hideKeybinding = self.createField("hideKeybinding", "h")
        self.playKeybinding = self.createField("playKeybinding", "space")

        self.dataType = self.createField("dataType", DataType.REFLECTIVITY)

    def toJson(self) -> str:
        raw: Dict[str, Any] = {}  # type:ignore

        for item in self.observables.items():
            raw[item[0]] = item[1].value

        return json.dumps(
            raw,
            sort_keys=True,
            indent=4,
        )

    def fromJson(self, jsonStr: str) -> None:
        raw = json.loads(jsonStr)

        for item in self.observables.items():
            if item[0] in raw:
                item[1].setValue(raw[item[0]])

    def createField(self, name: str, initialValue: T) -> Observable[T]:
        observable = Observable[T](initialValue)
        self.observables[name] = observable
        return observable

    def destroy(self) -> None:
        for observable in self.observables.values():
            observable.close()
