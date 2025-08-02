from typing import Dict, List
from uuid import UUID, uuid4
from pathlib import Path
import json
from importlib.resources import files

from arkparse import Classes
from arkparse import AsaSave
import arkparse.parsing.struct as structs
from arkparse.object_model.stackables import Ammo, Resource
from arkparse.object_model.stackables._stackable import Stackable
from arkparse.object_model.structures import Structure, StructureWithInventory
from arkparse.parsing.struct.actor_transform import ActorTransform
from arkparse.object_model.misc.object_owner import ObjectOwner
from arkparse.logging import ArkSaveLogger
import random

class Base:
    structures: Dict[UUID, Structure]
    location: ActorTransform
    keystone: Structure
    owner: ObjectOwner
    nr_of_turrets: int

    class TurretType:
        AUTO = Classes.structures.placed.turrets.auto
        HEAVY = Classes.structures.placed.turrets.heavy
        TEK = Classes.structures.placed.turrets.tek
        ALL = [AUTO, HEAVY, TEK]

    class GeneratorType:
        TEK = Classes.structures.placed.tek.generator
        ELECTRIC = Classes.structures.placed.metal.generator
        ALL = [TEK, ELECTRIC]

    stack_sizes = {
        Classes.resources.Crafted.gasoline: 100,
        Classes.resources.Basic.element: 100,
        Classes.equipment.ammo.advanced_rifle_bullet: 100,
        Classes.resources.Basic.element_shard: 1000
    }

    def __determine_location(self):
        average_x = 0
        average_y = 0
        average_z = 0

        for _, structure in self.structures.items():
            average_x += structure.location.x
            average_y += structure.location.y
            average_z += structure.location.z

        average_x /= len(self.structures)
        average_y /= len(self.structures)
        average_z /= len(self.structures)

        self.location = structs.ActorTransform(vector=structs.ArkVector(x=average_x, y=average_y, z=average_z))

    def __init__(self, keystone: UUID = None, structures: Dict[UUID, Structure] = None):
        self.structures = structures
        if self.structures is not None:
            self.__determine_location()
        self.set_keystone(keystone)
        self.__count_turrets()

    def __serialize(self):
        return {
            "location": self.location.as_json(),
            "keystone": str(self.keystone.object.uuid),
            "owner": self.owner.serialize(),
            "nr_of_turrets": self.nr_of_turrets,
        }
    
    def __count_turrets(self):
        count = 0
        for _, structure in self.structures.items():
            if structure.object.blueprint in [Classes.structures.placed.turrets.heavy,
                                              Classes.structures.placed.turrets.tek]:
                count += 1
            elif structure.object.blueprint == Classes.structures.placed.turrets.auto:
                count += 0.25
        self.nr_of_turrets = count

    def set_keystone(self, keystone: UUID):
        if keystone is not None:
            self.keystone = self.structures[keystone]
            self.location = self.keystone.location
            self.owner = self.keystone.owner
        else:
            self.keystone = None
            self.owner = None

    def move_to(self, new_location: ActorTransform, save: AsaSave = None):
        offset_x = new_location.x - self.location.x
        offset_y = new_location.y - self.location.y
        offset_z = new_location.z - self.location.z

        for _, structure in self.structures.items():
            structure.location.update(structure.location.x + offset_x, structure.location.y + offset_y, structure.location.z + offset_z)

        if save is not None:
            for _, structure in self.structures.items():
                save.modify_actor_transform(structure.object.uuid, structure.location.to_bytes())

    def set_owner(self, new_owner: ObjectOwner):
        for uuid, structure in self.structures.items():
            # print(f"Setting owner {new_owner} for structure {structure.object.uuid}")
            structure.owner.replace_self_with(new_owner, structure.binary)
            structure.update_binary()

    def store_binary(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "base.json", "w") as f:
            json.dump(self.__serialize(), f, indent=4)
        for _, structure in self.structures.items():
            structure.store_binary(path)

    def set_turret_ammo(self, save: AsaSave, bullets_in_heavy: int = 1, bullets_in_auto: int = 1, shards_in_tek: int = 1):
        amount = 0
        bullet = ""
        turrets = self.get_turrets()
    
        for turret in turrets:
            inventory = turret.inventory
            
            if inventory is None:
                raise Exception(f"{turret.get_short_name()} {turret.object.uuid} has no inventory")
            
            if turret.object.blueprint == Classes.structures.placed.turrets.heavy:
                bullet = Classes.equipment.ammo.advanced_rifle_bullet
                amount = bullets_in_heavy
            elif turret.object.blueprint == Classes.structures.placed.turrets.auto:
                bullet = Classes.equipment.ammo.advanced_rifle_bullet
                amount = bullets_in_auto
            elif turret.object.blueprint == Classes.structures.placed.turrets.tek:
                bullet = Classes.resources.Basic.element_shard
                amount = shards_in_tek

           
            ArkSaveLogger.objects_log(f"Padding {turret.get_short_name()} ({turret.object.uuid}) to {amount} bullets")
            self.__set_new_inventory(save, turret, bullet, amount)

            ArkSaveLogger.objects_log(f"Updating {turret.get_short_name()} and inventory in database")
            turret.update_binary()
            turret.inventory.update_binary()

        return len(turrets)
    
    def set_fuel_in_generators(self, save: AsaSave, nr_of_element: int = 1, nr_of_gasoline: int = 1) -> int:
        amount = 0
        generators: List[StructureWithInventory] = self.get_generators()

        for generator in generators:
            if not generator.inventory:
                raise Exception(f"Generators must have inventory!")
            
            # Reset the generators last checked fuel time to the current game time to prevent them from running out of fuel instantly
            generator.binary.replace_double(generator.object.find_property("LastCheckedFuelTime"), save.save_context.game_time)
            item_class = None
            if generator.object.blueprint == Classes.structures.placed.metal.generator:
                item_class = Classes.resources.Crafted.gasoline
                amount = nr_of_gasoline
            elif generator.object.blueprint == Classes.structures.placed.tek.generator:
                item_class = Classes.resources.Basic.element
                amount = nr_of_element

            ArkSaveLogger.objects_log(f"Adding fuel to generator {generator.object.uuid} (type={generator.get_short_name()})")
            self.__set_new_inventory(save, generator, item_class, amount)

            ArkSaveLogger.objects_log(f"Updating generator and inventory {generator.object.uuid} in database")
            generator.update_binary()
            generator.inventory.update_binary()

            ArkSaveLogger.objects_log(f"\n")

        return len(generators)
    
    def get_turrets(self, types: TurretType = TurretType.ALL) -> list[StructureWithInventory]:
        turrets = []
        for _, structure in self.structures.items():
            if structure.object.blueprint in types:
                turrets.append(structure)
        return turrets

    def get_generators(self, types: GeneratorType = GeneratorType.ALL) -> list[StructureWithInventory]:
        generators = []
        for _, structure in self.structures.items():
            if structure.object.blueprint in types:
                generators.append(structure)
        return generators
    
    def set_stack_sizes(self, advanced_rifle_bullet: int = 100, element: int = 100, element_shard: int = 1000, gasoline: int = 10):
        self.stack_sizes[Classes.resources.Crafted.gasoline] = gasoline
        self.stack_sizes[Classes.resources.Basic.element] = element
        self.stack_sizes[Classes.equipment.ammo.advanced_rifle_bullet] = advanced_rifle_bullet
        self.stack_sizes[Classes.resources.Basic.element_shard] = element_shard

    def __create_stack_item(self, save: AsaSave, item_class: str, quantity: int, parent_uuid: UUID) -> Stackable:
        """
        Creates a fuel item of the specified class and quantity.
        """
        stack: Stackable = None
        if item_class == Classes.resources.Crafted.gasoline:
            stack = Resource.generate_from_template(Classes.resources.Crafted.gasoline, save, parent_uuid)
        elif item_class == Classes.resources.Basic.element:
            stack = Resource.generate_from_template(Classes.resources.Basic.element, save, parent_uuid)
        elif item_class == Classes.equipment.ammo.advanced_rifle_bullet:
            stack = Ammo.generate_from_template(Classes.equipment.ammo.advanced_rifle_bullet, save, parent_uuid)
        elif item_class == Classes.resources.Basic.element_shard:
            stack = Resource.generate_from_template(Classes.resources.Basic.element_shard, save, parent_uuid)
        else:
            raise ValueError(f"Unknown fuel item class: {item_class}")

        stack.set_quantity(quantity)
        stack.update_binary()

        return stack
    
    def __set_new_inventory(self, save: AsaSave, structure: StructureWithInventory, item_class: str, quantity: int):
        stack_size = self.stack_sizes.get(item_class)
        space_available = True

        if not stack_size:
            raise ValueError(f"Unknown item class: {item_class}")
        
        previous_items = structure.inventory.items.copy()
        keep = list(previous_items.keys())[0]
        ArkSaveLogger.objects_log(f"Keeping item {keep} in inventory {structure.object.uuid} while adding new items, total original items: {len(previous_items)}")

        try:
            for key, _ in previous_items.items():
                if key != keep:
                    ArkSaveLogger.objects_log(f"Removing item {key} from inventory {structure.object.uuid} to make space for new items")
                    structure.inventory.remove_item(key)
                    save.remove_obj_from_db(key)

            num_full_stacks = quantity // stack_size
            remainder = quantity % stack_size
            if remainder == 0:
                remainder = stack_size
                num_full_stacks = num_full_stacks - 1

            ArkSaveLogger.objects_log(f"Adding {num_full_stacks} full stacks of {item_class} ({stack_size} each) and remainder {remainder} to inventory {structure.object.uuid}")

            if remainder > 0:
                stack = self.__create_stack_item(save, item_class, remainder, structure.object.uuid)
                structure.add_item(stack.object.uuid)

            if keep is not None:
                ArkSaveLogger.objects_log(f"Removing last original item {keep} in inventory {structure.object.uuid}")
                structure.inventory.remove_item(keep)
                save.remove_obj_from_db(keep)

            for _ in range(num_full_stacks):
                stack = self.__create_stack_item(save, item_class, stack_size, structure.object.uuid)
                space_available = structure.add_item(stack.object.uuid)

                if not space_available:
                    break

            if not space_available:
                ArkSaveLogger.objects_log(f"Inventory of {structure.object.uuid} is full at {structure.max_item_count} items, cannot add more ammo")
        except Exception as e:
            ArkSaveLogger.error_log(f"Error while setting new inventory for {structure.get_short_name()} ({structure.object.uuid}): {e}")
            raise e
