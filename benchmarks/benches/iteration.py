from __future__ import annotations

import re
import threading
from pathlib import Path

import cereggii
import numpy as np

from .. import utils
from ..utils import Axes, PerformanceReport


keys_count = 10_000_000
keys: list[int] | None = None


def prepare():
    global keys

    if keys is None:
        keys = np.random.default_rng(seed=0).choice(2 ** 5 * keys_count, size=keys_count, replace=False)  # distinct
        keys = keys.tolist()


def iteration(dict_factory, threads):
    prepare()

    params = {"dict_factory": dict_factory.__qualname__,
              "keys_count": keys_count,
              "threads": threads}

    d = dict_factory({
        k: None
        for k in keys
    })
    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def iterator(p, i):
        b1.wait()
        b2.wait()
        for j, _ in enumerate(d.items()):
            if j % p == i:
                pass

    def iterator_partitioned(p, i):
        b1.wait()
        b2.wait()
        for _ in d.fast_iter(partitions=p, this_partition=i):
            pass

    thrds = []
    for i in range(threads):
        t = threading.Thread(
            target=iterator_partitioned if issubclass(dict_factory, cereggii.AtomicDict) else iterator,
            args=(threads, i)
        )
        thrds.append(t)

    assert len(thrds) == threads

    def debug():
        debug_d = None
        debug_d_meta = None
        if isinstance(d, cereggii.AtomicDict):
            debug_d = d.debug()
            debug_d_meta = {m: debug_d['meta'][m] if m != 'generation' else None for m in debug_d['meta']}

        debug_stmts = [
            "len(d)",
        ]

        if debug_d:
            debug_stmts.extend([
                "debug_d_meta",
                "len(list(filter(lambda _: _ != 0, debug_d['index'])))",
                "len(list(d.fast_iter()))",
            ])

        debug_info = {}
        for stmt in debug_stmts:
            debug_info[stmt] = eval(stmt)

        return debug_info

    return utils.BenchmarkPlan(
        name="iteration",
        threads=thrds,
        barrier_1=b1,
        barrier_2=b2,
        params=params,
        debug=debug,
        wall_clock_time=None,
    )


def generate_report(reports_dir: Path) -> PerformanceReport:
    return utils.make_report(
        reports_dir,
        bm_dir_name="iteration",
        filter_re=re.compile(r".*"),
        sort_reports_by_param="threads",
        reporter=lambda reports: (
            PerformanceReport(
                name="iteration",
                dims=[
                    [Axes.threads],
                    [Axes.throughput, Axes.absolute_speedup],
                ],
                data={
                    "dict": {
                        "threads": list(map(lambda report: report.params["threads"], reports["dict"])),
                        "throughput": [
                            utils.throughput_dict(report)
                            for report in reports["dict"]
                        ],
                        "absolute speedup": [
                            utils.absolute_speedup_dict(report, reports["dict"][0])
                            for report in reports["dict"]
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
                },
                benchmark_reports={
                    "dict": reports["dict"],
                    "AtomicDict": reports["AtomicDict"],
                },
            )
        )
    )
