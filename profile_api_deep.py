"""Deep profiling: trace where threads spend time during API parallel parsing."""
import time
import threading
import functools
from collections import defaultdict

# Monkey-patch to trace lock contention and SQLite calls
_lock_stats = defaultdict(lambda: {"count": 0, "wait_time": 0.0, "hold_time": 0.0})
_call_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})
_stats_lock = threading.Lock()

class TracedLock:
    """Wrapper around a lock to measure contention."""
    def __init__(self, real_lock, name):
        self._real = real_lock
        self._name = name
        self._hold_start = threading.local()

    def acquire(self, *args, **kwargs):
        t0 = time.perf_counter()
        result = self._real.acquire(*args, **kwargs)
        t1 = time.perf_counter()
        self._hold_start.t = t1
        with _stats_lock:
            _lock_stats[self._name]["count"] += 1
            _lock_stats[self._name]["wait_time"] += (t1 - t0)
        return result

    def release(self, *args, **kwargs):
        t1 = time.perf_counter()
        hold = t1 - getattr(self._hold_start, 't', t1)
        with _stats_lock:
            _lock_stats[self._name]["hold_time"] += hold
        return self._real.release(*args, **kwargs)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()


def trace_lock(obj, attr_name, stat_name):
    """Replace a lock attribute on obj with a traced wrapper."""
    real_lock = getattr(obj, attr_name)
    setattr(obj, attr_name, TracedLock(real_lock, stat_name))


def trace_method(obj, method_name, stat_name):
    """Wrap a method to measure total call time and count."""
    original = getattr(obj, method_name)

    @functools.wraps(original)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = original(*args, **kwargs)
        t1 = time.perf_counter()
        with _stats_lock:
            _call_stats[stat_name]["count"] += 1
            _call_stats[stat_name]["total_time"] += (t1 - t0)
        return result

    setattr(obj, method_name, wrapper)


def main():
    from arkparse import AsaSave
    from arkparse.api import StructureApi, DinoApi

    from pathlib import Path
    SAVE_PATH = Path("examples/basic_parsing/Ragnarok_WP.ark")

    print("Loading save...")
    t0 = time.perf_counter()
    save = AsaSave(SAVE_PATH, read_only=True)
    print(f"  Save loaded in {time.perf_counter() - t0:.2f}s\n")

    sc = save.save_connection

    # Instrument the lock
    trace_lock(sc, "_db_lock", "db_lock")

    # Instrument key methods
    trace_method(sc, "is_in_db", "is_in_db")
    trace_method(sc, "get_game_object_by_id", "get_game_object_by_id")
    trace_method(sc, "get_game_obj_binary", "get_game_obj_binary")
    trace_method(sc, "get_class_of_uuid", "get_class_of_uuid")
    trace_method(sc, "cache_all_classes", "cache_all_classes")

    # ---- STRUCTURE API (with inventory) ----
    for workers in [1, 4]:
        print(f"=== StructureApi bypass_inventory=False, workers={workers} ===")
        sc.parsed_objects.clear()
        sc._class_cache.clear()
        _lock_stats.clear()
        _call_stats.clear()

        api = StructureApi(save)
        t0 = time.perf_counter()
        structs = api.get_all(bypass_inventory=False, max_workers=workers)
        elapsed = time.perf_counter() - t0

        print(f"  Total: {elapsed:.2f}s  |  Structures: {len(structs)}")
        print(f"\n  Lock stats:")
        for name, stats in sorted(_lock_stats.items()):
            print(f"    {name}: {stats['count']} acquisitions, "
                  f"wait={stats['wait_time']:.3f}s, hold={stats['hold_time']:.3f}s")
        print(f"\n  Method call stats:")
        for name, stats in sorted(_call_stats.items(), key=lambda x: -x[1]["total_time"]):
            avg = stats["total_time"] / stats["count"] if stats["count"] else 0
            print(f"    {name}: {stats['count']} calls, "
                  f"total={stats['total_time']:.3f}s, avg={avg*1000:.3f}ms")
        print()

    # ---- DINO API ----
    for workers in [1, 4]:
        print(f"=== DinoApi workers={workers} ===")
        sc.parsed_objects.clear()
        sc._class_cache.clear()
        _lock_stats.clear()
        _call_stats.clear()

        api = DinoApi(save)
        t0 = time.perf_counter()
        dinos = api.get_all(max_workers=workers)
        elapsed = time.perf_counter() - t0

        print(f"  Total: {elapsed:.2f}s  |  Dinos: {len(dinos)}")
        print(f"\n  Lock stats:")
        for name, stats in sorted(_lock_stats.items()):
            print(f"    {name}: {stats['count']} acquisitions, "
                  f"wait={stats['wait_time']:.3f}s, hold={stats['hold_time']:.3f}s")
        print(f"\n  Method call stats:")
        for name, stats in sorted(_call_stats.items(), key=lambda x: -x[1]["total_time"]):
            avg = stats["total_time"] / stats["count"] if stats["count"] else 0
            print(f"    {name}: {stats['count']} calls, "
                  f"total={stats['total_time']:.3f}s, avg={avg*1000:.3f}ms")
        print()


if __name__ == "__main__":
    main()
