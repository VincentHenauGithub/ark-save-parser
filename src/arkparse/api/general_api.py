from typing import Dict, List, Tuple
from uuid import UUID
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

from arkparse.logging.ark_save_logger import ArkSaveLogger, mark_as_worker_thread
from arkparse.object_model.ark_game_object import ArkGameObject
from arkparse.parsing import ArkBinaryParser
from arkparse.saves.asa_save import AsaSave
from arkparse.parsing import GameObjectReaderConfiguration
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase


def _is_parallel_enabled() -> bool:
    if hasattr(sys, '_is_gil_enabled'):
        return not sys._is_gil_enabled()
    return False


_PARALLEL_ENABLED = _is_parallel_enabled()


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
    
    def get_all(self, constructor, valid_filter = None, config = None, max_workers: int = 4) -> Dict[UUID, object]:
        objects = self.get_all_objects(config)

        parsed = {}
        to_parse: List[Tuple[UUID, ArkGameObject]] = []

        for key, obj in objects.items():
            if valid_filter and not valid_filter(obj):
                continue

            if key in self.parsed_objects:
                parsed[key] = self.parsed_objects[key]
            else:
                to_parse.append((key, obj))

        self._parse_batch(to_parse, parsed, constructor, max_workers)

        return parsed

    def _parse_batch(self, to_parse: List[Tuple[UUID, ArkGameObject]], parsed: Dict, constructor, max_workers: int):
        if _PARALLEL_ENABLED and max_workers > 1 and len(to_parse) > 0:
            ArkSaveLogger.api_log(f"Parsing {len(to_parse)} objects with {max_workers} workers...")
            save = self.save
            _worker_initialized = threading.local()
            error_count = [0]

            def parse_single(item):
                if not getattr(_worker_initialized, 'done', False):
                    mark_as_worker_thread()
                    _worker_initialized.done = True
                key, obj = item
                try:
                    return (key, constructor(obj.uuid, save), None)
                except Exception as e:
                    error_count[0] += 1
                    if error_count[0] <= 3:
                        ArkSaveLogger.error_log(f"Parallel parse error #{error_count[0]}: {type(e).__name__}: {e}")
                    return (key, None, str(e))

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(parse_single, to_parse))

            for key, obj, error in results:
                if obj is not None:
                    parsed[key] = obj
                    self.parsed_objects[key] = obj
                elif error is not None:
                    if not ArkSaveLogger._allow_invalid_objects:
                        raise RuntimeError(f"Parse error for {key}: {error}")
        else:
            for key, obj in to_parse:
                try:
                    parsed[key] = constructor(obj.uuid, self.save)
                    self.parsed_objects[key] = parsed[key]
                except Exception as e:
                    if ArkSaveLogger._allow_invalid_objects:
                        ArkSaveLogger.error_log(f"Failed to parse object {obj.uuid}: {e}")
                    else:
                        raise e
    