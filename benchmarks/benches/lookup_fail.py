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
to_lookup: list[int] | None = None


def prepare():
    global keys, to_lookup

    if keys is None:
        keys = np.random.default_rng(seed=0).choice(np.arange(2 ** 5 * keys_count),
                                                    size=keys_count,
                                                    replace=False)  # distinct
        keys = keys.tolist()

        to_lookup = np.random.default_rng(seed=0).choice(np.arange(2 ** 5 * keys_count, 2 ** 5 * keys_count * 2),
                                                         size=keys_count,
                                                         replace=False)  # distinct
        to_lookup = to_lookup.tolist()


def lookup_fail(dict_factory, threads):
    prepare()

    params = {"dict_factory": dict_factory.__qualname__,
              "keys_count": keys_count,
              "to_lookup": len(to_lookup),
              "threads": threads}

    if issubclass(dict_factory, Growt):
        return utils.BenchmarkPlan(
            name="lookup_fail",
            threads=[],
            barrier_1=None,  # noqa
            barrier_2=None,  # noqa
            params=params,
            debug=lambda: {},
            wall_clock_time=Growt().lookup_fail(
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

    thrds = []
    batches = utils.batched(to_lookup, threads)
    for batch in batches:
        t = threading.Thread(target=lookuper, args=(batch,))
        thrds.append(t)

    assert len(thrds) == threads
    assert sorted(itertools.chain.from_iterable(batches)) == sorted(to_lookup)
    assert len(set(keys).intersection(set(to_lookup))) == 0

    def debug():
        debug_d = None
        if isinstance(d, cereggii.AtomicDict):
            debug_d = d.debug()

        debug_stmts = [
            "len(d)",
        ]

        if debug_d:
            debug_d_meta = {m: debug_d['meta'][m] if m != 'generation' else None for m in debug_d['meta']}
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
        name="lookup_fail",
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
        bm_dir_name="lookup_fail",
        filter_re=re.compile(r".*"),
        sort_reports_by_param="threads",
        reporter=lambda reports: (
            PerformanceReport(
                name="lookup_fail",
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
