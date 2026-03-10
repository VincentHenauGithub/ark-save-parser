# arkparse_fast

High-performance Rust-based binary parser for ARK save files, providing 10-50x speedup over Python.

## Requirements

- **Rust** 1.70+ — [Install Rust](https://rustup.rs/)
- **Python** 3.9+
- **maturin** — `pip install maturin`

## Quick Start

### Development Build (editable install)

```powershell
cd arkparse_fast
maturin develop --release
```

This builds the Rust extension and installs it into your current Python environment.

### Production Build (wheel)

```powershell
cd arkparse_fast
maturin build --release
pip install target/wheels/arkparse_fast-*.whl
```

## Usage

### Direct Usage

```python
from arkparse_fast import FastBinaryReader, wildcard_decompress

# Load binary data
with open("save.ark", "rb") as f:
    data = f.read()

# Create reader with optional name table
reader = FastBinaryReader(data, name_table=["Name1", "Name2"])

# Read primitives
value = reader.read_uint32()
text = reader.read_string()
name = reader.read_name()

# Decompress ARK data
decompressed = wildcard_decompress(compressed_data)
```

### Integration with arkparse

The fast parser is designed as a drop-in replacement for `BaseValueParser`. 
See the shim in `src/arkparse/parsing/_fast_shim.py` for automatic fallback.

## API Reference

### `FastBinaryReader(data: bytes, name_table: list[str] | None = None)`

| Method | Description |
|--------|-------------|
| `read_int()` | Read signed 32-bit integer |
| `read_uint32()` | Read unsigned 32-bit integer |
| `read_uint16()` | Read unsigned 16-bit integer |
| `read_uint64()` | Read unsigned 64-bit integer |
| `read_int64()` | Read signed 64-bit integer |
| `read_short()` | Read signed 16-bit integer |
| `read_byte()` | Read single byte |
| `read_float()` | Read 32-bit float |
| `read_double()` | Read 64-bit double |
| `read_boolean()` | Read boolean (1 byte) |
| `read_bytes(count)` | Read `count` bytes |
| `read_string()` | Read length-prefixed string |
| `read_name(default=None)` | Read name from table |
| `read_uuid_as_string()` | Read 16-byte UUID as string |
| `peek_int()` | Peek at next int |
| `peek_byte()` | Peek at next byte |
| `peek_u16()` | Peek at next u16 |
| `skip_bytes(count)` | Skip `count` bytes |
| `position` | Current read position (property) |
| `size()` | Total buffer size |
| `has_more()` | True if more bytes available |

### `wildcard_decompress(data: bytes) -> bytes`

Decompress ARK's custom wildcard compression format.

## Benchmarks

Typical speedups on large save files:

| Operation | Python | Rust | Speedup |
|-----------|--------|------|---------|
| read_uint32 (1M calls) | ~800ms | ~15ms | **53x** |
| read_string (100K calls) | ~1.2s | ~40ms | **30x** |
| wildcard_decompress | ~2.5s | ~80ms | **31x** |

## Troubleshooting

### "maturin not found"

```powershell
pip install maturin
```

### "Rust compiler not found"

Install Rust from https://rustup.rs/ and restart your terminal.

### Import errors after build

Make sure you're using the same Python environment where you ran `maturin develop`.
