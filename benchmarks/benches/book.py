from __future__ import annotations

import collections
import itertools
import re
import threading
from pathlib import Path
from typing import Any

import cereggii
import nltk

from .. import utils
from ..growt import Growt
from ..utils import Axes, PerformanceReport


source: list[str] | None = None


def prepare():
    global source

    if source is None:
        nltk.download('punkt', quiet=True)

        with open(utils.data_dir / "la divina commedia.txt") as f:
            source = nltk.tokenize.word_tokenize(f.read(), language='italian')

        source = [s.lower() for s in source]


def book(dict_factory, threads, with_lock=False):
    prepare()
    # import sys
    # print(f"{sys._is_gil_enabled()=}")

    params = {"dict_factory": dict_factory.__qualname__,
              "source": len(source),
              "threads": threads}

    assert not issubclass(dict_factory, Growt)

    d = dict_factory()
    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)
    lock = threading.Lock()

    def atomic(i, source):
        b1.wait()
        b2.wait()
        for _ in range(len(source)):
            k = source[_]
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

    def builtin(i, source):
        b1.wait()
        b2.wait()
        for _ in range(len(source)):
            d[source[_]] += 1

    def builtin_lock(i, source):
        b1.wait()
        b2.wait()
        for _ in range(len(source)):
            with lock:
                d[source[_]] += 1

    thrds = []
    batched = utils.batched(source, threads)
    for i, batch in enumerate(batched):
        if dict_factory == cereggii.AtomicDict:
            target = atomic
        elif with_lock:
            target = builtin_lock
        else:
            target = builtin
        t = threading.Thread(target=atomic if dict_factory == cereggii.AtomicDict else builtin,
                             args=(i, batch))
        thrds.append(t)

    assert len(thrds) == threads
    assert sorted(itertools.chain.from_iterable(batched)) == sorted(source)

    def debug() -> dict[str, Any]:
        debug_d = None
        if isinstance(d, cereggii.AtomicDict):
            debug_d = d.debug()

        # noinspection PyUnusedLocal
        def compare_with_sequential():
            counter = collections.Counter(source)
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
        name="book",
        threads=thrds,
        barrier_1=b1,
        barrier_2=b2,
        params=params,
        debug=debug,
        wall_clock_time=None,
    )


def make_book_report(reports_dir: Path, name: str, filter_re: re.Pattern) -> PerformanceReport:
    len_source = "source"

    return utils.make_report(
        reports_dir,
        bm_dir_name="book",
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
                        "threads": list(map(lambda report: report.params["threads"], reports["Counter"])),
                        "throughput": [
                            utils.throughput_dict(report, len_source)
                            for report in reports["Counter"]
                        ],
                        "absolute speedup": [
                            utils.absolute_speedup_dict(report, reports["Counter"][0], len_source)
                            for report in reports["Counter"]
                        ]
                    },
                    "dict_lock": {
                        "threads": list(map(lambda report: report.params["threads"], reports["Counter"])),
                        "throughput": [
                            utils.throughput_dict(report, len_source)
                            for report in reports["Counter"]
                        ],
                        "absolute speedup": [
                            utils.absolute_speedup_dict(report, reports["Counter"][0], len_source)
                            for report in reports["Counter"]
                        ],
                    },
                    "AtomicDict": {
                        "threads": list(map(lambda report: report.params["threads"], reports["AtomicDict"])),
                        "throughput": [
                            utils.throughput_AtomicDict(report, len_source)
                            for report in reports["AtomicDict"]
                        ],
                        "absolute speedup": [
                            utils.absolute_speedup_AtomicDict(report, reports["AtomicDict"][0], len_source)
                            for report in reports["AtomicDict"]
                        ],
                    },
                },
                benchmark_reports={
                    "Counter": reports["Counter"],
                    "AtomicDict": reports["AtomicDict"],
                },
            )
        ),
    )


def generate_report(reports_dir: Path):
    report = make_book_report(reports_dir, "book", filter_re=re.compile(r"^((?!(with_lock=True)).)*$"))
    report_lock = make_book_report(reports_dir, "book_lock", filter_re=re.compile(r".*with_lock=True.*"))
    return PerformanceReport(
        name="book",
        dims=[
            [Axes.threads],
            [Axes.throughput, Axes.absolute_speedup],
        ],
        data={
            "dict": report.data["dict"],
            "AtomicDict": report.data["AtomicDict"],
            "dict_lock": report_lock.data["dict_lock"],
        },
        benchmark_reports={
            "Counter": report.benchmark_reports["Counter"],
            "Counter_lock": report_lock.benchmark_reports["Counter"],
            "AtomicDict": report.benchmark_reports["AtomicDict"],
        },
    )
