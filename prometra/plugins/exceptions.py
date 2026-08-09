class PluginError(Exception):
    """Base exception for all plugin system errors."""



class PluginNotFoundError(PluginError):
    """Raised when a requested plugin cannot be found."""



class PluginLoadError(PluginError):
    """Raised when loading a plugin file or class fails."""



class PluginExecutionError(PluginError):
    """Raised when an error occurs during plugin hook execution."""



class DuplicatePluginError(PluginError):
    """Raised when registering a plugin with an already existing name."""

