from dataclasses import dataclass
from typing import TYPE_CHECKING

import struct
from pathlib import Path
import json
from uuid import UUID
import numpy as np
import math

if TYPE_CHECKING:
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.enums.ark_map import ArkMap
from .ark_vector import ArkVector
from .ark_rotator import ArkRotator


FOUNDATION_DISTANCE = 300  # 300 units in ark is 1 foundation

@dataclass
class MapCoordinateParameters:
    origin_min_x: float
    origin_min_y: float
    origin_min_z: float

    origin_max_x: float
    origin_max_y: float
    origin_max_z: float

    playable_min_x: float
    playable_min_y: float
    playable_min_z: float

    playable_max_x: float
    playable_max_y: float
    playable_max_z: float

    def __init__(self, map: ArkMap):
        # These are the MapData grabbed from ASA Dev Kit.
        # A map can have multiple MapData associated to it, but at the moment none of the ASA maps available is doing so.
        # Origin Min-Max is used for minimap coords computation.
        # Playable Min-Max is used to know which MapData to query for computation.
        if map == ArkMap.SCORCHED_EARTH:
            self.origin_min_x = -393650.0
            self.origin_min_y = -393650.0
            self.origin_min_z = -25515.0
            self.origin_max_x = 393750.0
            self.origin_max_y = 393750.0
            self.origin_max_z = 66645.0
            self.playable_min_x = -393650.0
            self.playable_min_y = -393650.0
            self.playable_min_z = -25515.0
            self.playable_max_x = 393750.0
            self.playable_max_y = 393750.0
            self.playable_max_z = 66645.0
        elif map == ArkMap.THE_CENTER:
            self.origin_min_x = -524364.0
            self.origin_min_y = -337215.0
            self.origin_min_z = -171880.46875
            self.origin_max_x = 513040.0
            self.origin_max_y = 700189.0
            self.origin_max_z = 101159.6875
            self.playable_min_x = -524364.0
            self.playable_min_y = -337215.0
            self.playable_min_z = -171880.46875
            self.playable_max_x = 513040.0
            self.playable_max_y = 700189.0
            self.playable_max_z = 101159.6875
        elif map == ArkMap.ABERRATION:
            self.origin_min_x = -400000.0
            self.origin_min_y = -400000.0
            self.origin_min_z = -15000.0
            self.origin_max_x = 400000.0
            self.origin_max_y = 400000.0
            self.origin_max_z = 54695.0
            self.playable_min_x = -400000.0
            self.playable_min_y = -400000.0
            self.playable_min_z = -15000.0
            self.playable_max_x = 400000.0
            self.playable_max_y = 400000.0
            self.playable_max_z = 54695.0
        elif map == ArkMap.EXTINCTION:
            self.origin_min_x = -342900.0
            self.origin_min_y = -342900.0
            self.origin_min_z = -15000.0
            self.origin_max_x = 342900.0
            self.origin_max_y = 342900.0
            self.origin_max_z = 54695.0
            self.playable_min_x = -342900.0
            self.playable_min_y = -342900.0
            self.playable_min_z = -15000.0
            self.playable_max_x = 342900.0
            self.playable_max_y = 342900.0
            self.playable_max_z = 54695.0
        elif map == ArkMap.RAGNAROK:
            self.origin_min_x = -655000.0
            self.origin_min_y = -655000.0
            self.origin_min_z = -655000.0
            self.origin_max_x = 655000.0
            self.origin_max_y = 655000.0
            self.origin_max_z = 54695.0
            self.playable_min_x = -655000.0
            self.playable_min_y = -655000.0
            self.playable_min_z = -100000.0
            self.playable_max_x = 655000.0
            self.playable_max_y = 655000.0
            self.playable_max_z = 655000.0
        elif map == ArkMap.ASTRAEOS:
            self.origin_min_x = -800000.0
            self.origin_min_y = -800000.0
            self.origin_min_z = -15000.0
            self.origin_max_x = 800000.0
            self.origin_max_y = 800000.0
            self.origin_max_z = 54695.0
            self.playable_min_x = -800000.0
            self.playable_min_y = -800000.0
            self.playable_min_z = -15000.0
            self.playable_max_x = 800000.0
            self.playable_max_y = 800000.0
            self.playable_max_z = 54695.0
        elif map == ArkMap.SVARTALFHEIM:
            self.origin_min_x = -203250.0
            self.origin_min_y = -203250.0
            self.origin_min_z = -15000.0
            self.origin_max_x = 203250.0
            self.origin_max_y = 203250.0
            self.origin_max_z = 54695.0
            self.playable_min_x = -203250.0
            self.playable_min_y = -203250.0
            self.playable_min_z = -15000.0
            self.playable_max_x = 203250.0
            self.playable_max_y = 203250.0
            self.playable_max_z = 54695.0
        elif map == ArkMap.VALGUERO:
            self.origin_min_x = -408000.0
            self.origin_min_y = -408000.0
            self.origin_min_z = -655000.0
            self.origin_max_x = 408000.0
            self.origin_max_y = 408000.0
            self.origin_max_z = 54695.0
            self.playable_min_x = -408000.0
            self.playable_min_y = -408000.0
            self.playable_min_z = -100000.0
            self.playable_max_x = 408000.0
            self.playable_max_y = 408000.0
            self.playable_max_z = 655000.0
        elif map == ArkMap.CLUB_ARK:
            self.origin_min_x = -12812.0
            self.origin_min_y = -15121.0
            self.origin_min_z = -12500.0
            self.origin_max_x = 12078.0
            self.origin_max_y = 9770.0
            self.origin_max_z = 12500.0
            self.playable_min_x = -10581.0
            self.playable_min_y = -15121.0
            self.playable_min_z = -12500.0
            self.playable_max_x = 9847.0
            self.playable_max_y = 9770.0
            self.playable_max_z = 12500.0
        elif map == ArkMap.LOST_COLONY:
            self.origin_min_x = -408000.0
            self.origin_min_y = -408000.0
            self.origin_min_z = -15000.0
            self.origin_max_x = 408000.0
            self.origin_max_y = 408000.0
            self.origin_max_z = 54695.0
            self.playable_min_x = -408000.0
            self.playable_min_y = -408000.0
            self.playable_min_z = -15000.0
            self.playable_max_x = 408000.0
            self.playable_max_y = 408000.0
            self.playable_max_z = 54695.0
        else: # Fallback to MinimapData_Base, this is the default data if not overridden by the map (used by The Island for example).
            self.origin_min_x = -342900.0
            self.origin_min_y = -342900.0
            self.origin_min_z = -15000.0
            self.origin_max_x = 342900.0
            self.origin_max_y = 342900.0
            self.origin_max_z = 54695.0
            self.playable_min_x = -342900.0
            self.playable_min_y = -342900.0
            self.playable_min_z = -15000.0
            self.playable_max_x = 342900.0
            self.playable_max_y = 342900.0
            self.playable_max_z = 54695.0

    def transform_to(self, x: float, y: float) -> ArkVector:
        y_max_diff = y - self.origin_max_y
        x_max_diff = x - self.origin_max_x
        origin_y_diff = self.origin_min_y - self.origin_max_y
        origin_x_diff = self.origin_min_x - self.origin_max_x
        lat_ratio = y_max_diff / origin_y_diff
        lo_ratio = x_max_diff / origin_x_diff
        lat = MapCoordinateParameters.lerp(100.0, 0.0, lat_ratio)
        lo = MapCoordinateParameters.lerp(100.0, 0.0, lo_ratio)

        return lat, lo
    
    def transform_from(self, lat: float, lo: float) -> ArkVector:
        origin_y_diff = self.origin_min_y - self.origin_max_y
        origin_x_diff = self.origin_min_x - self.origin_max_x
        lat_ratio = MapCoordinateParameters.inv_lerp(100.0, 0.0, lat)
        lo_ratio = MapCoordinateParameters.inv_lerp(100.0, 0.0, lo)
        y_max_diff = lat_ratio * origin_y_diff
        x_max_diff = lo_ratio * origin_x_diff
        y = y_max_diff + self.origin_max_y
        x = x_max_diff + self.origin_max_x

        return ArkVector(x=x, y=y, z=0)

    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """Linear interpolate on the scale given by a to b, using t as the point on that scale."""
        return (1 - t) * a + t * b

    @staticmethod
    def inv_lerp(a: float, b: float, v: float) -> float:
        """Inverse linear interpolation, gets the fraction between a and b on which v resides."""
        return (v - a) / (b - a)

    @staticmethod
    def fit_transform_params(xs, ys, lats, los):
        # fit lo = m_x * x + b_x
        m_x, b_x = np.polyfit(xs, los, 1)
        # fit lat = m_y * y + b_y
        m_y, b_y = np.polyfit(ys, lats, 1)

        latitude_scale   = round(1.0 / m_x, 2)
        latitude_shift   = round(b_x, 2)
        longitude_scale  = round(1.0 / m_y, 2)
        longitude_shift  = round(b_y, 2)

        return latitude_scale, latitude_shift, longitude_scale, longitude_shift

class MapCoords:
    lat : float
    long : float
    in_cryopod: bool

    def __init__(self, lat, long, in_cryo = False):
        self.lat = lat
        self.long = long
        self.in_cryopod = in_cryo

    def distance_to(self, other: "MapCoords") -> float:
        if self.in_cryopod or other.in_cryopod:
            return float("inf")
        
        return ((self.lat - other.lat) ** 2 + (self.long - other.long) ** 2) ** 0.5

    def __str__(self) -> str:
        if self.in_cryopod:
            return f"(in cryopod)"
        else:
            return f"({self.lat:.2f}, {self.long:.2f})"
        
    def str_short(self) -> str:
        if self.in_cryopod:
            return f"(in cryopod)"
        else:
            return f"({self.lat:.2f}, {self.long:.2f})"
        
    def round(self, digits: int = 2):
        self.lat = round(self.lat, digits)
        self.long = round(self.long, digits)

    def as_actor_transform(self, map) -> "ActorTransform":

        return ActorTransform(vector=MapCoordinateParameters(map).transform_from(self.lat, self.long))

@dataclass
class ActorTransform:
    x: float = 0
    y: float = 0
    z: float = 0
    pitch: float = 0
    yaw: float = 0
    roll: float = 0
    in_cryopod: bool = False

    _quaternion: float = 0.0

    def __init__(self, reader: "ArkBinaryParser" = None, vector: ArkVector = None, rotator: ArkRotator = None, from_json: Path = None):
        if reader:
            # Initialize from ArkBinaryParser
            self.x = reader.read_double()
            self.y = reader.read_double()
            self.z = reader.read_double()
            self.pitch = reader.read_double()
            self.roll = reader.read_double()
            self.yaw = reader.read_double()
            self._quaternion = reader.read_double()
        elif vector:
            # Initialize from ArkVector and ArkRotator
            self.x = vector.x
            self.y = vector.y
            self.z = vector.z

            if rotator:
                self.pitch = rotator.pitch
                self.yaw = rotator.yaw
                self.roll = rotator.roll
            else:
                self.pitch = 0
                self.yaw = 0
                self.roll = 0
        elif from_json:
            # Initialize from JSON
            with open(from_json, "r") as f:
                data = json.load(f)
                self.x = data["x"]
                self.y = data["y"]
                self.z = data["z"]
                self.pitch = data["pitch"]
                self.yaw = data["yaw"] if data.get("unknown", None) is not None else data["roll"]
                self.roll = data["roll"] if data.get("unknown", None) is not None else data["yaw"]

    def __calc_quaterion(self):
        self._quaternion = math.sqrt(1-self.pitch**2 - self.yaw**2 - self.roll**2) if (1-self.pitch**2 - self.yaw**2 - self.roll**2) > 0 else 0

    @property
    def quaternion(self):
        self.__calc_quaterion()
        return self._quaternion

    def get_distance_to(self, other: "ActorTransform") -> float:
        if self.in_cryopod or other.in_cryopod:
            return float("inf")
        
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5
    
    def __str__(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
        
    def to_str_full(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f}) ({self.pitch:.2f}, {self.yaw:.2f}, {self.roll:.2f})"

    def as_map_coords(self, map) -> MapCoords:
        lat, long = MapCoordinateParameters(map).transform_to(self.x, self.y)
        return MapCoords(lat, long, self.in_cryopod)
    
    def is_within_distance(self, location: "ActorTransform", distance: float = None, foundations: int = None, tolerance: int = 10) -> bool:
        if self.in_cryopod or location.in_cryopod:
            return False

        if distance is not None:
            return (self.get_distance_to(location) + tolerance) <= distance
        elif foundations is not None:
            return (self.get_distance_to(location) + tolerance) <= foundations * FOUNDATION_DISTANCE
        else:
            raise ValueError("Either distance or foundations must be provided")
        
    def round(self, digits: int = 2):
        self.x = round(self.x, digits)
        self.y = round(self.y, digits)
        self.z = round(self.z, digits)
        self.pitch = round(self.pitch, digits)
        self.yaw = round(self.yaw, digits)
        self.roll = round(self.roll, digits)
        
    def is_at_map_coordinate(self, map: ArkMap, coordinates: MapCoords, tolerance = 0.1) -> bool:
        if self.in_cryopod:
            return False

        own_coords = self.as_map_coords(map)

        return abs(own_coords.lat - coordinates.lat) <= tolerance and abs(own_coords.long - coordinates.long) <= tolerance
    
    def as_json(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "pitch": self.pitch,
            "yaw": self.yaw,
            "roll": self.roll,
            "quaternion": self.quaternion
        }
    
    def update(self, new_x, new_y, new_z):
        self.x = new_x
        self.y = new_y
        self.z = new_z

    @staticmethod
    def from_json(data: json):
        loc = ActorTransform()
        loc.x = data["x"]
        loc.y = data["y"]
        loc.z = data["z"]
        loc.pitch = data["pitch"] 
        loc.yaw = data["yaw"] if data.get("unknown", None) is not None else data["roll"]
        loc.roll = data["roll"] if data.get("unknown", None) is not None else data["yaw"]
        loc.__calc_quaterion()

        return loc
    
    def to_bytes(self):
        return (
            struct.pack('<d', self.x) +
            struct.pack('<d', self.y) +
            struct.pack('<d', self.z) +
            struct.pack('<d', self.pitch) +
            struct.pack('<d', self.roll) +
            struct.pack('<d', self.yaw) +
            struct.pack('<d', self.quaternion)
        )
    
    def store_json(self, folder: Path, name: str = None):
        loc_path = folder / ("loc_" + str(name) + ".json")
        with open(loc_path, "w") as f:
            f.write(json.dumps(self.as_json(), indent=4))
