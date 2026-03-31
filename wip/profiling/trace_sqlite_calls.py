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

# Get the save connection for inspection
sc = save.save_connection

# Get all game objects first
dapi = DinoApi(save)
objects = dapi.get_all_objects()
print(f"Found {len(objects)} dino-related objects")

# Check what's in parsed_objects cache
print(f"Objects in parsed_objects cache: {len(sc.parsed_objects)}")

# Pick a tamed dino for testing
sample_obj = None
sample_uuid = None
for key, obj in objects.items():
    if "Dinos/" in obj.blueprint and "_Character_" in obj.blueprint:
        if obj.get_property_value("TamedTimeStamp") is not None:
            sample_obj = obj
            sample_uuid = obj.uuid
            break

print(f"\nSample dino UUID: {sample_uuid}")
print(f"Is sample in parsed_objects? {sample_uuid in sc.parsed_objects}")
print(f"Is sample in all_objects? {sample_uuid in objects}")

# Now let's trace exactly what happens during TamedDino construction
print("\n" + "="*60)
print("Tracing SQLite calls during TamedDino construction")
print("="*60)

# Patch is_in_db to trace calls
original_is_in_db = sc.is_in_db
original_get_game_obj_binary = sc.get_game_obj_binary

call_counts = {'is_in_db_cache_hit': 0, 'is_in_db_sqlite': 0, 'get_game_obj_binary': 0}
sqlite_uuids = []  # Track which UUIDs cause SQLite calls

def traced_is_in_db(obj_uuid):
    if obj_uuid in sc.parsed_objects:
        call_counts['is_in_db_cache_hit'] += 1
        return True
    call_counts['is_in_db_sqlite'] += 1
    sqlite_uuids.append(('is_in_db', obj_uuid))
    return original_is_in_db(obj_uuid)

def traced_get_game_obj_binary(obj_uuid):
    call_counts['get_game_obj_binary'] += 1
    sqlite_uuids.append(('get_game_obj_binary', obj_uuid))
    return original_get_game_obj_binary(obj_uuid)

# Apply patches
sc.is_in_db = traced_is_in_db
sc.get_game_obj_binary = traced_get_game_obj_binary

# Clear the cache for this specific object to test fresh
# if sample_uuid in sc.parsed_objects:
#     del sc.parsed_objects[sample_uuid]
#     print(f"Removed {sample_uuid} from cache for testing")

# Test WITH cache (don't remove)
print(f"Sample UUID still in cache: {sample_uuid in sc.parsed_objects}")

# Create TamedDino
print("\nCreating TamedDino...")
dino = TamedDino(sample_uuid, save=save)
print(f"TamedDino created: {dino}")

print(f"\nCall counts:")
print(f"  is_in_db cache hits: {call_counts['is_in_db_cache_hit']}")
print(f"  is_in_db SQLite calls: {call_counts['is_in_db_sqlite']}")
print(f"  get_game_obj_binary: {call_counts['get_game_obj_binary']}")

print(f"\nUUIDs that caused SQLite calls:")
for op, uuid in sqlite_uuids:
    in_cache = uuid in sc.parsed_objects
    # Try to get info about this object
    obj = sc.parsed_objects.get(uuid)
    bp = obj.blueprint if obj else "NOT IN CACHE"
    print(f"  {op}: {uuid} (blueprint={bp})")

# Now let's check if get_all_objects returns cached objects
print("\n" + "="*60)
print("Checking if get_all_objects returns cached objects")
print("="*60)

# The objects returned by get_all_objects - are they in parsed_objects?
objects_in_cache = sum(1 for uuid in objects if uuid in sc.parsed_objects)
print(f"Objects from get_all_objects in parsed_objects cache: {objects_in_cache}/{len(objects)}")

# What about dapi.all_objects?
if dapi.all_objects:
    all_objects_in_cache = sum(1 for uuid in dapi.all_objects if uuid in sc.parsed_objects)
    print(f"Objects from dapi.all_objects in parsed_objects cache: {all_objects_in_cache}/{len(dapi.all_objects)}")
