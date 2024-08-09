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


def batch_lookup(dict_factory, threads, batch_size=0):
    prepare()

    params = {"dict_factory": dict_factory.__qualname__,
              "keys_count": keys_count,
              "min_size": keys_count,
              "batch_size": batch_size,
              "threads": threads}

    if issubclass(dict_factory, Growt):
        return utils.BenchmarkPlan(
            name="batch_lookup",
            threads=[],
            barrier_1=None,  # noqa
            barrier_2=None,  # noqa
            params=params,
            debug=lambda: {},
            wall_clock_time=Growt().lookup_succ(
                threads=threads,
                keys_count=keys_count,
                min_size=keys_count,
            ),
        )

    d = dict_factory({
        k: None
        for k in keys
    })
    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def lookuper(keys):
        b1.wait()
        b2.wait()
        for _ in keys:
            d.get(_)  # noqa

    def batch_lookuper(keys):
        b1.wait()
        b2.wait()
        for batch in utils.batched_fixed(keys, batch_size):
            for _, v in d.batch_getitem({
                k: 0
                for k in batch
            }).items():
                assert v is None

    thrds = []
    batches = utils.batched(keys, threads)
    for batch in batches:
        t = threading.Thread(target=batch_lookuper if batch_size else lookuper, args=(batch,))
        thrds.append(t)

    assert len(thrds) == threads
    assert sorted(itertools.chain.from_iterable(batches)) == sorted(keys)

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
        name="batch_lookup",
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
        bm_dir_name="batch_lookup",
        filter_re=re.compile(r".*"),
        sort_reports_by_param="batch_size",
        reporter=lambda reports: (
            PerformanceReport(
                name="batch_lookup",
                dims=[
                    [Axes.batch_size],
                    [Axes.throughput, Axes.absolute_speedup],
                ],
                data={
                    "dict": {
                        "batch_size": list(map(lambda report: report.params["batch_size"], reports["dict"])),
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
                        "batch_size": list(map(lambda report: report.params["batch_size"], reports["AtomicDict"])),
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
                        "batch_size": list(map(lambda report: report.params["batch_size"], reports["Growt"])),
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
