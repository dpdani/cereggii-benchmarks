from __future__ import annotations

import random
import re
import threading
from pathlib import Path

import cereggii
import numpy as np

from .. import utils
from ..growt import Growt
from ..utils import Axes, PerformanceReport


keys_count = 10_000_000
rng = np.random.default_rng(seed=0)
max_val = keys_count // 5000
keys: list[int] | None = None


def prepare():
    global keys

    if keys is None:
        keys = rng.choice(max_val, size=keys_count)  # distinct
        keys = keys.tolist()


def mix(dict_factory, write_perc, threads, win_size=8192, min_size=0):
    prepare()

    params = {"dict_factory": dict_factory.__qualname__,
              "keys_count": keys_count,
              "write_perc": write_perc,
              "win_size": win_size,
              "min_size": min_size,
              "threads": threads}

    if issubclass(dict_factory, Growt):
        return utils.BenchmarkPlan(
            name="mix",
            threads=[],
            barrier_1=None,  # noqa
            barrier_2=None,  # noqa
            params=params,
            debug=lambda: {},
            wall_clock_time=Growt().mix(
                threads=threads,
                keys_count=keys_count,
                min_size=keys_count,
                wp=write_perc,
            ),
        )

    init = rng.choice(max_val, size=win_size * threads)
    pre_init = {k: None for k in init}

    if min_size:
        d = dict_factory(pre_init, min_size=min_size)
    else:
        d = dict_factory(pre_init)

    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def mixer(i, keys):
        rand = random.Random()
        all_keys = [*init, *keys]
        b1.wait()
        b2.wait()
        for j, k in enumerate(keys):
            if rand.randint(0, 100) / 100 < write_perc:
                d[k] = None
            else:
                lookup_k = all_keys[rand.randint(max(0, j - win_size * threads), j)]
                d.get(lookup_k, cereggii.NOT_FOUND)

    thrds = []
    batched = utils.batched(keys, threads)
    for i, batch in enumerate(batched):
        t = threading.Thread(target=mixer, args=(i, batch))
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
        name="mix",
        threads=thrds,
        barrier_1=b1,
        barrier_2=b2,
        params=params,
        debug=debug,
        wall_clock_time=None,
    )


def make_mix_report(reports_dir: Path, name: str, filter_re: re.Pattern) -> PerformanceReport:
    return utils.make_report(
        reports_dir,
        bm_dir_name="mix",
        filter_re=filter_re,
        sort_reports_by_param="write_perc",
        reporter=lambda reports: (
            PerformanceReport(
                name=name,
                dims=[
                    [Axes.write_perc],
                    [Axes.throughput, Axes.absolute_speedup],
                ],
                data={
                    "dict": {
                        "write_perc": list(map(lambda report: report.params["write_perc"], reports["dict"])),
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
                        "write_perc": list(map(lambda report: report.params["write_perc"], reports["AtomicDict"])),
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
                        "write_perc": list(map(lambda report: report.params["write_perc"], reports["Growt"])),
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


def generate_report(reports_dir: Path) -> PerformanceReport:
    return make_mix_report(
        reports_dir,
        name="mix",
        filter_re=re.compile(r"((dict, .*)|((AtomicDict|Growt), .* min_size=[1-9]([0-9]*), .*))"),
    )


def generate_report_growing(reports_dir: Path) -> PerformanceReport:
    return make_mix_report(
        reports_dir,
        name="mix_growing",
        filter_re=re.compile(r".*min_size=0.*"),
    )
