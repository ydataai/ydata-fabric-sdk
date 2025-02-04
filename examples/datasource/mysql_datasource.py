"""
    Example to create a MySQL datasource.
"""
import os

from ydata.sdk.connectors import Connector, ConnectorType
from ydata.sdk.datasources import DataSource
from ydata.sdk.datasources.datasource import DataSourceType

os.environ["YDATA_TOKEN"] = 'insert-token'

if __name__ == '__main__':

    USERNAME = "username"
    PASSWORD = "pass"
    HOSTNAME = "host"
    PORT = "3306"
    DATABASE_NAME = "berka"

    conn_str = {
        "hostname": HOSTNAME,
        "username": USERNAME,
        "password": PASSWORD,
        "port": PORT,
        "database": DATABASE_NAME,
    }

    conn = Connector.get(uid='insert-id')
    print(conn)

    """ Connector creation example
    connector = Connector.create(connector_type=ConnectorType.MYSQL,
                                  credentials=conn_str,
                                  name="MySQL Berka - SDK")
    """

    datasource = DataSource(datatype=DataSourceType.TABULAR,
                            connector=conn,
                            name="MySQL Berka - SDK")
                                #query={'query': 'SELECT * FROM trans;'})

