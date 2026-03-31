"""
Benchmark: Parallel parsing with free-threaded Python (no GIL)
Compare sequential vs parallel get_game_objects performance.
"""
import sys
import time
from pathlib import Path
from arkparse import AsaSave
from arkparse.saves.save_connection import _PARALLEL_ENABLED

SAVE_PATH = Path(r"D:\ARK servers\Ascended\arkparse\examples\basic_parsing\Ragnarok_WP.ark")

print(f"Python: {sys.version}")
print(f"GIL enabled: {sys._is_gil_enabled()}")
print(f"Parallel parsing auto-enabled: {_PARALLEL_ENABLED}")
print()

def benchmark_sequential():
    """Parse using sequential get_game_objects (force GIL mode)."""
    from arkparse.saves import save_connection
    original = save_connection._PARALLEL_ENABLED
    save_connection._PARALLEL_ENABLED = False
    
    save = AsaSave(SAVE_PATH)
    start = time.perf_counter()
    results = save.save_connection.get_game_objects()
    elapsed = time.perf_counter() - start
    
    save_connection._PARALLEL_ENABLED = original
    save.close()
    return elapsed, len(results)

def benchmark_parallel():
    """Parse using auto-parallel get_game_objects (GIL disabled mode)."""
    save = AsaSave(SAVE_PATH)
    
    start = time.perf_counter()
    results = save.save_connection.get_game_objects()
    elapsed = time.perf_counter() - start
    
    save.close()
    return elapsed, len(results)
    
if __name__ == "__main__":
    import os
    num_cpus = os.cpu_count()
    print(f"CPU cores: {num_cpus}")
    print()
    
    # Warmup
    print("Warming up...")
    save = AsaSave(SAVE_PATH)
    save.close()
    
    print("=" * 60)
    print(f"BENCHMARK: Sequential vs Parallel get_game_objects")
    print(f"Parallel uses 3 workers automatically when GIL disabled")
    print("=" * 60)
    print()
    
    # Sequential benchmark
    print("Running sequential benchmark...")
    seq_time, seq_count = benchmark_sequential()
    print(f"  Sequential: {seq_time:.2f}s ({seq_count:,} objects)")
    print()
    
    # Parallel benchmark (auto 3 workers)
    print("Running parallel benchmark (auto 3 workers)...")
    par_time, par_count = benchmark_parallel()
    speedup = seq_time / par_time
    print(f"  Parallel: {par_time:.2f}s ({par_count:,} objects) - {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    print()
    print("=" * 60)
    
    print("=" * 60)
