from dataclasses import dataclass
from typing import TYPE_CHECKING

import struct
from pathlib import Path
import json
from uuid import UUID
import numpy as np

if TYPE_CHECKING:
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser
from arkparse.enums.ark_map import ArkMap
from .ark_vector import ArkVector
from .ark_rotator import ArkRotator


FOUNDATION_DISTANCE = 300  # 300 units in ark is 1 foundation

@dataclass
class MapCoordinateParameters:
    latitude_shift: float
    longitude_shift: float
    latitude_scale: float
    longitude_scale: float

    def __init__(self, map: ArkMap):
        #https://arkparse.fandom.com/wiki/Coordinates
        if map == ArkMap.ABERRATION:
            self.latitude_shift = 50
            self.longitude_shift = 50
            self.latitude_scale = 8000
            self.longitude_scale = 8000
        elif map == ArkMap.EXTINCTION:
            self.latitude_shift = 50
            self.longitude_shift = 50
            self.latitude_scale = 6850
            self.longitude_scale = 6850
        elif map == ArkMap.THE_ISLAND:
            self.latitude_shift = 50
            self.longitude_shift = 50
            self.latitude_scale = 6850
            self.longitude_scale = 6850
        elif map == ArkMap.THE_CENTER:
            self.latitude_shift = 32.5
            self.longitude_shift = 50.5
            self.latitude_scale = 10380.52
            self.longitude_scale = 10374.29
        elif map == ArkMap.SCORCHED_EARTH:
            self.latitude_shift = 50
            self.longitude_shift = 50
            self.latitude_scale = 8000
            self.longitude_scale = 8000
        elif map == ArkMap.ASTRAEOS:
            self.latitude_shift = 50
            self.longitude_shift = 50
            self.latitude_scale = 16000
            self.longitude_scale = 16000
        elif map == ArkMap.RAGNAROK:
            self.latitude_shift = 50
            self.longitude_shift = 50
            self.latitude_scale = 13100
            self.longitude_scale = 13100
        else:
            raise ValueError(f"Map {map} not supported")
        
    def transform_to(self, x: float, y: float) -> ArkVector:
        lo = (x / self.latitude_scale) + self.latitude_shift
        lat = (y / self.longitude_scale) + self.longitude_shift

        # 2 digits after the comma
        return round(lat, 2), round(lo, 2)
    
    def transform_from(self, lat: float, lo: float) -> ArkVector:
        y = (lat - self.latitude_shift) * self.latitude_scale
        x = (lo - self.longitude_shift) * self.longitude_scale

        return ArkVector(x=x, y=y, z=0)
    
    @staticmethod
    def fit_transform_params(xs, ys, lats, los):
        # fit lo = m_x * x + b_x
        m_x, b_x = np.polyfit(xs, los, 1)
        # fit lat = m_y * y + b_y
        m_y, b_y = np.polyfit(ys, lats, 1)

        latitude_scale   = round(1.0 / m_x)
        latitude_shift   = round(b_x)
        longitude_scale  = round(1.0 / m_y)
        longitude_shift  = round(b_y)

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
            return f"({self.lat}, {self.long})"
        
    def str_short(self) -> str:
        if self.in_cryopod:
            return f"(in cryopod)"
        else:
            return f"({int(self.lat)}, {int(self.long)})"

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

    unknown: int = 0

    def __init__(self, reader: "ArkBinaryParser" = None, vector: ArkVector = None, rotator: ArkRotator = None, from_json: Path = None):
        if reader:
            # Initialize from ArkBinaryParser
            self.x = reader.read_double()
            self.y = reader.read_double()
            self.z = reader.read_double()
            self.pitch = reader.read_double()
            self.yaw = reader.read_double()
            self.roll = reader.read_double()
            self.unknown = reader.read_uint64()
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
                self.yaw = data["yaw"]
                self.roll = data["roll"]
                self.unknown = data["unknown"]
        

    def get_distance_to(self, other: "ActorTransform") -> float:
        if self.in_cryopod or other.in_cryopod:
            return float("inf")
        
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5
    
    def __str__(self) -> str:
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
            "unknown": self.unknown
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
        loc.yaw = data["yaw"]
        loc.roll = data["roll"]
        loc.unknown = data["unknown"]
        return loc
    
    def to_bytes(self):
        return (
            struct.pack('<d', self.x) +
            struct.pack('<d', self.y) +
            struct.pack('<d', self.z) +
            struct.pack('<d', self.pitch) +
            struct.pack('<d', self.yaw) +
            struct.pack('<d', self.roll) +
            struct.pack('<Q', self.unknown)
        )
    
    def store_json(self, folder: Path, name: str = None):
        loc_path = folder / ("loc_" + str(name) + ".json")
        with open(loc_path, "w") as f:
            f.write(json.dumps(self.as_json(), indent=4))