from typing import Optional

from pydantic.dataclasses import dataclass

from ydata.sdk.common.types import UID
from ydata.sdk.datasources._models.datatype import DataSourceType
from ydata.sdk.datasources._models.metadata.metadata import Metadata
from ydata.sdk.datasources._models.status import Status


@dataclass
class DataSource:
    uid: Optional[UID] = None
    author: Optional[str] = None
    name: Optional[str] = None
    datatype: Optional[DataSourceType] = None
    metadata: Optional[Metadata] = None
    status: Optional[Status] = None
    connector_ref: Optional[str] = None
    connector_type: Optional[str] = None

    def __post_init__(self):
        if self.metadata is not None:
            self.metadata = Metadata(**self.metadata)

        if self.status is not None:
            self.status = Status(**self.status)

    def to_payload(self):
        return {}
