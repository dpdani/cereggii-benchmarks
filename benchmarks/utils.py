from __future__ import annotations

import collections
import datetime
import json
import multiprocessing
import re
import signal
import subprocess
import threading
import time
from itertools import islice
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Callable, TypedDict

import click
import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from pydantic import BaseModel, parse_file_as

from ._perf_categories import perf_categories

from .reports import BenchmarkReport, BenchmarkReportData, BenchmarkReportPerf


now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

parent = Path(__file__).parent.parent

reports_dir = parent / 'reports' / now
data_dir = parent / 'data'


# BenchmarkReport = dict
# BenchmarkReportData = dict
# BenchmarkReportPerf = dict


def write_report(path, report: BenchmarkReport):
    full_path = reports_dir / path
    if full_path.exists():
        with open(full_path, 'r') as f:
            existing_runs = json.load(f)
    else:
        existing_runs = []
    runs = [*existing_runs, report.dict()]
    # runs = [*existing_runs, report]
    with open(full_path, 'w') as f:
        json.dump(runs, f, indent=2, ensure_ascii=False)


def batched(lst, n):
    partitions = [
        [] for _ in range(n)
    ]
    for i, e in enumerate(lst):
        partitions[i % n].append(e)
    return partitions


def batched_fixed(iterable, n):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        yield batch


def threads():
    for i in range(100):
        if (1 << i) > multiprocessing.cpu_count():
            return
        yield 1 << i


class BenchmarkPlan(TypedDict):
    name: str
    threads: list[threading.Thread]
    barrier_1: threading.Barrier
    barrier_2: threading.Barrier
    params: dict[str, str]
    debug: Callable[[], dict[str, Any]]
    wall_clock_time: float | None


def execute_benchmark_plan(plan: BenchmarkPlan) -> None:
    if len(plan['threads']) > 0:
        for t in plan['threads']:
            t.start()

        plan['barrier_1'].wait()

        tids = ','.join(map(lambda t: str(t.native_id), plan['threads']))

        perf_i = 0
        perf_out = reports_dir / f'{perf_i}.perf'
        while perf_out.exists():
            perf_i += 1
            perf_out = reports_dir / f'{perf_i}.perf'

        record = f"perf record -q -o '{perf_out}' --freq=9999 --tid={tids} sleep 999999 >/dev/null 2>&1"
        print(f"    - {record}")

        record = subprocess.Popen(record, shell=True)
        time.sleep(1)

        plan['barrier_2'].wait()

        started = time.time()
        for t in plan['threads']:
            t.join()
        wall_clock_time = time.time() - started

        record.send_signal(signal.SIGINT)
        record.wait()
        time.sleep(.1)

        perf_out_json = reports_dir / f"{perf_out}.json"
        convert = f"perf data convert -i '{perf_out}' --to-json '{perf_out_json}' >/dev/null 2>&1"
        print(f"    - {convert}")
        try:
            subprocess.check_call(convert, shell=True)
        except CalledProcessError:
            click.secho("Error while converting perf data to json: "
                        "perf record probably failed.", fg='yellow')
            return

        samples, time_usage, time_in_cereggii = aggregate_time_usage(perf_out_json)
        perf_out_json.unlink()
    else:
        wall_clock_time = plan["wall_clock_time"]
        perf_out = ""
        samples = []
        time_usage = {}
        time_in_cereggii = {}

    write_report(
        'report.json',
        BenchmarkReport(
            name=plan['name'],
            params=plan['params'],
            data=BenchmarkReportData(
                wall_clock_time=wall_clock_time,
                perf=BenchmarkReportPerf(
                    perf_out=str(perf_out),
                    samples=len(samples),
                    time_spent_samples=dict(sort_dict_desc_values(time_usage)),
                    time_spent_perc={
                        category: s / len(samples)
                        for category, s in sort_dict_desc_values(time_usage)
                    },
                    time_in_cereggii_samples=dict(sort_dict_desc_values(time_in_cereggii)),
                    time_in_cereggii_perc={
                        symbol: s / sum(time_in_cereggii.values())
                        for symbol, s in sort_dict_desc_values(time_in_cereggii)
                    },
                ),
                debug=plan['debug'](),
            ),
        ),
    )


def sort_dict_desc_values(time_usage):
    return sorted(time_usage.items(), key=lambda _: (_[1], _[0]), reverse=True)


def aggregate_time_usage(perf_out_json):
    time_usage = collections.Counter()
    time_in_cereggii = collections.Counter()
    time_in_python = collections.Counter()

    with open(perf_out_json) as f:
        samples = json.load(f)["samples"]

        for sample in samples:
            callchain = list(filter(lambda _: "symbol" in _, sample["callchain"]))
            if not callchain:
                time_usage["other"] += 1
                continue

            category_found = False

            for category in perf_categories:
                if not category_found and any(map(lambda _: _["symbol"] in perf_categories[category], callchain)):
                    time_usage[category] += 1
                    category_found = True

            if not category_found:
                if any(map(lambda _: _["dso"] == "_cereggii.so", callchain)):
                    time_usage["cereggii"] += 1
                elif any(map(lambda _: "kernel" in _["dso"], callchain)):
                    time_usage["kernel"] += 1
                elif any(map(lambda _: _["dso"] == "_random.nogil-39b-x86_64-linux-gnu.so", callchain)):
                    time_usage["py_rng"] += 1
                elif any(map(lambda _: _["dso"].startswith("libpython") or _["dso"].startswith("python"), callchain)):
                    time_usage["py_other"] += 1
                else:
                    time_usage["other"] += 1

            # if any(map(lambda _: _["symbol"] in _perf_categories.cereggii_ref_counting, callchain)):
            #     time_usage["cereggii_ref_counting"] += 1
            # elif any(map(lambda _: _["dso"] == "_cereggii.so", callchain)):
            #     time_usage["cereggii"] += 1
            # elif any(map(lambda _: _["symbol"] in _perf_categories.ref_counting, callchain)):
            #     time_usage["ref_counting"] += 1
            # elif any(map(lambda _: _["symbol"] in _perf_categories.interpreter, callchain)):
            #     time_usage["interpreter"] += 1
            # elif any(map(lambda _: _["symbol"] in _perf_categories.py_mutex, callchain)):
            #     time_usage["pymutex"] += 1
            # elif any(map(lambda _: _["symbol"] in _perf_categories.py_dict, callchain)):
            #     time_usage["dict"] += 1
            # elif any(map(lambda _: "kernel" in _["dso"] and _["symbol"] in _perf_categories.scheduler, callchain)):
            #     time_usage["kernel_scheduler"] += 1
            # elif any(map(lambda _: "kernel" in _["dso"], callchain)):
            #     time_usage["kernel"] += 1
            # elif any(map(lambda _: _["dso"].startswith("libpython"), callchain)):
            #     time_usage["other_python"] += 1
            # else:
            #     time_usage["other"] += 1

            if any(map(lambda _: _["dso"].startswith("libpython") or _["dso"].startswith("python"), callchain)):
                time_in_python[callchain[-1]["symbol"]] += 1

            if any(map(lambda _: _["dso"] == "_cereggii.so", callchain)):
                time_in_cereggii[callchain[-1]["symbol"]] += 1

    # pprint.pprint(time_in_python)
    return samples, time_usage, time_in_cereggii


def zipf_distribution(n, s, size=None):
    ranks = np.arange(1, n + 1)
    normalization_constant = np.sum(1 / ranks ** s)
    probabilities = (1 / ranks ** s) / normalization_constant

    return np.random.default_rng(seed=256).choice(ranks, size=size, p=probabilities)


class Axis(TypedDict):
    title: str
    unit: str
    scale: str


Dimension = list[Axis]


class Axes:
    threads = {"title": "threads", "unit": "count", "scale": ""}
    throughput = {"title": "throughput", "unit": "MOps/s", "scale": ""}
    absolute_speedup = {"title": "absolute speedup", "unit": "factor", "scale": ""}
    skew = {"title": "skew", "unit": "factor", "scale": ""}
    write_perc = {"title": "write_perc", "unit": "factor", "scale": ""}
    batch_size = {"title": "batch_size", "unit": "count", "scale": "log"}


matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'font.size': 11,
    'text.usetex': True,
    'pgf.rcfonts': False,
})


class PerformanceReport(BaseModel):
    name: str

    dims: list[Dimension]
    data: dict[str, dict[str, list[float]]]

    benchmark_reports: dict[str, list[BenchmarkReport]]

    @staticmethod
    def factory_style(factory):
        styles = {
            "dict": "ko-",
            "dict_ideal": "ko--",
            "dict_lock": "ko--",
            "AtomicDict": "kx-",
            "Growt": "ks-",
        }
        return styles[factory]

    def make_plot(self, out_dir: Path, legend_position: str = "upper right") -> None:
        assert len(self.dims) == 2  # only do 2D plots
        assert 1 <= len(self.dims[1]) <= 2

        plt.margins(0)
        fig, ax1 = plt.subplots()

        x_axis = self.dims[0][0]["title"]
        y_axis = self.dims[1][0]["title"]

        ax1.set_xlabel(f"{x_axis} ({self.dims[0][0]['unit']})")
        ax1.set_ylabel(f"{y_axis} ({self.dims[1][0]['unit']})")
        ax1.tick_params(left=True, right=True, labelleft=True, labelright=True)
        if scale := self.dims[0][0]["scale"]:
            ax1.set_xscale(scale)

        # additional_axes = []

        # for dim in self.dims[1][1:]:
        #     ax2 = ax1.twinx()
        #     additional_axes.append((ax2, dim))
        #     ax2.set_ylabel(f"{dim['title']} ({dim['unit']})")
        #     # ax2.tick_params(axis="y", colors="b")

        for factory in self.data:
            ax1.plot(
                self.data[factory][x_axis],
                self.data[factory][y_axis],
                self.factory_style(factory),
                label=factory,
            )

            # for ax2, dim in additional_axes:
            #     ax2.plot(self.data[factory][x_axis], self.data[factory][dim["title"]], factory_style[factory])

        self.mangle_plot(ax1)

        ax1.legend(loc=legend_position)
        plt.title(self.name)
        plt.savefig(str(out_dir / f"{self.name}.png"), bbox_inches='tight')
        pgf_out = out_dir / f"{self.name}.pgf"
        plt.savefig(str(pgf_out))
        self.mangle_pgf(pgf_out)

    def mangle_plot(self, ax):
        if self.name == "batch_lookup":
            x_min = self.data["AtomicDict"]["batch_size"][0]
            x_max = self.data["AtomicDict"]["batch_size"][-1]
            for factory in ["dict", "AtomicDict", "Growt"]:
                ax.plot(
                    [1],
                    self.data[factory]["throughput"][0],
                    self.factory_style(factory),
                )
                ax.hlines(
                    y=self.data[factory]["throughput"][0],
                    xmin=x_min, xmax=x_max,
                    color=self.factory_style(factory)[0],
                    linestyles='--',
                )

    @staticmethod
    def mangle_pgf(pgf: Path) -> None:
        with open(pgf, 'r') as f:
            content = f.read()
        with open(pgf, 'w') as f:
            f.write(content.replace("_", "\\_"))


def throughput_dict(report: BenchmarkReport, amount: str = "keys_count") -> float:
    assert report.params["dict_factory"] in ("dict", "Counter", "OrderedDict")
    return (report.params[amount] / (
            report.data.wall_clock_time * report.data.perf.time_spent_perc["py_dict"]
    )) / 1_000_000


def absolute_speedup_dict(report: BenchmarkReport, report_base: BenchmarkReport, amount: str = "keys_count") -> float:
    return throughput_dict(report, amount=amount) / throughput_dict(report_base, amount=amount)


def throughput_AtomicDict(report: BenchmarkReport, amount: str = "keys_count") -> float:
    assert report.params["dict_factory"] == "AtomicDict"
    return (report.params[amount] / (report.data.wall_clock_time * (
            report.data.perf.time_spent_perc["cereggii"]
            + report.data.perf.time_spent_perc.get("cereggii_ref_counting", 0)
    ))) / 1_000_000


def absolute_speedup_AtomicDict(report: BenchmarkReport, report_base: BenchmarkReport,
                                amount: str = "keys_count") -> float:
    return throughput_AtomicDict(report, amount=amount) / throughput_AtomicDict(report_base, amount=amount)


def throughput_Growt(report: BenchmarkReport, amount: str = "keys_count") -> float:
    assert report.params["dict_factory"] == "Growt"
    return (report.params[amount] / report.data.wall_clock_time) / 1_000_000


def absolute_speedup_Growt(report: BenchmarkReport, report_base: BenchmarkReport, amount: str = "keys_count") -> float:
    return throughput_Growt(report, amount=amount) / throughput_Growt(report_base, amount=amount)


def pick_benchmark_report(reports: list[BenchmarkReport]) -> BenchmarkReport:
    assert len(reports) % 2 == 1
    return sorted(
        reports,
        key=lambda r: r.data.wall_clock_time
    )[int(len(reports) / 2)]


def make_report(reports_dir: Path, bm_dir_name: str, filter_re: re.Pattern | None,
                sort_reports_by_param: str,
                reporter: Callable[[dict[str, list[BenchmarkReport]]], PerformanceReport]) -> PerformanceReport:
    reports = list(reports_dir.glob(f"{bm_dir_name}/*/report.json"))
    reports = [
        str(report.relative_to(reports_dir / bm_dir_name).parent)
        for report in reports
    ]

    if filter_re is not None:
        reports = list(filter(lambda path: filter_re.match(path) is not None, reports))

    bm_reports: dict[str, BenchmarkReport] = {}
    for benchmark_report_set in reports:
        benchmark_report = pick_benchmark_report(parse_file_as(
            list[BenchmarkReport],
            reports_dir / bm_dir_name / benchmark_report_set / "report.json"
        ))
        bm_reports[benchmark_report_set] = benchmark_report

    reports_aggregated = {}

    for factory in ["dict", "AtomicDict", "Growt", "Counter", "AtomicInt", "int"]:
        reports_names = list(filter(lambda report_name: report_name.startswith(f"{factory},"), bm_reports))
        reports_aggregated[factory] = sorted(
            [bm_reports[name] for name in reports_names],
            key=lambda report: report.params[sort_reports_by_param]
        )

    return reporter(reports_aggregated)
