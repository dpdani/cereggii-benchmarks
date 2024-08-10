import json
import re
import subprocess
import time
from pathlib import Path

import click
import humanize

from benchmarks.config import config


def run_hardware_benchmarks(reports_dir: Path):
    cas_perfs = [
        "casperf8",
        "casperf16",
        "casperf32",
        "casperf64",
        "casperf128",
        "casperf64multiline",
        "casperf8uncontended",
        "casperf8contended",
    ]
    results = {}

    pattern = re.compile(r".*real (.*).*", flags=re.MULTILINE)

    print("  - Hardware benchmarking")
    started = time.time()

    for cas in cas_perfs:
        assert (config["hw_perf_dir"] / "build" / cas).is_file()

        amount = 4294967295
        if cas == "casperf64multiline":
            amount = 1048576

        command = f"time -p ./build/{cas}"
        print(f"    - {command}")
        out = subprocess.check_output(command, cwd=config["hw_perf_dir"], shell=True, stderr=subprocess.STDOUT)

        results[cas] = amount / float(pattern.search(out.decode()).groups()[0]) / 1_000_000

    # command = "./build/cache"
    # print(f"    - {command}")
    # cache = subprocess.check_output(command, cwd=config["hw_perf_dir"]).decode()
    cache = ""

    took = time.time() - started
    click.secho(f"    hardware benchmarks completed in {humanize.naturaldelta(took)}", fg="green")

    result = {
        "cas": results,
        "cache": cache,
    }

    with open(reports_dir / config["hw_perf_json"], "w") as f:
        json.dump(result, f)
