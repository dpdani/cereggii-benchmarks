import re
import threading
from pathlib import Path

import cereggii

from .. import utils
from ..growt import Growt
from ..utils import Axes, PerformanceReport


keys_count = 10_000_000


def update_contention(dict_factory, skew, threads):
    params = {"dict_factory": dict_factory.__qualname__,
              "keys_count": keys_count,
              "skew": skew,
              "min_size": keys_count,
              "threads": threads}

    if issubclass(dict_factory, Growt):
        return utils.BenchmarkPlan(
            name="update_contention",
            threads=[],
            barrier_1=None,  # noqa
            barrier_2=None,  # noqa
            params=params,
            debug=lambda: {},
            wall_clock_time=Growt().update_contention(
                threads=threads,
                keys_count=keys_count,
                min_size=keys_count,
                skew=skew,
            ),
        )

    keys = utils.zipf_distribution(keys_count, skew, keys_count)
    keys = keys.tolist()

    d = dict_factory({
        k: None
        for k in range(keys_count)
    })
    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def contender(i, keys):
        b1.wait()
        b2.wait()
        for _ in keys:
            d[_] = None  # noqa

    thrds = []
    batched = utils.batched(keys, threads)
    for i, batch in enumerate(batched):
        t = threading.Thread(target=contender, args=(i, batch))
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
        name="update_contention",
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
        bm_dir_name="update_contention",
        filter_re=re.compile(r".*"),
        sort_reports_by_param="skew",
        reporter=lambda reports: (
            PerformanceReport(
                name="update_contention",
                dims=[
                    [Axes.skew],
                    [Axes.throughput, Axes.absolute_speedup],
                ],
                data={
                    "dict": {
                        "skew": list(map(lambda report: report.params["skew"], reports["dict"])),
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
                    "dict": reports["dict"],
                    "AtomicDict": reports["AtomicDict"],
                    "Growt": reports["Growt"],
                }
            )
        )
    )
