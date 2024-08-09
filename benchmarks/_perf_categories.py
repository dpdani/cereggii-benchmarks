perf_categories = dict(
    cereggii_ref_counting={
        "AtomicRef_Get",
        "AtomicRef_Get@plt",
    },

    ref_counting={
        "_Py_IncRefShared",
        "_Py_IncRefShared@plt",
        "_Py_DecRefShared",
        "_Py_DecRefShared@plt",
        "_Py_MergeZeroRefcount",
        "_Py_MergeZeroRefcount@plt",

        # 3.13
        "_Py_DecRefSharedDebug",
        "_Py_DecRefSharedDebug@plt",
        "_Py_NewReference",
        "_Py_TryIncrefCompare",
        "_Py_MergeZeroLocalRefcount@plt",

    },

    interpreter={
        "_PyEval_Fast",
    },

    py_compare={
        "PyObject_RichCompare",
        "PyObject_RichCompareBool",
        "PyObject_RichCompareBool@plt",
        "object_richcompare",
        "long_richcompare",
        "PyUnicode_RichCompare",
    },

    py_hash={
        "PyObject_Hash",
        "PyObject_Hash@plt",
        "_Py_HashBytes",
        "_Py_HashBytes@plt",
        "unicode_hash",
        "long_hash",
    },

    py_dict={
        "dict_ass_sub",
        "dict_subscript_slow",
        "pydict_get_slow_blah.isra.0",
        "dict_lookup_missing",
        "PyDict_SetItem",
        "PyDict_SetItem@plt",
        "slot_mp_subscript",
        "slot_mp_ass_subscript",
        "resize",
        "reserve",
        "dict_hashes",
        "get_index",
        "keys_nentries",
        "dict_iter",
        "DICT_NEXT_VERSION",
        "_PyDict_ClearFreeList",
        "_PyDict_DebugMallocStats",
        "_PyDict_Fini",
        "free_keys_object",
        "compute_hash",
        "usable_fraction",
        "dict_entry_hash",
        "_PyDict_CheckConsistency",
        "index_size",
        "bsr",
        "usable_fraction",
        "capacity_from_usable",
        "dict_indices",
        "key_is_interned",
        "new_keys_object",
        "free_keys_object",
        "new_dict",
        "PyDict_New",
        "dict_entry_hash",
        "perturb_hash",
        "find_locked",
        "find",
        "pydict_get",
        "value_for_key_locked",
        "value_for_key_retry",
        "value_for_entry",
        "prepare_insert",
        "dict_hashes",
        "insert_index",
        "get_index",
        "keys_nentries",
        "entry_at",
        "next_entry",
        "prev_entry",
        "find_or_prepare_insert",
        "find_first_non_full",
        "insert",
        "prepare_insert",
        "pydict_get_slow_blah",
        "pydict_get",
        "_PyDict_HasOnlyStringKeys",
        "_PyDict_MaybeUntrack",
        "resize",
        "reserve",
        "_PyDict_NewPresizedWithType",
        "_PyDict_NewPresized",
        "PyDict_GetItem",
        "_PyDict_GetItem_KnownHash",
        "PyDict_GetItemWithError",
        "PyDict_GetItemWithError2_slow",
        "PyDict_GetItemWithError2",
        "vm_try_load",
        "vm_load_global",
        "_PyDict_GetItemIdWithError",
        "_PyDict_GetItemStringWithError",
        "assign",
        "finish_erase",
        "erase",
        "PyDict_SetItem",
        "_PyDict_SetItem_KnownHash",
        "PyDict_DelItem",
        "_PyDict_DelItem_KnownHash",
        "_PyDict_DelItemIf",
        "PyDict_Clear",
        "_PyDict_Next",
        "PyDict_Next",
        "_PyDict_Pop_KnownHash",
        "_PyDict_Pop",
        "_PyDict_FromKeys",
        "dict_dealloc",
        "dict_repr",
        "dict_length",
        "dict_lookup_missing",
        "dict_subscript_slow",
        "dict_subscript",
        "dict_ass_sub",
        "read_entry",
        "dict_keys",
        "dict_values",
        "dict_items",
        "dict_fromkeys_impl",
        "dict_update_arg",
        "dict_update_common",
        "dict_update",
        "PyDict_MergeFromSeq2",
        "dict_merge_dict",
        "dict_merge",
        "PyDict_Update",
        "PyDict_Merge",
        "_PyDict_MergeEx",
        "dict_copy",
        "PyDict_Copy",
        "PyDict_Size",
        "PyDict_Keys",
        "PyDict_Values",
        "PyDict_Items",
        "dict_equal",
        "dict_richcompare",
        "dict___contains__",
        "dict_get_impl",
        "_PyDict_SetDefault",
        "PyDict_SetDefault",
        "dict_setdefault_impl",
        "dict_clear",
        "dict_pop_impl",
        "dict_popitem_impl",
        "dict_traverse",
        "dict_tp_clear",
        "dictiter_new",
        "_PyDict_SizeOf",
        "_PyDict_KeysSize",
        "dict_sizeof",
        "dict_or",
        "dict_ior",
        "dictkeys_new",
        "dictitems_new",
        "dictvalues_new",
        "PyDict_Contains",
        "_PyDict_Contains",
        "dict_new",
        "dict_init",
        "dict_vectorcall",
        "dict_iter",
        "_PyDict_GetItemId",
        "PyDict_GetItemString",
        "_PyDict_SetItemId",
        "PyDict_SetItemString",
        "_PyDict_DelItemId",
        "PyDict_DelItemString",
        "dictiterobject",
        "dictiter_new",
        "dictiter_dealloc",
        "dictiter_traverse",
        "dictiter_len",
        "dictiter_reduce",
        "dictiter_iternextkey",
        "dictiter_iternextvalue",
        "dictiter_iternextitem",
        "dictreviter_iternext",
        "dict___reversed___impl",
        "dictiter_reduce",
        "dictview_dealloc",
        "dictview_traverse",
        "dictview_len",
        "_PyDictView_New",
        "all_contained_in",
        "dictview_richcompare",
        "dictview_repr",
        "dictkeys_iter",
        "dictkeys_contains",
        "dictviews_to_set",
        "dictviews_sub",
        "dictitems_contains",
        "_PyDictView_Intersect",
        "dictviews_or",
        "dictviews_xor",
        "dictviews_isdisjoint",
        "dictkeys_reversed",
        "dictkeys_new",
        "dictkeys_reversed",
        "dictitems_iter",
        "dictitems_contains",
        "dictitems_reversed",
        "dictitems_new",
        "dictitems_reversed",
        "dictvalues_iter",
        "dictvalues_reversed",
        "dictvalues_new",
        "dictvalues_reversed",
        "initialize_dict",
        "PyObject_GenericGetDict",
        "_PyObjectDict_SetItem",

        # 3.13
        "PyDict_LOG_MINSIZE",
        "PyDict_MINSIZE",
        "ASSERT_DICT_LOCKED",
        "load_keys_nentries",
        "set_keys",
        "set_values",
        "split_keys_entry_added",
        "split_keys_entry_added",
        "set_keys",
        "set_values",
        "load_keys_nentries",
        "PERTURB_SHIFT",
        "dictresize",
        "dict_iter",
        "setitem_lock_held",
        "dict_setdefault_ref_lock_held",
        "_PyObject_InlineValuesConsistencyCheck",
        "unicode_get_hash",
        "_PyDict_DebugMallocStats",
        "free_keys_object",
        "dictkeys_incref",
        "dictkeys_decref",
        "dictkeys_get_index",
        "if",
        "dictkeys_set_index",
        "if",
        "calculate_log2_keysize",
        "estimate_log2_keysize",
        "Py_EMPTY_KEYS",
        "get_index_from_order",
        "dump_entries",
        "_PyDict_CheckConsistency",
        "new_keys_object",
        "if",
        "free_keys_object",
        "values_size_from_count",
        "new_values",
        "free_values",
        "new_dict",
        "new_dict_with_shared_keys",
        "clone_combined_dict_keys",
        "PyDict_New",
        "lookdict_index",
        "do_lookup",
        "compare_unicode_generic",
        "unicodekeys_lookup_generic",
        "compare_unicode_unicode",
        "unicodekeys_lookup_unicode",
        "compare_generic",
        "dictkeys_generic_lookup",
        "_PyDictKeys_StringLookup",
        "unicodekeys_lookup_unicode_threadsafe",
        "_Py_dict_lookup",
        "ensure_shared_on_read",
        "ensure_shared_on_resize",
        "compare_unicode_generic_threadsafe",
        "unicodekeys_lookup_generic_threadsafe",
        "compare_unicode_unicode_threadsafe",
        "unicodekeys_lookup_unicode_threadsafe",
        "compare_generic_threadsafe",
        "dictkeys_generic_lookup_threadsafe",
        "_Py_dict_lookup_threadsafe",
        "_Py_dict_lookup_threadsafe",
        "_PyDict_HasOnlyStringKeys",
        "_PyDict_MaybeUntrack",
        "is_unusable_slot",
        "find_empty_slot",
        "insertion_resize",
        "insert_combined_dict",
        "insert_split_key",
        "insert_split_value",
        "insertdict",
        "insert_to_emptydict",
        "build_indices_generic",
        "build_indices_unicode",
        "dictresize",
        "dict_new_presized",
        "_PyDict_NewPresized",
        "_PyDict_FromItems",
        "dict_getitem",
        "PyDict_GetItem",
        "_PyDict_LookupIndex",
        "_PyDict_GetItem_KnownHash",
        "_PyDict_GetItemRef_KnownHash_LockHeld",
        "_PyDict_GetItemRef_KnownHash",
        "PyDict_GetItemRef",
        "_PyDict_GetItemRef_Unicode_LockHeld",
        "PyDict_GetItemWithError",
        "_PyDict_GetItemWithError",
        "_PyDict_GetItemIdWithError",
        "_PyDict_GetItemStringWithError",
        "_PyDict_LoadGlobal",
        "setitem_take2_lock_held",
        "_PyDict_SetItem_Take2",
        "PyDict_SetItem",
        "setitem_lock_held",
        "_PyDict_SetItem_KnownHash_LockHeld",
        "_PyDict_SetItem_KnownHash",
        "delete_index_from_values",
        "delitem_common",
        "PyDict_DelItem",
        "delitem_knownhash_lock_held",
        "_PyDict_DelItem_KnownHash",
        "delitemif_lock_held",
        "_PyDict_DelItemIf",
        "clear_lock_held",
        "PyDict_Clear",
        "_PyDict_Next",
        "PyDict_Next",
        "_PyDict_Pop_KnownHash",
        "pop_lock_held",
        "PyDict_Pop",
        "PyDict_PopString",
        "_PyDict_Pop",
        "dict_dict_fromkeys",
        "dict_set_fromkeys",
        "_PyDict_FromKeys",
        "dict_dealloc",
        "dict_repr_lock_held",
        "dict_repr",
        "dict_length",
        "dict_subscript",
        "dict_ass_sub",
        "keys_lock_held",
        "PyDict_Keys",
        "values_lock_held",
        "PyDict_Values",
        "items_lock_held",
        "PyDict_Items",
        "dict_fromkeys_impl",
        "dict_update_arg",
        "dict_update_common",
        "dict_update",
        "merge_from_seq2_lock_held",
        "PyDict_MergeFromSeq2",
        "dict_dict_merge",
        "dict_merge",
        "PyDict_Update",
        "PyDict_Merge",
        "_PyDict_MergeEx",
        "dict_copy_impl",
        "copy_values",
        "copy_lock_held",
        "PyDict_Copy",
        "PyDict_Size",
        "dict_equal_lock_held",
        "dict_equal",
        "dict_richcompare",
        "dict___contains__",
        "dict_get_impl",
        "dict_setdefault_ref_lock_held",
        "PyDict_SetDefaultRef",
        "PyDict_SetDefault",
        "dict_setdefault_impl",
        "dict_clear_impl",
        "dict_pop_impl",
        "dict_popitem_impl",
        "dict_traverse",
        "dict_tp_clear",
        "dictiter_new",
        "sizeof_lock_held",
        "_PyDict_SizeOf",
        "_PyDict_KeysSize",
        "dict___sizeof___impl",
        "dict_or",
        "dict_ior",
        "PyDict_Contains",
        "PyDict_ContainsString",
        "_PyDict_Contains_KnownHash",
        "_PyDict_ContainsId",
        "dict_new",
        "dict_init",
        "dict_vectorcall",
        "dict_iter",
        "PyDict_GetItemString",
        "PyDict_GetItemStringRef",
        "_PyDict_SetItemId",
        "PyDict_SetItemString",
        "_PyDict_DelItemId",
        "PyDict_DelItemString",
        "dictiterobject",
        "dictiter_new",
        "dictiter_dealloc",
        "dictiter_traverse",
        "dictiter_len",
        "dictiter_reduce",
        "dictiter_iternext_threadsafe",
        "dictiter_iternextkey_lock_held",
        "dictiter_iternextkey",
        "dictiter_iternextvalue_lock_held",
        "dictiter_iternextvalue",
        "dictiter_iternextitem_lock_held",
        "acquire_key_value",
        "dictiter_iternext_threadsafe",
        "has_unique_reference",
        "acquire_iter_result",
        "dictiter_iternextitem",
        "dictreviter_iter_lock_held",
        "dictreviter_iternext",
        "dict___reversed___impl",
        "dictiter_reduce",
        "dictview_dealloc",
        "dictview_traverse",
        "dictview_len",
        "_PyDictView_New",
        "dictview_mapping",
        "all_contained_in",
        "dictview_richcompare",
        "dictview_repr",
        "dictkeys_iter",
        "dictkeys_contains",
        "dictviews_to_set",
        "dictviews_sub",
        "dictitems_contains",
        "_PyDictView_Intersect",
        "dictviews_or",
        "dictitems_xor_lock_held",
        "dictitems_xor",
        "dictviews_xor",
        "dictviews_isdisjoint",
        "dictkeys_reversed",
        "dict_keys_impl",
        "dictkeys_reversed",
        "dictitems_iter",
        "dictitems_contains",
        "dictitems_reversed",
        "dict_items_impl",
        "dictitems_reversed",
        "dictvalues_iter",
        "dictvalues_reversed",
        "dict_values_impl",
        "dictvalues_reversed",
        "_PyDict_NewKeysForClass",
        "_PyObject_InitInlineValues",
        "make_dict_from_instance_attributes",
        "_PyObject_MaterializeManagedDict_LockHeld",
        "_PyObject_MaterializeManagedDict",
        "_PyDict_SetItem_LockHeld",
        "store_instance_attr_lock_held",
        "store_instance_attr_dict",
        "_PyObject_StoreInstanceAttribute",
        "_PyObject_ManagedDictValidityCheck",
        "_PyObject_TryGetInstanceAttribute",
        "_PyObject_IsInstanceDictEmpty",
        "PyObject_VisitManagedDict",
        "set_dict_inline_values",
        "_PyObject_SetManagedDict",
        "PyObject_ClearManagedDict",
        "_PyDict_DetachFromObject",
        "ensure_managed_dict",
        "ensure_nonmanaged_dict",
        "PyObject_GenericGetDict",
        "_PyObjectDict_SetItem",
        "_PyDictKeys_DecRef",
        "_PyDictKeys_GetVersionForCurrentState",
        "validate_watcher_id",
        "PyDict_Watch",
        "PyDict_Unwatch",
        "PyDict_AddWatcher",
        "PyDict_ClearWatcher",
        "dict_event_name",
        "_PyDict_SendEvent",
        "_PyObject_InlineValuesConsistencyCheck",
    },

    py_mutex={
        "_PyMutex_unlock_slow",
        "_PyMutex_lock_slow",
        "_PyMutex_unlock_slow@plt",
        "_PyMutex_lock_slow@plt",
        # from kernel dso
        "do_futex",
        "futex_wait",
        "futex_wait_queue",
        "futex_wake",
        "futex_q_lock",
        "get_futex_key",
        "futex_unqueue",
        "__futex_unqueue",
        "futex_wake_mark",
        "__x64_sys_futex",
        "try_to_wake_up",
        "native_write_msr",
        "_raw_spin_lock",
        "_raw_spin_unlock",
        "raw_spin_rq_unlock",
        "raw_spin_rq_lock_nested",
        "__raw_spin_lock_irqsave",
        "_raw_spin_unlock_irqrestore",
        "__rcu_read_lock",
        "__rcu_read_unlock",
        "lock_vma_under_rcu",
        "pick_next_task_fair",
        # PyMutex frequently reads the system clock
        "clock_gettime",
        "clock_gettime@plt",
        "update_rq_clock",

        # 3.13
        "mutex_entry",
        "_Py_yield",
        "_PyMutex_LockTimed",
        "mutex_unpark",
        "_PyMutex_TryUnlock",
        "raw_mutex_entry",
        "_PyRawMutex_LockSlow",
        "_PyRawMutex_UnlockSlow",
        "_PyEvent_IsSet",
        "_PyEvent_Notify",
        "PyEvent_Wait",
        "PyEvent_WaitTimed",
        "unlock_once",
        "_PyOnceFlag_CallOnceSlow",
        "recursive_mutex_is_owned_by",
        "_PyRecursiveMutex_IsLockedByCurrentThread",
        "_PyRecursiveMutex_Lock",
        "_PyRecursiveMutex_Unlock",
        "_Py_WRITE_LOCKED",
        "_PyRWMutex_READER_SHIFT",
        "_Py_RWMUTEX_MAX_READERS",
        "rwmutex_set_parked_and_wait",
        "rwmutex_reader_count",
        "_PyRWMutex_RLock",
        "_PyRWMutex_RUnlock",
        "_PyRWMutex_Lock",
        "_PyRWMutex_Unlock",
        "_PySeqLock_LockWrite",
        "_PySeqLock_AbandonWrite",
        "_PySeqLock_UnlockWrite",
        "_PySeqLock_BeginRead",
        "_PySeqLock_EndRead",
        "_PySeqLock_AfterFork",
        "PyMutex_Lock",
        "PyMutex_Unlock",
        "_PyCriticalSection_BeginSlow",
        "_PyCriticalSection2_BeginSlow",
        "untag_critical_section",
        "_PyCriticalSection_SuspendAll",
        "_PyCriticalSection_Resume",
        "PyCriticalSection_Begin",
        "PyCriticalSection_End",
        "PyCriticalSection2_Begin",
        "PyCriticalSection2_End",
    },

    scheduler={
        "__schedule",
        "schedule",
        # "perf_event_context_sched_out",  # maybe not?
        # "__perf_event_task_sched_out",
        # "__perf_event_task_sched_in",
        "native_sched_clock",
        "sched_clock",
        "sched_clock_cpu",
        "sched_clock_noinstr",
    },

)