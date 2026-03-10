"""
Shim module that provides automatic fallback between fast (Rust) and pure Python parsers.

Usage in arkparse:
    from arkparse.parsing._fast_shim import get_binary_reader_class
    
    BinaryReader = get_binary_reader_class()
    reader = BinaryReader(data, save_context)
"""

import logging
from typing import List, Tuple

_logger = logging.getLogger(__name__)

# Try to import the fast Rust implementation
_FAST_AVAILABLE = False
_FastBinaryReader = None
_wildcard_decompress_fast = None
_find_all_patterns_fast = None
_contains_any_pattern_fast = None
_batch_extract_class_ids_fast = None
_filter_objects_by_patterns_fast = None

try:
    from arkparse_fast import FastBinaryReader as _FastBinaryReader
    from arkparse_fast import wildcard_decompress as _wildcard_decompress_fast
    from arkparse_fast import find_all_patterns as _find_all_patterns_fast
    from arkparse_fast import contains_any_pattern as _contains_any_pattern_fast
    from arkparse_fast import batch_extract_class_ids as _batch_extract_class_ids_fast
    from arkparse_fast import filter_objects_by_patterns as _filter_objects_by_patterns_fast
    _FAST_AVAILABLE = True
    _logger.debug("arkparse_fast extension loaded — using Rust parser")
except ImportError:
    _logger.debug("arkparse_fast not available — using pure Python parser")


def is_fast_available() -> bool:
    """Check if the fast Rust parser is available."""
    return _FAST_AVAILABLE


def get_fast_binary_reader():
    """
    Get the FastBinaryReader class if available.
    
    Returns:
        FastBinaryReader class or None if not available.
    """
    return _FastBinaryReader


def wildcard_decompress(data: bytes) -> bytes:
    """
    Decompress ARK wildcard-compressed data.
    
    Uses Rust implementation if available, otherwise falls back to Python.
    
    Args:
        data: Compressed bytes
        
    Returns:
        Decompressed bytes
    """
    if _wildcard_decompress_fast is not None:
        return _wildcard_decompress_fast(data)
    
    # Fallback to Python implementation
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser
    return ArkBinaryParser._wildcard_decompress_python(data)


class HybridBinaryReader:
    """
    Hybrid reader that wraps either the fast Rust reader or falls back to Python.
    
    Maintains API compatibility with BaseValueParser while using the faster
    implementation when available.
    """
    
    def __init__(self, data: bytes, save_context=None):
        self.save_context = save_context
        
        if _FAST_AVAILABLE and _FastBinaryReader is not None:
            # Extract name table from save_context if available
            name_table = None
            if save_context and hasattr(save_context, 'get_name_table'):
                name_table = save_context.get_name_table()
            elif save_context and hasattr(save_context, 'name_table'):
                name_table = save_context.name_table
            
            self._reader = _FastBinaryReader(data, name_table)
            self._is_fast = True
        else:
            # Fall back to Python implementation
            from arkparse.parsing._base_value_parser import BaseValueParser
            self._reader = BaseValueParser(data, save_context)
            self._is_fast = False
    
    @property
    def position(self) -> int:
        return self._reader.position
    
    @position.setter
    def position(self, value: int):
        self._reader.position = value
    
    @property
    def byte_buffer(self) -> bytes:
        if self._is_fast:
            raise AttributeError("Direct byte_buffer access not supported with fast reader")
        return self._reader.byte_buffer
    
    def __getattr__(self, name):
        """Delegate all other method calls to the underlying reader."""
        return getattr(self._reader, name)


def get_binary_reader_class():
    """
    Get the appropriate binary reader class.
    
    Returns HybridBinaryReader which automatically uses the fast implementation
    when available.
    """
    return HybridBinaryReader


# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Batch operations with fallbacks
# ─────────────────────────────────────────────────────────────────────────────

def find_all_patterns(data: bytes, pattern: bytes) -> List[int]:
    """
    Find all occurrences of a pattern in binary data.
    
    Note: Python's bytes.find() is already highly optimized (uses SIMD),
    so we always use the Python implementation.
    
    Args:
        data: Binary data to search
        pattern: Pattern to find
        
    Returns:
        List of positions where pattern was found
    """
    # Python's bytes.find is faster than Rust for this - uses SIMD
    positions = []
    pos = 0
    while True:
        pos = data.find(pattern, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    return positions


def contains_any_pattern(data: bytes, patterns: List[bytes]) -> bool:
    """
    Check if data contains any of the given patterns.
    
    Note: Python's `in` operator for bytes is already highly optimized,
    so we always use the Python implementation.
    
    Args:
        data: Binary data to search
        patterns: List of patterns to check
        
    Returns:
        True if any pattern is found
    """
    # Python's `in` operator is faster than Rust - uses optimized C/SIMD
    for pattern in patterns:
        if pattern in data:
            return True
    return False


def batch_extract_class_ids(objects: List[bytes]) -> List[Tuple[int, int]]:
    """
    Extract class name IDs from multiple binary objects.
    
    Args:
        objects: List of binary object data
        
    Returns:
        List of (name_id, object_index) tuples
    """
    if _batch_extract_class_ids_fast is not None:
        return _batch_extract_class_ids_fast(objects)
    
    # Python fallback
    import struct
    results = []
    for idx, data in enumerate(objects):
        if len(data) >= 8:
            name_id = struct.unpack('<I', data[:4])[0]
            results.append((name_id, idx))
    return results


def filter_objects_by_patterns(objects: List[bytes], patterns: List[bytes]) -> List[int]:
    """
    Filter objects that contain any of the given patterns.
    
    Note: Python's `in` operator is highly optimized, so we always use Python.
    
    Args:
        objects: List of binary object data
        patterns: List of byte patterns to match
        
    Returns:
        List of indices of matching objects
    """
    # Python's `in` operator is faster than Rust for pattern matching
    matching = []
    for idx, data in enumerate(objects):
        for pattern in patterns:
            if pattern in data:
                matching.append(idx)
                break
    return matching