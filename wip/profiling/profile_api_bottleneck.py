"""
Profile where time is spent in DinoApi.get_all() to understand parallelization limits.
"""
import time
import sys
import cProfile
import pstats
from io import StringIO
from pathlib import Path

def check_gil_status():
    if hasattr(sys, '_is_gil_enabled'):
        return not sys._is_gil_enabled()
    return False

print(f"Python: {sys.version}")
print(f"GIL disabled: {check_gil_status()}")

save_file = Path(r"C:\Users\Vincent\Downloads\Astraeos_WP\Astraeos_WP.ark")
if not save_file.exists():
    save_file = Path("examples/basic_parsing/Ragnarok_WP.ark")

from arkparse import AsaSave
from arkparse.api import DinoApi
from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.object_model.dinos.dino import Dino

print(f"\nLoading save: {save_file}")
save = AsaSave(save_file)

# Get all game objects first
dapi = DinoApi(save)
objects = dapi.get_all_objects()
print(f"Found {len(objects)} dino-related objects")

# Separate dinos from cryopods
dino_objs = []
for key, obj in objects.items():
    if "Dinos/" in obj.blueprint and "_Character_" in obj.blueprint:
        is_tamed = obj.get_property_value("TamedTimeStamp") is not None
        dino_objs.append((key, obj, is_tamed))

print(f"Found {len(dino_objs)} actual dinos to parse")

# Profile single dino construction
print("\n" + "="*60)
print("Profiling single TamedDino construction (100 samples)")
print("="*60)

# Take 100 tamed dinos
tamed_samples = [(k, o) for k, o, is_tamed in dino_objs if is_tamed][:100]

profiler = cProfile.Profile()
profiler.enable()

for key, obj in tamed_samples:
    dino = TamedDino(obj.uuid, save=save)

profiler.disable()

# Print top 20 time consumers
stats_stream = StringIO()
stats = pstats.Stats(profiler, stream=stats_stream)
stats.strip_dirs()
stats.sort_stats('cumulative')
stats.print_stats(30)
print(stats_stream.getvalue())

# Now let's time individual operations
print("\n" + "="*60)
print("Timing individual operations (1000 iterations)")
print("="*60)

sample_obj = tamed_samples[0][1]
sample_uuid = sample_obj.uuid

# Time property lookups
iterations = 1000

start = time.perf_counter()
for _ in range(iterations):
    val = sample_obj.get_property_value("TamedTimeStamp")
property_time = time.perf_counter() - start
print(f"get_property_value: {property_time*1000:.2f}ms total, {property_time/iterations*1000000:.2f}us per call")

start = time.perf_counter()
for _ in range(iterations):
    val = sample_obj.get_property_value("bIsBaby", False)
property_default_time = time.perf_counter() - start
print(f"get_property_value (with default): {property_default_time*1000:.2f}ms total, {property_default_time/iterations*1000000:.2f}us per call")

# Time save.get_game_object_by_id
start = time.perf_counter()
for _ in range(iterations):
    obj = save.get_game_object_by_id(sample_uuid)
get_obj_time = time.perf_counter() - start
print(f"save.get_game_object_by_id: {get_obj_time*1000:.2f}ms total, {get_obj_time/iterations*1000000:.2f}us per call")

# Time save.is_in_db
start = time.perf_counter()
for _ in range(iterations):
    val = save.is_in_db(sample_uuid)
is_in_db_time = time.perf_counter() - start
print(f"save.is_in_db: {is_in_db_time*1000:.2f}ms total, {is_in_db_time/iterations*1000000:.2f}us per call")

# Time full TamedDino construction
print("\n" + "="*60)
print("Full dino construction timing")
print("="*60)

times = []
for key, obj in tamed_samples[:20]:
    start = time.perf_counter()
    dino = TamedDino(obj.uuid, save=save)
    elapsed = time.perf_counter() - start
    times.append(elapsed)

avg_time = sum(times) / len(times)
print(f"Average TamedDino construction: {avg_time*1000:.2f}ms")
print(f"Estimated time for {len(tamed_samples)} dinos: {avg_time * len(tamed_samples):.2f}s")

# Check if there's any thread-local or locking overhead
print("\n" + "="*60)
print("Checking for locks/threading overhead")
print("="*60)

# Check if AsaSave has any locks
import inspect
print(f"AsaSave class attributes: {[a for a in dir(save) if not a.startswith('_') and not callable(getattr(save, a, None))]}")

# Check save_connection
if hasattr(save, 'save_connection'):
    sc = save.save_connection
    lock_attrs = [a for a in dir(sc) if 'lock' in a.lower()]
    print(f"SaveConnection lock-related attributes: {lock_attrs}")
    
    # Check if there's a db_lock
    if hasattr(sc, 'db_lock'):
        print(f"db_lock type: {type(sc.db_lock)}")
