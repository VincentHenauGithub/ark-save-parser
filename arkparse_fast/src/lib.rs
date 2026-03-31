//! arkparse_fast — High-performance binary parser for ARK save files
//!
//! This crate provides a drop-in replacement for the Python BaseValueParser,
//! offering 10-50x speedups on large save files.

use byteorder::{LittleEndian, ReadBytesExt};
use pyo3::exceptions::{PyIndexError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList};
use std::io::Cursor;

/// Fast binary reader for ARK save files.
///
/// Mirrors the Python `BaseValueParser` interface for seamless integration.
#[pyclass]
pub struct FastBinaryReader {
    data: Vec<u8>,
    position: usize,
    name_table: Option<Vec<String>>,
}

#[pymethods]
impl FastBinaryReader {
    #[new]
    #[pyo3(signature = (data, name_table=None))]
    fn new(data: &[u8], name_table: Option<Vec<String>>) -> Self {
        FastBinaryReader {
            data: data.to_vec(),
            position: 0,
            name_table,
        }
    }

    /// Current read position in the buffer.
    #[getter]
    fn position(&self) -> usize {
        self.position
    }

    #[setter]
    fn set_position(&mut self, pos: usize) {
        self.position = pos;
    }

    /// Total size of the buffer.
    fn size(&self) -> usize {
        self.data.len()
    }

    /// Returns True if there are more bytes to read.
    fn has_more(&self) -> bool {
        self.position < self.data.len()
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Primitive reads
    // ─────────────────────────────────────────────────────────────────────────

    /// Read a signed 32-bit integer (little-endian).
    fn read_int(&mut self) -> PyResult<i32> {
        self.ensure_bytes(4)?;
        let mut cursor = Cursor::new(&self.data[self.position..]);
        let val = cursor.read_i32::<LittleEndian>().unwrap();
        self.position += 4;
        Ok(val)
    }

    /// Read an unsigned 32-bit integer (little-endian).
    fn read_uint32(&mut self) -> PyResult<u32> {
        self.ensure_bytes(4)?;
        let mut cursor = Cursor::new(&self.data[self.position..]);
        let val = cursor.read_u32::<LittleEndian>().unwrap();
        self.position += 4;
        Ok(val)
    }

    /// Read an unsigned 16-bit integer (little-endian).
    fn read_uint16(&mut self) -> PyResult<u16> {
        self.ensure_bytes(2)?;
        let mut cursor = Cursor::new(&self.data[self.position..]);
        let val = cursor.read_u16::<LittleEndian>().unwrap();
        self.position += 2;
        Ok(val)
    }

    /// Read an unsigned 64-bit integer (little-endian).
    fn read_uint64(&mut self) -> PyResult<u64> {
        self.ensure_bytes(8)?;
        let mut cursor = Cursor::new(&self.data[self.position..]);
        let val = cursor.read_u64::<LittleEndian>().unwrap();
        self.position += 8;
        Ok(val)
    }

    /// Read a signed 64-bit integer (little-endian).
    fn read_int64(&mut self) -> PyResult<i64> {
        self.ensure_bytes(8)?;
        let mut cursor = Cursor::new(&self.data[self.position..]);
        let val = cursor.read_i64::<LittleEndian>().unwrap();
        self.position += 8;
        Ok(val)
    }

    /// Read a signed 16-bit integer (little-endian).
    fn read_short(&mut self) -> PyResult<i16> {
        self.ensure_bytes(2)?;
        let mut cursor = Cursor::new(&self.data[self.position..]);
        let val = cursor.read_i16::<LittleEndian>().unwrap();
        self.position += 2;
        Ok(val)
    }

    /// Read a single byte.
    fn read_byte(&mut self) -> PyResult<u8> {
        self.ensure_bytes(1)?;
        let val = self.data[self.position];
        self.position += 1;
        Ok(val)
    }

    /// Read a single byte as unsigned (same as read_byte for Rust).
    fn read_unsigned_byte(&mut self) -> PyResult<u8> {
        self.read_byte()
    }

    /// Read a 32-bit float (little-endian).
    fn read_float(&mut self) -> PyResult<f32> {
        self.ensure_bytes(4)?;
        let mut cursor = Cursor::new(&self.data[self.position..]);
        let val = cursor.read_f32::<LittleEndian>().unwrap();
        self.position += 4;
        Ok(val)
    }

    /// Read a 64-bit double (little-endian).
    fn read_double(&mut self) -> PyResult<f64> {
        self.ensure_bytes(8)?;
        let mut cursor = Cursor::new(&self.data[self.position..]);
        let val = cursor.read_f64::<LittleEndian>().unwrap();
        self.position += 8;
        Ok(val)
    }

    /// Read a boolean (1 byte, non-zero = true).
    fn read_boolean(&mut self) -> PyResult<bool> {
        Ok(self.read_byte()? != 0)
    }

    /// Read `count` bytes and return as Python bytes.
    fn read_bytes<'py>(&mut self, py: Python<'py>, count: usize) -> PyResult<Bound<'py, PyBytes>> {
        self.ensure_bytes(count)?;
        let slice = &self.data[self.position..self.position + count];
        self.position += count;
        Ok(PyBytes::new(py, slice))
    }

    /// Skip `count` bytes.
    fn skip_bytes(&mut self, count: usize) {
        self.position += count;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // String reads
    // ─────────────────────────────────────────────────────────────────────────

    /// Read a length-prefixed string (ARK format).
    /// Negative length indicates UTF-16LE encoding.
    fn read_string(&mut self) -> PyResult<Option<String>> {
        let length = self.read_int()?;
        if length == 0 {
            return Ok(None);
        }

        let is_multibyte = length < 0;
        let abs_length = length.unsigned_abs() as usize;

        if is_multibyte {
            // UTF-16LE string
            let byte_count = (abs_length * 2).saturating_sub(2);
            self.ensure_bytes(byte_count + 2)?;
            
            let bytes = &self.data[self.position..self.position + byte_count];
            self.position += byte_count;
            
            // Read null terminator (2 bytes for UTF-16)
            self.position += 2;
            
            // Decode UTF-16LE
            let u16_chars: Vec<u16> = bytes
                .chunks_exact(2)
                .map(|chunk| u16::from_le_bytes([chunk[0], chunk[1]]))
                .collect();
            
            Ok(Some(String::from_utf16_lossy(&u16_chars)))
        } else {
            // ASCII string
            let byte_count = abs_length.saturating_sub(1);
            self.ensure_bytes(byte_count + 1)?;
            
            let bytes = &self.data[self.position..self.position + byte_count];
            self.position += byte_count;
            
            // Read null terminator
            self.position += 1;
            
            Ok(Some(String::from_utf8_lossy(bytes).into_owned()))
        }
    }

    /// Read a name from the name table (or fall back to read_string if no table).
    #[pyo3(signature = (default=None))]
    fn read_name(&mut self, default: Option<String>) -> PyResult<String> {
        if self.name_table.is_none() {
            return self.read_string()?.ok_or_else(|| {
                PyValueError::new_err("Name is None and no default provided")
            });
        }

        let name_id = self.read_uint32()? as usize;
        
        let name = self.name_table
            .as_ref()
            .and_then(|t| t.get(name_id).cloned())
            .or(default)
            .ok_or_else(|| {
                PyValueError::new_err(format!("Name with id {} not found", name_id))
            })?;

        // Read the "always zero" field
        let _ = self.read_int()?;
        
        Ok(name)
    }

    /// Peek at the next int without advancing the position.
    fn peek_int(&mut self) -> PyResult<i32> {
        let pos = self.position;
        let val = self.read_int()?;
        self.position = pos;
        Ok(val)
    }

    /// Peek at the next byte without advancing the position.
    fn peek_byte(&mut self) -> PyResult<u8> {
        let pos = self.position;
        let val = self.read_byte()?;
        self.position = pos;
        Ok(val)
    }

    /// Peek at the next u16 without advancing the position.
    fn peek_u16(&mut self) -> PyResult<u16> {
        let pos = self.position;
        let val = self.read_uint16()?;
        self.position = pos;
        Ok(val)
    }

    /// Read a UUID (16 bytes) and return as string.
    /// Matches Python's UUID(bytes=...) format which treats bytes as big-endian.
    fn read_uuid_as_string(&mut self) -> PyResult<String> {
        self.ensure_bytes(16)?;
        let bytes: [u8; 16] = self.data[self.position..self.position + 16]
            .try_into()
            .unwrap();
        self.position += 16;
        
        // Format as UUID string - use big-endian (network byte order) for first 3 fields
        // to match Python's UUID(bytes=...) behavior per RFC 4122
        Ok(format!(
            "{:02x}{:02x}{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}",
            bytes[0], bytes[1], bytes[2], bytes[3],
            bytes[4], bytes[5],
            bytes[6], bytes[7],
            bytes[8], bytes[9],
            bytes[10], bytes[11], bytes[12], bytes[13], bytes[14], bytes[15]
        ))
    }

    /// Read `count` bytes and return as hex string.
    fn read_bytes_as_hex(&mut self, count: usize) -> PyResult<String> {
        self.ensure_bytes(count)?;
        let slice = &self.data[self.position..self.position + count];
        self.position += count;
        Ok(slice.iter().map(|b| format!("{:02X}", b)).collect::<Vec<_>>().join(" "))
    }

    /// Read an array of strings.
    fn read_strings_array<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        let count = self.read_uint32()? as usize;
        let list = PyList::empty(py);
        for _ in 0..count {
            if let Some(s) = self.read_string()? {
                list.append(s)?;
            }
        }
        Ok(list)
    }

    /// Set the name table for name lookups.
    fn set_name_table(&mut self, names: Vec<String>) {
        self.name_table = Some(names);
    }
}

impl FastBinaryReader {
    fn ensure_bytes(&self, count: usize) -> PyResult<()> {
        if self.position + count > self.data.len() {
            Err(PyIndexError::new_err(format!(
                "Buffer underflow: need {} bytes at position {}, but only {} available",
                count,
                self.position,
                self.data.len() - self.position
            )))
        } else {
            Ok(())
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Wildcard decompression (the custom ARK decompression algorithm)
// ─────────────────────────────────────────────────────────────────────────────

/// Fast implementation of the ARK wildcard decompression algorithm.
#[pyfunction]
fn wildcard_decompress(py: Python<'_>, input: &[u8]) -> PyResult<Py<PyBytes>> {
    #[derive(PartialEq)]
    enum ReadState {
        None,
        Escape,
        Switch,
    }

    let mut output: Vec<u8> = Vec::with_capacity(input.len() * 2);
    let mut fifo: Vec<u8> = Vec::new();
    let mut state = ReadState::None;
    let mut pos = 0;

    while pos < input.len() || !fifo.is_empty() {
        if !fifo.is_empty() {
            output.push(fifo.remove(0));
            continue;
        }

        let byte = input[pos];
        pos += 1;

        if state == ReadState::Switch {
            let return_value = 0xF0 | ((byte & 0xF0) >> 4);
            fifo.push(0xF0 | (byte & 0x0F));
            output.push(return_value);
            state = ReadState::None;
            continue;
        }

        if state == ReadState::None {
            match byte {
                0xF0 => {
                    state = ReadState::Escape;
                    continue;
                }
                0xF1 => {
                    state = ReadState::Switch;
                    continue;
                }
                0xF2..=0xFE => {
                    let byte_count = (byte & 0x0F) as usize;
                    fifo.extend(std::iter::repeat(0).take(byte_count));
                    continue;
                }
                0xFF => {
                    if pos + 2 > input.len() {
                        return Err(PyValueError::new_err(
                            "Unexpected end of stream after 0xFF",
                        ));
                    }
                    let b1 = input[pos];
                    let b2 = input[pos + 1];
                    pos += 2;
                    fifo.extend([0, 0, 0, b1, 0, 0, 0, b2, 0, 0, 0]);
                    continue;
                }
                _ => {}
            }
        }

        state = ReadState::None;
        output.push(byte);
    }

    Ok(PyBytes::new(py, &output).into())
}

// ─────────────────────────────────────────────────────────────────────────────
// Batch operations for high-performance scanning
// ─────────────────────────────────────────────────────────────────────────────

/// Find all occurrences of a pattern in binary data.
/// Returns a list of positions where the pattern was found.
#[pyfunction]
fn find_all_patterns(data: &[u8], pattern: &[u8]) -> Vec<usize> {
    let mut positions = Vec::new();
    let mut pos = 0;
    
    while pos + pattern.len() <= data.len() {
        if let Some(found) = data[pos..].windows(pattern.len()).position(|w| w == pattern) {
            positions.push(pos + found);
            pos += found + 1;
        } else {
            break;
        }
    }
    
    positions
}

/// Check if data contains any of the given patterns.
/// Returns true as soon as any pattern is found (early exit).
#[pyfunction]
fn contains_any_pattern(data: &[u8], patterns: Vec<Vec<u8>>) -> bool {
    for pattern in patterns {
        if data.windows(pattern.len()).any(|w| w == pattern.as_slice()) {
            return true;
        }
    }
    false
}

/// Read a name ID from binary data at the given position.
/// Returns (name_id, new_position).
#[pyfunction]
fn read_name_id_at(data: &[u8], position: usize) -> PyResult<(u32, usize)> {
    if position + 8 > data.len() {
        return Err(PyIndexError::new_err("Buffer underflow reading name ID"));
    }
    
    let name_id = u32::from_le_bytes([
        data[position],
        data[position + 1],
        data[position + 2],
        data[position + 3],
    ]);
    
    // Skip the "always zero" int after the name ID
    Ok((name_id, position + 8))
}

/// Batch read class names from multiple binary objects.
/// Each object is expected to have: name_id (4 bytes) + always_zero (4 bytes) at position 0.
/// Returns list of (name_id, data_index) tuples.
#[pyfunction]
fn batch_extract_class_ids(objects: Vec<Vec<u8>>) -> Vec<(u32, usize)> {
    objects
        .iter()
        .enumerate()
        .filter_map(|(idx, data)| {
            if data.len() >= 8 {
                let name_id = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
                Some((name_id, idx))
            } else {
                None
            }
        })
        .collect()
}

/// Filter objects that contain any of the given byte patterns.
/// Returns indices of objects that match.
#[pyfunction]
fn filter_objects_by_patterns(objects: Vec<Vec<u8>>, patterns: Vec<Vec<u8>>) -> Vec<usize> {
    objects
        .iter()
        .enumerate()
        .filter_map(|(idx, data)| {
            for pattern in &patterns {
                if data.windows(pattern.len()).any(|w| w == pattern.as_slice()) {
                    return Some(idx);
                }
            }
            None
        })
        .collect()
}

/// Python module definition.
#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FastBinaryReader>()?;
    m.add_function(wrap_pyfunction!(wildcard_decompress, m)?)?;
    m.add_function(wrap_pyfunction!(find_all_patterns, m)?)?;
    m.add_function(wrap_pyfunction!(contains_any_pattern, m)?)?;
    m.add_function(wrap_pyfunction!(read_name_id_at, m)?)?;
    m.add_function(wrap_pyfunction!(batch_extract_class_ids, m)?)?;
    m.add_function(wrap_pyfunction!(filter_objects_by_patterns, m)?)?;
    Ok(())
}
