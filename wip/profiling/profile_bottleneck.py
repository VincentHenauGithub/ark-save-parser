"""
Profile to find where time is actually spent in the API operations.
"""
import cProfile
import pstats
from pathlib import Path
from io import StringIO
import logging

# Suppress logging
logging.disable(logging.ERROR)

from arkparse import AsaSave
from arkparse.api import StructureApi

def main():
    print("Loading save...")
    save = AsaSave(Path(r"tests/test_data/set_1/Astraeos_WP/Astraeos_WP.ark"))
    
    print("Creating API...")
    sapi = StructureApi(save)
    
    print("Profiling get_all_with_inventory...")
    profiler = cProfile.Profile()
    profiler.enable()
    result = sapi.get_all_with_inventory()
    profiler.disable()
    
    print(f"Structures found: {len(result)}")
    print()
    print("=" * 80)
    print("TOP 40 BY TOTAL TIME (where time is actually spent):")
    print("=" * 80)
    
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('tottime')
    ps.print_stats(40)
    print(s.getvalue())

if __name__ == "__main__":
    main()
