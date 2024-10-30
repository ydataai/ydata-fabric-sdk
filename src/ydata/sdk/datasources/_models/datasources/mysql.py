from dataclasses import dataclass

from ydata.sdk.datasources._models.datasource import DataSource


@dataclass
class MySQLDataSource(DataSource):

    query: str = None
    tables: dict = None

    def to_payload(self):
        self.dict()
