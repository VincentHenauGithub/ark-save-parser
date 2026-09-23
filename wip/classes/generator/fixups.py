"""Hand edits that sit alongside the generated content, re-applied after a rebuild.

The generator only ever adds blueprints it has not seen before, so renaming or
regrouping what it wrote earlier means resetting the target modules to their
pre-generation state and building again. These are the handful of by-hand
corrections that reset would otherwise throw away.

``prepare`` runs before the build (it renames a class the generator needs to be
able to name unambiguously); ``apply`` runs after it.

Each is idempotent: applying it twice is a no-op.
"""

from pathlib import Path

CLASSES_DIR = Path(__file__).resolve().parents[3] / "src" / "arkparse" / "classes"

# (module, before, after, why). `before` must appear exactly once.
FIXUPS = [
    ("placed_structures.py",
     "all_bps = stone.all_bps + metal.all_bps + thatch.all_bps + tek.all_bps",
     "all_bps = stone.all_bps + metal.all_bps + thatch.all_bps + adobe.all_bps + tek.all_bps",
     "Adobe was defined but never rolled up"),

    ("dinos.py",
     '    rex = "/PA_EVO_Pack_01/Dinos/EVO_Rex/Paleo/EVO_Paleo_Rex_Character_BP',
     '    paleo_rex = "/PA_EVO_Pack_01/Dinos/EVO_Rex/Paleo/EVO_Paleo_Rex_Character_BP',
     "Paleo.rex was defined twice, shadowing the first blueprint"),
    ("dinos.py",
     "               giga, rex, legacy_rex, rex, mosa, deinotherium]",
     "               giga, rex, legacy_rex, paleo_rex, mosa, mosa2, deinotherium]",
     "...and Paleo.all_bps had lost mosa2 with it"),

    ("equipment.py",
     '    tranq_dart: str = "/Game/PrimalEarth/CoreBlueprints/Weapons/PrimalItemAmmo_AggroTranqDart',
     '    aggro_tranq_dart: str = "/Game/PrimalEarth/CoreBlueprints/Weapons/PrimalItemAmmo_AggroTranqDart',
     "Ammo.tranq_dart was defined twice, shadowing AggroTranqDart"),
    ("equipment.py",
     "all_bps = [zipline, advanced_bullet, advanced_rifle_bullet, advanced_sniper_bullet, tranq_dart,",
     "all_bps = [zipline, advanced_bullet, advanced_rifle_bullet, advanced_sniper_bullet, aggro_tranq_dart,",
     "...and Ammo.all_bps referred to the shadowed name"),
    ("equipment.py",
     "    all_bps = [shield, cannon]",
     "    # Not backpacks: excluded from all_bps so the armour lookup stays correct.\n"
     "    extras = [missile_pod, transformer]\n\n"
     "    all_bps = [shield, cannon]",
     "Mek's pod and transformer are real blueprints, just not backpacks"),
]

# Gear pieces the dumps turned up that belong with the other companion gear
# rather than in Misc, keyed by the attribute the generator gave them.
GEAR = {
    "dino_companion_gear_chibi_basket": "chibi_basket",
    "dino_companion_gear_spyglass": "spyglass",
}


def _move_gear(text):
    """Move newly dumped companion gear from Misc into ArmaDoggoGear.gear."""
    for generated, attr in GEAR.items():
        line = next((l for l in text.split("\n") if l.strip().startswith(generated + ":")), None)
        if line is None:
            continue
        path = line.split('"')[1]
        text = text.replace(line + "\n", "")
        text = text.replace('    bait_trap: str = "',
                            f'    {attr}: str = "{path}"\n    bait_trap: str = "')
        text = text.replace(", " + generated, "")
        text = text.replace(generated + ", ", "")
    text = text.replace("            camping_gear, picnic_set, battle_spikes, bait_trap]",
                        "            camping_gear, picnic_set, battle_spikes, chibi_basket,\n"
                        "            spyglass, bait_trap]")
    # Roll the two deliberately-excluded lists into the module total, so a save
    # dump comes back clean without changing what counts as armour.
    old = "mek.all_bps + arma_doggo_gear.all_bps"
    if old in text:
        text = text.replace(old, "mek.all_bps + mek.extras + \\\n            "
                                 "arma_doggo_gear.all_bps + arma_doggo_gear.gear")
    return text


def prepare():
    """Edits that have to be in place before the generator runs.

    equipment.py declared two classes called Misc -- one for odd armour, one
    for tools -- and the second silently shadowed the first at module level.
    Anything appending to "Misc" would have hit the armour one and leaked
    weapons into Armor.all_bps, which the armour-rating lookup reads. The tools
    one becomes Tools; Equipment.misc still points at it, so nothing downstream
    changes.
    """
    path = CLASSES_DIR / "equipment.py"
    text = path.read_text(encoding="utf-8")
    if "class Tools:" in text:
        return
    head, sep, tail = text.rpartition("class Misc:")
    assert sep, "equipment.py: no Misc class to rename"
    text = head + "class Tools:" + tail
    old, new = "    misc: Misc = Misc()", "    misc: Tools = Tools()"
    head, sep, tail = text.rpartition(old)
    assert sep, "equipment.py: Equipment.misc not found"
    path.write_text(head + new + tail, encoding="utf-8")
    print(f"  {'equipment.py':24s} tools Misc renamed to Tools (it shadowed the armour Misc)")


def apply():
    for module, before, after, why in FIXUPS:
        path = CLASSES_DIR / module
        text = path.read_text(encoding="utf-8")
        if after in text:
            continue
        assert text.count(before) == 1, f"{module}: {text.count(before)} matches for {why}"
        path.write_text(text.replace(before, after), encoding="utf-8")
        print(f"  {module:24s} {why}")

    path = CLASSES_DIR / "equipment.py"
    path.write_text(_move_gear(path.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"  {'equipment.py':24s} companion gear moved out of Misc")


if __name__ == "__main__":
    prepare()
    apply()
