from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from . import benches
from .config import config
from .utils import PerformanceReport


class PerformanceReportSuite(BaseModel):
    cpu_info: str
    hw: dict
    reports: dict[str, PerformanceReport]


def generate_reports(reports_dir: Path) -> PerformanceReportSuite:
    assert reports_dir.is_dir()

    reports = [
        benches.aggregation.generate_report(reports_dir),
        benches.aggregation.generate_report_growing(reports_dir),
        benches.book.generate_report(reports_dir),
        benches.batch_lookup.generate_report(reports_dir),
        benches.delete.generate_report(reports_dir),
        benches.insert.generate_report(reports_dir),
        benches.insert.generate_report_growing(reports_dir),
        benches.iteration.generate_report(reports_dir),
        benches.lookup_contention.generate_report(reports_dir),
        benches.lookup_fail.generate_report(reports_dir),
        benches.lookup_succ.generate_report(reports_dir),
        benches.mix.generate_report(reports_dir),
        benches.mix.generate_report_growing(reports_dir),
        benches.update_contention.generate_report(reports_dir),
    ]

    return PerformanceReportSuite(
        cpu_info=Path("/proc/cpuinfo").read_text(),
        hw=json.loads((reports_dir / config["hw_perf_json"]).read_text()),
        reports={
            report.name: report
            for report in reports
        }
    )


def write_reports(suite: PerformanceReportSuite, reports_dir: Path) -> Path:
    performance_reports_dir = reports_dir / "_performance_reports"
    performance_reports_dir.mkdir(exist_ok=True)
    report_path = performance_reports_dir / "performance_report.json"

    with open(report_path, "w") as f:
        f.write(suite.json(indent=2, ensure_ascii=False))
    assert report_path.is_file()

    for report in suite.reports.values():
        report.make_plot(performance_reports_dir)

    return report_path
