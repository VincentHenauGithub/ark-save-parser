import json
from uuid import UUID

from arkparse import AsaSave
from arkparse.logging.ark_save_logger import ArkSaveLogger
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.enums import ArkEquipmentStat
from arkparse.classes.equipment import Armor as ArmorBps, Shields as ShieldBps, Saddles as SaddleBps, Weapons, Misc

from .__equipment import Equipment
from ...utils.json_utils import DefaultJsonEncoder

_LOGGED_WARNINGS = set()

class EquipmentWithDurability(Equipment):
    durability: float = 0

    @staticmethod
    def get_default_dura(bp: str) -> float:
        if bp in ArmorBps.chitin.all_bps:
            return 50
        elif bp in ArmorBps.ghillie.all_bps or bp in ArmorBps.leather.all_bps or bp in ArmorBps.desert.all_bps:
            return 45
        elif bp in ArmorBps.fur.all_bps:
            return 125
        elif bp in ArmorBps.cloth.all_bps:
            return 25
        elif bp in ArmorBps.riot.all_bps or bp in ArmorBps.flak.all_bps or bp in ArmorBps.tek.all_bps:
            return 120
        elif bp in ArmorBps.scuba.pants:
            return 50
        elif bp in [ArmorBps.scuba.chest, ArmorBps.scuba.flippers, ArmorBps.scuba.goggles]:
            return 45
        elif bp in ArmorBps.hazard.all_bps:
            return 85.5
        elif bp == ShieldBps.metal:
            return 1250
        elif bp == ShieldBps.riot:
            return 2300
        elif bp == ShieldBps.wood:
            return 350
        elif bp == ArmorBps.misc.gas_mask:
            return 50
        elif bp == ArmorBps.misc.miners_helmet:
            return 120
        elif bp == ArmorBps.misc.night_vision_goggles:
            return 45
        elif bp in [SaddleBps.tapejara_tek, SaddleBps.rex_tek, SaddleBps.mosa_tek, SaddleBps.megalodon_tek,
                    SaddleBps.rock_drake_tek]:
            return 120
        elif bp == SaddleBps.mole_rat:
            return 500
        elif bp in SaddleBps.all_bps:
            return 100
        elif bp == Weapons.advanced.compound_bow:
            return 55
        elif bp == Weapons.primitive.sword:
            return 70
        elif bp == Misc.prod:
            return 10
        elif bp == Weapons.primitive.bow:
            return 50
        elif bp == Weapons.primitive.crossbow:
            return 100
        elif bp == Misc.harpoon:
            return 100
        elif bp == Weapons.primitive.simple_pistol:
            return 60
        elif bp == Weapons.advanced.longneck:
            return 70
        elif bp in [Weapons.primitive.shotgun, Weapons.advanced.chainsaw]:
            return 80
        elif bp == Weapons.advanced.fabricated_pistol:
            return 60
        elif bp == Weapons.advanced.fabricated_shotgun:
            return 120
        elif bp == Weapons.advanced.fabricated_sniper:
            return 70
        elif bp == Weapons.advanced.rocket_launcher:
            return 120
        elif bp == Weapons.advanced.tek_rifle:
            return 80
        elif bp in [Weapons.gathering.sickle, Weapons.gathering.metal_hatchet, Weapons.gathering.metal_pick, 
                    Weapons.gathering.stone_hatchet, Weapons.gathering.stone_pick, Weapons.gathering.fishing_rod,
                    Weapons.advanced.assault_rifle, Weapons.primitive.slingshot, Weapons.primitive.stone_club,
                    Weapons.primitive.pike, Weapons.primitive.lance, Weapons.advanced.flamethrower, Weapons.primitive.torch]:
            return 40
        elif bp == Misc.climb_pick:
            return 65
        else:
            if bp not in _LOGGED_WARNINGS:
                _LOGGED_WARNINGS.add(bp)
                print(f"WARNING: No durability found for {bp}, using default value of 1")
            return 1

    def __init_props__(self):
        super().__init_props__()
            
        dura = self.object.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)
        self.durability = self.get_actual_value(ArkEquipmentStat.DURABILITY, dura)

    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)

    def get_average_stat(self, __stats = []) -> float:
        return super().get_average_stat(__stats + [self.get_internal_value(ArkEquipmentStat.DURABILITY)])
    
    def get_implemented_stats(self) -> list:
        return [ArkEquipmentStat.DURABILITY]

    def get_internal_value(self, stat: ArkEquipmentStat) -> int:
        if stat == ArkEquipmentStat.DURABILITY:
            d = EquipmentWithDurability.get_default_dura(self.object.blueprint)
            value = int((self.durability - d)/(d*0.00025))
            return value if value >= d else d
        else:
            raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
        
    def get_actual_value(self, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.DURABILITY:
            d = EquipmentWithDurability.get_default_dura(self.object.blueprint)
            value = d * (0.00025*internal_value + 1)
            return value
        else:
            raise ValueError(f"Stat {stat} is not valid for {self.class_name}")
        
    def set_stat(self, stat: ArkEquipmentStat, value: float):
        if stat == ArkEquipmentStat.DURABILITY:
            self.__set_durability(value)
        else:
            raise ValueError(f"Stat {stat} is not valid for {self.class_name}")

    def __set_durability(self, durability: float):
        self.durability = durability
        clipped = self._set_internal_stat_value(self.get_internal_value(ArkEquipmentStat.DURABILITY), ArkEquipmentStat.DURABILITY)
        if clipped:
            self.durability = self.get_actual_value(ArkEquipmentStat.DURABILITY, 65535)
            ArkSaveLogger.warning_log(f"Durability value clipped to {self.durability} for {self.object.blueprint}")

    def _get_stat_for_rating(self, stat: ArkEquipmentStat, rating: float, multiplier: float) -> float:
        if stat == ArkEquipmentStat.DURABILITY:
            return round(rating / multiplier, 1)
        else:
            return super()._get_stat_for_rating(stat, rating, multiplier)

    def to_json_obj(self):
        json_obj = super().to_json_obj()
        json_obj["Durability"] = self.durability
        return json_obj

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder)
