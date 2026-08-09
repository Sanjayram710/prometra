class ConnectorError(Exception):
    """Base exception for all connector errors."""



class ConnectorRegistrationError(ConnectorError):
    """Raised when a connector fails to register."""



class ConnectorLifecycleError(ConnectorError):
    """Raised when a connector fails to start, stop, or initialize."""

