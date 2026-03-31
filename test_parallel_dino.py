"""
Test parallel object model creation with pre-cached objects.
"""
import time
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

def check_gil_status():
    if hasattr(sys, '_is_gil_enabled'):
        return not sys._is_gil_enabled()
    return False

print(f"Python: {sys.version}")
print(f"GIL disabled: {check_gil_status()}")

# Use smaller save file for faster testing
save_file = Path("examples/basic_parsing/Ragnarok_WP.ark")
if not save_file.exists():
    save_file = Path(r"C:\Users\Vincent\Downloads\Astraeos_WP\Astraeos_WP.ark")

from arkparse import AsaSave
from arkparse.api import DinoApi
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.object_model.dinos.dino import Dino

print(f"\nLoading save: {save_file}")
save = AsaSave(save_file)

# Get all game objects first (this caches them)
dapi = DinoApi(save)
objects = dapi.get_all_objects()
print(f"Found {len(objects)} dino-related objects")

# Get tamed dino objects
tamed_items = []
for key, obj in objects.items():
    if "Dinos/" in obj.blueprint and "_Character_" in obj.blueprint:
        if obj.get_property_value("TamedTimeStamp") is not None:
            is_baby = obj.get_property_value("bIsBaby", False)
            tamed_items.append((key, obj, is_baby))

print(f"Found {len(tamed_items)} tamed dinos to test")

# Test sequential vs parallel TamedDino construction
print("\n" + "="*60)
print("Testing object model construction speed")
print("="*60)

# Use first 5000 tamed dinos for testing
test_items = tamed_items[:5000]
print(f"Testing with {len(test_items)} dinos")

# Sequential test
print("\nSequential (1 worker)...", end=" ", flush=True)
start = time.perf_counter()
seq_results = []
for key, obj, is_baby in test_items:
    dino = TamedDino(obj.uuid, save=save)
    seq_results.append(dino)
seq_time = time.perf_counter() - start
print(f"{seq_time:.3f}s ({len(test_items)/seq_time:.0f} dinos/sec)")

# Parallel test with 4 workers
print("Parallel (4 workers)...", end=" ", flush=True)

def create_dino(item):
    key, obj, is_baby = item
    return TamedDino(obj.uuid, save=save)

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as executor:
    par_results = list(executor.map(create_dino, test_items))
par_time_4 = time.perf_counter() - start
print(f"{par_time_4:.3f}s ({len(test_items)/par_time_4:.0f} dinos/sec)")

# Parallel test with 8 workers
print("Parallel (8 workers)...", end=" ", flush=True)
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as executor:
    par_results = list(executor.map(create_dino, test_items))
par_time_8 = time.perf_counter() - start
print(f"{par_time_8:.3f}s ({len(test_items)/par_time_8:.0f} dinos/sec)")

print(f"\nSpeedup 4 workers: {seq_time/par_time_4:.2f}x")
print(f"Speedup 8 workers: {seq_time/par_time_8:.2f}x")

# Now let's check if there are ANY locks being hit
print("\n" + "="*60)
print("Checking for remaining lock contention")
print("="*60)

# Check if any methods we call have locks
sc = save.save_connection
print(f"db_lock type: {type(sc._db_lock)}")

# Try to see if we're hitting the lock during construction
lock_acquisitions = [0]
original_acquire = sc._db_lock.acquire

def traced_acquire(*args, **kwargs):
    lock_acquisitions[0] += 1
    return original_acquire(*args, **kwargs)

sc._db_lock.acquire = traced_acquire

# Create some dinos
test_items_small = test_items[:100]
for key, obj, is_baby in test_items_small:
    dino = TamedDino(obj.uuid, save=save)

print(f"Lock acquisitions for 100 dinos: {lock_acquisitions[0]}")
