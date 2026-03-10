"""
Deep performance profiler for arkparse internals.

Instruments the core parsing classes to identify exact bottlenecks.
"""

from time import perf_counter
from collections import defaultdict
from functools import wraps
import threading

class DeepProfiler:
    """Thread-safe profiler for deep instrumentation."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.timings = defaultdict(lambda: {"count": 0, "total": 0.0, "min": float('inf'), "max": 0.0})
        self.enabled = True
        self.depth = 0
        self.call_stack = []
        self._initialized = True
    
    def reset(self):
        self.timings.clear()
        self.depth = 0
        self.call_stack = []
    
    def time(self, name):
        """Context manager for timing a block."""
        profiler = self
        
        class TimerContext:
            def __init__(ctx, name):
                ctx.name = name
                ctx.start = None
            
            def __enter__(ctx):
                if not profiler.enabled:
                    return ctx
                ctx.start = perf_counter()
                profiler.depth += 1
                profiler.call_stack.append(name)
                return ctx
            
            def __exit__(ctx, *args):
                if not profiler.enabled or ctx.start is None:
                    return
                elapsed = perf_counter() - ctx.start
                profiler.depth -= 1
                profiler.call_stack.pop()
                
                entry = profiler.timings[name]
                entry["count"] += 1
                entry["total"] += elapsed
                entry["min"] = min(entry["min"], elapsed)
                entry["max"] = max(entry["max"], elapsed)
        
        return TimerContext(name)
    
    def profile_method(self, name=None):
        """Decorator to profile a method."""
        profiler = self
        
        def decorator(func):
            method_name = name or f"{func.__module__}.{func.__qualname__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                with profiler.time(method_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def report(self, min_total_ms=0.1, top_n=50):
        """Print performance report."""
        print("\n" + "=" * 100)
        print("DEEP PERFORMANCE PROFILE")
        print("=" * 100)
        
        # Filter and sort by total time descending
        filtered = {k: v for k, v in self.timings.items() 
                    if v["total"] * 1000 >= min_total_ms}
        
        sorted_timings = sorted(
            filtered.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )[:top_n]
        
        total_root_time = sum(
            t["total"] for name, t in self.timings.items() 
            if not any(name.startswith(other + ".") for other in self.timings.keys())
        )
        
        print(f"\n{'Operation':<55} {'Calls':>10} {'Total(s)':>10} {'Avg(ms)':>10} {'Min(ms)':>10} {'Max(ms)':>10}")
        print("-" * 105)
        
        for name, data in sorted_timings:
            avg_ms = (data["total"] / data["count"] * 1000) if data["count"] > 0 else 0
            min_ms = data["min"] * 1000 if data["min"] != float('inf') else 0
            max_ms = data["max"] * 1000
            
            # Truncate long names
            display_name = name if len(name) <= 55 else "..." + name[-52:]
            
            print(f"{display_name:<55} {data['count']:>10} {data['total']:>10.3f} {avg_ms:>10.3f} {min_ms:>10.3f} {max_ms:>10.3f}")
        
        print("-" * 105)
        print(f"\nShowing top {len(sorted_timings)} operations with >= {min_total_ms}ms total time")


# Global profiler instance
profiler = DeepProfiler()


def install_hooks():
    """Install profiling hooks into arkparse internals."""
    
    # ─────────────────────────────────────────────────────────────────────────
    # Hook: BaseValueParser read methods
    # ─────────────────────────────────────────────────────────────────────────
    from arkparse.parsing._base_value_parser import BaseValueParser
    
    original_read_string = BaseValueParser.read_string
    original_read_name = BaseValueParser.read_name
    original_read_uint32 = BaseValueParser.read_uint32
    original_read_int = BaseValueParser.read_int
    original_read_float = BaseValueParser.read_float
    original_read_double = BaseValueParser.read_double
    original_read_bytes = BaseValueParser.read_bytes
    
    def profiled_read_string(self):
        with profiler.time("BaseValueParser.read_string"):
            return original_read_string(self)
    
    def profiled_read_name(self, default=None, is_peek=False):
        with profiler.time("BaseValueParser.read_name"):
            return original_read_name(self, default, is_peek)
    
    def profiled_read_uint32(self):
        with profiler.time("BaseValueParser.read_uint32"):
            return original_read_uint32(self)
    
    def profiled_read_int(self):
        with profiler.time("BaseValueParser.read_int"):
            return original_read_int(self)
    
    def profiled_read_float(self):
        with profiler.time("BaseValueParser.read_float"):
            return original_read_float(self)
    
    def profiled_read_double(self):
        with profiler.time("BaseValueParser.read_double"):
            return original_read_double(self)
    
    def profiled_read_bytes(self, count):
        with profiler.time("BaseValueParser.read_bytes"):
            return original_read_bytes(self, count)
    
    BaseValueParser.read_string = profiled_read_string
    BaseValueParser.read_name = profiled_read_name
    BaseValueParser.read_uint32 = profiled_read_uint32
    BaseValueParser.read_int = profiled_read_int
    BaseValueParser.read_float = profiled_read_float
    BaseValueParser.read_double = profiled_read_double
    BaseValueParser.read_bytes = profiled_read_bytes
    
    # ─────────────────────────────────────────────────────────────────────────
    # Hook: ArkPropertyContainer.read_properties
    # ─────────────────────────────────────────────────────────────────────────
    from arkparse.parsing.ark_property_container import ArkPropertyContainer
    
    original_read_properties = ArkPropertyContainer.read_properties
    
    def profiled_read_properties(self, byte_buffer, propertyClass, next_object_index):
        with profiler.time("ArkPropertyContainer.read_properties"):
            return original_read_properties(self, byte_buffer, propertyClass, next_object_index)
    
    ArkPropertyContainer.read_properties = profiled_read_properties
    
    # ─────────────────────────────────────────────────────────────────────────
    # Hook: ArkProperty.read_property
    # ─────────────────────────────────────────────────────────────────────────
    from arkparse.parsing.ark_property import ArkProperty
    
    original_read_property = ArkProperty.read_property
    
    @staticmethod
    def profiled_read_property(byte_buffer, in_array=False):
        with profiler.time("ArkProperty.read_property"):
            return original_read_property(byte_buffer, in_array)
    
    ArkProperty.read_property = profiled_read_property
    
    # ─────────────────────────────────────────────────────────────────────────
    # Hook: ArkGameObject.__init__
    # ─────────────────────────────────────────────────────────────────────────
    from arkparse.object_model.ark_game_object import ArkGameObject
    
    original_game_object_init = ArkGameObject.__init__
    
    def profiled_game_object_init(self, uuid=None, blueprint=None, binary_reader=None, from_custom_bytes=False, no_header=False):
        with profiler.time("ArkGameObject.__init__"):
            return original_game_object_init(self, uuid, blueprint, binary_reader, from_custom_bytes, no_header)
    
    ArkGameObject.__init__ = profiled_game_object_init
    
    # ─────────────────────────────────────────────────────────────────────────
    # Hook: Structure classes
    # ─────────────────────────────────────────────────────────────────────────
    from arkparse.object_model.structures import Structure, StructureWithInventory
    
    original_structure_init = Structure.__init__
    original_structure_with_inv_init = StructureWithInventory.__init__
    
    def profiled_structure_init(self, uuid=None, save=None):
        with profiler.time("Structure.__init__"):
            return original_structure_init(self, uuid, save)
    
    def profiled_structure_with_inv_init(self, uuid=None, save=None, bypass_inventory=False):
        with profiler.time("StructureWithInventory.__init__"):
            return original_structure_with_inv_init(self, uuid, save, bypass_inventory)
    
    Structure.__init__ = profiled_structure_init
    StructureWithInventory.__init__ = profiled_structure_with_inv_init
    
    # ─────────────────────────────────────────────────────────────────────────
    # Hook: Inventory
    # ─────────────────────────────────────────────────────────────────────────
    from arkparse.object_model.misc.inventory import Inventory
    
    original_inventory_init = Inventory.__init__
    
    def profiled_inventory_init(self, uuid=None, save=None):
        with profiler.time("Inventory.__init__"):
            return original_inventory_init(self, uuid, save)
    
    Inventory.__init__ = profiled_inventory_init
    
    # ─────────────────────────────────────────────────────────────────────────
    # Hook: SaveConnection methods
    # ─────────────────────────────────────────────────────────────────────────
    from arkparse.saves.save_connection import SaveConnection
    
    original_get_game_objects = SaveConnection.get_game_objects
    original_get_game_obj_binary = SaveConnection.get_game_obj_binary
    original_parse_as_predefined = SaveConnection.parse_as_predefined_object
    
    def profiled_get_game_objects(self, reader_config=None):
        with profiler.time("SaveConnection.get_game_objects"):
            if reader_config is None:
                from arkparse.parsing import GameObjectReaderConfiguration
                reader_config = GameObjectReaderConfiguration()
            return original_get_game_objects(self, reader_config)
    
    def profiled_get_game_obj_binary(self, obj_uuid):
        with profiler.time("SaveConnection.get_game_obj_binary"):
            return original_get_game_obj_binary(self, obj_uuid)
    
    @staticmethod
    def profiled_parse_as_predefined(obj_uuid, class_name, byte_buffer):
        with profiler.time("SaveConnection.parse_as_predefined_object"):
            return original_parse_as_predefined(obj_uuid, class_name, byte_buffer)
    
    SaveConnection.get_game_objects = profiled_get_game_objects
    SaveConnection.get_game_obj_binary = profiled_get_game_obj_binary
    SaveConnection.parse_as_predefined_object = profiled_parse_as_predefined
    
    # ─────────────────────────────────────────────────────────────────────────
    # Hook: ArkBinaryParser
    # ─────────────────────────────────────────────────────────────────────────
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser
    
    original_find_byte_sequence = ArkBinaryParser.find_byte_sequence
    
    def profiled_find_byte_sequence(self, pattern, adjust_offset=-1, print_findings=False):
        with profiler.time("ArkBinaryParser.find_byte_sequence"):
            return original_find_byte_sequence(self, pattern, adjust_offset, print_findings)
    
    ArkBinaryParser.find_byte_sequence = profiled_find_byte_sequence
    
    print("[Profiler] Deep instrumentation hooks installed")


def uninstall_hooks():
    """Remove profiling hooks (restores original methods)."""
    # This would require storing original methods - for simplicity, 
    # just restart Python to remove hooks
    print("[Profiler] To remove hooks, restart Python")
