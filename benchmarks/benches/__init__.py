from . import (
    aggregation,
    batch_lookup,
    book,
    delete,
    insert,
    int_counter,
    int_counter_handle,
    iteration,
    lookup_contention,
    lookup_fail,
    lookup_succ,
    mix,
    update_contention,
)


benchmarks = {
    'book': book.book,
    'insert': insert.insert,
    'mix': mix.mix,
    'lookup_succ': lookup_succ.lookup_succ,
    'lookup_fail': lookup_fail.lookup_fail,
    'delete': delete.delete,
    'lookup_contention': lookup_contention.lookup_contention,
    'update_contention': update_contention.update_contention,
    'aggregation': aggregation.aggregation,
    'int_counter': int_counter.int_counter,
    'int_counter_handle': int_counter_handle.int_counter_handle,
    'iteration': iteration.iteration,
    'batch_lookup': batch_lookup.batch_lookup,
}
