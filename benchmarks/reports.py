from pydantic import BaseModel


class BenchmarkReportPerf(BaseModel):
    perf_out: str
    samples: int
    time_spent_samples: dict[str, int]
    time_spent_perc: dict[str, float]
    time_in_cereggii_samples: dict[str, int]
    time_in_cereggii_perc: dict[str, float]


class BenchmarkReportData(BaseModel):
    wall_clock_time: float
    perf: BenchmarkReportPerf
    debug: dict


class BenchmarkReport(BaseModel):
    name: str
    params: dict
    data: BenchmarkReportData
