# (mostly) Copied from https://github.com/docker-library/python/blob/master/3.9/bullseye/Dockerfile

FROM buildpack-deps:trixie AS builder

COPY growt /cereggii-benchmarks/growt

RUN apt-get update && apt-get install -yqq cmake

RUN cd /cereggii-benchmarks/growt \
        && mkdir build \
        && cd build \
        && cmake .. \
        && make -j

COPY hw-perf /cereggii-benchmarks/hw-perf

RUN cd /cereggii-benchmarks/hw-perf \
    && mkdir "build" \
    && BUILD_DIR=/cereggii-benchmarks/hw-perf/build make build-all

FROM buildpack-deps:trixie

# ensure local python is preferred over distribution python
ENV PATH=/usr/local/bin:$PATH

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG=C.UTF-8

# extra dependencies (over what buildpack-deps already includes)
RUN apt-get update && apt-get install -y --no-install-recommends \
		libbluetooth-dev \
		tk-dev \
		uuid-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY ./cpython /usr/src/python

RUN set -ex \
	\
	&& cd /usr/src/python \
	&& gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" \
	&& ./configure \
		--build="$gnuArch" \
		--enable-loadable-sqlite-extensions \
		--enable-optimizations \
		--enable-option-checking=fatal \
		--enable-shared \
		--with-system-expat \
		--with-system-ffi \
	&& make -j "$(nproc)" \
	&& make install \
	&& rm -rf /usr/src/python \
	\
	&& find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
			-o \( -type f -a \( -name '*.pyc' -o -name '*.pyo' -o -name '*.a' \) \) \
		\) -exec rm -rf '{}' + \
	\
	&& ldconfig \
	\
	&& python3 --version

# make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python3-config python-config \
	&& ln -s pip3 pip

COPY --from=builder /cereggii-benchmarks/growt/build /cereggii-benchmarks/growt/build
COPY --from=builder /cereggii-benchmarks/hw-perf/build /cereggii-benchmarks/hw-perf/build

RUN apt-get update -qq && apt-get install -yqq linux-perf strace time poppler-utils

RUN wget -qO- "https://yihui.org/tinytex/install-bin-unix.sh" | sh

ENV PATH=$PATH:/root/bin

RUN tlmgr install underscore pgf

WORKDIR /cereggii-benchmarks

COPY pyproject.toml .

RUN pip install -e .

COPY . .

VOLUME ./reports

ENTRYPOINT ["python", "-m", "benchmarks", "start"]
