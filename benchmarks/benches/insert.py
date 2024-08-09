from __future__ import annotations

import itertools
import re
import threading
from pathlib import Path

import cereggii
import numpy as np

from .. import utils
from ..growt import Growt
from ..utils import Axes, PerformanceReport


keys_count = 10_000_000
keys: list[int] | None = None


def prepare():
    global keys

    if keys is None:
        keys = np.random.default_rng(seed=0).choice(2 ** 5 * keys_count, size=keys_count, replace=False)  # distinct
        keys = keys.tolist()


def insert(dict_factory, min_size, threads):
    prepare()

    params = {"dict_factory": dict_factory.__qualname__,
              "keys_count": keys_count,
              "min_size": min_size,
              "threads": threads}

    if issubclass(dict_factory, Growt):
        return utils.BenchmarkPlan(
            name="insert",
            threads=[],
            barrier_1=None,  # noqa
            barrier_2=None,  # noqa
            params=params,
            debug=lambda: {},
            wall_clock_time=Growt().insert(
                threads=threads,
                keys_count=keys_count,
                min_size=min_size,
            ),
        )

    if min_size:
        d = dict_factory(min_size=min_size)
    else:
        d = dict_factory()
    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def inserter(keys):
        b1.wait()
        b2.wait()
        for _ in keys:
            d[_] = None

    thrds = []
    batched = utils.batched(keys, threads)
    for i, batch in enumerate(batched):
        t = threading.Thread(target=inserter, args=(batch,))
        thrds.append(t)

    assert len(thrds) == threads
    assert sorted(itertools.chain.from_iterable(batched)) == sorted(keys)

    def debug():
        debug_d = None
        if isinstance(d, cereggii.AtomicDict):
            debug_d = d.debug()

        debug_stmts = [
            "len(d)",
        ]

        if debug_d:
            debug_stmts.extend([
                "debug_d['meta']['log_size']",
                "len(list(filter(lambda _: _ != 0, debug_d['index'])))",
                "len(list(d.fast_iter()))",
            ])

        debug_info = {}
        for stmt in debug_stmts:
            debug_info[stmt] = eval(stmt)

        return debug_info

    return utils.BenchmarkPlan(
        name="insert",
        threads=thrds,
        barrier_1=b1,
        barrier_2=b2,
        params=params,
        debug=debug,
        wall_clock_time=None,
    )


def make_insert_report(reports_dir: Path, name: str, filter_re: re.Pattern) -> PerformanceReport:
    return utils.make_report(
        reports_dir,
        bm_dir_name="insert",
        filter_re=filter_re,
        sort_reports_by_param="threads",
        reporter=lambda reports: (
            PerformanceReport(
                name=name,
                dims=[
                    [Axes.threads],
                    [Axes.throughput, Axes.absolute_speedup],
                ],
                data={
                    "dict": {
                        "threads": [
                            reports["dict"][0].params["threads"],
                            reports["dict"][-1].params["threads"],
                        ],
                        "throughput": [
                            utils.throughput_dict(reports["dict"][0]),
                            utils.throughput_dict(reports["dict"][-1]),
                        ],
                        "absolute speedup": [
                            utils.absolute_speedup_dict(reports["dict"][0], reports["dict"][0]),
                            utils.absolute_speedup_dict(reports["dict"][-1], reports["dict"][0]),
                        ],
                    },
                    "dict_ideal": {
                        "threads": list(utils.threads()),
                        "throughput": [
                            utils.throughput_dict(reports["dict"][0]) * t
                            for t in utils.threads()
                        ],
                        "absolute speedup": [
                            t
                            for t in utils.threads()
                        ],
                    },
                    "AtomicDict": {
                        "threads": list(map(lambda report: report.params["threads"], reports["AtomicDict"])),
                        "throughput": [
                            utils.throughput_AtomicDict(report)
                            for report in reports["AtomicDict"]
                        ],
                        "absolute speedup": [
                            utils.absolute_speedup_AtomicDict(report, reports["AtomicDict"][0])
                            for report in reports["AtomicDict"]
                        ],
                    },
                    "Growt": {
                        "threads": list(map(lambda report: report.params["threads"], reports["Growt"])),
                        "throughput": [
                            utils.throughput_Growt(report)
                            for report in reports["Growt"]
                        ],
                        "absolute speedup": [
                            utils.absolute_speedup_Growt(report, reports["Growt"][0])
                            for report in reports["Growt"]
                        ],
                    },
                },
                benchmark_reports={
                    "dict": reports["dict"],
                    "AtomicDict": reports["AtomicDict"],
                    "Growt": reports["Growt"],
                },
            )
        )
    )


def generate_report(reports_dir: Path):
    return make_insert_report(
        reports_dir,
        name="insert",
        filter_re=re.compile(r"(dict, min_size=0,|AtomicDict, min_size=10_000_000,|Growt, min_size=10_000_000)"),
    )


def generate_report_growing(reports_dir: Path) -> PerformanceReport:
    return make_insert_report(
        reports_dir,
        name="insert_growing",
        filter_re=re.compile(r"(dict, min_size=0,|AtomicDict, min_size=50_000,|Growt, min_size=50_000)"),
    )
