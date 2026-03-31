#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified ASA JSON Exporter
- Option 2: Eigene Prozesse ohne Pool → jeder Export-Prozess beendet sich direkt nach Fertigstellung (RAM wird freigegeben).
- Priorität: 'tamed' zuerst, dann 'structures', danach die übrigen Typen in der ursprünglichen Reihenfolge.
- Parallelmodus (--parallel=1) startet alle angeforderten Typen gleichzeitig als Einmal-Prozesse.
- Serieller Modus (--parallel=0, Default) lädt das Save genau einmal und führt Exporte nacheinander aus.
- Ausgabeformat: [OK][type] Wrote  XXXX entries in YY.yy secs -> <pfad>
- Neues Flag: --withcryo=1 aktiviert Cryopod-Dinos **nur** für den Tamed-Export. Für andere Typen wird es ignoriert.

Beispiele:
  py asv_json_export/export_json.py --type="all" --serverkey="staging_a" --savegame=".../Astraeos_WP.ark" --output=../output
  py asv_json_export/export_json.py --type="tamed" --withcryo=1 --serverkey="staging_a" --savegame=".../Astraeos_WP.ark" --output=../output
  py asv_json_export/export_json.py --type="players,tamed" --parallel=1 --withcryo=0 --serverkey="staging_a" --savegame=".../Astraeos_WP.ark" --output=../output
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from zoneinfo import ZoneInfo
import multiprocessing as mp
from pprint import pprint
from datetime import datetime, timedelta

# arkparse
from arkparse.saves.asa_save import AsaSave
from arkparse.enums import ArkMap
from arkparse.api.player_api import PlayerApi
from arkparse.api.dino_api import DinoApi, Dino, TamedDino, TamedBaby
from arkparse.api import StructureApi
from arkparse.helpers.dino.is_wild_tamed import is_wild_tamed
from arkparse.object_model.structures import StructureWithInventory
from arkparse.parsing import GameObjectReaderConfiguration

def get_mp_context():
    """
    Windows: spawn (Pflicht)
    Linux/Unix: fork (schneller), fallback spawn falls fork nicht verfügbar ist.
    """
    if sys.platform.startswith("win"):
        return mp.get_context("spawn")
    try:
        return mp.get_context("fork")
    except ValueError:
        return mp.get_context("spawn")


# ---------- CLI ----------

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Unified ASA JSON Exporter")
    p.add_argument("--savegame", type=Path, required=True, help="Pfad zur .ark Datei")
    p.add_argument("--output", type=Path, required=True, help="Basis-Output-Ordner")
    p.add_argument("--serverkey", type=str, required=True, help="Server-Key (z.B. extinction_a)")
    p.add_argument(
        "--type",
        type=str,
        required=True,
        help='Exporttypen, kommasepariert. Erlaubt: "players,structures,tamed,wild" oder "all"',
    )
    # Parallel-Flag
    p.add_argument("--parallel", type=int, default=1, choices=(0, 1), help="0=seriell, 1=parallel (Einmal-Prozesse, default)")
    # Wild-spezifische Parameter
    p.add_argument("--max-level", type=int, default=150, help="Levelcap für normale Wild-Dinos")
    p.add_argument("--max-level-bionic", type=int, default=180, help="Levelcap für Bionic/TEK Wild-Dinos")
    # Tamed-spezifisch
    p.add_argument("--withcryo", type=int, default=1, choices=(0, 1),
                   help="1 = Cryopod-Dinos einbeziehen beim Tamed-Export, 1 = mit Cryos (Default). Für andere Typen ignoriert.")
    return p

# ---------- Configuration ----------

SUPPORTED_TYPES = {"players", "structures", "tamed", "wild"}

MAP_NAME_MAPPING: Dict[str, ArkMap] = {
    "Aberration_WP": ArkMap.ABERRATION,
    "Extinction_WP": ArkMap.EXTINCTION,
    "TheIsland_WP": ArkMap.THE_ISLAND,
    "Ragnarok_WP": ArkMap.RAGNAROK,
    "ScorchedEarth_WP": ArkMap.SCORCHED_EARTH,
    "TheCenter_WP": ArkMap.THE_CENTER,
    "Astraeos_WP": ArkMap.ASTRAEOS,
    "Valguero_WP": ArkMap.VALGUERO,
    "LostColony_WP": ArkMap.LOST_COLONY,
}

STAT_NAME_MAP = {
    "hp": "health",
    "stam": "stamina",
    "melee": "melee_damage",
    "weight": "weight",
    "speed": "movement_speed",
    "food": "food",
    "oxy": "oxygen",
    "craft": "crafting_speed",
}

ADDED_KEY_MAP = {
    "health": "hp-a",
    "stamina": "stam-a",
    "melee_damage": "melee-a",
    "weight": "weight-a",
    "movement_speed": "speed-a",
    "food": "food-a",
    "oxygen": "oxy-a",
}

EPOCH_LOGIN = datetime(2019, 1, 1, tzinfo=timezone.utc)  # für Player LoginTime Konvertierung

# ---------- Utilities ---------
def atomic_write_json(obj: Any, target: Path, export_folder: Path) -> None:
    """
    CIFS-robustes atomic write (orjson-only):
    - Temp file IM Zielordner (target.parent) anlegen (wichtig bei SMB/CIFS)
    - orjson für schnelle Serialisierung
    - Fallback-Strategie, falls os.replace() auf CIFS zickt
    """
    target = Path(target)
    target_parent = target.parent
    target_parent.mkdir(parents=True, exist_ok=True)

    tmp_name: Optional[str] = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(target_parent), suffix=".tmp") as tf:
            json.dump(
                obj,
                tf,
                ensure_ascii=False,
                default=json_default,
                separators=(",", ":"),
            )
            tf.write("\n")
            tmp_name = tf.name

        # Primary attempt
        try:
            os.replace(tmp_name, str(target))
        except Exception:
            # CIFS fallback: remove target first then replace
            try:
                if target.exists():
                    target.unlink()
            except Exception:
                pass
            os.replace(tmp_name, str(target))

    finally:
        # Wenn replace erfolgreich war, existiert tmp nicht mehr.
        # Wenn vorher was schief ging, räumen wir auf.
        if tmp_name and os.path.exists(tmp_name):
            try:
                os.unlink(tmp_name)
            except Exception:
                pass

def get_map_key_from_savepath(save_path: Path) -> Tuple[str, str]:
    """Gibt (map_folder, map_key) zurück"""
    return save_path.parent.name, save_path.stem

def asa_login_to_mysql_local(ts: float | int | None, tz_name: str = "Europe/Berlin") -> Optional[str]:
    if not ts:
        return None
    try:
        x = float(ts)
        # Cisco ASA REST-API Epoch: 01.01.2018 00:00:00 UTC
        asa_base = datetime(2018, 1, 1, tzinfo=ZoneInfo("UTC"))

        # Berechnung
        dt = asa_base + timedelta(seconds=x)
        dt_local = dt.astimezone(ZoneInfo(tz_name))

        return dt_local.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

def is_active_within_months(login_time: float | int | None, months: int = 2) -> bool:
    if login_time is None:
        return False
    try:
        x = float(login_time)
    except Exception:
        return False
    if x > 1e11:
        x /= 1000.0
    dt = EPOCH_LOGIN + timedelta(seconds=x)
    return dt >= datetime.now(timezone.utc) - timedelta(days=30 * months)

def parse_asa_stamp(ts: Optional[str]) -> Optional[str]:
    """'YYYY.MM.DD-HH.MM.SS' -> 'YYYY-MM-DD HH:MM:SS'"""
    if not ts:
        return None
    try:
        dt = datetime.strptime(ts, "%Y.%m.%d-%H.%M.%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def is_bionic(class_name: str) -> bool:
    s = class_name or ""
    return ("Bionic" in s) or ("Tek" in s) or ("TEK" in s)

def safe_color_indices(raw: Any, length: int = 6) -> List[Optional[int]]:
    if raw is None:
        return [None] * length
    if isinstance(raw, (list, tuple)):
        vals = list(raw)[:length]
        out: List[Optional[int]] = []
        for v in vals:
            try:
                out.append(int(v))
            except Exception:
                out.append(None)
        return out + [None] * (length - len(out))
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                inner = s[1:-1].strip()
                if not inner:
                    return [None] * length
                parts = [p.strip() for p in inner.split(",")]
                out: List[Optional[int]] = []
                for p in parts[:length]:
                    try:
                        out.append(int(float(p)))
                    except Exception:
                        out.append(None)
                return out + [None] * (length - len(out))
            except Exception:
                return [None] * length
    return [None] * length

def pad_colors_literal_eval(color_indices: Any, length: int = 6) -> List[Optional[int]]:
    if isinstance(color_indices, str):
        try:
            color_indices = ast.literal_eval(color_indices)
        except (ValueError, SyntaxError):
            color_indices = []
    if not isinstance(color_indices, (list, tuple)):
        color_indices = []
    out: List[Optional[int]] = []
    for v in list(color_indices)[:length]:
        try:
            out.append(int(v))
        except (TypeError, ValueError):
            out.append(None)
    out += [None] * max(0, length - len(out))
    return out

def resolve_coords_xyz_to_map(latlon_provider, ark_map: Optional[ArkMap]) -> Tuple[Tuple[float, float], str]:
    loc = getattr(latlon_provider, "location", None)
    if not loc:
        return (0.0, 0.0), ""
    ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
    if ark_map is None:
        return (0.0, 0.0), ccc
    try:
        coords = loc.as_map_coords(ark_map)
        if coords is not None:
            return (coords.lat, coords.long), ccc
    except Exception:
        pass
    return (0.0, 0.0), ccc

def wild_within_caps(dino_class: str, level: Optional[int], cap_normal: int, cap_bionic: int) -> bool:
    if level is None:
        return False
    return level <= (cap_bionic if is_bionic(dino_class) else cap_normal)

def json_default(o: Any):
    if isinstance(o, (UUID, Path)):
        return str(o)
    return str(o)

# ---------- Exporter: Players ----------

def export_players(save: AsaSave, export_folder: Path, save_path: Path) -> Tuple[str, int]:
    player_api = PlayerApi(save)

    # Tribe-Namen map
    tribes_by_id: Dict[int, str] = {}
    for tribe in getattr(player_api, "tribes", []):
        try:
            tid = getattr(tribe, "tribe_id", None)
            name = getattr(tribe, "name", None) or getattr(tribe, "tribe_name", None) or ""
            if (tid is None or not name) and hasattr(tribe, "to_json_obj"):
                tj = tribe.to_json_obj() or {}
                tid = tid if tid is not None else tj.get("TribeID")
                name = name or tj.get("TribeName", "")
            if tid is not None:
                tribes_by_id[int(tid)] = str(name or "")
        except Exception:
            continue

    players: List[Dict[str, Any]] = []
    map_folder, _ = get_map_key_from_savepath(save_path)
    for p in getattr(player_api, "players", []):
        if p.tribe is None:
            continue

        map_key = save_path.stem
        ark_map = MAP_NAME_MAPPING.get(map_key)
        if ark_map is None:
            raise ValueError(f"Unknown map key '{map_key}' for tamed export")

        lat = 0.0
        lon = 0.0
        ccc = ""
        loc = p.location
        if loc is not None:
            ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
            coords = loc.as_map_coords(ark_map) if ark_map else None
            lat = getattr(coords, "lat", 0.0) if coords else 0.0
            lon = getattr(coords, "long", 0.0) if coords else 0.0

        entry = {
            "playerid": str(p.id_),
            "steam": p.name,
            "name": p.char_name,
            "tribeid": p.tribe,
            "tribe": tribes_by_id.get(p.tribe),
            "sex": "Female" if p.config.is_female else "Male",
            "lvl": p.stats.level,
            "lat": lat,
            "lon": lon,
            "hp": p.stats.stats.health,
            "stam": p.stats.stats.stamina,
            "melee": p.stats.stats.melee_damage,
            "weight": p.stats.stats.weight,
            "speed": p.stats.stats.movement_speed,
            "food": p.stats.stats.food,
            "water": p.stats.stats.water,
            "oxy": p.stats.stats.oxygen,
            "craft": p.stats.stats.crafting_speed,
            "fort": p.stats.stats.fortitude,
#             "active": is_active_within_months(p.login_time, months=1),
#             "last_login": asa_login_to_mysql_local(p.login_time, tz_name="Europe/Berlin"),
#             "last_login_d": p.login_time,
            "ccc": ccc,
            "steamid": str(p.unique_id),
            "ip": p.ip_address,
            "achievements": [],
            "inventory": [],
            "deaths": int(p.nr_of_deaths),
            # "last_death": p.last_time_died,
        }
        players.append(entry)

    payload = {"map": map_folder, "data": players}
    path = export_folder / "Players.json"
    atomic_write_json(payload, path, export_folder)
    return ("Players.json", len(players))

# ---------- Exporter: Structures ----------

def export_structures(save: AsaSave, export_folder: Path, save_path: Path) -> Tuple[str, int]:
    structure_api = StructureApi(save)
    map_folder, map_key = get_map_key_from_savepath(save_path)
    ark_map = MAP_NAME_MAPPING.get(map_key)

    out: List[Dict[str, Any]] = []
    for structure in structure_api.get_all().values():
        owner_name = structure.object.get_property_value("OwnerName")
        if owner_name is None:
            continue
        tribe_id = structure.object.get_property_value("TargetingTeam")
        if tribe_id is None:
            continue

        created = parse_asa_stamp(structure.object.get_property_value("OriginalPlacedTimeStamp", 0))
        (lat, lon), ccc = resolve_coords_xyz_to_map(structure, ark_map)

        out.append(
            {
                "tribeid": tribe_id,
                "tribe": owner_name,
                "struct": f"{structure.get_short_name()}_C",
                "name": structure.object.get_property_value("BoxName"),
                "lat": lat,
                "lon": lon,
                "ccc": ccc,
                "created": created,
                "inventory": [],
            }
        )

    payload = {"map": map_folder, "data": out}
    path = export_folder / "Structures.json"
    atomic_write_json(payload, path, export_folder)
    return ("Structures.json", len(out))

# ---------- Hilfsfunktionen (Tamed) ----------

def _tamed_owner_field(dino: Any, field: str) -> Optional[Any]:
    try:
        if not getattr(dino, "is_cryopodded", False) and getattr(dino, "owner", None):
            return getattr(dino.owner, field, None)
        cryo_owner = getattr(getattr(getattr(dino, "cryopod", None), "dino", None), "owner", None)
        return getattr(cryo_owner, field, None) if cryo_owner else None
    except Exception:
        return None

def _tamed_location(dino: Any) -> Optional[Any]:
    if not getattr(dino, "is_cryopodded", False) and getattr(dino, "location", None):
        return dino.location
    cryo_dino = getattr(getattr(dino, "cryopod", None), "dino", None)
    return getattr(cryo_dino, "location", None)

def _extract_added_stat_values(stat_string: str) -> Dict[str, int]:
    if not stat_string:
        return {}
    matches = dict((k, v) for k, v in re.findall(r"(\w+)=([\d.]+)", stat_string))
    result: Dict[str, int] = {}
    for src_key, dst_key in ADDED_KEY_MAP.items():
        if src_key in matches:
            try:
                num = float(matches[src_key])
                result[dst_key] = int(num) if num.is_integer() else int(round(num))
            except ValueError:
                continue
    return result

# ---------- Exporter: Tamed ----------
def export_tamed(save: AsaSave, export_folder: Path, save_path: Path, with_cryo: bool) -> Tuple[str, int]:
    dino_api = DinoApi(save)

    # Read all possible cryopod storages to override later the right tribe_id (transfer-bug) and coords
    structure_api = StructureApi(save)
    # possible_cryopod_storages = ['CryoFridge_C', 'CryoHospital_Base_C', 'IceBox_C', 'StorageBox_Large_C', 'LinkedStorage_C', 'StorageBox_Small_C', 'StorageBox_Huge_C']
    possible_cryopod_storages = ['CryoFridge_C', 'CryoHospital_Base_C']
    config = GameObjectReaderConfiguration(blueprint_name_filter=lambda name: name is not None and any(cls in name for cls in possible_cryopod_storages))

#     config = GameObjectReaderConfiguration(
#         blueprint_name_filter=lambda name: name is not None and (
#             any(s in name for s in {"CryoFridge_C", "CryoHospital_Base_C"}) or
#             any(c in name for c in {"PrimalItem_WeaponEmptyCryopod_C"})
#         ),
#         property_names=["OwnerName", "TargetingTeam", "OriginalPlacedTimeStamp", "BoxName", "InventoryUUID"]
#     )

    storages = structure_api.get_all(config)

    inventory_map: Dict[UUID, Dict[str, Any]] = {}
    for key, storage in storages.items():
        if not isinstance(storage, StructureWithInventory):
            continue

        if storage.owner.tribe_id is not None and storage.owner.properties.location is not None:
            inventory_map[storage.inventory_uuid] = {
                "tribe_id": storage.owner.tribe_id,
                "location": storage.owner.properties.location,
            }

    map_folder = save_path.parent.name
    map_key = save_path.stem
    ark_map = MAP_NAME_MAPPING.get(map_key)
    if ark_map is None:
        raise ValueError(f"Unknown map key '{map_key}' for tamed export")

    tamed_out: List[Dict[str, Any]] = []

    # mit/ohne Cryo je nach Flag
    for dino_id, dino in dino_api.get_all_tamed(with_cryo).items():
        if not isinstance(dino, (TamedDino, TamedBaby)):
            continue

        dino_json = dino.to_json_obj()

        dino_class_short = getattr(dino, "tamed_name", "") or ""
        dino_class = dino_json.get("ItemArchetype").split(".")[-1] or dino_class_short

        is_cryo = bool(getattr(dino, "is_cryopodded", False))

        # Position (keine Weltposition bei Cryo)
        loc = _tamed_location(dino)
        ccc, lat, lon = "", 0.0, 0.0
        if loc is not None and not is_cryo:
            ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
            coords = loc.as_map_coords(ark_map) if ark_map else None
            lat = getattr(coords, "lat", 0.0) if coords else 0.0
            lon = getattr(coords, "long", 0.0) if coords else 0.0

        tribe_id = _tamed_owner_field(dino, "tamer_tribe_id")
        tamer_name = _tamed_owner_field(dino, "tamer_string")
        if (tribe_id == 2000000000 and dino_json.get("TargetingTeam")) or tribe_id is None:
            tribe_id = dino_json.get("TargetingTeam")

        # Override tribe_id if the dino was transferred
        if(is_cryo):
            if dino.cryopod.owner_inv_uuid and dino.cryopod.owner_inv_uuid in inventory_map:
                map_entry = inventory_map[dino.cryopod.owner_inv_uuid]
                tribe_id = map_entry["tribe_id"]
                loc = map_entry["location"]

                if loc is not None:
                    ccc = f"{loc.x:.2f} {loc.y:.2f} {loc.z:.2f}"
                    coords = loc.as_map_coords(ark_map) if ark_map else None
                    lat = getattr(coords, "lat", 0.0) if coords else 0.0
                    lon = getattr(coords, "long", 0.0) if coords else 0.0

        # Stats (wild/tamed/mut)
        stats_entry: Dict[str, int] = {}
        for prefix, field in STAT_NAME_MAP.items():
            base = getattr(getattr(getattr(dino, "stats", None), "base_stat_points", None), field, 0)
            add = getattr(getattr(getattr(dino, "stats", None), "added_stat_points", None), field, 0)
            mut = getattr(getattr(getattr(dino, "stats", None), "mutated_stat_points", None), field, 0)
            stats_entry[f"{prefix}-w"] = int(base or 0)
            stats_entry[f"{prefix}-t"] = int(add or 0)
            stats_entry[f"{prefix}-m"] = int(mut or 0)

        c0, c1, c2, c3, c4, c5 = pad_colors_literal_eval(dino_json.get("ColorSetIndices", "[]"))

        entry: Dict[str, Any] = {
            "id": str(dino_id),
            "tribeid": tribe_id,
            "tribe": dino_json.get("TribeName", "") or "",
            "tamer": tamer_name or "",
            "imprinter": _tamed_owner_field(dino, "imprinter") or "",
            "imprint": float(getattr(dino, "percentage_imprinted", 0.0) or 0.0),
            "creature": dino_class,
            "name": getattr(dino, "tamed_name", "") or "",
            "sex": "Female" if getattr(dino, "is_female", False) else "Male",
            "base": getattr(getattr(dino, "stats", None), "base_level", None),
            "lvl": getattr(getattr(dino, "stats", None), "current_level", None),
            "lat": lat,
            "lon": lon,
            "cryo": is_cryo,
            "ccc": ccc,
            "isMating": False,
            "isNeutered": False,
            "isClone": False,
            "maturation": float(getattr(dino, "percentage_matured", 100.0)) if isinstance(dino, TamedBaby) else "100",
            "traits": [],
            "inventory": [],
            "is_wild_tamed": bool(is_wild_tamed(dino)),
            "tamedAtTime": parse_asa_stamp(dino_json.get("TamedTimeStamp")),
            "mut-f": dino_json.get("RandomMutationsFemale"),
            "mut-m": dino_json.get("RandomMutationsMale"),
            "c0": c0, "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
        }
        entry.update(stats_entry)

        stat_values = dino_json.get("StatValues", "")
        if stat_values:
            entry.update(_extract_added_stat_values(stat_values))

        tamed_out.append(entry)

    payload = {"map": map_folder, "data": tamed_out}
    path = export_folder / "TamedDinos.json"
    atomic_write_json(payload, path, export_folder)
    return ("TamedDinos.json", len(tamed_out))

# ---------- Exporter: Wild ----------

def export_wild(save: AsaSave, export_folder: Path, save_path: Path, cap_normal: int, cap_bionic: int) -> Tuple[str, int]:
    dino_api = DinoApi(save)

    # Für "map" im Payload: server_folder (= Elternordner mit *_a), fallback map_folder
    server_folder = None
    for p in save_path.parents:
        if p.name.endswith("_a"):
            server_folder = p.name
            break
    if server_folder is None:
        server_folder = save_path.parent.name

    map_key = save_path.stem
    ark_map = MAP_NAME_MAPPING.get(map_key)

    out: List[Dict[str, Any]] = []
    for dino_id, dino in dino_api.get_all_wild_tamables().items():
        if not isinstance(dino, Dino):
            continue

        dino_json = dino.to_json_obj()

        lvl = dino.stats.base_level if dino.stats else None

        dino_class_short = getattr(dino, "tamed_name", "") or ""
        dino_class = dino_json.get("ItemArchetype").split(".")[-1] or dino_class_short

        if "_Corrupt" in dino_class:
            continue
        if not wild_within_caps(dino_class, lvl, cap_normal, cap_bionic):
            continue

        (lat, lon), ccc = resolve_coords_xyz_to_map(dino, ark_map)
        coords = (lat, lon)

        s = dino.stats
        colors = safe_color_indices(dino_json.get("ColorSetIndices"))
        try:
            int_id = int(str(dino_id))
            int_id = int_id if -(2**63) <= int_id < 2**63 else None
        except Exception:
            int_id = None

        out.append(
            {
                "id": int_id if int_id is not None else str(dino_id),
                "creature": dino_class,
                "sex": "Female" if dino.is_female else "Male",
                "lvl": (s.base_level if s else None),
                "lat": coords[0],
                "lon": coords[1],
                "hp": int(getattr(getattr(s, "base_stat_points", None), "health", 0) or 0),
                "stam": int(getattr(getattr(s, "base_stat_points", None), "stamina", 0) or 0),
                "melee": int(getattr(getattr(s, "base_stat_points", None), "melee_damage", 0) or 0),
                "weight": int(getattr(getattr(s, "base_stat_points", None), "weight", 0) or 0),
                "speed": int(getattr(getattr(s, "base_stat_points", None), "movement_speed", 0) or 0),
                "food": int(getattr(getattr(s, "base_stat_points", None), "food", 0) or 0),
                "oxy": int(getattr(getattr(s, "base_stat_points", None), "oxygen", 0) or 0),
                "craft": int(getattr(getattr(s, "base_stat_points", None), "crafting_speed", 0) or 0),
                "c0": colors[0],
                "c1": colors[1],
                "c2": colors[2],
                "c3": colors[3],
                "c4": colors[4],
                "c5": colors[5],
                "ccc": ccc,
                "tameable": True,
                "trait": str(dino_json.get("GeneTraits", "") or ""),
            }
        )

    payload = {"map": server_folder, "data": out}
    path = export_folder / "WildDinos.json"
    atomic_write_json(payload, path, export_folder)
    return ("WildDinos.json", len(out))

# ---------- Typen/Prio ----------

def parse_types(type_arg: str) -> List[str]:
    t = (type_arg or "").strip().lower()
    if not t:
        raise ValueError("--type darf nicht leer sein")
    if t == "all":
        return sorted(SUPPORTED_TYPES)
    parts = [p.strip() for p in t.split(",") if p.strip()]
    unknown = [p for p in parts if p not in SUPPORTED_TYPES]
    if unknown:
        raise ValueError(f"Unbekannte Typen in --type: {', '.join(unknown)}. Erlaubt: {', '.join(sorted(SUPPORTED_TYPES))} oder 'all'.")
    # Reihenfolge beibehalten, Duplikate entfernen
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            out.append(p)
            seen.add(p)
    return out

def prioritize_types(types: List[str]) -> List[str]:
    """
    Priorität: 'tamed' zuerst, 'structures' als zweites (falls jeweils gesetzt),
    die restlichen folgen in der ursprünglichen Reihenfolge.
    """
    out: List[str] = []
    if "tamed" in types:
        out.append("tamed")
    if "structures" in types:
        out.append("structures")
    for t in types:
        if t not in ("tamed", "structures"):
            out.append(t)
    return out

# ---------- Child-Worker (eigener Prozess) ----------

def child_worker(t: str, save_path: Path, export_folder: Path, max_level: int, max_level_bionic: int,
                 with_cryo_flag: int, result_q: mp.Queue):
    """
    Läuft in einem separaten Prozess:
      - öffnet ein eigenes AsaSave
      - führt genau EINEN Export aus
      - legt Ergebnis/Fehler ins result_q
    Hinweis: with_cryo_flag wirkt NUR bei tamed, ansonsten ignoriert.
    """
    t0 = time()
    try:
        export_folder.mkdir(parents=True, exist_ok=True)
        save = AsaSave(save_path)

        if t == "tamed":
            fname, cnt = export_tamed(save, export_folder, save_path, bool(with_cryo_flag))
        elif t == "players":
            fname, cnt = export_players(save, export_folder, save_path)
        elif t == "structures":
            fname, cnt = export_structures(save, export_folder, save_path)
        elif t == "wild":
            fname, cnt = export_wild(save, export_folder, save_path, max_level, max_level_bionic)
        else:
            raise ValueError(f"Unsupported export type: {t}")
        elapsed = time() - t0
        result_q.put({"type": t, "ok": True, "file": str(export_folder / fname), "count": cnt, "elapsed": elapsed, "error": None})
    except Exception as e:
        elapsed = time() - t0
        result_q.put({"type": t, "ok": False, "file": None, "count": 0, "elapsed": elapsed, "error": str(e)})

# ---------- Main ----------

def main() -> None:
    global_start = time()

    requested = ["tamed", "structures", "wild"]
    save_path = Path(r"C:\Users\Vincent\Downloads\Astraeos_WP\Astraeos_WP.ark")
    export_folder = Path.cwd() / "pleinx"

    results: List[Tuple[str, int]] = []

    if 1 and len(requested) > 1:
        # Paralleler Modus: Einmal-Prozesse, die sich nach Fertigstellung direkt beenden
        ctx = get_mp_context()
        result_q: mp.Queue = ctx.Queue()

        # Prozesse in priorisierter Reihenfolge starten
        
        procs: List[mp.Process] = []
        for t in requested:
            p = ctx.Process(
                target=child_worker,
                args=(t, save_path, export_folder, 150, 180, 1, result_q),
            )
            p.start()
            procs.append(p)

        finished = 0
        total = len(procs)
        while finished < total:
            msg = result_q.get()  # blockiert bis ein Ergebnis kommt
            t = msg["type"]
            if msg["ok"]:
                results.append((Path(msg["file"]).name, msg["count"]))
                print(f"[OK][{t}] Wrote {msg['count']:>6} entries in {msg['elapsed']:.2f} secs -> {msg['file']}")
            else:
                print(f"[ERR][{t}] in {msg['elapsed']:.2f} secs -> {msg['error']}")
            finished += 1

        # Aufräumen (sicherstellen, dass alle Prozesse beendet sind)
        for p in procs:
            p.join()

    else:
        # Seriell: Save einmal laden und wiederverwenden (ressourcenschonend)
        save = AsaSave(save_path)

        for t in requested:
            t0 = time()
            if t == "tamed":
                res = export_tamed(save, export_folder, save_path, True)
            elif t == "structures":
                res = export_structures(save, export_folder, save_path)
            elif t == "players":
                res = export_players(save, export_folder, save_path)
            elif t == "wild":
                res = export_wild(save, export_folder, save_path, 200, 200)
            else:
                raise ValueError(f"Unsupported export type: {t}")
            elapsed = time() - t0
            results.append(res)
            print(f"[OK][{t}] Wrote {res[1]:>6} entries in {elapsed:.2f} secs -> {export_folder / res[0]}")

    # Zusammenfassung
    total_entries = sum(c for _, c in results)
    took = time() - global_start
    print(f"Finished {len(results)} export(s), total entries: {total_entries}, runtime: {took:.2f}s")


if __name__ == "__main__":
    from arkparse.logging import ArkSaveLogger
    ArkSaveLogger.disable_all_logs()
    mp.freeze_support()
    main()