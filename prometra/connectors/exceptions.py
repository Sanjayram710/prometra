class ConnectorError(Exception):
    """Base exception for all connector errors."""
    pass

class ConnectorRegistrationError(ConnectorError):
    """Raised when a connector fails to register."""
    pass

class ConnectorLifecycleError(ConnectorError):
    """Raised when a connector fails to start, stop, or initialize."""
    pass
