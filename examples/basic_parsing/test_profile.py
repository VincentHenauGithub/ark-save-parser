"""
Performance profiling script for arkparse structure parsing.
Identifies bottlenecks by timing each major operation with deep instrumentation.
"""

from time import perf_counter
from pathlib import Path
from collections import defaultdict

# Install deep profiling hooks BEFORE importing arkparse
from deep_profiler import profiler, install_hooks
install_hooks()

# Now import arkparse (hooks will instrument the imports)
from arkparse import AsaSave
from arkparse.api import StructureApi
from arkparse.classes import Classes

# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Load save file
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 70)
print("PHASE 1: Loading save file")
print("=" * 70)

with profiler.time("TOTAL: Load save file"):
    save = AsaSave(Path(r".\Aberration_WP.ark"))

print(f"Save loaded. Map: {save.save_context.map_name}")
print(f"Total names in name table: {len(save.save_context.names)}")

# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: Create structure API and get objects
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PHASE 2: Get all structure objects")
print("=" * 70)

with profiler.time("TOTAL: Create StructureApi"):
    structure_api = StructureApi(save)

with profiler.time("TOTAL: Get all structure objects"):
    all_objects = structure_api.get_all_objects()

print(f"Found {len(all_objects)} structure objects")

# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Get structures with inventory
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PHASE 3: Get structures with inventory")
print("=" * 70)

with profiler.time("TOTAL: Get all with inventory"):
    structures_with_inv = structure_api.get_all_with_inventory()

print(f"Found {len(structures_with_inv)} structures with inventory")

# ─────────────────────────────────────────────────────────────────────────────
# Phase 4: Process inventories
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("PHASE 4: Processing inventories")
print("=" * 70)

element_bp = Classes.resources.Basic.element
element_per_tribe = defaultdict(int)
parsed = 0

with profiler.time("TOTAL: Process all inventories"):
    for structure in structures_with_inv.values():
        if not structure.owner or not structure.owner.tribe_id:
            continue
        
        with profiler.time("Inventory.get_items_of_class"):
            element_stacks = structure.inventory.get_items_of_class(element_bp)
        
        for element in element_stacks.values():
            element_per_tribe[structure.owner.tribe_id] += element.quantity
        
        parsed += 1
        if parsed % 5000 == 0:
            print(f"Processed {parsed} inventories...")

print(f"Processed {parsed} structures with valid owners")

# ─────────────────────────────────────────────────────────────────────────────
# Performance Report
# ─────────────────────────────────────────────────────────────────────────────

profiler.report(min_total_ms=1.0, top_n=40)

# ─────────────────────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("Element per tribe:")
print("=" * 70)
for tribe_id, amount in sorted(element_per_tribe.items()):
    print(f"Tribe {tribe_id}: {amount:,}")
