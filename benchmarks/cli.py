import multiprocessing
import shutil
import subprocess
import sys
import time
import timeit
from collections import Counter, OrderedDict
from pathlib import Path

import click
import humanize
import typer
from cereggii import AtomicDict, AtomicInt

from . import __doc__ as doc, benches, utils
from .growt import Growt
from .hw_perf import run_hardware_benchmarks


app = typer.Typer()

tables = [
    AtomicDict,
    Growt,
    OrderedDict,
    Counter,
    dict,
]

integers = [
    AtomicInt,
    int,
]


@app.command()
def run(benchmark: str, arguments: str, reports_dir: Path, repeats: int):
    assert reports_dir.exists()
    utils.reports_dir = reports_dir
    # noinspection PyUnusedLocal
    benchmark = benches.benchmarks[benchmark]
    stmt = f'utils.execute_benchmark_plan(benchmark({arguments}))'
    timeit.timeit(stmt, number=repeats, globals=globals() | locals())


def run_benchmark(benchmark: str, arguments: str, repeats=5):
    assert benchmark in benches.benchmarks
    reports_dir = utils.reports_dir / benchmark / arguments
    # shutil.rmtree(reports_dir, ignore_errors=True)
    reports_dir.mkdir(exist_ok=False, parents=True)
    sub = (f"python -m benchmarks "
           f"run '{benchmark}' '{arguments}' '{reports_dir}' {repeats}")
    print(f"  - {sub}")
    started = time.time()
    subprocess.check_call(sub, shell=True)
    took = time.time() - started
    subprocess.check_call("find -type f -wholename '*.perf' -exec gzip {} +", cwd=reports_dir, shell=True)
    click.secho(f"    benchmark '{benchmark}({arguments})' completed in {humanize.naturaldelta(took)}", fg="green")


@app.command()
def start():
    click.secho(doc.lstrip(), bold=True)

    print(f"{sys.version=}\n")

    print("Initializing perf... ", end='')
    subprocess.check_call("perf record -q -o /dev/null sleep 1", shell=True)
    print("done.\n")

    cpu_count = multiprocessing.cpu_count()
    print(f"Found {cpu_count=}.\n")

    utils.reports_dir.mkdir(exist_ok=False, parents=True)

    print(f"Will write reports to {utils.reports_dir}.\n\nRunning benchmarks:")

    started = time.time()

    run_hardware_benchmarks(utils.reports_dir)

    for t in utils.threads():
        run_benchmark('book', f'AtomicDict, threads={t}')
        run_benchmark('book', f'Counter, threads={t}')
        run_benchmark('book', f'Counter, with_lock=True, threads={t}')

    for t in utils.threads():
        run_benchmark('insert', f'AtomicDict, min_size=50_000, threads={t}')
        run_benchmark('insert', f'Growt, min_size=50_000, threads={t}')
        run_benchmark('insert', f'AtomicDict, min_size=10_000_000, threads={t}')
        run_benchmark('insert', f'Growt, min_size=10_000_000, threads={t}')
    run_benchmark('insert', f'dict, min_size=0, threads={1}')
    run_benchmark('insert', f'dict, min_size=0, threads={cpu_count}', repeats=1)  # this is *very* slow

    for t in utils.threads():
        run_benchmark('lookup_succ', f"AtomicDict, threads={t}")
        run_benchmark('lookup_succ', f"Growt, threads={t}")
        run_benchmark('lookup_succ', f"dict, threads={t}")

    for t in utils.threads():
        run_benchmark('lookup_fail', f"AtomicDict, threads={t}")
        run_benchmark('lookup_fail', f"Growt, threads={t}")
        run_benchmark('lookup_fail', f"dict, threads={t}")

    for t in utils.threads():
        run_benchmark('delete', f"Growt, threads={t}")
        run_benchmark('delete', f"AtomicDict, threads={t}")
    run_benchmark('delete', f"dict, threads={1}")
    run_benchmark('delete', f"dict, threads={cpu_count}")

    for s in [0.25, 0.50, 0.75, 0.85, 0.90, 0.95, 1.0, 1.05, 1.10, 1.25, 1.50, 2.0]:
        run_benchmark('lookup_contention', f"dict, skew={s}, threads=1")
        run_benchmark('lookup_contention', f"AtomicDict, skew={s}, threads={cpu_count}")
        run_benchmark('lookup_contention', f"Growt, skew={s}, threads={cpu_count}")
        run_benchmark('update_contention', f"dict, skew={s}, threads=1")
        run_benchmark('update_contention', f"AtomicDict, skew={s}, threads={cpu_count}")
        run_benchmark('update_contention', f"Growt, skew={s}, threads={cpu_count}")
        run_benchmark('aggregation', f"Counter, skew={s}, threads=1")
        run_benchmark('aggregation', f"AtomicDict, skew={s}, threads={cpu_count}")
        run_benchmark('aggregation', f"Growt, skew={s}, threads={cpu_count}")
        run_benchmark('aggregation', f"AtomicDict, skew={s}, threads={cpu_count}, min_size=10_000_000")
        run_benchmark('aggregation', f"Growt, skew={s}, threads={cpu_count}, min_size=10_000_000")

    win = 8192
    for wp in [0.05, 0.10, 0.25, 0.50, 0.75]:
        for min_size in [0, int(wp * 10_000_000 + win * cpu_count)]:
            # run_benchmark('mix', f"AtomicDict, write_perc={wp}, min_size={min_size}, win_size={win}, threads={cpu_count}")
            run_benchmark('mix', f"Growt, write_perc={wp}, min_size={min_size}, win_size={win}, threads={cpu_count}")
        run_benchmark('mix', f"dict, write_perc={wp}, min_size=0, win_size={win}, threads=1")

    for t in utils.threads():
        run_benchmark('int_counter', f"AtomicInt, amount={2 ** 20}, threads={t}")
        run_benchmark('int_counter', f"int, amount={2 ** 20}, threads={t}")
        # run_benchmark('int_counter_handle', f"AtomicInt, amount={2**20}, threads={t}")

    for t in utils.threads():
        run_benchmark('iteration', f"AtomicDict, threads={t}")
        run_benchmark('iteration', f"dict, threads={t}")

    for batch_size in [1, 2, 64, 128, 1024, 4096, 16384, 65536, 1048576]:
        run_benchmark('batch_lookup', f"AtomicDict, threads={cpu_count}, batch_size={batch_size}")
    run_benchmark('batch_lookup', f"AtomicDict, threads={cpu_count}, batch_size={0}")
    run_benchmark('batch_lookup', f"dict, threads={cpu_count}, batch_size={0}")
    run_benchmark('batch_lookup', f"Growt, threads={cpu_count}, batch_size={0}")

    took = time.time() - started
    click.secho(f"\nBenchmarks completed in {humanize.naturaldelta(took)}.\n", fg='green', bold=True)

    print("Preparing binaries and shared libraries for perf inspections... ", end='')
    prepare_shared()
    print("done.")

    make_performance_report(utils.reports_dir)


def prepare_shared():
    from ._shared import shared

    shared_dir = utils.reports_dir / '_shared'
    shared_dir.mkdir()

    for path in shared:
        path = Path(path)
        if path.is_symlink():
            continue
        if not path.exists():
            print("probably not inside a container, skipping... ", end='')
            break
        dst = shared_dir / str(path)[1:]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)


def make_performance_report(reports_dir: Path):
    from .performance_report import generate_reports, write_reports
    report = generate_reports(reports_dir)
    path = write_reports(report, reports_dir)
    click.secho(f"Wrote performance report in {path}", fg='green')


@app.command()
def make_perf_report(reports_dir: Path):
    make_performance_report(reports_dir)
