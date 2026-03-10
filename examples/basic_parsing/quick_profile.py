"""
Quick performance profiling using cProfile - no custom instrumentation.
"""
import cProfile
import pstats
from pathlib import Path
from io import StringIO

# Suppress arkparse verbose logging
import logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.disable(logging.ERROR)

from arkparse import AsaSave
from arkparse.api import StructureApi
from arkparse.classes import Classes

def profile_parsing():
    """Profile the main parsing operations."""
    
    # Load save file
    save = AsaSave(Path(r".\Aberration_WP.ark"))
    
    # Create structure API and get objects
    structure_api = StructureApi(save)
    all_objects = structure_api.get_all_objects()
    print(f"Found {len(all_objects)} structure objects")
    
    # Get structures with inventory  
    structures_with_inv = structure_api.get_all_with_inventory()
    print(f"Found {len(structures_with_inv)} structures with inventory")
    
    # Process inventories
    element_bp = Classes.resources.Basic.element
    total_element = 0
    for structure in structures_with_inv.values():
        if not structure.owner or not structure.owner.tribe_id:
            continue
        element_stacks = structure.inventory.get_items_of_class(element_bp)
        for element in element_stacks.values():
            total_element += element.quantity
    
    print(f"Total element found: {total_element:,}")

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    
    profile_parsing()
    
    profiler.disable()
    
    # Print stats
    print("\n" + "=" * 80)
    print("TOP 40 FUNCTIONS BY CUMULATIVE TIME")
    print("=" * 80)
    
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(40)
    print(s.getvalue())
    
    print("\n" + "=" * 80)
    print("TOP 40 FUNCTIONS BY TOTAL TIME (excluding subcalls)")
    print("=" * 80)
    
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('tottime')
    ps.print_stats(40)
    print(s.getvalue())
