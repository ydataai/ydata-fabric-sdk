from __future__ import annotations

from time import sleep
from typing import Dict, List, Optional, Union

from ydata.datascience.common import PrivacyLevel
from ydata.sdk.common.client import Client
from ydata.sdk.common.config import BACKOFF
from ydata.sdk.common.exceptions import ConnectorError, InputError
from ydata.sdk.common.types import UID, Project
from ydata.sdk.connectors.connector import Connector, ConnectorType
from ydata.sdk.datasources import DataSource
from ydata.sdk.datasources._models.datatype import DataSourceType
from ydata.sdk.datasources._models.metadata.data_types import DataType
from ydata.sdk.synthesizers.synthesizer import BaseSynthesizer


class MultiTableSynthesizer(BaseSynthesizer):
    """MultiTable synthesizer class.

    Methods
    -------
    - `fit`: train a synthesizer instance.
    - `sample`: request synthetic data.
    - `status`: current status of the synthesizer instance.

    Note:
            The synthesizer instance is created in the backend only when the `fit` method is called.

    Arguments:
        write_connector (UID | Connector): Connector of type RDBMS to be used to write the samples
        uid (UID): (optional) UID to identify this synthesizer
        name (str): (optional) Name to be used when creating the synthesizer. Calculated internally if not provided
        client (Client): (optional) Client to connect to the backend
    """

    def __init__(
            self, write_connector: Union[Connector, UID], uid: Optional[UID] = None, name: Optional[str] = None,
            project: Optional[Project] = None, client: Optional[Client] = None):

        super().__init__(uid, name, project, client)

        connector = self._check_or_fetch_connector(write_connector)
        self.__write_connector = connector.uid

    def fit(self, X: DataSource,
            datatype: Optional[Union[DataSourceType, str]] = None,
            dtypes: Optional[Dict[str, Union[str, DataType]]] = None,
            anonymize: Optional[dict] = None) -> None:
        """Fit the synthesizer.

        The synthesizer accepts as training dataset a YData [`DataSource`][ydata.sdk.datasources.DataSource].
        Except X, all the other arguments are for now ignored until they are supported.

        Arguments:
            X (DataSource): DataSource to Train
        """
        #self._fit_from_datasource(X, datatype=DataSourceType.MULTITABLE)
        super().fit(X, datatype=DataSourceType.MULTITABLE)

    def sample(self, frac: Union[int, float] = 1, write_connector: Optional[Union[Connector, UID]] = None) -> None:
        """Sample from a [`MultiTableSynthesizer`][ydata.sdk.synthesizers.MultiTableSynthesizer]
        instance.
        The sample is saved in the connector that was provided in the synthesizer initialization
        or in the

        Arguments:
            frac (int | float): fraction of the sample to be returned
        """

        assert frac >= 0.1, InputError(
            "It is not possible to generate an empty synthetic data schema. Please validate the input provided. ")
        assert frac <= 5, InputError(
            "It is not possible to generate a database that is 5x bigger than the original dataset. Please validate the input provided.")

        payload = {
            'fraction': frac,
        }

        if write_connector is not None:
            connector = self._check_or_fetch_connector(write_connector)
            payload['writeConnector'] = connector.uid

        response = self._client.post(
            f"/synthesizer/{self.uid}/sample", json=payload, project=self._project)

        data = response.json()
        sample_uid = data.get('uid')
        sample_status = None
        while sample_status not in ['finished', 'failed']:
            self._logger.info('Sampling from the synthesizer...')
            response = self._client.get(
                f'/synthesizer/{self.uid}/history', project=self._project)
            history = response.json()
            sample_data = next((s for s in history if s.get('uid') == sample_uid), None)
            sample_status = sample_data.get('status', {}).get('state')
            sleep(BACKOFF)

        print(
            f"Sample created and saved into connector with ID {self.__write_connector or write_connector}")

    def _create_payload(self) -> dict:
        payload = super()._create_payload()
        payload['writeConnector'] = self.__write_connector

        return payload

    def _check_or_fetch_connector(self, write_connector: Union[Connector, UID]) -> Connector:
        self._logger.debug(f'Write connector is {write_connector}')
        if isinstance(write_connector, str):
            self._logger.debug(f'Write connector is of type `UID` {write_connector}')
            write_connector = Connector.get(write_connector)
            self._logger.debug(f'Using fetched connector {write_connector}')

        if write_connector.uid is None:
            raise InputError("Invalid connector provided as input for write")

        if write_connector.type not in [ConnectorType.AZURE_SQL, ConnectorType.MYSQL, ConnectorType.SNOWFLAKE]:
            raise ConnectorError(
                f"Invalid type `{write_connector.type}` for the provided connector")

        return write_connector
