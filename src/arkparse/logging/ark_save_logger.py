import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

from arkparse.utils.tm_files import read_config_file, write_config_file, TEMP_FILES_DIR

class ArkSaveLogger:
    class LogTypes(Enum):
        PARSER = "parser"
        INFO = "info"
        API = "api"
        ERROR = "error"
        DEBUG = "debug"
        WARNING = "warning"
        SAVE = "save"
        OBJECTS = "objects"
        ALL = "all"

    class LogColors:
        WHITE = "\033[0m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        GREEN = "\033[92m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

    current_struct_path = []
    _allow_invalid_objects = None
    _file = ""
    _byte_buffer = None
    _temp_file_path = TEMP_FILES_DIR
    _file_viewer_enabled = None
    _log_level_states = None
    # Cached boolean for fast parser_log checks (updated by __init_config and set_log_level)
    _parser_log_enabled = False

    __LOG_CONFIG_FILE_NAME = "logger"

    @staticmethod
    def _is_log_enabled(log_type: "ArkSaveLogger.LogTypes") -> bool:
        """Fast check if a log type is enabled (avoids expensive work when logging is off)."""
        if ArkSaveLogger._log_level_states is None:
            ArkSaveLogger.__init_config()
        return ArkSaveLogger._log_level_states.get(log_type.value, False) or ArkSaveLogger._log_level_states["all"]

    @staticmethod
    def save_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.SAVE, ArkSaveLogger.LogColors.GREEN)

    @staticmethod
    def parser_log(message: str):
        # Fast path: check cached boolean directly (no method call overhead)
        if not ArkSaveLogger._parser_log_enabled:
            return
        struct_header = ""
        max = 15
        curr = 0
        for struct in ArkSaveLogger.current_struct_path:
            struct_header += f"[{struct}]"
            curr += 1
            if curr >= max:
                struct_header += "[...]"
                break
        ArkSaveLogger.__log(struct_header + message, ArkSaveLogger.LogTypes.PARSER, ArkSaveLogger.LogColors.CYAN)

    @staticmethod
    def info_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.INFO, ArkSaveLogger.LogColors.BOLD)

    @staticmethod
    def api_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.API, ArkSaveLogger.LogColors.MAGENTA)

    @staticmethod
    def error_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.ERROR, ArkSaveLogger.LogColors.RED)

    @staticmethod
    def debug_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.DEBUG, ArkSaveLogger.LogColors.BLUE)

    @staticmethod
    def warning_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.WARNING, ArkSaveLogger.LogColors.YELLOW)

    @staticmethod
    def objects_log(message: str):
        ArkSaveLogger.__log(message, ArkSaveLogger.LogTypes.OBJECTS, ArkSaveLogger.LogColors.CYAN)

    @staticmethod
    def __init_config():
        config = read_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME)
        if config is None:
            ArkSaveLogger._log_level_states = {
                ArkSaveLogger.LogTypes.PARSER.value: False,
                ArkSaveLogger.LogTypes.INFO.value: False,
                ArkSaveLogger.LogTypes.API.value: False,
                ArkSaveLogger.LogTypes.ERROR.value: False,
                ArkSaveLogger.LogTypes.DEBUG.value: False,
                ArkSaveLogger.LogTypes.WARNING.value: False,
                ArkSaveLogger.LogTypes.OBJECTS.value: False,
                ArkSaveLogger.LogTypes.SAVE.value: False,
                "all": False
            }
            ArkSaveLogger._file_viewer_enabled = True
            config = {
                "levels": ArkSaveLogger._log_level_states,
                "fve": False,
                "allow_invalid": True
            }
            write_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME, config)
        else:
            ArkSaveLogger._log_level_states = config["levels"]
            ArkSaveLogger._file_viewer_enabled = config["fve"]
            ArkSaveLogger._allow_invalid_objects = config["allow_invalid"]
        # Update cached parser_log state for fast checks
        ArkSaveLogger._parser_log_enabled = (
            ArkSaveLogger._log_level_states.get(ArkSaveLogger.LogTypes.PARSER.value, False) 
            or ArkSaveLogger._log_level_states.get("all", False)
        )

    @staticmethod
    def __log(message: str, log_type: "ArkSaveLogger.LogTypes", color: "ArkSaveLogger.LogColors" = None):
        if ArkSaveLogger._log_level_states is None:
            ArkSaveLogger.__init_config()
        
        if (not ArkSaveLogger._log_level_states.get(log_type.value, False)) and not ArkSaveLogger._log_level_states["all"]:
            return
        
        if color is None:
            color = ArkSaveLogger.LogColors.WHITE

        message = f"{color}[{log_type.value}]{ArkSaveLogger.LogColors.RESET} {message}"

        print(message)

    @staticmethod
    def set_log_level(log_type: "ArkSaveLogger.LogTypes", state: bool, set_globally: bool = False):
        if ArkSaveLogger._log_level_states is None:
            ArkSaveLogger.__init_config()
        ArkSaveLogger._log_level_states[log_type.value] = state
        
        # Update cached parser_log state if relevant log type changed
        if log_type == ArkSaveLogger.LogTypes.PARSER or log_type == ArkSaveLogger.LogTypes.ALL:
            ArkSaveLogger._parser_log_enabled = (
                ArkSaveLogger._log_level_states.get(ArkSaveLogger.LogTypes.PARSER.value, False) 
                or ArkSaveLogger._log_level_states.get("all", False)
            )

        if set_globally:
            global_config = read_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME)
            global_config["levels"][log_type.value] = state
            write_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME, global_config)

    @staticmethod
    def disable_all_logs():
        if ArkSaveLogger._log_level_states is None:
            ArkSaveLogger.__init_config()
        for key in ArkSaveLogger._log_level_states.keys():
            ArkSaveLogger._log_level_states[key] = False
        ArkSaveLogger.allow_invalid_objects(False)

    @staticmethod
    def enter_struct(struct_name: str):
        ArkSaveLogger.current_struct_path.append(struct_name)

    @staticmethod
    def allow_invalid_objects(state: bool = True, set_globally: bool = False):
        if ArkSaveLogger._allow_invalid_objects is None:
            ArkSaveLogger.__init_config()

        ArkSaveLogger._allow_invalid_objects = state

        if set_globally:
            global_config = read_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME)
            global_config["allow_invalid"] = state
            write_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME, global_config)

    @staticmethod
    def exit_struct():
        if len(ArkSaveLogger.current_struct_path) > 0:
            ArkSaveLogger.current_struct_path.pop()

    @staticmethod
    def enable_hex_view(state: bool = True, set_globally: bool = False):
        ArkSaveLogger._file_viewer_enabled = state
        if set_globally:
            global_config = read_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME)
            global_config["fve"] = state
            write_config_file(ArkSaveLogger.__LOG_CONFIG_FILE_NAME, global_config)

    @staticmethod
    def reset_struct_path():
        ArkSaveLogger.current_struct_path = []

    @staticmethod
    def set_file(reader: "ArkBinaryParser", name: str):
        if ArkSaveLogger._temp_file_path != "" and ArkSaveLogger._file_viewer_enabled:
            ArkSaveLogger._byte_buffer = reader
            ArkSaveLogger._file = ArkSaveLogger._temp_file_path / name
            with open(ArkSaveLogger._file, 'wb') as f:
                f.write(reader.byte_buffer)

    @staticmethod
    def open_hex_view(wait: bool = False):
        if ArkSaveLogger._file_viewer_enabled is None:
            ArkSaveLogger.__init_config()
            
        if ArkSaveLogger._file_viewer_enabled and ArkSaveLogger._byte_buffer is not None:
            parser = Path(__file__).resolve().parent.parent.parent / 'binary-reader' / 'binary_visualizer.py'
            logging.info("[File viewer] Opening hex view")
            subprocess.Popen(['python', parser, '-f', ArkSaveLogger._file, '-i', str(ArkSaveLogger._byte_buffer.get_position())])
            if wait:
                input("Press Enter to continue...")