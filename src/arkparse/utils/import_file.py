from uuid import UUID
from typing import Dict
from pathlib import Path
import json

class ImportFile:
    def __init__(self, path: str):
        def read_bytes_from_file(file_path: Path) -> bytes:
            with open(file_path, "rb") as f:
                return f.read()
            
        file = path.replace("\\", "/").split("/")[-1]
        uuid = UUID(file.split("_")[1].split('.')[0])
        t = file.split("_")[0]
        name_path = None if t == "loc" else Path(path).parent / (file.split('.')[0] + "_n.json")

        self.path: Path = Path(path)
        self.type: str = t
        self.uuid: UUID = uuid
        self.names: Dict[int, str] = json.loads(name_path.read_text()) if name_path is not None else None
        self.bytes = read_bytes_from_file(path)