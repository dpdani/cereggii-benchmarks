import sys
import threading

from cereggii import AtomicInt

from .. import utils


def int_counter_handle(int_factory, amount, threads):
    params = {"int_factory": int_factory.__qualname__,
              "amount": amount,
              "threads": threads}

    assert issubclass(int_factory, AtomicInt)

    class Spam:
        def __init__(self):
            self.i = int_factory()

    spam = Spam()

    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def counter():
        h = spam.i.get_handle()
        b1.wait()
        b2.wait()
        for _ in range(amount // threads):
            h += 1

    thrds = []
    for _ in range(threads):
        t = threading.Thread(target=counter)
        thrds.append(t)

    assert len(thrds) == threads

    def debug():
        nonlocal spam  # seems to be actually important (gc somehow messing up?)

        get_ = {
            "i": spam.i.get(),
        }
        print("got")
        sys.stdout.flush()
        return get_

    return utils.BenchmarkPlan(
        name="int_counter_handle",
        threads=thrds,
        barrier_1=b1,
        barrier_2=b2,
        params=params,
        debug=debug,
        wall_clock_time=None,
    )
