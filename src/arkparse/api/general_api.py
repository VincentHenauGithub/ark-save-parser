from typing import Dict
from uuid import UUID

from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase

class GeneralApi:
    def __init__(self, save: AsaSave, config: GameObjectReaderConfiguration= GameObjectReaderConfiguration()):
        self.save = save
        self.config = config
        self.all_objects = None
        self.parsed_objects: Dict[UUID, ParsedObjectBase] = {}

    def get_all_objects(self, config: GameObjectReaderConfiguration = None) -> Dict[UUID, ArkGameObject]:
        reuse = False
        if config is None:
            reuse = True
            if self.all_objects is not None:
                return self.all_objects

            config = self.config

        objects = self.save.get_game_objects(config)

        if reuse:
            self.all_objects = objects

        return objects
    
    def get_all(self, constructor, valid_filter = None, config = None) -> Dict[UUID, object]:
        objects = self.get_all_objects(config)

        parsed = {}

        for key, obj in objects.items():
            if valid_filter and not valid_filter(obj):
                continue

            if key in self.parsed_objects:
                parsed[key] = self.parsed_objects[key]
            else:
                parsed[key] = constructor(obj.uuid, self.save)
                self.parsed_objects[key] = parsed[key]

        return parsed
    