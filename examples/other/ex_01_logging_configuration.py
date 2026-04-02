from arkparse.logging import ArkSaveLogger

# The logger can log at multiple levesl, such as:
# - parser: For parsing related logs
# - info: General information logs
# - api: For API related logs
# - error: For error logs
# - debug: For debugging logs
# - warning: For warning logs
# - save: For save related logs

# Log levels can be set globally or individually for each type.
# For example, if api logging is set to True, all logs of type api will be printed.
# Other log types will not be printed unless they are also set to True.

ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.API, True)
print("API logging enabled.")
ArkSaveLogger.info_log("This is an info log.")
ArkSaveLogger.error_log("This is an error log.")
ArkSaveLogger.api_log("This is an API log.")
ArkSaveLogger.save_log("This is a save log.")

# When the script ends, the log levels will reset to their defaults.
# Unless, the log level is set globally.
# In that case, the log levels will be saved to a configuration file.
# Which can be used to restore the log levels when the script is run again.

ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.API, False)
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ERROR, True, set_globally=True)
print("\nGlobal log levels:")
ArkSaveLogger.info_log("This is an info log.")
ArkSaveLogger.error_log("This is an error log.")
ArkSaveLogger.api_log("This is an API log.")
ArkSaveLogger.save_log("This is a save log.")

# If you run this script twice, the error log will be printed both times above,
# because the log level for error logs is set globally to True.

# All types of logging can be enabled as well using the "all" key.

ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ALL, True)
print("\nAll log levels enabled.")
ArkSaveLogger.info_log("This is an info log.")
ArkSaveLogger.error_log("This is an error log.")
ArkSaveLogger.api_log("This is an API log.")
ArkSaveLogger.save_log("This is a save log.")
ArkSaveLogger.debug_log("This is a debug log.")
ArkSaveLogger.warning_log("This is a warning log.")
ArkSaveLogger.parser_log("This is a parser log.")
ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes.ALL, False)

# Worker thread logging can be enabled/disabled.
# By default, logging is disabled in parallel worker threads for performance.
# Enable this to see logs from parallel parsing workers (when using free-threaded Python).

ArkSaveLogger.enable_worker_logging(True)  # Enable logging in worker threads
ArkSaveLogger.enable_worker_logging(False)  # Disable (default)
