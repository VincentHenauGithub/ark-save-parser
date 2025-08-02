
from uuid import UUID

from arkparse import AsaSave
from arkparse.object_model.stackables._stackable import Stackable
from arkparse.parsing import ArkBinaryParser

class Resource(Stackable):
    def __init__(self, uuid: UUID, save: AsaSave):
        super().__init__(uuid, save)

    def __str__(self):
        return super().to_string("Resource")
    
    @staticmethod
    def generate_from_template(class_: str, save: AsaSave, owner_inventory_uuid: UUID):
        uuid, _ = Stackable._generate(save)
        rsrc = Resource(uuid, save)
        name_id = save.save_context.get_name_id(class_) # gnerate name id if needed
        if name_id is None:
            save.add_name_to_name_table(class_)
        rsrc.replace_uuid(owner_inventory_uuid, rsrc.owner_inv_uuid)
        rsrc.reidentify(uuid, class_)
        return rsrc
    
