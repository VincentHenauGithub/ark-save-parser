"""
Benchmark script comparing Python vs Rust parser performance.

Run this after building the Rust extension:
    cd arkparse_fast && maturin develop --release
    python benchmark.py
"""

import time
import struct
import random

# Number of iterations for each benchmark
N_ITERATIONS = 100_000


def generate_test_data(n_strings: int = 1000) -> bytes:
    """Generate realistic test data mimicking ARK save format."""
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


def benchmark_python_reader(data: bytes, n_reads: int):
    """Benchmark pure Python reader."""
    from arkparse.parsing._base_value_parser import BaseValueParser
    
    reader = BaseValueParser(data, None)
    
    start = time.perf_counter()
    for _ in range(n_reads):
        reader.position = 0
        reader.read_uint32()
        reader.read_uint32()
        reader.read_float()
        reader.read_string()
        reader.read_int()
        reader.read_uint64()
    elapsed = time.perf_counter() - start
    
    return elapsed


def benchmark_rust_reader(data: bytes, n_reads: int):
    """Benchmark Rust reader."""
    try:
        from arkparse_fast import FastBinaryReader
    except ImportError:
        print("  [!] arkparse_fast not installed. Run: cd arkparse_fast && maturin develop --release")
        return None
    
    reader = FastBinaryReader(data, None)
    
    start = time.perf_counter()
    for _ in range(n_reads):
        reader.position = 0
        reader.read_uint32()
        reader.read_uint32()
        reader.read_float()
        reader.read_string()
        reader.read_int()
        reader.read_uint64()
    elapsed = time.perf_counter() - start
    
    return elapsed


def benchmark_wildcard_decompress():
    """Benchmark wildcard decompression."""
    # Generate test compressed data (simplified)
    compressed = bytes([
        0x01, 0x02, 0x03,  # Normal bytes
        0xF3,  # Insert 3 zeros
        0x04, 0x05,
        0xF0, 0xF0,  # Escaped 0xF0
        0x06, 0x07,
    ] * 10000)
    
    # Python implementation
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser
    start = time.perf_counter()
    for _ in range(100):
        ArkBinaryParser._wildcard_decompress_python(compressed)
    python_time = time.perf_counter() - start
    
    # Rust implementation
    try:
        from arkparse_fast import wildcard_decompress
        start = time.perf_counter()
        for _ in range(100):
            wildcard_decompress(compressed)
        rust_time = time.perf_counter() - start
    except ImportError:
        rust_time = None
    
    return python_time, rust_time


def benchmark_pattern_matching():
    """Benchmark pattern matching in binary data."""
    # Generate test data with embedded patterns
    data = bytearray()
    patterns = [b'ItemQuantity\x00', b'OwnerInventory\x00', b'MyInventoryComponent\x00']
    
    for i in range(10000):
        data.extend(struct.pack('<I', i))
        if i % 100 == 0:
            data.extend(random.choice(patterns))
        data.extend(b'\x00' * 20)
    
    data = bytes(data)
    n_iter = 1000
    
    # Python implementation
    start = time.perf_counter()
    for _ in range(n_iter):
        for pattern in patterns:
            if pattern in data:
                break
    python_time = time.perf_counter() - start
    
    # Rust implementation
    try:
        from arkparse_fast import contains_any_pattern
        start = time.perf_counter()
        for _ in range(n_iter):
            contains_any_pattern(data, patterns)
        rust_time = time.perf_counter() - start
    except ImportError:
        rust_time = None
    
    return python_time, rust_time


def benchmark_batch_pattern_filter():
    """Benchmark filtering multiple objects by patterns."""
    # Generate 1000 test objects
    patterns = [b'ItemQuantity\x00', b'OwnerInventory\x00']
    objects = []
    
    for i in range(1000):
        obj = bytearray()
        obj.extend(struct.pack('<I', i))
        if i % 10 == 0:  # 10% have the pattern
            obj.extend(random.choice(patterns))
        obj.extend(b'\x00' * 100)
        objects.append(bytes(obj))
    
    n_iter = 100
    
    # Python implementation
    start = time.perf_counter()
    for _ in range(n_iter):
        matching = []
        for idx, data in enumerate(objects):
            for pattern in patterns:
                if pattern in data:
                    matching.append(idx)
                    break
    python_time = time.perf_counter() - start
    
    # Rust implementation
    try:
        from arkparse_fast import filter_objects_by_patterns
        start = time.perf_counter()
        for _ in range(n_iter):
            filter_objects_by_patterns(objects, patterns)
        rust_time = time.perf_counter() - start
    except ImportError:
        rust_time = None
    
    return python_time, rust_time


def main():
    print("=" * 60)
    print("arkparse_fast Benchmark")
    print("=" * 60)
    print()
    
    # Generate test data
    print("Generating test data...")
    data = generate_test_data(n_strings=1000)
    print(f"Test data size: {len(data):,} bytes")
    print()
    
    # Run benchmarks
    n_reads = 10000
    
    print(f"Benchmarking read operations ({n_reads:,} iterations)...")
    print()
    
    print("  Python reader:")
    python_time = benchmark_python_reader(data, n_reads)
    print(f"    Time: {python_time:.3f}s")
    
    print()
    print("  Rust reader:")
    rust_time = benchmark_rust_reader(data, n_reads)
    if rust_time:
        print(f"    Time: {rust_time:.3f}s")
        speedup = python_time / rust_time
        print(f"    Speedup: {speedup:.1f}x")
    
    print()
    print("-" * 60)
    print()
    
    print("Benchmarking wildcard_decompress (100 iterations)...")
    print()
    
    python_decomp, rust_decomp = benchmark_wildcard_decompress()
    print(f"  Python: {python_decomp:.3f}s")
    if rust_decomp:
        print(f"  Rust:   {rust_decomp:.3f}s")
        print(f"  Speedup: {python_decomp / rust_decomp:.1f}x")
    else:
        print("  Rust:   [not available]")
    
    print()
    print("-" * 60)
    print()
    
    print("Benchmarking pattern matching (1000 iterations)...")
    print()
    
    python_pattern, rust_pattern = benchmark_pattern_matching()
    print(f"  Python: {python_pattern:.3f}s")
    if rust_pattern:
        print(f"  Rust:   {rust_pattern:.3f}s")
        print(f"  Speedup: {python_pattern / rust_pattern:.1f}x")
    else:
        print("  Rust:   [not available]")
    
    print()
    print("-" * 60)
    print()
    
    print("Benchmarking batch object filtering (100 iterations, 1000 objects)...")
    print()
    
    python_batch, rust_batch = benchmark_batch_pattern_filter()
    print(f"  Python: {python_batch:.3f}s")
    if rust_batch:
        print(f"  Rust:   {rust_batch:.3f}s")
        print(f"  Speedup: {python_batch / rust_batch:.1f}x")
    else:
        print("  Rust:   [not available]")
    
    print()
    print("=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
