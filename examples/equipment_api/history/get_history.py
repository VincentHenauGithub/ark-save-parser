import json
import sys
from pathlib import Path
from uuid import UUID
from typing import Dict, Set
from datetime import datetime

from arkparse import AsaSave
from arkparse.api import EquipmentApi, PlayerApi
from arkparse.object_model.equipment.__equipment import Equipment
from arkparse.object_model.equipment import Weapon, Armor, Saddle, Shield
from arkparse.enums import ArkItemQuality
from arkparse.logging import ArkSaveLogger


ArkSaveLogger.disable_all_logs()

# Setup log file
log_file_path = Path(__file__).parent / f"equipment_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file = open(log_file_path, 'w', encoding='utf-8')

def log(msg: str, end='\n'):
    """Print to both console and log file."""
    print(msg, end=end, flush=True)
    log_file.write(msg + end)
    log_file.flush()

# Load ark file paths from json
with open(Path(__file__).parent / "ark_files.json", "r") as f:
    ark_files = json.load(f)

quality_limit = 2
tribe_filter = "Strahds Entourage"

def get_equipment_snapshot(save_path: Path) -> Dict[str, dict]:
    """Get all equipment with rating > quality_limit from a save file.
    Returns dict keyed by item string representation (content-based) instead of UUID."""
    save = AsaSave(save_path)
    equipment_api = EquipmentApi(save)
    player_api = PlayerApi(save)
    
    weapons: Dict[UUID, Weapon] = equipment_api.get_all(EquipmentApi.Classes.WEAPON)
    armors: Dict[UUID, Armor] = equipment_api.get_all(EquipmentApi.Classes.ARMOR)
    shields: Dict[UUID, Shield] = equipment_api.get_all(EquipmentApi.Classes.SHIELD)
    saddles: Dict[UUID, Saddle] = equipment_api.get_all(EquipmentApi.Classes.SADDLE)
    
    snapshot = {}
    for d in [weapons, armors, shields, saddles]:
        d: Dict[UUID, Equipment]
        for key, value in d.items():
            if value.rating > quality_limit:
                value.get_owner(player_api)
                tribe_name = value.tribe.name if value.tribe else "Unknown"
                
                # Filter by tribe
                if tribe_name != tribe_filter:
                    continue
                
                # Use string representation as key to identify identical items
                item_key = str(value)
                snapshot[item_key] = {
                    'type': type(value).__name__,
                    'name': value.get_short_name(),
                    'rating': value.rating,
                    'quality': ArkItemQuality(value.quality).name,
                    'is_bp': value.is_bp,
                    'tribe': tribe_name,
                    'avg_stat': value.get_average_stat(),
                    'str': str(value)
                }
    return snapshot


def print_diff(prev_snapshot: Dict[str, dict], curr_snapshot: Dict[str, dict], save_name: str):
    """Print differences between two snapshots."""
    prev_keys: Set[str] = set(prev_snapshot.keys())
    curr_keys: Set[str] = set(curr_snapshot.keys())
    
    added = curr_keys - prev_keys
    removed = prev_keys - curr_keys
    
    if not added and not removed:
        return False  # No changes
    
    log(f"\n{'='*60}")
    log(f"SAVE: {save_name}")
    log(f"{'='*60}")
    
    if added:
        log(f"\n  [+] ADDED ({len(added)}):")
        for item_key in sorted(added, key=lambda k: (curr_snapshot[k]['quality'], curr_snapshot[k]['rating']), reverse=True):
            eq = curr_snapshot[item_key]
            bp_str = " [BP]" if eq['is_bp'] else ""
            log(f"      {eq['str']}{bp_str}")
    
    if removed:
        log(f"\n  [-] REMOVED ({len(removed)}):")
        for item_key in sorted(removed, key=lambda k: (prev_snapshot[k]['quality'], prev_snapshot[k]['rating']), reverse=True):
            eq = prev_snapshot[item_key]
            bp_str = " [BP]" if eq['is_bp'] else ""
            log(f"      {eq['str']}{bp_str}")
    
    return True


# Process all saves and track progression
prev_snapshot = {}
changes_found = 0

for i, ark_path in enumerate(ark_files):
    save_name = Path(ark_path).stem
    log(f"\rProcessing {i+1}/{len(ark_files)}: {save_name}...", end="")
    
    try:
        curr_snapshot = get_equipment_snapshot(Path(ark_path))
        
        if i == 0:
            # First save - show initial state
            log(f"\n{'='*60}")
            log(f"INITIAL STATE: {save_name}")
            log(f"Tribe: {tribe_filter}")
            log(f"{'='*60}")
            log(f"  Total equipment with rating > {quality_limit}: {len(curr_snapshot)}")
            
            # Show all items
            items = list(curr_snapshot.values())
            log(f"\n  All items:")
            for eq in sorted(items, key=lambda x: (x['quality'], x['rating']), reverse=True):
                bp_str = " [BP]" if eq['is_bp'] else ""
                log(f"      {eq['str']}{bp_str}")
        else:
            # Subsequent saves - show diff only
            if print_diff(prev_snapshot, curr_snapshot, save_name):
                changes_found += 1
        
        prev_snapshot = curr_snapshot
        
    except Exception as e:
        log(f"\n  ERROR processing {save_name}: {e}")

log(f"\n\n{'='*60}")
log(f"SUMMARY ({tribe_filter}): {changes_found} saves had equipment changes (rating > {quality_limit})")
log(f"Final equipment count: {len(prev_snapshot)}")
log(f"{'='*60}")

log_file.close()
print(f"\nLog saved to: {log_file_path}")
