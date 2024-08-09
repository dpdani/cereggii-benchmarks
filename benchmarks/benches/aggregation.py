import collections
import itertools
import re
import threading
from pathlib import Path
from typing import Any

import cereggii

from .. import utils
from ..growt import Growt
from ..utils import Axes, PerformanceReport


keys_count = 10_000_000


def aggregation(dict_factory, skew, threads, min_size=0):
    params = {"dict_factory": dict_factory.__qualname__,
              "keys_count": keys_count,
              "skew": skew,
              "min_size": min_size,
              "threads": threads}

    if issubclass(dict_factory, Growt):
        return utils.BenchmarkPlan(
            name="aggregation",
            threads=[],
            barrier_1=None,  # noqa
            barrier_2=None,  # noqa
            params=params,
            debug=lambda: {},
            wall_clock_time=Growt().aggregation(
                threads=threads,
                keys_count=keys_count,
                min_size=min_size,
                skew=skew,
            ),
        )

    keys = utils.zipf_distribution(keys_count, skew, keys_count)
    keys = keys.tolist()

    if min_size:
        d = dict_factory(min_size=min_size)
    else:
        d = dict_factory()

    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def atomic(i, keys):
        b1.wait()
        b2.wait()
        for _ in range(len(keys)):
            k = keys[_]
            expected = d.get(k, cereggii.NOT_FOUND)
            desired = 1
            while True:
                try:
                    if expected is not cereggii.NOT_FOUND:
                        desired = expected + 1
                    assert expected != desired
                    d.compare_and_set(k, expected, desired)
                except cereggii.ExpectationFailed:
                    expected = d.get(k, cereggii.NOT_FOUND)
                else:
                    break

    def builtin(i, keys):
        b1.wait()
        b2.wait()
        for _ in range(len(keys)):
            d[keys[_]] += 1

    thrds = []
    batched = utils.batched(keys, threads)
    for i, batch in enumerate(batched):
        t = threading.Thread(target=atomic if dict_factory == cereggii.AtomicDict else builtin,
                             args=(i, batch))
        thrds.append(t)

    assert len(thrds) == threads
    assert sorted(itertools.chain.from_iterable(batched)) == sorted(keys)

    def debug() -> dict[str, Any]:
        debug_d = None
        if isinstance(d, cereggii.AtomicDict):
            debug_d = d.debug()

        # noinspection PyUnusedLocal
        def compare_with_sequential():
            counter = collections.Counter(keys)
            diff = {}
            it = d.fast_iter() if isinstance(d, cereggii.AtomicDict) else d.items()
            for k, v in it:
                if counter[k] != v:
                    diff[k] = {"d": v, "counter": counter[k]}
            return diff

        debug_stmts = [
            "len(d)",
            "compare_with_sequential()",
        ]

        if debug_d:
            debug_stmts.extend([
                "debug_d['meta']['log_size']",
                "len(list(filter(lambda _: _ != 0, debug_d['index'])))",
                "len(list(d.fast_iter()))",
                "sum(map(lambda _: _[1], d.fast_iter()))",
            ])
        else:
            debug_stmts.extend([
                "sum(d.values())",
            ])

        debug_info = {}
        for stmt in debug_stmts:
            debug_info[stmt] = eval(stmt)

        return debug_info

    return utils.BenchmarkPlan(
        name="aggregation",
        threads=thrds,
        barrier_1=b1,
        barrier_2=b2,
        params=params,
        debug=debug,
        wall_clock_time=None,
    )


def make_aggregation_report(reports_dir: Path, name: str, filter_re: re.Pattern) -> PerformanceReport:
    return utils.make_report(
        reports_dir,
        bm_dir_name="aggregation",
        filter_re=filter_re,
        sort_reports_by_param="skew",
        reporter=lambda reports: (
            PerformanceReport(
                name=name,
                dims=[
                    [Axes.skew],
                    [Axes.throughput, Axes.absolute_speedup],
                ],
                data={
                    "dict": {
                        "skew": list(map(lambda report: report.params["skew"], reports["Counter"])),
                        "throughput": [
                            utils.throughput_dict(report)
                            for report in reports["Counter"]
                        ],
                        "absolute speedup": [
                            utils.absolute_speedup_dict(report, reports["Counter"][0])
                            for report in reports["Counter"]
                        ],
                    },
                    "AtomicDict": {
                        "skew": list(map(lambda report: report.params["skew"], reports["AtomicDict"])),
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
                        "skew": list(map(lambda report: report.params["skew"], reports["Growt"])),
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
                    "dict": reports["Counter"],
                    "AtomicDict": reports["AtomicDict"],
                    "Growt": reports["Growt"],
                },
            )
        ),
    )


def generate_report(reports_dir: Path) -> PerformanceReport:
    return make_aggregation_report(
        reports_dir,
        name="aggregation",
        filter_re=re.compile(r"((Counter, .*)|((AtomicDict|Growt), (.*), min_size=10_000_000))"),
    )


def generate_report_growing(reports_dir: Path) -> PerformanceReport:
    return make_aggregation_report(
        reports_dir,
        name="aggregation_growing",
        filter_re=re.compile(r"((Counter, .*)|((AtomicDict|Growt), skew=\d\.\d+, threads=\d+))$"),
    )
