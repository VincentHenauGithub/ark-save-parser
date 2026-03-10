"""
arkparse_fast — High-performance binary parser for ARK save files.

Provides a drop-in replacement for BaseValueParser with 10-50x speedups.

Usage:
    from arkparse_fast import FastBinaryReader, wildcard_decompress
    
    reader = FastBinaryReader(data, name_table=["Name1", "Name2", ...])
    value = reader.read_uint32()
"""

from ._native import (
    FastBinaryReader,
    wildcard_decompress,
    find_all_patterns,
    contains_any_pattern,
    read_name_id_at,
    batch_extract_class_ids,
    filter_objects_by_patterns,
)

__all__ = [
    "FastBinaryReader",
    "wildcard_decompress",
    "find_all_patterns",
    "contains_any_pattern",
    "read_name_id_at",
    "batch_extract_class_ids",
    "filter_objects_by_patterns",
]
__version__ = "0.1.0"
