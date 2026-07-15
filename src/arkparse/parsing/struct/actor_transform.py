from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, List

import struct
from pathlib import Path
import json
import numpy as np
import math

if TYPE_CHECKING:
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.enums.ark_map import ArkMap
from .ark_vector import ArkVector
from .ark_rotator import ArkRotator


FOUNDATION_DISTANCE = 300  # 300 units in ark is 1 foundation

@dataclass
class Bounds:
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float


@dataclass
class MapData:
    origin: Bounds
    playable: Bounds
    sub_map_name: Optional[str]

    def contains(self, x: float, y: float, z: float) -> bool:
        return (
                self.origin.min_x <= x <= self.origin.max_x
                and self.origin.min_y <= y <= self.origin.max_y
                and self.origin.min_z <= z <= self.origin.max_z
        )


@dataclass
class MapCoordinateParameters:
    map_data: List[MapData] = field(default_factory=list)

    def __init__(self, map: ArkMap):
        if map == ArkMap.SCORCHED_EARTH:
            self.map_data = [
                MapData(
                    origin=Bounds(-393650.0, -393650.0, -25515.0, 393750.0, 393750.0, 66645.0),
                    playable=Bounds(-393650.0, -393650.0, -25515.0, 393750.0, 393750.0, 66645.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.THE_CENTER:
            self.map_data = [
                MapData(
                    origin=Bounds(-524364.0, -337215.0, -171880.46875, 513040.0, 700189.0, 101159.6875),
                    playable=Bounds(-524364.0, -337215.0, -171880.46875, 513040.0, 700189.0, 101159.6875),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.ABERRATION:
            self.map_data = [
                MapData(
                    origin=Bounds(-400000.0, -400000.0, -15000.0, 400000.0, 400000.0, 54695.0),
                    playable=Bounds(-400000.0, -400000.0, -15000.0, 400000.0, 400000.0, 54695.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.EXTINCTION:
            self.map_data = [
                MapData(
                    origin=Bounds(-342900.0, -342900.0, -15000.0, 342900.0, 342900.0, 54695.0),
                    playable=Bounds(-342900.0, -342900.0, -15000.0, 342900.0, 342900.0, 54695.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.RAGNAROK:
            self.map_data = [
                MapData(
                    origin=Bounds(-655000.0, -655000.0, -655000.0, 655000.0, 655000.0, 54695.0),
                    playable=Bounds(-655000.0, -655000.0, -100000.0, 655000.0, 655000.0, 655000.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.ASTRAEOS:
            self.map_data = [
                MapData(
                    origin=Bounds(-800000.0, -800000.0, -15000.0, 800000.0, 800000.0, 54695.0),
                    playable=Bounds(-800000.0, -800000.0, -15000.0, 800000.0, 800000.0, 54695.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.SVARTALFHEIM:
            self.map_data = [
                MapData(
                    origin=Bounds(-203250.0, -203250.0, -15000.0, 203250.0, 203250.0, 54695.0),
                    playable=Bounds(-203250.0, -203250.0, -15000.0, 203250.0, 203250.0, 54695.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.VALGUERO:
            self.map_data = [
                MapData(
                    origin=Bounds(-408000.0, -408000.0, -655000.0, 408000.0, 408000.0, 54695.0),
                    playable=Bounds(-408000.0, -408000.0, -100000.0, 408000.0, 408000.0, 655000.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.CLUB_ARK:
            self.map_data = [
                MapData(
                    origin=Bounds(-12812.0, -15121.0, -12500.0, 12078.0, 9770.0, 12500.0),
                    playable=Bounds(-10581.0, -15121.0, -12500.0, 9847.0, 9770.0, 12500.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.LOST_COLONY:
            self.map_data = [
                MapData(
                    origin=Bounds(-408000.0, -408000.0, -15000.0, 408000.0, 408000.0, 54695.0),
                    playable=Bounds(-408000.0, -408000.0, -15000.0, 408000.0, 408000.0, 54695.0),
                    sub_map_name=None
                )
            ]
        elif map == ArkMap.GENESIS1:
            self.map_data = [
                MapData(
                    origin=Bounds(-1107501.0, -1107500.0, 129392.0, 1107499.0, 1107500.0, 404392.0),
                    playable=Bounds(-1107501.0, -1107500.0, 129392.0, 1107499.0, 1107500.0, 404392.0),
                    sub_map_name="Ocean"
                ),
                MapData(
                    origin=Bounds(-410001.0, -410000.0, -399952.0, 409999.0, 410000.0, 100048.0),
                    playable=Bounds(-410001.0, -410000.0, -399952.0, 409999.0, 410000.0, 100048.0),
                    sub_map_name="OtherBiomes"
                )
            ]
        else:  # Fallback MinimapData_Base (ex : The Island)
            self.map_data = [
                MapData(
                    origin=Bounds(-342900.0, -342900.0, -15000.0, 342900.0, 342900.0, 54695.0),
                    playable=Bounds(-342900.0, -342900.0, -15000.0, 342900.0, 342900.0, 54695.0),
                    sub_map_name=None
                )
            ]

    def _get_map_data_by_coords(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None) -> MapData:
        if x is None or y is None or z is None:
            return self.map_data[0]
        for data in self.map_data:
            if data.contains(x, y, z):
                return data
        return self.map_data[0]

    def _get_map_data_by_sub_name(self, sub_name: Optional[str]) -> Optional[MapData]:
        if sub_name is not None:
            for map_data in self.map_data:
                if map_data.sub_map_name is not None and map_data.sub_map_name.casefold() == sub_name.casefold():
                    return map_data
        return self.map_data[0]

    def transform_to(self, x: float, y: float, z: float = 0.0) -> tuple[float, float, Optional[str]]:
        map_data = self._get_map_data_by_coords(x, y, z)

        y_max_diff = y - map_data.origin.max_y
        x_max_diff = x - map_data.origin.max_x
        origin_y_diff = map_data.origin.min_y - map_data.origin.max_y
        origin_x_diff = map_data.origin.min_x - map_data.origin.max_x
        lat_ratio = y_max_diff / origin_y_diff
        lo_ratio = x_max_diff / origin_x_diff
        lat = MapCoordinateParameters.lerp(100.0, 0.0, lat_ratio)
        lo = MapCoordinateParameters.lerp(100.0, 0.0, lo_ratio)

        return lat, lo, map_data.sub_map_name

    def transform_from(self, lat: float, lo: float, sub_map_name: Optional[str] = None) -> ArkVector:
        map_data = self._get_map_data_by_sub_name(sub_map_name)

        origin_y_diff = map_data.origin.min_y - map_data.origin.max_y
        origin_x_diff = map_data.origin.min_x - map_data.origin.max_x
        lat_ratio = MapCoordinateParameters.inv_lerp(100.0, 0.0, lat)
        lo_ratio = MapCoordinateParameters.inv_lerp(100.0, 0.0, lo)
        y_max_diff = lat_ratio * origin_y_diff
        x_max_diff = lo_ratio * origin_x_diff
        y = y_max_diff + map_data.origin.max_y
        x = x_max_diff + map_data.origin.max_x

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

        latitude_scale = round(1.0 / m_x, 2)
        latitude_shift = round(b_x, 2)
        longitude_scale = round(1.0 / m_y, 2)
        longitude_shift = round(b_y, 2)

        return latitude_scale, latitude_shift, longitude_scale, longitude_shift

class MapCoords:
    lat : float
    long : float
    in_cryopod: bool
    sub_map_name: Optional[str]

    def __init__(self, lat, long, in_cryo = False, sub_map_name = None):
        self.lat = lat
        self.long = long
        self.in_cryopod = in_cryo
        self.sub_map_name = sub_map_name

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
        return ActorTransform(vector=MapCoordinateParameters(map).transform_from(self.lat, self.long, self.sub_map_name))

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
                self.yaw = data["yaw"] if data.get("unknown", None) is None else data["roll"]
                self.roll = data["roll"] if data.get("unknown", None) is None else data["yaw"]

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
        lat, long, sub_map_name = MapCoordinateParameters(map).transform_to(self.x, self.y, self.z)
        return MapCoords(lat, long, self.in_cryopod, sub_map_name)
    
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
        
    def is_at_map_coordinate(self, map: ArkMap, coordinates: MapCoords, tolerance: float = 0.1, check_if_same_sub_map: bool = True) -> bool:
        if self.in_cryopod:
            return False

        own_coords = self.as_map_coords(map)

        same_coords: bool = (abs(own_coords.lat - coordinates.lat) <= tolerance and abs(own_coords.long - coordinates.long) <= tolerance)

        same_sub_map = True
        if check_if_same_sub_map:
            same_sub_map = (own_coords.sub_map_name is None and coordinates.sub_map_name is None) or (own_coords.sub_map_name.casefold() == coordinates.sub_map_name.casefold())

        return same_coords and same_sub_map
    
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
        loc.yaw = data["yaw"] if data.get("unknown", None) is None else data["roll"]
        loc.roll = data["roll"] if data.get("unknown", None) is None else data["yaw"]
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
