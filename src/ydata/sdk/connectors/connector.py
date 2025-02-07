from io import BytesIO
from json import loads as json_loads
from pathlib import Path
from typing import Dict, Optional, TypeVar, Union
from uuid import uuid4

from pandas import DataFrame as pdDataFrame

from ydata.sdk.common.client import Client
from ydata.sdk.common.client.utils import init_client
from ydata.sdk.common.config import LOG_LEVEL
from ydata.sdk.common.exceptions import CredentialTypeError
from ydata.sdk.common.logger import create_logger
from ydata.sdk.common.types import UID, Project
from ydata.sdk.connectors._models.connector import Connector as mConnector
from ydata.sdk.connectors._models.connector_list import ConnectorsList
from ydata.sdk.connectors._models.connector_type import ConnectorType
from ydata.sdk.connectors._models.credentials.credentials import Credentials
from ydata.sdk.connectors._models.local_connector import LocalConnector as mLocalConnector
from ydata.sdk.connectors._models.rdbms_connector import RDBMSConnector as mRDBMSConnector
from ydata.sdk.connectors._models.schema import Schema
from ydata.sdk.connectors._models.upload import Upload
from ydata.sdk.utils.model_mixin import ModelFactoryMixin

_T = TypeVar('_T', bound='Connector')


class Connector(ModelFactoryMixin):
    """A [`Connector`][ydata.sdk.connectors.Connector] allows to connect and
    access data stored in various places. The list of available connectors can
    be found [here][ydata.sdk.connectors.ConnectorType].

    Arguments:
        connector_type (Union[ConnectorType, str]): Type of the connector to be created
        credentials (dict): Connector credentials
        name (Optional[str]): (optional) Connector name
        project (Optional[Project]): (optional) Project name for this Connector
        client (Client): (optional) Client to connect to the backend

    Attributes:
        uid (UID): UID fo the connector instance (creating internally)
        type (ConnectorType): Type of the connector
    """

    _MODEL_CLASS = mConnector

    _model: Optional[mConnector]

    def __init__(
            self, connector_type: Union[ConnectorType, str, None] = None, credentials: Optional[Dict] = None,
            name: Optional[str] = None, project: Optional[Project] = None, client: Optional[Client] = None):
        self._init_common(client=client)

        self._model = self.create(connector_type=connector_type,
                                  credentials=credentials,
                                  name=name, project=project,
                                  client=client)

        self._project = project

    @init_client
    def _init_common(self, client: Optional[Client] = None):
        self._client = client
        self._logger = create_logger(__name__, level=LOG_LEVEL)

    @property
    def uid(self) -> UID:
        return self._model.uid

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def type(self) -> ConnectorType:
        return ConnectorType(self._model.type)

    @property
    def project(self) -> Project:
        return self._project or self._client.project

    @staticmethod
    @init_client
    def get(
        uid: UID, project: Optional[Project] = None, client: Optional[Client] = None
    ) -> _T:
        """Get an existing connector.

        Arguments:
            uid (UID): Connector identifier
            project (Optional[Project]): (optional) Project name from where to get the connector
            client (Optional[Client]): (optional) Client to connect to the backend

        Returns:
            Connector
        """
        response = client.get(f'/connector/{uid}', project=project)
        data = response.json()
        data_type = data["type"]
        connector_class = _connector_type_to_model(
            ConnectorType._init_connector_type(data_type))
        connector = connector_class._init_from_model_data(
            connector_class._MODEL_CLASS(**data))
        connector._project = project

        return connector

    @staticmethod
    def _init_credentials(
        connector_type: ConnectorType, credentials: Union[str, Path, Dict, Credentials]
    ) -> Credentials:
        _credentials = None

        if isinstance(credentials, str):
            credentials = Path(credentials)

        if isinstance(credentials, Path):
            try:
                _credentials = json_loads(credentials.open().read())
            except Exception:
                raise CredentialTypeError(
                    'Could not read the credentials. Please, check your path or credentials structure.')

        try:
            from ydata.sdk.connectors._models.connector_map import TYPE_TO_CLASS
            credential_cls = TYPE_TO_CLASS.get(connector_type.value)
            _credentials = credential_cls(**_credentials)
        except Exception:
            raise CredentialTypeError(
                "Could not create the credentials. Verify the path or the structure your credentials.")

        return _credentials

    @staticmethod
    def create(
        connector_type: Union[ConnectorType, str], credentials: Union[str, Path, Dict, Credentials],
        name: Optional[str] = None, project: Optional[Project] = None, client: Optional[Client] = None
    ) -> _T:
        """Create a new connector.

        Arguments:
            connector_type (Union[ConnectorType, str]): Type of the connector to be created
            credentials (dict): Connector credentials
            name (Optional[str]): (optional) Connector name
            project (Optional[Project]): (optional) Project where to create the connector
            client (Client): (optional) Client to connect to the backend

        Returns:
            New connector
        """
        connector_type = ConnectorType._init_connector_type(connector_type)
        connector_class = _connector_type_to_model(connector_type)

        payload = {
            "type": connector_type.value,
            "credentials": credentials if isinstance(credentials, dict) else credentials.dict(by_alias=True)
        }

        if client is None:
            model = connector_class._create(payload, name, project)
        else:
            model = connector_class._create(payload, name, project, client)

        connector = connector_class._init_from_model_data(model)
        connector._project = project
        return connector

    @classmethod
    @init_client
    def _create(
        cls, payload: dict, name: Optional[str] = None, project: Optional[Project] = None,
        client: Optional[Client] = None
    ) -> _MODEL_CLASS:
        _name = name if name is not None else str(uuid4())
        payload["name"] = _name
        response = client.post('/connector/', project=project, json=payload)
        data = response.json()

        return cls._MODEL_CLASS(**data)

    @staticmethod
    @init_client
    def list(project: Optional[Project] = None, client: Optional[Client] = None) -> ConnectorsList:
        """List the connectors instances.

        Arguments:
            project (Optional[Project]): (optional) Project name from where to list the connectors
            client (Client): (optional) Client to connect to the backend

        Returns:
            List of connectors
        """
        response = client.get('/connector', project=project)
        data: list = response.json()
        return ConnectorsList(data)

    def __repr__(self):
        return self._model.__repr__()


class RDBMSConnector(Connector):

    _MODEL_CLASS = mRDBMSConnector
    _model: Optional[mRDBMSConnector]

    @property
    def schema(self) -> Optional[Schema]:
        return self._model.db_schema


class LocalConnector(Connector):
    _MODEL_CLASS = mLocalConnector
    _model: Optional[mLocalConnector]

    @staticmethod
    def create(
        source: Union[pdDataFrame, str, Path], connector_type: Union[ConnectorType, str] = ConnectorType.FILE,
        name: Optional[str] = None, project: Optional[Project] = None, client: Optional[Client] = None
    ) -> "LocalConnector":
        """Create a new connector.

        Arguments:
            source (Union[pdDataFrame, str, Path]): pandas dataframe, string or path to a file
            name (Optional[str]): (optional) Connector name
            project (Optional[Project]): (optional) Project where to create the connector
            client (Client): (optional) Client to connect to the backend

        Returns:
            New connector
        """

        if isinstance(source, str):
            source = Path(source)

        if isinstance(source, pdDataFrame):
            upload = LocalConnector._upload_dataframe(source, project, client=client)
        else:
            upload = LocalConnector._upload_file(source, project, client=client)

        model = mLocalConnector(name=name, type=connector_type, file=upload.uid)
        model = LocalConnector._create(model.dict(
            by_alias=True), name, project, client=client)

        connector = LocalConnector._init_from_model_data(model)
        connector._project = project
        return connector

    @staticmethod
    def _upload_dataframe(
        source: pdDataFrame, project: Optional[Project] = None, client: Optional[Client] = None
    ) -> Upload:
        buffer = BytesIO()
        source.to_csv(buffer, index=False)
        return LocalConnector._upload(buffer, project, client=client)

    @staticmethod
    def _upload_file(source: Path, project: Optional[Project] = None, client: Optional[Client] = None) -> Upload:
        with source.open('rb') as f:
            buffer = BytesIO(f.read())
            return LocalConnector._upload(buffer, project, client=client)

    @staticmethod
    @init_client
    def _upload(source_bytes: BytesIO, project: Optional[Project] = None, client: Optional[Client] = None) -> Upload:
        length = source_bytes.getbuffer().nbytes

        created_upload = client.post(
            "/upload", project=project, json={"size": length}, raise_for_status=True)
        created_upload.raise_for_status()
        created_upload_dict = created_upload.json()

        upload_id = created_upload_dict["uid"]
        chunk_size = int(created_upload_dict["chunkSize"])

        source_bytes.seek(0)
        while True:
            chunk_bytes = source_bytes.read(chunk_size)
            if not chunk_bytes:
                break

            upload_response = client.patch(
                f"/upload/{upload_id}", content=chunk_bytes, project=project, raise_for_status=True
            )
            data = upload_response.json()
            upload = Upload(**data)

        return upload


def _connector_type_to_model(connector_type: ConnectorType) -> _T:
    return RDBMSConnector if connector_type.is_rdbms else LocalConnector if connector_type is ConnectorType.FILE else Connector
