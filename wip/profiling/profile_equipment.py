"""cProfile individual equipment constructors to find the bottleneck."""
import cProfile
import pstats
import io
import time
import sys
from pathlib import Path

save_path = Path(r"C:\Users\Vincent\Downloads\Astraeos_WP\Astraeos_WP.ark")

from arkparse import AsaSave
from arkparse.api import EquipmentApi

print(f"Python {sys.version.split()[0]}")

print("Loading save...")
save = AsaSave(save_path)
print("Save loaded.")

eapi = EquipmentApi(save)

# First, get all objects to warm the cache
print("Warming cache with get_all_objects...")
t0 = time.perf_counter()
all_objs = eapi.get_all_objects()
print(f"  {len(all_objs)} objects cached in {time.perf_counter()-t0:.2f}s")

# Profile each equipment type
for name, cls in [("WEAPON", EquipmentApi.Classes.WEAPON),
                  ("ARMOR", EquipmentApi.Classes.ARMOR),
                  ("SADDLE", EquipmentApi.Classes.SADDLE),
                  ("SHIELD", EquipmentApi.Classes.SHIELD)]:
    # Reset parsed_objects to force re-parsing
    eapi.parsed_objects = {}
    
    pr = cProfile.Profile()
    pr.enable()
    items = eapi.get_all(cls, max_workers=1)  # Single thread for clean profiling
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(25)
    
    print(f"\n{'='*80}")
    print(f"  {name}: {len(items)} items")
    print(f"{'='*80}")
    print(s.getvalue())
