from __future__ import annotations

import re
import threading
from pathlib import Path

import cereggii
import numpy as np

from .. import utils
from ..growt import Growt
from ..utils import Axes, PerformanceReport


pre_keys_count = 10_000
keys_count = 1_000_000
keys: list[int] | None = None


def prepare():
    global keys

    if keys is None:
        keys = np.random.default_rng(seed=0).choice(2 ** 5 * (keys_count + pre_keys_count),
                                                    size=keys_count + pre_keys_count,
                                                    replace=False)  # distinct
        keys = keys.tolist()


def delete(dict_factory, threads):
    prepare()

    params = {"dict_factory": dict_factory.__qualname__,
              "keys_count": keys_count,
              "window_size": pre_keys_count,
              "min_size": pre_keys_count,
              "threads": threads}

    if issubclass(dict_factory, Growt):
        return utils.BenchmarkPlan(
            name="delete",
            threads=[],
            barrier_1=None,  # noqa
            barrier_2=None,  # noqa
            params=params,
            debug=lambda: {},
            wall_clock_time=Growt().delete(
                threads=threads,
                keys_count=keys_count,
                min_size=pre_keys_count,
                window_size=pre_keys_count,
            ),
        )

    d = dict_factory({
        k: None
        for k in keys[:pre_keys_count - 1]
    })
    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def deleter(keys, window_size):
        b1.wait()
        b2.wait()

        for k in keys[:window_size]:
            d[k] = None

        for i, k in enumerate(keys[window_size:]):
            d[k] = None
            del d[keys[i]]

    thrds = []
    batched = utils.batched(keys[pre_keys_count:], threads)
    batched_pre_keys = utils.batched(keys[:pre_keys_count], threads)
    for i, batch in enumerate(batched):
        pre = batched_pre_keys[i]
        t = threading.Thread(target=deleter, args=([*pre, *batch], len(pre)))
        thrds.append(t)

    assert len(thrds) == threads

    def debug():
        debug_d = None
        if isinstance(d, cereggii.AtomicDict):
            debug_d = d.debug()

        debug_stmts = [
            "len(d)",
        ]

        if debug_d:
            debug_d_meta = {m: debug_d['meta'][m] if m != 'generation' else id(debug_d['meta']['generation']) for m in
                            debug_d['meta']}
            debug_stmts.extend([
                "debug_d_meta",
                "len(list(filter(lambda _: _ != 0, debug_d['index'])))",
                "len(list(d.fast_iter()))",
                f"len(list(filter(lambda _: _ == {debug_d['meta']['tombstone']}, debug_d['index'])))",
                "len(list(filter(lambda block: len(block['entries']) == 0, debug_d['blocks'])))",
            ])

        debug_info = {}
        for stmt in debug_stmts:
            debug_info[stmt] = eval(stmt)

        return debug_info

    return utils.BenchmarkPlan(
        name="delete",
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
        bm_dir_name="delete",
        filter_re=re.compile(".*"),
        sort_reports_by_param="threads",
        reporter=lambda reports: (
            PerformanceReport(
                name="delete",
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
