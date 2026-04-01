"""
Comparison script for fast (Rust) vs pure Python parser implementations.

Run this script with and without ArkparseFast to compare:
    
    # With fast parser:
    .\\.venv_fast\\Scripts\\Activate.ps1; python compare_fast_vs_python.py
    
    # Without fast parser (pure Python):
    .\\.venv_no_fast\\Scripts\\Activate.ps1; python compare_fast_vs_python.py
"""

import time
import sys
from pathlib import Path

from arkparse.parsing._base_value_parser import BaseValueParser
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.parsing._fast_shim import is_fast_available, HybridBinaryReader

# Check if fast parser is available
try:
    from ArkparseFast import FastBinaryReader, wildcard_decompress as fast_wildcard_decompress
    FAST_AVAILABLE = True
    print("=" * 70)
    print("MODE: FAST (Rust) parser enabled")
    print("=" * 70)
except ImportError:
    FAST_AVAILABLE = False
    print("=" * 70)
    print("MODE: Pure Python parser (ArkparseFast NOT installed)")
    print("=" * 70)

def test_real_save_file():
    """Test with real ARK save file if available."""
    print("\n--- Test 9: Real Save File Test ---")
    
    # Look for a test save file
    save_paths = [
        # Path("tests/test_data/set_1/Astraeos_WP/Astraeos_WP.ark"),
        # Path("examples/basic_parsing/Ragnarok_WP.ark"),
        # Path("examples/basic_parsing/LostColony_WP.ark"),
        Path(r"C:\Users\Vincent\Downloads\Astraeos_WP\Astraeos_WP.ark"),
        # Path("Ragnarok_WP.ark"),
    ]
    
    save_file = None
    for path in save_paths:
        if path.exists():
            save_file = path
            break
    
    if save_file is None:
        print("  No save file found, skipping real file test")
        return
    
    print(f"  Testing with: {save_file}")
    
    try:
        from arkparse import AsaSave
        
        start = time.perf_counter()
        save = AsaSave(save_file)
        load_time = time.perf_counter() - start
        
        print(f"  Save loaded in {load_time:.2f}s")
        print(f"  Using fast parser: {is_fast_available()}")
        
    except Exception as e:
        print(f"  Error loading save: {e}")


def test_api_benchmarks():
    """
    Benchmark API operations and save results for cross-mode comparison.
    Results are saved to JSON for verification between fast/non-fast runs.
    """
    import json
    import hashlib
    
    print("\n--- Test 10: API Benchmarks (StructureApi, DinoApi, EquipmentApi) ---")
    
    # Look for a test save file
    save_paths = [
        # Path("tests/test_data/set_1/Astraeos_WP/Astraeos_WP.ark"),
        # Path("examples/basic_parsing/Ragnarok_WP.ark"),
        # Path("examples/basic_parsing/LostColony_WP.ark"),
        Path(r"C:\Users\Vincent\Downloads\Astraeos_WP\Astraeos_WP.ark"),
        # Path("Ragnarok_WP.ark"),
    ]
    
    save_file = None
    for path in save_paths:
        if path.exists():
            save_file = path
            break
    
    if save_file is None:
        print("  No save file found, skipping API benchmarks")
        return
    
    print(f"  Using save file: {save_file}")
    print(f"  Fast parser: {is_fast_available()}")
    print()
    
    try:
        from arkparse import AsaSave
        from arkparse.api import StructureApi, DinoApi, EquipmentApi
        
        # Load save file
        print("  Loading save file...")
        start = time.perf_counter()
        save = AsaSave(save_file)
        load_time = time.perf_counter() - start
        print(f"  Save loaded in {load_time:.2f}s")
        
        # Create APIs
        sapi = StructureApi(save)
        dapi = DinoApi(save)
        eapi = EquipmentApi(save)
        
        results = {
            'mode': 'fast' if is_fast_available() else 'python',
            'save_file': str(save_file),
        }
        
        # Benchmark 1: StructureApi.get_all_with_inventory()
        print("\n  [1] StructureApi.get_all_with_inventory()")
        start = time.perf_counter()
        structures_with_inv = sapi.get_all_with_inventory()
        struct_time = time.perf_counter() - start
        
        # Extract comparable data
        struct_uuids = sorted([str(uuid) for uuid in structures_with_inv.keys()])
        struct_hash = hashlib.md5('|'.join(struct_uuids).encode()).hexdigest()
        
        results['structures'] = {
            'count': len(structures_with_inv),
            'time': struct_time,
            'uuid_hash': struct_hash,
        }
        print(f"      Found: {len(structures_with_inv)} structures with inventory")
        print(f"      Time:  {struct_time:.3f}s")
        print(f"      Hash:  {struct_hash[:16]}...")
        
        # Benchmark 2: DinoApi.get_all()
        print("\n  [2] DinoApi.get_all()")
        start = time.perf_counter()
        all_dinos = dapi.get_all()
        dino_time = time.perf_counter() - start
        
        # Extract comparable data
        dino_uuids = sorted([str(uuid) for uuid in all_dinos.keys()])
        dino_hash = hashlib.md5('|'.join(dino_uuids).encode()).hexdigest()
        
        # Get some dino stats for comparison
        dino_classes = {}
        for dino in all_dinos.values():
            cls_name = dino.blueprint if hasattr(dino, 'blueprint') else str(type(dino).__name__)
            dino_classes[cls_name] = dino_classes.get(cls_name, 0) + 1
        
        results['dinos'] = {
            'count': len(all_dinos),
            'time': dino_time,
            'uuid_hash': dino_hash,
            'class_counts': dict(sorted(dino_classes.items())[:10]),  # Top 10
        }
        print(f"      Found: {len(all_dinos)} dinos")
        print(f"      Time:  {dino_time:.3f}s")
        print(f"      Hash:  {dino_hash[:16]}...")
        
        # Benchmark 3: EquipmentApi.get_all() for all equipment types
        print("\n  [3] EquipmentApi.get_all() (all types)")
        start = time.perf_counter()
        # Get all equipment types
        all_equipment = {}
        all_equipment.update(eapi.get_all(EquipmentApi.Classes.WEAPON))
        all_equipment.update(eapi.get_all(EquipmentApi.Classes.ARMOR))
        all_equipment.update(eapi.get_all(EquipmentApi.Classes.SADDLE))
        all_equipment.update(eapi.get_all(EquipmentApi.Classes.SHIELD))
        equip_time = time.perf_counter() - start
        
        # Extract comparable data
        equip_uuids = sorted([str(uuid) for uuid in all_equipment.keys()])
        equip_hash = hashlib.md5('|'.join(equip_uuids).encode()).hexdigest()
        
        results['equipment'] = {
            'count': len(all_equipment),
            'time': equip_time,
            'uuid_hash': equip_hash,
        }
        print(f"      Found: {len(all_equipment)} equipment items")
        print(f"      Time:  {equip_time:.3f}s")
        print(f"      Hash:  {equip_hash[:16]}...")
        
        # Total time
        total_api_time = struct_time + dino_time + equip_time
        results['total_api_time'] = total_api_time
        print(f"\n  Total API time: {total_api_time:.3f}s")
        
        # Save results for comparison
        results_file = Path(f"api_benchmark_results_{results['mode']}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n  Results saved to: {results_file}")
        
        # Try to load and compare with other mode's results
        other_mode = 'python' if is_fast_available() else 'fast'
        other_file = Path(f"api_benchmark_results_{other_mode}.json")
        
        if other_file.exists():
            print(f"\n  --- Comparing with {other_mode} mode results ---")
            with open(other_file) as f:
                other_results = json.load(f)
            
            # Compare outputs
            all_match = True
            comparisons = [
                ('structures', 'Structures with inventory'),
                ('dinos', 'Dinos'),
                ('equipment', 'Equipment'),
            ]
            
            for key, name in comparisons:
                current = results[key]
                other = other_results[key]
                
                count_match = current['count'] == other['count']
                hash_match = current['uuid_hash'] == other['uuid_hash']
                
                if count_match and hash_match:
                    speedup = other['time'] / current['time'] if current['time'] > 0 else 0
                    print(f"    {name}: MATCH (count={current['count']}, speedup={speedup:.2f}x)")
                else:
                    all_match = False
                    print(f"    {name}: MISMATCH!")
                    print(f"      Current: count={current['count']}, hash={current['uuid_hash'][:16]}")
                    print(f"      Other:   count={other['count']}, hash={other['uuid_hash'][:16]}")
            
            if all_match:
                total_speedup = other_results['total_api_time'] / results['total_api_time']
                print(f"\n  All API outputs MATCH between fast and Python modes!")
                print(f"  Overall API speedup: {total_speedup:.2f}x")
            else:
                print(f"\n  WARNING: Some API outputs differ between modes!")
        else:
            print(f"\n  Run with {other_mode} mode to compare results:")
            print(f"    .\\.venv_{other_mode}\\Scripts\\Activate.ps1; python compare_fast_vs_python.py")
        
    except Exception as e:
        import traceback
        print(f"  Error during API benchmarks: {e}")
        traceback.print_exc()


def main():
    """Run all comparison tests."""
    print()
    print("Fast parser available:", FAST_AVAILABLE)
    print("Python version:", sys.version.split()[0])
    print()
    
    test_api_benchmarks()
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
