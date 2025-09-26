import os
import atexit
import shutil
from pathlib import Path
import json
from typing import Union
from uuid import uuid4

def __base_cache_dir() -> Path:
    """
    Creates a directory for configuration files under the temp files directory.

    Returns:
        Path: The Path object of the created directory.
    """
    override = os.getenv('ARKPARSE_TMP')
    if override:
        return Path(override)
    if os.name == 'nt':
        return Path(os.getenv('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    return Path(os.getenv('XDG_CACHE_HOME', Path.home() / '.cache'))

def __create_temp_files_folder() -> Path:
    base_dir = __base_cache_dir()
    temp_files_dir = base_dir / 'asp' / 'temp_files' / str(uuid4())
    temp_files_dir.mkdir(parents=True, exist_ok=True)
    return temp_files_dir

TEMP_FILES_DIR = __create_temp_files_folder()

def __cleanup_temp_dir():
    if os.getenv('ARKPARSE_KEEP_TEMP', '0') == '1':
        return
    try:
        shutil.rmtree(TEMP_FILES_DIR, ignore_errors=True)
    except Exception:
        pass

atexit.register(__cleanup_temp_dir)

def __create_config_directory() -> Path:
    base_dir = __base_cache_dir()
    config_dir = base_dir / 'asp' / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

CONFIG_FILE_DIR = __create_config_directory()

def write_config_file(filename: str, content: Union[dict, list]):
    """
    Writes content to a configuration file in the config directory.

    Args:
        filename (str): The name of the configuration file.
        content (json): The content to write to the file.
    """
    config_file_path = CONFIG_FILE_DIR / (filename + '.json')
    config_file_path.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(content, (dict, list)):
        raise ValueError('Content must be a dictionary or a list.')
    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=4)

def read_config_file(filename: str) -> Union[dict, list]:
    """
    Reads content from a configuration file in the config directory.

    Args:
        filename (str): The name of the configuration file.

    Returns:
        Union[dict, list]: The content of the configuration file.
    """
    config_file_path = CONFIG_FILE_DIR / (filename + '.json')
    if not config_file_path.exists():
        return None
    with open(config_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_temp_file_handle(filename: str = None) -> Path:
    """
    Returns a temporary file handle in the temp files directory.
    """
    if filename is None:
        filename = uuid4().hex + '.bin'
    temp_file_path = TEMP_FILES_DIR / filename
    temp_file_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_file_path.exists():
        temp_file_path.touch()
    return temp_file_path