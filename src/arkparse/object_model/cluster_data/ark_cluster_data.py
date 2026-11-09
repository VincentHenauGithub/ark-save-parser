import json
from pathlib import Path

from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.object_model.cluster_data.cluster_data_item import ClusterDataItem
from arkparse.parsing.ark_archive import ArkArchive
from arkparse.object_model.cluster_data.cluster_data_dino import ClusterDataDino
from arkparse.utils.json_utils import DefaultJsonEncoder


class ClusterData:
    def __init__(self, path: Path, uuid: str):
        self._path = path
        self._uuid = uuid
        self._archive_object: ArkArchive = self._parse()
        self._ark_data = self._archive_object.get_object_by_class("/Script/ShooterGame.ArkCloudInventoryData")
        if self._ark_data is None:
            self._ark_data = self._archive_object.get_object_by_class("/Script/ShooterGame.PrimalLocalProfile")
            self._ark_data = self._ark_data.get_property_value("MyArkData", None)
        self._ark_data_items: list[ArkGameObject] = self._ark_data.get_property_value("ArkItems", [])
        self._uploaded_dinos: list[ArkGameObject] = self._ark_data.get_property_value("ArkTamedDinosData", [])

        self.dinos: list[ClusterDataDino] = []
        self.items: list[ClusterDataItem] = []

        for item in self._ark_data_items:
            item = ClusterDataItem(item, len(self._ark_data_items))
            self.items.append(item)

        for dino in self._uploaded_dinos:
            dino_data = ClusterDataDino(dino, len(self.dinos))
            self.dinos.append(dino_data)

    def _check_exists(self):
        path_exists = self._path.exists()

        if not path_exists:
            raise FileNotFoundError(f"Cluster data folder not found at path: {self._path}")

        file_path = self._path / f"{self._uuid}"
        file_exists = file_path.exists()

        if not file_exists:
            raise FileNotFoundError(f"Cluster data file not found in folder: {file_path}")
        
    def _parse(self) -> ArkArchive:
        self._check_exists()

        file_path = self._path / f"{self._uuid}"
        with open(file_path, "rb") as f:
            data = f.read()

        return ArkArchive(data, from_store=False)

    def __str__(self):
        return f" Path: {self._path.__str__()} - UUID: {self._uuid} - Dinos: {self.dinos} - Items: {self.items}"

    def to_json_obj(self, include_owner_inv_uuid=True):
        dinos_json = [dino.to_json_obj() for dino in self.dinos]
        items_json = [item.to_json_obj() for item in self.items]
        return {"Path": self._path.__str__(), "UUID": self._uuid, "Dinos": dinos_json, "Items": items_json}

    def to_json_str(self):
        return json.dumps(self.to_json_obj(), default=lambda o: o.to_json_obj() if hasattr(o, 'to_json_obj') else None,
                          indent=4, cls=DefaultJsonEncoder)
