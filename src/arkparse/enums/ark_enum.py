from enum import Enum
from arkparse.logging import ArkSaveLogger

class ArkEnumValue:
    enum_name: str
    enum_value: str

    def __init__(self, name: str):
        ArkSaveLogger.parser_log(f"Creating ArkEnumValue with name: {name}")
        if "::" in name:
            self.enum_name = name.split('::')[0]
            self.enum_value = name.split('::')[1]
        elif "_" in name:
            self.enum_name = name.split('_')[0]
            self.enum_value = name.split('_')[1]
        else:
            raise ValueError(f"Invalid enum name format: {name}")

    def __str__(self):
        return f"{self.enum_name}->{self.enum_value}"

    def to_json_obj(self):
        return { "name": self.enum_name, "value": self.enum_value }
