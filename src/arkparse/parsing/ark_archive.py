from pathlib import Path
from typing import List, Optional

from arkparse.logging import ArkSaveLogger
from arkparse.saves.save_context import SaveContext

from .ark_object import ArkObject
from arkparse.parsing._legacy_parsing.ark_binary_parser import ArkBinaryParser as LegacyArkBinaryParser
from arkparse.parsing._legacy_parsing.ark_property import ArkProperty as LegacyArkProperty

from .ark_binary_parser import ArkBinaryParser
from .ark_property import ArkProperty

class ArkArchive:
    def __init__(self, archive_data: bytes, from_store: bool = True, cluster_dino: bool = False):
        self.objects: List[ArkObject] = []
        
        # Set up the save context and binary parser
        save_context: SaveContext = SaveContext()
        self.data = ArkBinaryParser(archive_data, save_context)

        # Setup for potential logging
        ArkSaveLogger.set_file(self.data, "debug.bin")
        ArkSaveLogger.enter_struct("ArkArchive")
        
        # Determine the save version and adjust parsing accordingly
        if not cluster_dino:
            save_context.save_version = self.data.read_int()

        old_save = False
        propertyClass = ArkProperty
        if save_context.save_version != 7 and not cluster_dino:
            old_save = True
            propertyClass = LegacyArkProperty
            ArkSaveLogger.parser_log(f"Detected old save format (pre Unreal 5.5), using legacy parser")
            data_offset = 8 if from_store else 0
            self.data = LegacyArkBinaryParser(archive_data[data_offset:], save_context)
            save_context.save_version = self.data.read_int()
        
        ArkSaveLogger.parser_log(f"Archive version: {save_context.save_version}")

        # Parse 5.5 specific data
        if not old_save or cluster_dino:
            # For Unreal 5.5 there are 2 extra 32-bit integers here
            extra1 = self.data.read_int()
            extra2 = self.data.read_int()
            ArkSaveLogger.parser_log(f"5.5 specific extra data read: {extra1}, {extra2}")

        # Read the number of objects in the archive
        count = self.data.read_int()

        ArkSaveLogger.parser_log(f"Number of objects in archive: {count}")
        for _ in range(count):
            self.objects.append(ArkObject.from_reader(self.data, cluster_dino))
        ArkSaveLogger.parser_log(f"Read {len(self.objects)} objects from archive (expected={count})")

        if len(self.objects) == 0:
            ArkSaveLogger.open_hex_view(True)

        # Read properties for each object
        for i, obj in enumerate(self.objects):
            ArkSaveLogger.enter_struct(obj.class_name.split(".")[-1])
            extra_offset = 0 if old_save else 1 # Don't quite remember why this is? TBD to find out
            self.data.set_position(obj.properties_offset + extra_offset)
            ArkSaveLogger.parser_log(f"Reading properties for object \'{obj.class_name}\' at {self.data.get_position()}")

            next_object_index = self.data.size()
            if i + 1 < len(self.objects):
                next_object_index = self.objects[i + 1].properties_offset
            
            try:
                obj.read_properties(self.data, propertyClass, next_object_index)
            except Exception as e:
                ArkSaveLogger.error_log(f"Error reading properties for object \'{obj.class_name}\' at {self.data.get_position()}: {e}")
                self.data.structured_print()
                # Notify any registered debug handler (e.g. the testbench dumper).
                # Archives reload from their raw bytes via ArkArchive(data, from_store).
                ArkSaveLogger._notify_object_failure(
                    None, obj.class_name, self.data, e,
                    kind="archive", reload_hint={"from_store": from_store},
                )
                raise e
            ArkSaveLogger.exit_struct()

        ArkSaveLogger.exit_struct()

    def get_all_objects_by_class(self, class_name: str) -> List[ArkObject]:
        return [obj for obj in self.objects if obj.class_name == class_name]

    def get_object_by_class(self, class_name: str) -> Optional[ArkObject]:
        return next((obj for obj in self.objects if obj.class_name == class_name), None)

    def get_object_by_uuid(self, uuid_: str) -> Optional[ArkObject]:
        return next((obj for obj in self.objects if obj.uuid == uuid_), None)

    def get_object_by_index(self, index: int) -> ArkObject:
        return self.objects[index]
    
    def __str__(self):
        return f"ArkArchive(objects={len(self.objects)})" + "\n" + "\n".join([str(obj) for obj in self.objects])
