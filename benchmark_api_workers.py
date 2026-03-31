"""
Benchmark script to test optimal worker counts for parallel API parsing.

This script tests different worker counts for DinoApi and StructureApi
to find the optimal parallelization settings for free-threaded Python.

Run with Python 3.14t (free-threaded):
    .\.venv314t\Scripts\Activate.ps1; python benchmark_api_workers.py
"""

import time
import sys
import json
import gc
from pathlib import Path
from typing import Dict, List, Tuple
import os


def check_gil_status():
    """Check if GIL is enabled/disabled."""
    if hasattr(sys, '_is_gil_enabled'):
        return not sys._is_gil_enabled()
    return False


def run_benchmark():
    print("=" * 70)
    print("API Worker Count Benchmark")
    print("=" * 70)
    print(f"Python version: {sys.version}")
    print(f"GIL disabled: {check_gil_status()}")
    
    if not check_gil_status():
        print("\nWARNING: GIL is enabled. Parallel parsing will not provide benefits.")
        print("Run with free-threaded Python (3.14t) for meaningful parallel results.")
        print("=" * 70)
    
    # Look for test save file
    save_paths = [
        # Path(r"C:\Users\Vincent\Downloads\Astraeos_WP\Astraeos_WP.ark"),
        # Path("tests/test_data/set_1/Astraeos_WP/Astraeos_WP.ark"),
        Path("examples/basic_parsing/Ragnarok_WP.ark"),
        Path("examples/basic_parsing/LostColony_WP.ark"),
    ]
    
    save_file = None
    for path in save_paths:
        if path.exists():
            save_file = path
            break
    
    if save_file is None:
        print("No save file found for benchmarking!")
        return
    
    print(f"\nUsing save file: {save_file}")
    print()
    
    from arkparse import AsaSave
    from arkparse.api import DinoApi
    
    # Worker counts to test
    worker_counts = [1, 2, 3, 4, 6, 8, 10, 12]
    
    # Number of runs per configuration for averaging
    num_runs = 1
    
    results = {
        'python_version': sys.version,
        'gil_disabled': check_gil_status(),
        'save_file': str(save_file),
        'num_runs': num_runs,
        'dino_api': {},
    }
    
    print("Loading save file...")
    load_start = time.perf_counter()
    save = AsaSave(save_file)
    load_time = time.perf_counter() - load_start
    print(f"Save loaded in {load_time:.2f}s")
    results['save_load_time'] = load_time
    
    # =====================================================
    # Benchmark DinoApi
    # =====================================================
    print("\n" + "=" * 70)
    print("DinoApi Benchmark")
    print("=" * 70)
    
    print("\nWarming up DinoApi...")
    dapi = DinoApi(save)
    warmup_dinos = dapi.get_all(max_workers=1)  # Warm-up run
    baseline_count = len(warmup_dinos)  # Use returned dict size, not cache size
    print(f"Found {baseline_count} dinos")
    
    for workers in worker_counts:
        times = []
        print(f"\nTesting {workers} worker(s)...", end=" ", flush=True)
        
        for run in range(num_runs):
            # Reset caches completely
            dapi.parsed_dinos.clear()
            dapi.parsed_cryopods.clear()
            dapi.all_objects = None  # Also reset the objects cache
            gc.collect()
            
            start = time.perf_counter()
            t0 = time.perf_counter()
            dapi.get_all_objects()  # Force reload of game objects  
            t1 = time.perf_counter()
            dinos = dapi.get_all(max_workers=workers)
            t2 = time.perf_counter()
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            
            print(f"\n  get_all_objects: {t1-t0:.2f}s, get_all: {t2-t1:.2f}s, total: {elapsed:.2f}s")
            
            # Verify result count matches
            if len(dinos) != baseline_count:
                print(f"\nWARNING: Count mismatch! Expected {baseline_count}, got {len(dinos)}")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        results['dino_api'][workers] = {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'times': times,
        }
        
        print(f"avg={avg_time:.3f}s (min={min_time:.3f}, max={max_time:.3f})")
    
    # Find best worker count for dinos
    best_dino_workers = min(results['dino_api'].keys(), 
                           key=lambda w: results['dino_api'][w]['avg_time'])
    baseline_dino_time = results['dino_api'][1]['avg_time']
    best_dino_time = results['dino_api'][best_dino_workers]['avg_time']
    dino_speedup = baseline_dino_time / best_dino_time if best_dino_time > 0 else 0
    
    print(f"\nDinoApi: Best = {best_dino_workers} workers ({dino_speedup:.2f}x speedup)")
    results['dino_api_best'] = {
        'workers': best_dino_workers,
        'speedup': dino_speedup,
    }
    
    # =====================================================
    # Summary
    # =====================================================
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"DinoApi: Best = {best_dino_workers} workers ({dino_speedup:.2f}x speedup)")
    
    # Save results
    mode = 'nogil' if check_gil_status() else 'gil'
    results_file = Path(f"api_workers_benchmark_{mode}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    # Print table
    print("\n" + "-" * 70)
    print("Timing Table (seconds)")
    print("-" * 70)
    print(f"{'Workers':<10} {'DinoApi':<15}")
    print("-" * 70)
    
    for workers in worker_counts:
        dino_t = results['dino_api'][workers]['avg_time']
        print(f"{workers:<10} {dino_t:<15.3f}")
    
    print("-" * 70)
    
    return results


if __name__ == "__main__":
    run_benchmark()
