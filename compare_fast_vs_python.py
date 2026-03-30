"""
Comparison script for fast (Rust) vs pure Python parser implementations.

Run this script with and without arkparse_fast to compare:
    
    # With fast parser:
    .\\.venv_fast\\Scripts\\Activate.ps1; python compare_fast_vs_python.py
    
    # Without fast parser (pure Python):
    .\\.venv_no_fast\\Scripts\\Activate.ps1; python compare_fast_vs_python.py
"""

import time
import struct
import sys
from pathlib import Path

# Check if fast parser is available
try:
    from arkparse_fast import FastBinaryReader, wildcard_decompress as fast_wildcard_decompress
    FAST_AVAILABLE = True
    print("=" * 70)
    print("MODE: FAST (Rust) parser enabled")
    print("=" * 70)
except ImportError:
    FAST_AVAILABLE = False
    print("=" * 70)
    print("MODE: Pure Python parser (arkparse_fast NOT installed)")
    print("=" * 70)

from arkparse.parsing._base_value_parser import BaseValueParser
from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.parsing._fast_shim import is_fast_available, HybridBinaryReader


def generate_test_data(n_strings: int = 1000) -> bytes:
    """Generate realistic test data mimicking ARK save format."""
    import random
    data = bytearray()
    
    for _ in range(n_strings):
        # Add some uint32s
        data.extend(struct.pack('<I', random.randint(0, 2**32 - 1)))
        data.extend(struct.pack('<I', random.randint(0, 2**32 - 1)))
        
        # Add a float
        data.extend(struct.pack('<f', random.uniform(-1000, 1000)))
        
        # Add a string (ARK format: length-prefixed)
        s = f"TestString_{random.randint(0, 9999)}"
        encoded = s.encode('ascii') + b'\x00'
        data.extend(struct.pack('<i', len(encoded)))
        data.extend(encoded)
        
        # Add some more integers
        data.extend(struct.pack('<i', random.randint(-1000, 1000)))
        data.extend(struct.pack('<Q', random.randint(0, 2**64 - 1)))
    
    return bytes(data)


def test_basic_reads():
    """Test basic read operations and verify correctness."""
    print("\n--- Test 1: Basic Read Operations ---")
    
    # Create test data
    test_data = (
        struct.pack('<i', -12345) +      # int32
        struct.pack('<I', 4294967295) +  # uint32
        struct.pack('<H', 65535) +       # uint16
        struct.pack('<Q', 2**64 - 1) +   # uint64
        struct.pack('<f', 3.14159) +     # float
        struct.pack('<d', 2.71828182845) + # double
        struct.pack('<h', -32768) +      # short (int16)
        bytes([255]) +                   # byte
        struct.pack('<i', 5) + b'test\x00'  # string "test"
    )
    
    results = {}
    
    # Test with BaseValueParser (Python)
    py_reader = BaseValueParser(test_data, None)
    py_results = {
        'int': py_reader.read_int(),
        'uint32': py_reader.read_uint32(),
        'uint16': py_reader.read_uint16(),
        'uint64': py_reader.read_uint64(),
        'float': py_reader.read_float(),
        'double': py_reader.read_double(),
        'short': py_reader.read_short(),
        'byte': py_reader.read_byte(),
        'string': py_reader.read_string(),
    }
    results['Python'] = py_results
    
    # Test with FastBinaryReader (Rust) if available
    if FAST_AVAILABLE:
        rust_reader = FastBinaryReader(test_data, None)
        rust_results = {
            'int': rust_reader.read_int(),
            'uint32': rust_reader.read_uint32(),
            'uint16': rust_reader.read_uint16(),
            'uint64': rust_reader.read_uint64(),
            'float': rust_reader.read_float(),
            'double': rust_reader.read_double(),
            'short': rust_reader.read_short(),
            'byte': rust_reader.read_byte(),
            'string': rust_reader.read_string(),
        }
        results['Rust'] = rust_results
        
        # Compare results
        all_match = True
        for key in py_results:
            py_val = py_results[key]
            rust_val = rust_results[key]
            match = py_val == rust_val
            if not match:
                # Handle float comparison with tolerance
                if isinstance(py_val, float):
                    match = abs(py_val - rust_val) < 1e-6
            if not match:
                print(f"  MISMATCH {key}: Python={py_val}, Rust={rust_val}")
                all_match = False
        
        if all_match:
            print("  All basic read operations match between Python and Rust!")
        else:
            print("  WARNING: Some values differ!")
    else:
        print("  Python results:", py_results)
    
    return results


def test_string_edge_cases():
    """Test string parsing edge cases."""
    print("\n--- Test 2: String Edge Cases ---")
    
    test_cases = [
        ("Empty string (length=0)", struct.pack('<i', 0)),
        ("ASCII string", struct.pack('<i', 6) + b'hello\x00'),
        ("String with special chars", struct.pack('<i', 10) + b'test\x00\x01\x02\x03\x04\x00'),
    ]
    
    for name, data in test_cases:
        py_reader = BaseValueParser(data, None)
        py_result = py_reader.read_string()
        
        if FAST_AVAILABLE:
            rust_reader = FastBinaryReader(data, None)
            rust_result = rust_reader.read_string()
            match = py_result == rust_result
            status = "MATCH" if match else "DIFFER"
            print(f"  {name}: {status}")
            if not match:
                print(f"    Python: {repr(py_result)}")
                print(f"    Rust:   {repr(rust_result)}")
        else:
            print(f"  {name}: Python={repr(py_result)}")


def test_utf16_strings():
    """Test UTF-16 string handling."""
    print("\n--- Test 3: UTF-16 String Handling ---")
    
    # Create UTF-16 test string
    test_str = "Tëst™"
    utf16_data = test_str.encode('utf-16-le') + b'\x00\x00'
    # Negative length indicates UTF-16
    length = -(len(test_str) + 1)
    data = struct.pack('<i', length) + utf16_data
    
    py_reader = BaseValueParser(data, None)
    py_result = py_reader.read_string()
    print(f"  Python UTF-16 result: {repr(py_result)}")
    
    if FAST_AVAILABLE:
        rust_reader = FastBinaryReader(data, None)
        rust_result = rust_reader.read_string()
        print(f"  Rust UTF-16 result:   {repr(rust_result)}")
        if py_result == rust_result:
            print("  UTF-16 strings MATCH!")
        else:
            print("  WARNING: UTF-16 strings DIFFER!")


def test_uuid_formatting():
    """Test UUID string formatting."""
    print("\n--- Test 4: UUID Formatting ---")
    
    # Create a known UUID bytes
    uuid_bytes = bytes([
        0x01, 0x23, 0x45, 0x67,  # first 4 bytes
        0x89, 0xAB,              # bytes 4-5
        0xCD, 0xEF,              # bytes 6-7
        0x01, 0x23,              # bytes 8-9
        0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF  # bytes 10-15
    ])
    
    py_reader = BaseValueParser(uuid_bytes, None)
    py_uuid = py_reader.read_uuid_as_string()
    print(f"  Python UUID: {py_uuid}")
    
    if FAST_AVAILABLE:
        rust_reader = FastBinaryReader(uuid_bytes, None)
        rust_uuid = rust_reader.read_uuid_as_string()
        print(f"  Rust UUID:   {rust_uuid}")
        if py_uuid.lower() == rust_uuid.lower():
            print("  UUIDs MATCH (case-insensitive)!")
        else:
            print("  WARNING: UUIDs DIFFER!")


def test_wildcard_decompress():
    """Test wildcard decompression algorithm."""
    print("\n--- Test 5: Wildcard Decompression ---")
    
    # Generate test compressed data
    test_cases = [
        ("Normal bytes", bytes([0x01, 0x02, 0x03, 0x04, 0x05])),
        ("Zero padding (0xF3)", bytes([0x01, 0xF3, 0x02])),  # Insert 3 zeros
        ("Zero padding (0xF5)", bytes([0x01, 0xF5, 0x02])),  # Insert 5 zeros
        ("Escape 0xF0", bytes([0xF0, 0xF0])),  # Escaped 0xF0 -> outputs 0xF0
        ("Switch mode", bytes([0xF1, 0x12])),  # Switch produces 0xF1 and 0xF2
        ("Mixed data", bytes([0x01, 0x02, 0xF3, 0x04, 0xF0, 0xF0, 0x05])),
    ]
    
    for name, compressed in test_cases:
        py_result = ArkBinaryParser._wildcard_decompress_python(compressed)
        
        if FAST_AVAILABLE:
            rust_result = fast_wildcard_decompress(compressed)
            match = py_result == rust_result
            status = "MATCH" if match else "DIFFER"
            print(f"  {name}: {status}")
            if not match:
                print(f"    Input:  {compressed.hex()}")
                print(f"    Python: {py_result.hex()}")
                print(f"    Rust:   {rust_result.hex()}")
        else:
            print(f"  {name}: Python decompress OK (len={len(py_result)})")


def test_performance():
    """Benchmark performance comparison."""
    print("\n--- Test 6: Performance Benchmark ---")
    
    # Generate test data
    data = generate_test_data(n_strings=1000)
    n_iterations = 1000
    
    print(f"  Test data size: {len(data):,} bytes")
    print(f"  Iterations: {n_iterations:,}")
    
    # Benchmark Python reader
    print("\n  Benchmarking Python reader...")
    start = time.perf_counter()
    for _ in range(n_iterations):
        reader = BaseValueParser(data, None)
        reader.position = 0
        while reader.position + 50 < len(data):
            reader.read_uint32()
            reader.read_uint32()
            reader.read_float()
            reader.read_string()
            reader.read_int()
            reader.read_uint64()
    python_time = time.perf_counter() - start
    print(f"    Python time: {python_time:.3f}s")
    
    # Benchmark Rust reader if available
    if FAST_AVAILABLE:
        print("\n  Benchmarking Rust reader...")
        start = time.perf_counter()
        for _ in range(n_iterations):
            reader = FastBinaryReader(data, None)
            reader.position = 0
            while reader.position + 50 < len(data):
                reader.read_uint32()
                reader.read_uint32()
                reader.read_float()
                reader.read_string()
                reader.read_int()
                reader.read_uint64()
        rust_time = time.perf_counter() - start
        print(f"    Rust time:   {rust_time:.3f}s")
        print(f"    Speedup:     {python_time / rust_time:.1f}x")
    
    # Benchmark wildcard decompress
    print("\n  Benchmarking wildcard_decompress...")
    compressed = bytes([
        0x01, 0x02, 0x03, 0xF3, 0x04, 0x05, 0xF0, 0xF0, 0x06, 0x07,
    ] * 10000)
    
    start = time.perf_counter()
    for _ in range(100):
        ArkBinaryParser._wildcard_decompress_python(compressed)
    python_decomp_time = time.perf_counter() - start
    print(f"    Python decompress: {python_decomp_time:.3f}s")
    
    if FAST_AVAILABLE:
        start = time.perf_counter()
        for _ in range(100):
            fast_wildcard_decompress(compressed)
        rust_decomp_time = time.perf_counter() - start
        print(f"    Rust decompress:   {rust_decomp_time:.3f}s")
        print(f"    Speedup:           {python_decomp_time / rust_decomp_time:.1f}x")


def test_hybrid_reader():
    """Test the HybridBinaryReader that auto-selects implementation."""
    print("\n--- Test 7: HybridBinaryReader Integration ---")
    
    print(f"  is_fast_available(): {is_fast_available()}")
    
    test_data = struct.pack('<I', 12345) + struct.pack('<i', 5) + b'test\x00'
    
    reader = HybridBinaryReader(test_data, None)
    print(f"  Using fast reader: {reader._is_fast}")
    
    uint_val = reader.read_uint32()
    str_val = reader.read_string()
    print(f"  Read uint32: {uint_val}")
    print(f"  Read string: {str_val}")
    
    if uint_val == 12345 and str_val == "test":
        print("  HybridBinaryReader works correctly!")
    else:
        print("  WARNING: HybridBinaryReader returned unexpected values!")


def test_error_handling():
    """Test error handling for edge cases."""
    print("\n--- Test 8: Error Handling ---")
    
    # Test buffer underflow
    small_data = bytes([0x01, 0x02])
    
    print("  Testing buffer underflow on read_uint32...")
    py_reader = BaseValueParser(small_data, None)
    try:
        py_reader.read_uint32()
        print("    Python: No error raised (unexpected)")
    except (IndexError, ValueError) as e:
        print(f"    Python: Correctly raised {type(e).__name__}")
    
    if FAST_AVAILABLE:
        rust_reader = FastBinaryReader(small_data, None)
        try:
            rust_reader.read_uint32()
            print("    Rust: No error raised (unexpected)")
        except Exception as e:
            print(f"    Rust: Correctly raised {type(e).__name__}")


def test_real_save_file():
    """Test with real ARK save file if available."""
    print("\n--- Test 9: Real Save File Test ---")
    
    # Look for a test save file
    save_paths = [
        # Path("tests/test_data/set_1/Astraeos_WP/Astraeos_WP.ark"),
        # Path("examples/basic_parsing/Ragnarok_WP.ark"),
        Path("examples/basic_parsing/LostColony_WP.ark"),
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
        Path("examples/basic_parsing/LostColony_WP.ark"),
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
    
    test_basic_reads()
    test_string_edge_cases()
    test_utf16_strings()
    test_uuid_formatting()
    test_wildcard_decompress()
    test_performance()
    test_hybrid_reader()
    test_error_handling()
    test_real_save_file()
    test_api_benchmarks()
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
