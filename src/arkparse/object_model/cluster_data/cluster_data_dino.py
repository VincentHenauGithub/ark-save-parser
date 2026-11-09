import json

from arkparse.object_model.dinos.tamed_dino import TamedDino
from arkparse.parsing.ark_property_container import ArkPropertyContainer
from arkparse.parsing.ark_archive import ArkArchive
from arkparse.classes import Dinos
from arkparse.utils.json_utils import DefaultJsonEncoder


class ClusterDataDino:

    def __init__(self, cluster_dino_data: ArkPropertyContainer, dino_index: int):
        self._data = cluster_dino_data
        self._dino_index = dino_index
        self._actual_dino_data = bytes(cluster_dino_data.get_property_value("DinoData"))
        self._dino_obj = None
        self._status_obj = None
        self._ai_controller_obj = None
        self._inv_obj = None
        self.version = cluster_dino_data.get_property_value("Version")
        self.upload_time = cluster_dino_data.get_property_value("UploadTime")

        if self.version != 7:
            raise ValueError(f"Unsupported cluster dino data version: {self.version} for dino index {dino_index}")

        # temp write binary
        self._archive = ArkArchive(self._actual_dino_data, from_store=False, cluster_dino=True)
        for obj in self._archive.objects:
            # print(obj.class_name)
            if obj.class_name in Dinos.all_bps:
                # print(f"Found dino archetype: {obj.class_name}")
                self._dino_obj = obj
            if "CharacterStatusComponent" in obj.class_name:
                # print(f"Found status component: {obj.class_name}")
                self._status_obj = obj
            if "AIController" in obj.class_name:
                # print(f"Found AI controller: {obj.class_name}")
                self._ai_controller_obj = obj
            if "InventoryComponent" in obj.class_name:
                # print(f"Found inventory component: {obj.class_name}")
                self._inv_obj = obj

        if self._dino_obj is None:
            raise ValueError(f"Could not find dino archetype in cluster dino data for dino index {dino_index}")
        
        if self._status_obj is None:
            raise ValueError(f"Could not find status component in cluster dino data for dino index {dino_index}")
        
        self.dino = TamedDino.from_object(self._dino_obj, self._status_obj)
        if self._ai_controller_obj:
            self.dino.ai_controller = self._ai_controller_obj
        if self._inv_obj:
            self.dino._inventory = self._inv_obj
            self.dino.inv_uuid = self._inv_obj.uuid

        # print(self.dino)

    def __str__(self):
        return f"ClusterDataDino(dino={self.dino})"

    def to_json_obj(self):
        return {
            "Version": self.version,
            "UploadTime": self.upload_time,
            "Dino": self.dino.to_json_obj()
        }

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None,
                          indent=4, cls=DefaultJsonEncoder)

