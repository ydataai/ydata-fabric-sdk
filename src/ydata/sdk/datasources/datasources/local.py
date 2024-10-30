from typing import Optional, Union

from ydata.sdk.common.client import Client, get_client
from ydata.sdk.common.types import Project
from ydata.sdk.connectors.connector import LocalConnector
from ydata.sdk.datasources._models.datatype import DataSourceType
from ydata.sdk.datasources._models.filetype import FileType
from ydata.sdk.datasources.datasource import DataSource

class LocalDataSource(DataSource):

    def __init__(
        self, connector: LocalConnector, name: Optional[str] = None, project: Optional[Project] = None,
        datatype: Optional[Union[DataSourceType, str]] = DataSourceType.TABULAR,
        filetype: Union[FileType, str] = FileType.CSV, separator: str = ",", wait_for_metadata: bool = True,
        client: Optional[Client] = None
    ):
        client = get_client(client)

        name = name or connector.name
        payload = {
            "fileType": FileType(filetype).value,
            "separator": separator,
        }

        super().__init__(
            connector=connector, datatype=datatype, name=name, project=project,
            wait_for_metadata=wait_for_metadata, client=client, **payload
        )
