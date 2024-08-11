import datetime
from typing import List

import pynexrad

from lib.model.record import Record
from lib.model.scan import Scan
from lib.model.scan_data import ScanData
from lib.model.sweep_meta import SweepMeta


def sweepMetaFromSweep(sweep: pynexrad.Sweep, offset: int) -> SweepMeta:
    return SweepMeta(
        sweep.elevation,
        sweep.az_first,
        sweep.az_step,
        sweep.az_count,
        sweep.range_first,
        sweep.range_step,
        sweep.range_count,
        offset,
    )


def scanDataFromScan(scan: pynexrad.Scan) -> ScanData:
    total_sweeps_meta_size = sum([len(m.data) for m in scan.sweeps])
    data = bytearray(total_sweeps_meta_size)

    sweeps = []
    offset = 0
    for meta in scan.sweeps:
        sweeps.append(sweepMetaFromSweep(meta, offset))
        data[offset:] = meta.data
        offset += len(meta.data)

    return ScanData(sweeps, data)


def scanFromLevel2File(record: Record, file: pynexrad.Level2File) -> Scan:
    return Scan(
        record,
        scanDataFromScan(file.reflectivity),
        scanDataFromScan(file.velocity),
    )


class RadarProvider:
    def load(self, record: Record) -> Scan:
        key = record.awsKey()

        print("Fetching from s3:", key)

        level2File = pynexrad.download_nexrad_file(
            record.station,
            record.time.year,
            record.time.month,
            record.time.day,
            key,
        )

        print("Post-processing", key)
        return scanFromLevel2File(record, level2File)

    def search(self, record: Record, count: int) -> List[Record]:
        searchTime = record.time.astimezone(datetime.timezone.utc)

        records = self.getScans(
            record.station,
            searchTime.year,
            searchTime.month,
            searchTime.day,
        )

        if len(records) < count:
            previousDay = searchTime - datetime.timedelta(days=1)

            records.extend(
                self.getScans(
                    record.station,
                    previousDay.year,
                    previousDay.month,
                    previousDay.day,
                )
            )

        records = list(filter(lambda r: r.time <= searchTime, records))
        records.sort(key=lambda r: r.time)

        if len(records) <= count:
            return records

        return records[-count:]

    def getScans(self, radar: str, year: int, month: int, day: int) -> List[Record]:
        resp = pynexrad.list_records(radar, year, month, day)

        records = []

        for key in resp:
            record = Record.parse(key)
            if record:
                records.append(record)

        return records
