class PluginError(Exception):
    """Base exception for all plugin system errors."""
    pass

class PluginNotFoundError(PluginError):
    """Raised when a requested plugin cannot be found."""
    pass

class PluginLoadError(PluginError):
    """Raised when loading a plugin file or class fails."""
    pass

class PluginExecutionError(PluginError):
    """Raised when an error occurs during plugin hook execution."""
    pass

class DuplicatePluginError(PluginError):
    """Raised when registering a plugin with an already existing name."""
    pass
