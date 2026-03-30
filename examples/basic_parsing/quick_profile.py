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
from arkparse.api import StructureApi, DinoApi, EquipmentApi
from arkparse.classes import Classes


def benchmark_functions(sapi: StructureApi, dapi: DinoApi, eapi: EquipmentApi):
    """Run the benchmark functions."""
    
    # 1 - Get structures with inventory
    structures_with_inv = sapi.get_all_with_inventory()
    print(f"Found {len(structures_with_inv)} structures with inventory")

    # 2 - Get all dinos
    all_dinos = dapi.get_all()
    print(f"Found {len(all_dinos)} dinos")

    # 3 - Get all equipment types
    all_equipment = {}
    all_equipment.update(eapi.get_all(EquipmentApi.Classes.WEAPON))
    all_equipment.update(eapi.get_all(EquipmentApi.Classes.ARMOR))
    all_equipment.update(eapi.get_all(EquipmentApi.Classes.SADDLE))
    all_equipment.update(eapi.get_all(EquipmentApi.Classes.SHIELD))
    print(f"Found {len(all_equipment)} equipment items")


def profile_parsing():
    """Profile the main parsing operations."""
    
    # Load save file
    save = AsaSave(Path(r"C:\Data\personal\software\ark-save-parser\tests\test_data\set_1\Astraeos_WP\Astraeos_WP.ark"))
    
    # Create APIs
    structure_api = StructureApi(save)
    dino_api = DinoApi(save)
    equipment_api = EquipmentApi(save)
    
    # Run the benchmarked functions
    benchmark_functions(structure_api, dino_api, equipment_api)

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    
    profile_parsing()
    
    profiler.disable()
    
    # Print stats
    print("\n" + "=" * 80)
    print("TOP 50 FUNCTIONS BY CUMULATIVE TIME")
    print("=" * 80)
    
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(50)
    print(s.getvalue())
    
    print("\n" + "=" * 80)
    print("TOP 50 FUNCTIONS BY TOTAL TIME (excluding subcalls)")
    print("=" * 80)
    
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('tottime')
    ps.print_stats(50)
    print(s.getvalue())
