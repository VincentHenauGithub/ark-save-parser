"""Correctness check for selective parsing: a selective parse must yield identical
results for the properties it selected, compared against a full parse of the same
save. Run this against any save you care about before trusting a new selection.

usage: python verify_selective_parsing.py [save.ark]
"""
import sys
from pathlib import Path

from arkparse import AsaSave
from arkparse.api.dino_api import DinoApi
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.logging import ArkSaveLogger

ArkSaveLogger.allow_invalid_objects(True)
SAVE = Path(r"D:\ARK servers\Ascended\arkparse\tests\test_data\set_2\Ragnarok_WP\Ragnarok_WP.ark")

SEL = [
    "bIsFemale", "DinoID1", "DinoID2", "GeneTraits", "bIsDead",
    "SavedBaseWorldLocation", "MyCharacterStatusComponent", "Owner",
    "TamedName", "TamerString", "TamingTeamID", "TargetingTeam", "TamedTimeStamp",
    "OwningPlayerID", "OwningPlayerName", "MyInventoryComponent", "bIsBaby", "BabyAge",
    "BaseCharacterLevel", "DinoImprintingQuality",
    "NumberOfLevelUpPointsApplied", "NumberOfLevelUpPointsAppliedTamed",
    "NumberOfMutationsAppliedTamed", "CurrentStatusValues",
]
SELSET = set(SEL)
bp = DinoApi._DEFAULT_CONFIG.blueprint_name_filter


def snapshot(objs, only=None):
    out = {}
    for uid, o in objs.items():
        props = {}
        for p in o.properties:
            if only is not None and p.name not in only:
                continue
            props.setdefault(p.name, []).append((p.type, repr(p.value), p.nr_of_bytes))
        out[uid] = (o.blueprint, props)
    return out


s1 = AsaSave(SAVE)
full = snapshot(s1.get_game_objects(GameObjectReaderConfiguration(blueprint_name_filter=bp)), only=SELSET)
s1.close()

s2 = AsaSave(SAVE)
sel = snapshot(s2.get_game_objects(
    GameObjectReaderConfiguration(blueprint_name_filter=bp, selected_property_names=SEL)))
s2.close()

errors = []
if set(full) != set(sel):
    errors.append(f"object sets differ: full={len(full)} sel={len(sel)} "
                  f"missing={len(set(full) - set(sel))} extra={len(set(sel) - set(full))}")

checked_objs = 0
checked_props = 0
for uid in set(full) & set(sel):
    bp_f, pf = full[uid]
    bp_s, ps = sel[uid]
    checked_objs += 1
    if bp_f != bp_s:
        errors.append(f"{uid}: blueprint {bp_f!r} != {bp_s!r}")
    if set(pf) != set(ps):
        errors.append(f"{uid} ({bp_f}): selected property names differ: "
                      f"only_full={sorted(set(pf) - set(ps))} only_sel={sorted(set(ps) - set(pf))}")
        continue
    for name in pf:
        checked_props += 1
        if pf[name] != ps[name]:
            errors.append(f"{uid} ({bp_f}) prop {name}: {pf[name]} != {ps[name]}")

print(f"objects compared: {checked_objs}, selected properties compared: {checked_props}")
if errors:
    print(f"MISMATCHES: {len(errors)}")
    for e in errors[:25]:
        print("  " + e)
    sys.exit(1)
print("PASS: selective parse matches full parse for every selected property")
