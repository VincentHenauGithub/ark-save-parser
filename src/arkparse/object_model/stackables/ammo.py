
from uuid import UUID

from arkparse import AsaSave
from arkparse.object_model.stackables._stackable import Stackable
from arkparse.parsing import ArkBinaryParser

class Ammo(Stackable):
    def __init__(self, uuid: UUID, binary: ArkBinaryParser):
        super().__init__(uuid, binary)

    def __str__(self):
        return super().to_string("Ammo")
    
    @staticmethod
    def generate_from_template(class_: str, save: AsaSave, owner_inventory_uuid: UUID):
        uuid, parser = Stackable._generate(save)
        parser.replace_bytes(uuid.bytes, position=len(parser.byte_buffer) - 16)
        rsrc = Ammo(uuid, save)
        rsrc.replace_uuid(owner_inventory_uuid, rsrc.owner_inv_uuid)
        rsrc.reidentify(uuid, class_)
        return rsrc

    
