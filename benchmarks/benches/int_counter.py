import threading

from cereggii import AtomicInt

from .. import utils


def int_counter(int_factory, amount, threads):
    params = {"int_factory": int_factory.__qualname__,
              "amount": amount,
              "threads": threads}

    class Spam:
        def __init__(self):
            self.i = int_factory()

    spam = Spam()

    b1 = threading.Barrier(threads + 1)
    b2 = threading.Barrier(threads + 1)

    def counter():
        b1.wait()
        b2.wait()
        for _ in range(amount // threads):
            spam.i += 1

    thrds = []
    for _ in range(threads):
        t = threading.Thread(target=counter)
        thrds.append(t)

    assert len(thrds) == threads

    def debug():
        return {
            "i": spam.i if not isinstance(spam.i, AtomicInt) else spam.i.get(),
        }

    return utils.BenchmarkPlan(
        name="int_counter",
        threads=thrds,
        barrier_1=b1,
        barrier_2=b2,
        params=params,
        debug=debug,
        wall_clock_time=None,
    )
