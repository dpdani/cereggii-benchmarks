from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from . import benches
from .utils import PerformanceReport


def generate_reports(reports_dir: Path) -> dict[str, PerformanceReport]:
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
    return {
        report.name: report
        for report in reports
    }


class PerformanceReportFile(BaseModel):
    __root__: dict[str, PerformanceReport]


def write_reports(reports: dict[str, PerformanceReport], reports_dir: Path) -> Path:
    performance_reports_dir = reports_dir / "_performance_reports"
    performance_reports_dir.mkdir(exist_ok=True)
    report_path = performance_reports_dir / "performance_report.json"
    performance_report_file = PerformanceReportFile(__root__=reports)
    with open(report_path, "w") as f:
        f.write(performance_report_file.json(indent=2, ensure_ascii=False))
    assert report_path.is_file()

    for report in reports.values():
        report.make_plot(performance_reports_dir)

    return report_path
