import json
import math
from pathlib import Path
from typing import Dict, Any
from uuid import UUID

from arkparse.logging import ArkSaveLogger
from arkparse.object_model.dinos import Dino
from arkparse.object_model.equipment import Weapon, Shield, Armor, Saddle
from arkparse.object_model.equipment.__equipment_with_armor import EquipmentWithArmor
from arkparse.object_model.equipment.__equipment_with_durability import EquipmentWithDurability
from arkparse.object_model.structures import Structure, StructureWithInventory
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.api import EquipmentApi, PlayerApi, StructureApi, DinoApi
from arkparse.parsing import ArkBinaryParser
from arkparse.parsing.struct.ark_item_net_id import ArkItemNetId
from arkparse.parsing.struct import ActorTransform
from arkparse.parsing.struct import ObjectReference
from arkparse.saves.asa_save import AsaSave
from arkparse.saves.save_connection import SaveConnection
from arkparse.utils.json_utils import DefaultJsonEncoder

from arkparse.enums import ArkEquipmentStat
from arkparse.object_model.equipment.__armor_defaults import _get_default_hypoT, _get_default_hyperT

class JsonApi:
    def __init__(self, save: AsaSave, ignore_error: bool = False):
        self.save = save
        self.ignore_error = ignore_error

    def __del__(self):
        self.save = None

    # -----------------
    # UTILITY FUNCTIONS
    # -----------------

    @staticmethod
    def get_actual_value(obj: ArkGameObject, stat: ArkEquipmentStat, internal_value: int) -> float:
        if stat == ArkEquipmentStat.ARMOR:
            d = EquipmentWithArmor.get_default_armor(obj.blueprint)
            return round(d * (0.0002 * internal_value + 1), 1)
        elif stat == ArkEquipmentStat.DURABILITY:
            d = EquipmentWithDurability.get_default_dura(obj.blueprint)
            return d * (0.00025 * internal_value + 1)
        elif stat == ArkEquipmentStat.DAMAGE:
            return round(100.0 + internal_value / 100, 1)
        elif stat == ArkEquipmentStat.HYPOTHERMAL_RESISTANCE:
            if internal_value == 0:
                return 0
            d = _get_default_hypoT(obj.blueprint)
            return round(d * (0.0002 * internal_value + 1), 1)
        elif stat == ArkEquipmentStat.HYPERTHERMAL_RESISTANCE:
            if internal_value == 0:
                return 0
            d = _get_default_hyperT(obj.blueprint)
            return round(d * (0.0002 * internal_value + 1), 1)
        else:
            return 0

    @staticmethod
    def primal_item_to_json_obj(obj: ArkGameObject):
        # Grab already set properties
        json_obj: Dict[str, Any] = {"UUID": obj.uuid.__str__(),
                                    "ClassName": "item",
                                    "ItemArchetype": obj.blueprint}

        # Grab item ID if it exists
        if obj.has_property("ItemID"):
            item_id: ArkItemNetId = obj.get_property_value("ItemID")
            if item_id is not None:
                json_obj["ItemID"] = item_id.to_json_obj()

        # Grab item owner inventory if it exists
        if obj.has_property("OwnerInventory"):
            owner_inv: ObjectReference = obj.get_property_value("OwnerInventory")
            if owner_inv is not None and owner_inv.value is not None:
                json_obj["OwnerInventoryUUID"] = owner_inv.value

        # Grab specific item stats
        if obj.has_property("ItemStatValues"):
            if "/PrimalItemArmor_" in obj.blueprint:
                armor = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.ARMOR.value, default=0)
                json_obj["Armor"] = JsonApi.get_actual_value(obj, ArkEquipmentStat.ARMOR, armor)
                dura = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.DURABILITY.value, default=0)
                json_obj["Durability"] = JsonApi.get_actual_value(obj, ArkEquipmentStat.DURABILITY, dura)
                if "Saddle" not in obj.blueprint:
                    hypo = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPOTHERMAL_RESISTANCE.value, default=0)
                    json_obj["HypothermalResistance"] = JsonApi.get_actual_value(obj, ArkEquipmentStat.HYPOTHERMAL_RESISTANCE, hypo)
                    hyper = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.HYPERTHERMAL_RESISTANCE.value, default=0)
                    json_obj["HyperthermalResistance"] = JsonApi.get_actual_value(obj, ArkEquipmentStat.HYPERTHERMAL_RESISTANCE, hyper)
            if "/PrimalItem_" in obj.blueprint:
                damage = obj.get_property_value("ItemStatValues", position=ArkEquipmentStat.DAMAGE.value, default=0)
                json_obj["Damage"] = JsonApi.get_actual_value(obj, ArkEquipmentStat.DAMAGE, damage)

        # Grab remaining properties if any
        if obj.properties is not None and len(obj.properties) > 0:
            for prop in obj.properties:
                if prop is not None and \
                        prop.name is not None and \
                        len(prop.name) > 0 and \
                        "ItemID" not in prop.name and \
                        "OwnerInventory" not in prop.name and \
                        "ItemStatValues" not in prop.name:
                    prop_value = obj.get_property_value(prop.name)
                    if "NextSpoilingTime" in prop.name or "SavedDurability" in prop.name:
                        if math.isnan(prop.value):
                            prop_value = None
                    json_obj[prop.name] = prop_value

        return json_obj

    # ----------------
    # EXPORT FUNCTIONS
    # ----------------

    def export_armors(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting armors...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get armors.
        armors: Dict[UUID, Armor] = equipment_api.get_all(EquipmentApi.Classes.ARMOR)

        # Format armors into JSON.
        all_armors = []
        for armor in armors.values():
            all_armors.append(armor.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "armors.json", "w") as text_file:
            text_file.write(json.dumps(all_armors, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Armors successfully exported.")

    def export_weapons(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting weapons...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get weapons.
        weapons: Dict[UUID, Weapon] = equipment_api.get_all(EquipmentApi.Classes.WEAPON)

        # Format weapons into JSON.
        all_weapons = []
        for weapon in weapons.values():
            all_weapons.append(weapon.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "weapons.json", "w") as text_file:
            text_file.write(json.dumps(all_weapons, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Weapons successfully exported.")

    def export_shields(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting shields...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get shields.
        shields: Dict[UUID, Shield] = equipment_api.get_all(EquipmentApi.Classes.SHIELD)

        # Format shields into JSON.
        all_shields = []
        for shield in shields.values():
            all_shields.append(shield.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "shields.json", "w") as text_file:
            text_file.write(json.dumps(all_shields, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Shields successfully exported.")

    def export_saddles(self, equipment_api: EquipmentApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting saddles...")

        # Get equipment API if not provided.
        if equipment_api is None:
            equipment_api = EquipmentApi(self.save)

        # Get saddles.
        saddles: Dict[UUID, Saddle] = equipment_api.get_all(EquipmentApi.Classes.SADDLE)

        # Format saddles into JSON.
        all_saddles = []
        for saddle in saddles.values():
            all_saddles.append(saddle.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "saddles.json", "w") as text_file:
            text_file.write(json.dumps(all_saddles, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Saddles successfully exported.")

    def export_player_pawns(self, player_api: PlayerApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting player pawns...")

        # Get player API if not provided.
        if player_api is None:
            player_api = PlayerApi(self.save, self.ignore_error)

        # Get player pawns.
        player_pawns: Dict[UUID, ArkGameObject] = player_api.pawns

        # Format player pawns into JSON.
        all_pawns = []
        for pawn_obj in player_pawns.values():
            # Grab already set properties
            pawn_data: Dict[str, Any] = { "UUID": pawn_obj.uuid.__str__(),
                                          "ClassName": "player",
                                          "ItemArchetype": pawn_obj.blueprint }

            # Grab pawn location if it exists
            if pawn_obj.has_property("SavedBaseWorldLocation"):
                pawn_location = ActorTransform(vector = pawn_obj.get_property_value("SavedBaseWorldLocation"))
                if pawn_location is not None:
                    pawn_data["ActorTransformX"] = pawn_location.x
                    pawn_data["ActorTransformY"] = pawn_location.y
                    pawn_data["ActorTransformZ"] = pawn_location.z

            # Grab pawn inventory UUID if it exists
            if pawn_obj.has_property("MyInventoryComponent"):
                inv_comp = pawn_obj.get_property_value("MyInventoryComponent")
                if inv_comp is not None and inv_comp.value is not None:
                    pawn_data["InventoryUUID"] = inv_comp.value

            # Grab pawn owner inventory UUID if it exists
            if pawn_obj.has_property("OwnerInventory"):
                owner_inv: ObjectReference = pawn_obj.get_property_value("OwnerInventory")
                if owner_inv is not None and owner_inv.value is not None:
                    pawn_data["OwnerInventoryUUID"] = owner_inv.value

            # Grab remaining properties if any
            if pawn_obj.properties is not None and len(pawn_obj.properties) > 0:
                for prop in pawn_obj.properties:
                    if prop is not None and \
                            prop.name is not None and \
                            len(prop.name) > 0 and \
                            "SavedBaseWorldLocation" not in prop.name and \
                            "MyInventoryComponent" not in prop.name and \
                            "OwnerInventory" not in prop.name:
                        pawn_data[prop.name] = pawn_obj.get_property_value(prop.name)

            all_pawns.append(pawn_data)

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "player_pawns.json", "w") as text_file:
            text_file.write(json.dumps(all_pawns, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Player pawns successfully exported.")

    def export_players(self, player_api: PlayerApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting players...")

        # Get player API if not provided.
        if player_api is None:
            player_api = PlayerApi(self.save, self.ignore_error)

        # Format players into JSON.
        all_players = []
        for player in player_api.players:
            player_json_obj = player.to_json_obj()
            found: bool = False
            for p in player_api.pawns.values():
                uniqueid = p.get_property_value("PlatformProfileID", None)
                if uniqueid is not None and hasattr(uniqueid, "value") and player.unique_id == uniqueid.value:
                    found = True
                    break
            player_json_obj["FoundOnMap"] = found
            all_players.append(player_json_obj)

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "players.json", "w") as text_file:
            text_file.write(json.dumps(all_players, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Players successfully exported.")

    def export_tribes(self, player_api: PlayerApi = None, export_folder_path: str = Path.cwd() / "json_exports", include_players_data: bool = False):
        ArkSaveLogger.api_log("Exporting tribes...")

        # Get player API if not provided.
        if player_api is None:
            player_api = PlayerApi(self.save, self.ignore_error)

        # Format tribes into JSON.
        all_tribes = []
        for tribe in player_api.tribes:
            # Grab the tribe json object
            tribe_json_obj = tribe.to_json_obj()
            # Grab tribe members as json objects if they exists
            tribe_members = []
            for p in player_api.tribe_to_player_map[tribe.tribe_id]:
                if include_players_data:
                    player_json_obj = p.to_json_obj()
                else:
                    player_json_obj = { "PlayerCharacterName": p.char_name, "PlayerDataID": p.id_ }
                player_json_obj["IsActive"] = True
                tribe_members.append(player_json_obj)
            for idx, p_id in enumerate(tribe.member_ids):
                is_active = False
                for pl in player_api.tribe_to_player_map[tribe.tribe_id]:
                    if pl.id_ == p_id:
                        is_active = True
                if not is_active:
                    tribe_members.append({ "PlayerCharacterName": tribe.members[idx], "PlayerDataID": p_id, "IsActive": False })
            tribe_json_obj["TribeMembers"] = tribe_members
            # Add to the tribes array
            all_tribes.append(tribe_json_obj)

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "tribes.json", "w") as text_file:
            text_file.write(
                json.dumps(all_tribes, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Tribes successfully exported.")

    def export_dinos(self, dino_api: DinoApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting dinos...")

        # Get dino API if not provided.
        if dino_api is None:
            dino_api = DinoApi(self.save)

        # Get dinos.
        dinos: Dict[UUID, Dino] = dino_api.get_all()

        # Format dinos into JSON.
        all_dinos = []
        for dino in dinos.values():
            all_dinos.append(dino.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "dinos.json", "w") as text_file:
            text_file.write(json.dumps(all_dinos, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Dinos successfully exported.")

    def export_structures(self, structure_api: StructureApi = None, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting structures...")

        # Get structure API if not provided.
        if structure_api is None:
            structure_api = StructureApi(self.save)

        # Get structures.
        structures: dict[UUID, Structure | StructureWithInventory] = structure_api.get_all()

        # Format dinos into JSON.
        all_structures = []
        for structure in structures.values():
            all_structures.append(structure.to_json_obj())

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "structures.json", "w") as text_file:
            text_file.write(json.dumps(all_structures, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Structures successfully exported.")

    def export_items(self, export_folder_path: str = Path.cwd() / "json_exports", include_engrams: bool = False):
        ArkSaveLogger.api_log("Exporting items...")

        # Parse and format items as JSON.
        all_items = []
        query = "SELECT key, value FROM game"
        with self.save.save_connection.connection as conn:
            cursor = conn.execute(query)
            for row in cursor:
                try:
                    obj_uuid = SaveConnection.byte_array_to_uuid(row[0])
                    byte_buffer = ArkBinaryParser(row[1], self.save.save_context)
                    class_name = byte_buffer.read_name()

                    if "/PrimalItemArmor_" not in class_name and \
                            "/PrimalItem_" not in class_name and \
                            "/PrimalItemAmmo_" not in class_name and \
                            "/PrimalItemC4Ammo" not in class_name and \
                            "/PrimalItemResource_" not in class_name and \
                            "/DroppedItemGeneric_" not in class_name and \
                            "/PrimalItemConsumable_" not in class_name:
                        continue

                    obj = SaveConnection.parse_as_predefined_object(obj_uuid, class_name, byte_buffer)
                    if obj is not None:
                        is_engram = False
                        if obj.has_property("bIsEngram"):
                            is_engram = obj.get_property_value("bIsEngram", False)
                        if is_engram and not include_engrams:
                            continue
                        all_items.append(JsonApi.primal_item_to_json_obj(obj))
                except Exception as e:
                    if ArkSaveLogger._allow_invalid_objects:
                        ArkSaveLogger.error_log(f"Failed to parse item {UUID(row[0])}: {e}")
                    else:
                        raise e

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "items.json", "w") as text_file:
            text_file.write(json.dumps(all_items, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Items successfully exported.")

    def export_save_file_info(self, export_folder_path: str = Path.cwd() / "json_exports"):
        ArkSaveLogger.api_log("Exporting save file info...")

        save_info = { "MapName": self.save.save_context.map_name, "GameTime": self.save.save_context.game_time, "CurrentDay": self.save.save_context.current_day, "CurrentTime": self.save.save_context.current_time }

        # Create json exports folder if it does not exist.
        path_obj = Path(export_folder_path)
        if not (path_obj.exists() and path_obj.is_dir()):
            path_obj.mkdir(parents=True, exist_ok=True)

        # Write JSON.
        with open(path_obj / "save_info.json", "w") as text_file:
            text_file.write(json.dumps(save_info, default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None, indent=4, cls=DefaultJsonEncoder))

        ArkSaveLogger.api_log("Save file info successfully exported.")

    def export_all(self,
                   equipment_api: EquipmentApi = None,
                   player_api: PlayerApi = None,
                   dino_api: DinoApi = None,
                   structure_api: StructureApi = None,
                   export_folder_path: str = Path.cwd() / "json_exports"):
        self.export_save_file_info(export_folder_path=export_folder_path)
        self.export_armors(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_weapons(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_shields(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_saddles(equipment_api=equipment_api, export_folder_path=export_folder_path)
        self.export_items(export_folder_path=export_folder_path)
        self.export_structures(structure_api=structure_api, export_folder_path=export_folder_path)
        self.export_dinos(dino_api=dino_api, export_folder_path=export_folder_path)
        self.export_player_pawns(player_api=player_api, export_folder_path=export_folder_path)
        self.export_players(player_api=player_api, export_folder_path=export_folder_path)
        self.export_tribes(player_api=player_api, export_folder_path=export_folder_path)
