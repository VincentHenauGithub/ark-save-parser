from pathlib import Path

from arkparse.api.json_api import JsonApi

def test_export_objects(map_save, temp_file_folder: Path):
    """
    Test to export all objects from the current map's save file to JSON.
    """
    map_name, save = map_save
    JsonApi(save).export_all(export_folder_path=temp_file_folder / f"json_exports_{map_name.name.lower()}")
