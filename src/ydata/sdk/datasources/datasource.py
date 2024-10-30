from time import sleep
from typing import Dict, Optional, Type, Union  # noqa: TYP001
from uuid import uuid4

from ydata.sdk.common.client import Client
from ydata.sdk.common.client.utils import init_client
from ydata.sdk.common.config import BACKOFF, LOG_LEVEL
from ydata.sdk.common.logger import create_logger
from ydata.sdk.common.types import UID, Project
from ydata.sdk.connectors.connector import Connector, ConnectorType
from ydata.sdk.datasources._models.connector_to_datasource import CONNECTOR_TO_DATASOURCE
from ydata.sdk.datasources._models.datasource import DataSource as mDataSource
from ydata.sdk.datasources._models.datasource_list import DataSourceList
from ydata.sdk.datasources._models.datatype import DataSourceType
from ydata.sdk.datasources._models.metadata.metadata import Metadata
from ydata.sdk.datasources._models.status import State, Status
from ydata.sdk.utils.model_mixin import ModelFactoryMixin
from ydata.sdk.utils.model_utils import filter_dict

from src.ydata.sdk.synthesizers.synthesizer import logger


class DataSource(ModelFactoryMixin):
    """A [`DataSource`][ydata.sdk.datasources.DataSource] represents a dataset
    to be used by a Synthesizer as training data.

    Arguments:
        connector (Connector): Connector from which the datasource is created
        datatype (Optional[Union[DataSourceType, str]]): (optional) DataSource type
        name (Optional[str]): (optional) DataSource name
        project (Optional[Project]): (optional) Project name for this datasource
        wait_for_metadata (bool): If `True`, wait until the metadata is fully calculated
        client (Client): (optional) Client to connect to the backend
        **config: Datasource specific configuration

    Attributes:
        uid (UID): UID fo the datasource instance
        datatype (DataSourceType): Data source type
        status (Status): Status of the datasource
        metadata (Metadata): Metadata associated to the datasource
    """

    def __init__(
        self, connector: Connector, datatype: Optional[Union[DataSourceType, str]] = DataSourceType.TABULAR,
        name: Optional[str] = None, project: Optional[Project] = None, wait_for_metadata: bool = True,
        client: Optional[Client] = None, **config
    ):
        datasource_type = CONNECTOR_TO_DATASOURCE.get(connector.type)
        self._init_common(client=client)
        self._model: Optional[mDataSource] = self._create_model(
            connector=connector, datasource_type=datasource_type, datatype=datatype,
            config=config, name=name, client=self._client)

        if wait_for_metadata:
            self._model = DataSource._wait_for_metadata(self)._model

        self._project = project

    @init_client
    def _init_common(self, client: Optional[Client] = None):
        self._client = client
        self._logger = create_logger(__name__, level=LOG_LEVEL)

    @property
    def uid(self) -> UID:
        return self._model.uid

    @property
    def datatype(self) -> DataSourceType:
        return self._model.datatype

    @property
    def project(self) -> Project:
        return self._project or self._client.project

    @property
    def status(self) -> Status:
        try:
            self._model = self.get(uid=self._model.uid,
                                   project=self.project, client=self._client)._model
            return self._model.status
        except Exception:  # noqa: PIE786
            return Status.unknown()

    @property
    def metadata(self) -> Optional[Metadata]:
        return self._model.metadata

    @staticmethod
    @init_client
    def list(project: Optional[Project] = None, client: Optional[Client] = None) -> DataSourceList:
        """List the  [`DataSource`][ydata.sdk.datasources.DataSource]
        instances.

        Arguments:
            project (Optional[Project]): (optional) Project name from where to list the datasources
            client (Client): (optional) Client to connect to the backend

        Returns:
            List of datasources
        """
        def __process_data(data: list) -> list:
            to_del = ['metadata']
            for e in data:
                for k in to_del:
                    e.pop(k, None)
            return data

        response = client.get('/datasource', project=project)
        data: list = response.json()
        data = __process_data(data)

        return DataSourceList(data)

    @staticmethod
    @init_client
    def get(uid: UID, project: Optional[Project] = None, client: Optional[Client] = None) -> "DataSource":
        """Get an existing [`DataSource`][ydata.sdk.datasources.DataSource].

        Arguments:
            uid (UID): DataSource identifier
            project (Optional[Project]): (optional) Project name from where to get the connector
            client (Client): (optional) Client to connect to the backend

        Returns:
            DataSource
        """
        response = client.get(f'/datasource/{uid}', project=project)
        data: list = response.json()
        datasource_type = CONNECTOR_TO_DATASOURCE.get(
            ConnectorType(data['connector']['type']))
        datasource = DataSource._model_from_api(data, datasource_type)
        #datasource = DataSource._init_from_model_data(model)
        datasource._project = project
        return datasource

    @classmethod
    def create(
        cls, connector: Connector, datatype: Optional[Union[DataSourceType, str]] = DataSourceType.TABULAR,
        name: Optional[str] = None, project: Optional[Project] = None, wait_for_metadata: bool = True,
        client: Optional[Client] = None, **config
    ) -> "DataSource":
        """Create a new [`DataSource`][ydata.sdk.datasources.DataSource].

        Arguments:
            connector (Connector): Connector from which the datasource is created
            datatype (Optional[Union[DataSourceType, str]]): (optional) DataSource type
            name (Optional[str]): (optional) DataSource name
            project (Optional[Project]): (optional) Project name for this datasource
            wait_for_metadata (bool): If `True`, wait until the metadata is fully calculated
            client (Client): (optional) Client to connect to the backend
            **config: Datasource specific configuration

        Returns:
            DataSource
        """
        datasource_type = CONNECTOR_TO_DATASOURCE.get(connector.type)
        return cls._create(
            connector=connector, datasource_type=datasource_type, datatype=datatype, config=config, name=name,
            project=project, wait_for_metadata=wait_for_metadata, client=client)

    @classmethod
    def _create(
        cls, connector: Connector, datasource_type: Type[mDataSource],
        datatype: Optional[Union[DataSourceType, str]] = DataSourceType.TABULAR, config: Optional[Dict] = None,
        name: Optional[str] = None, project: Optional[Project] = None, wait_for_metadata: bool = True,
        client: Optional[Client] = None
    ) -> "DataSource":
        model = DataSource._create_model(
            connector, datasource_type, datatype, config, name, project, client)
        datasource = DataSource._init_from_model_data(model)

        if wait_for_metadata:
            datasource._model = DataSource._wait_for_metadata(datasource)._model

        datasource._project = project

        return datasource

    @classmethod
    @init_client
    def _create_model(
        cls, connector: Connector, datasource_type: Type[mDataSource],
        datatype: Optional[Union[DataSourceType, str]] = DataSourceType.TABULAR, config: Optional[Dict] = None,
        name: Optional[str] = None, project: Optional[Project] = None, client: Optional[Client] = None
    ) -> mDataSource:
        _name = name if name is not None else str(uuid4())
        _config = config if config is not None else {}
        payload = {
            "name": _name,
            "connector": {
                "uid": connector.uid,
                "type": ConnectorType(connector.type).value
            },
            "dataType": DataSourceType(datatype).value
        }
        if connector.type != ConnectorType.FILE:
            _config = datasource_type(**config).to_payload()
        payload.update(_config)
        response = client.post('/datasource/', project=project, json=payload)
        data: list = response.json()
        return DataSource._model_from_api(data, datasource_type)

    @staticmethod
    def _wait_for_metadata(datasource):
        logger = create_logger(__name__, level=LOG_LEVEL)
        while State(datasource.status.state) not in [State.AVAILABLE, State.FAILED, State.UNAVAILABLE]:
            logger.info(f'Calculating metadata [{datasource.status}]')
            datasource = DataSource.get(uid=datasource.uid, client=datasource._client)
            sleep(BACKOFF)
        return datasource

    @staticmethod
    def _model_from_api(data: Dict, datasource_type: Type[mDataSource]) -> mDataSource:
        data['datatype'] = data.pop('dataType', None)
        data['connector_ref'] = data['connector']['uid']
        data['connector_type'] = data['connector']['type']
        data = filter_dict(datasource_type, data)
        model = datasource_type(**data)
        return model

    def __repr__(self):
        return self._model.__repr__()
