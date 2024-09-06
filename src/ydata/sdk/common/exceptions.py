from typing import Dict, Optional

from pandas.errors import EmptyDataError as pdEmptyDataError

from ydata.core.error import FabricError


class SDKError(Exception):
    """Base Exception for all SDK errors."""

    def __init__(self, *args: object) -> None:
        if len(args) == 1 and isinstance(args[0], str):
            msg = [a for a in args][0]
            msg += "\nFor support please contact YData at: support@ydata.ai"
            super().__init__(msg)
        else:
            super().__init__(*args)


class ResponseError(FabricError):
    """Wrapper around Fabric Exception to capture error response from the
    backend."""

    def __init__(
            self,
            context: Optional[Dict[str, str]] = None,
            httpCode: Optional[int] = None,
            name: Optional[str] = None,
            description: Optional[str] = None,
            returnValue: Optional[str] = None):
        self.description = description
        self.return_value = returnValue
        FabricError.__init__(self, context=context, http_code=httpCode, name=name)


class ClientException(SDKError):
    """Base Exception for Client related exceptions."""


class ClientCreationError(ClientException):
    """Raised when a Client could not be created."""

    def __init__(self, message=None):
        from ydata.sdk.common.client.client import HELP_TEXT
        if message is None:
            message = f"Could not initialize a client. It usually means that no token could be found or the token needs to be refreshed.\n{
                HELP_TEXT}"

        super().__init__(message)


class ClientHandshakeError(ClientException):
    """Raised when handshake could not be performed - likely a token issue"""

    def __init__(self, auth_link: str):
        self.auth_link = auth_link
        super().__init__("")


class ConnectorError(SDKError):
    """Base exception for ConnectorError."""


class InvalidConnectorError(ConnectorError):
    """Raised when a connector is invalid."""


class CredentialTypeError(ConnectorError):
    """Raised when credentials are not formed properly."""


class EmptyDataError(pdEmptyDataError, SDKError):
    """Raised when no data is available."""


class DataSourceError(SDKError):
    """Base exception for DataSourceError."""


class DataSourceNotAvailableError(DataSourceError):
    """Raised when a datasource needs to be available."""


class SynthesizerException(SDKError):
    """Base Exception for Synthesizer related exception."""


class NotReadyError(SynthesizerException):
    """Raised when a Synthesizer is not read."""


class NotTrainedError(SynthesizerException):
    """Raised when a Synthesizer is not trained."""


class NotInitializedError(SynthesizerException):
    """Raised when a Synthesizer is not initialized."""

    def __init__(self, message="The synthesizer is not initialized.\n Use `fit` to train the synthesizer or `get` to retrieve an existing instance."):
        super().__init__(message)


class AlreadyFittedError(SynthesizerException):
    """Raised when a Synthesizer is already trained."""

    def __init__(self, message="The synthesizer is already fitted!"):
        super().__init__(message)


class DataTypeMissingError(SynthesizerException):
    """Raise when the DataType is missing and cannot be deduced from the
    context."""


class DataSourceAttrsError(SynthesizerException):
    """Raise when the DataSourceAttrs is missing or invalid."""


class FittingError(SynthesizerException):
    """Raised when a Synthesizer fails during training."""


class InputError(SDKError):
    """Raised for any user input related error."""
