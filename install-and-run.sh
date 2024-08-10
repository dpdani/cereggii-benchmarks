#!/usr/bin/env bash

set -euxo pipefail

git clone https://github.com/dpdani/cereggii-benchmarks
cd cereggii-benchmarks
./enable-perf.sh
git submodule update --init
cd growt
git submodule update utils
cd ..
docker build --tag 'cereggii_benchmarks' .
mkdir -p ./reports
docker run 'cereggii_benchmarks' \
  --cap-add PERFMON --cap-add SYS_PTRACE \
  -v ./reports:/cereggii-benchmarks/reports
