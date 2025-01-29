from abc import ABC, abstractmethod
from io import StringIO
from time import sleep
from typing import Dict, List, Optional, Union
from uuid import uuid4

from pandas import DataFrame as pdDataFrame
from pandas import read_csv
from typeguard import typechecked

from ydata.datascience.common import PrivacyLevel
from ydata.sdk.common.client import Client
from ydata.sdk.common.client.utils import init_client
from ydata.sdk.common.config import BACKOFF, LOG_LEVEL
from ydata.sdk.common.exceptions import (AlreadyFittedError, DataSourceAttrsError, DataSourceNotAvailableError,
                                         DataTypeMissingError, EmptyDataError, FittingError, InputError)
from ydata.sdk.common.logger import create_logger
from ydata.sdk.common.types import UID, Project
from ydata.sdk.connectors import LocalConnector
from ydata.sdk.datasources._models.attributes import DataSourceAttrs
from ydata.sdk.datasources._models.datatype import DataSourceType
from ydata.sdk.datasources._models.metadata.data_types import DataType
from ydata.sdk.datasources._models.metadata.metadata import Metadata
from ydata.sdk.datasources._models.status import State as dsState
from ydata.sdk.synthesizers._models.status import PrepareState, Status, TrainingState
from ydata.sdk.synthesizers._models.synthesizer import Synthesizer as mSynthesizer
from ydata.sdk.synthesizers._models.synthesizers_list import SynthesizersList
from ydata.sdk.synthesizers.anonymizer import build_and_validate_anonimization
from ydata.sdk.utils.logger import SDKLogger
from ydata.sdk.utils.model_mixin import ModelFactoryMixin

logger = SDKLogger(name="SynthesizersLogger")


@typechecked
class BaseSynthesizer(ABC, ModelFactoryMixin):
    """Main synthesizer class.

    This class cannot be directly instanciated because of the specificities between [`RegularSynthesizer`][ydata.sdk.synthesizers.RegularSynthesizer], [`TimeSeriesSynthesizer`][ydata.sdk.synthesizers.TimeSeriesSynthesizer] or [`MultiTableSynthesizer`][ydata.sdk.synthesizers.MultiTableSynthesizer] `sample` methods.

    Methods
    -------
    - `fit`: train a synthesizer instance.
    - `sample`: request synthetic data.
    - `status`: current status of the synthesizer instance.

    Note:
            The synthesizer instance is created in the backend only when the `fit` method is called.

    Arguments:
        client (Client): (optional) Client to connect to the backend
    """

    def __init__(
            self, uid: Optional[UID] = None, name: Optional[str] = None,
            project: Optional[Project] = None, client: Optional[Client] = None):
        self._init_common(client=client)
        self._model = mSynthesizer(uid=uid, name=name or str(uuid4()))
        self._project = project

    @init_client
    def _init_common(self, client: Optional[Client] = None):
        self._client = client
        self._logger = create_logger(__name__, level=LOG_LEVEL)

    @property
    def project(self) -> Project:
        return self._project or self._client.project

    def fit(self, X,
            privacy_level: PrivacyLevel = PrivacyLevel.HIGH_FIDELITY,
            datatype: Optional[Union[DataSourceType, str]] = None,
            sortbykey: Optional[Union[str, List[str]]] = None,
            entities: Optional[Union[str, List[str]]] = None,
            generate_cols: Optional[List[str]] = None,
            exclude_cols: Optional[List[str]] = None,
            dtypes: Optional[Dict[str, Union[str, DataType]]] = None,
            target: Optional[str] = None,
            anonymize: Optional[dict] = None,
            condition_on: Optional[List[str]] = None) -> None:
        """Fit the synthesizer.

        The synthesizer accepts as training dataset either a pandas [`DataFrame`][pandas.DataFrame] directly or a YData [`DataSource`][ydata.sdk.datasources.DataSource].
        When the training dataset is a pandas [`DataFrame`][pandas.DataFrame], the argument `datatype` is required as it cannot be deduced.

        The argument`sortbykey` is mandatory for [`TimeSeries`][ydata.sdk.datasources.DataSourceType.TIMESERIES].

        By default, if `generate_cols` or `exclude_cols` are not specified, all columns are generated by the synthesizer.
        The argument `exclude_cols` has precedence over `generate_cols`, i.e. a column `col` will not be generated if it is in both list.

        Arguments:
            X (Union[DataSource, pandas.DataFrame]): Training dataset
            privacy_level (PrivacyLevel): Synthesizer privacy level (defaults to high fidelity)
            datatype (Optional[Union[DataSourceType, str]]): (optional) Dataset datatype - required if `X` is a [`pandas.DataFrame`][pandas.DataFrame]
            sortbykey (Union[str, List[str]]): (optional) column(s) to use to sort timeseries datasets
            entities (Union[str, List[str]]): (optional) columns representing entities ID
            generate_cols (List[str]): (optional) columns that should be synthesized
            exclude_cols (List[str]): (optional) columns that should not be synthesized
            dtypes (Dict[str, Union[str, DataType]]): (optional) datatype mapping that will overwrite the datasource metadata column datatypes
            target (Optional[str]): (optional) Target for the dataset
            name (Optional[str]): (optional) Synthesizer instance name
            anonymize (Optional[str]): (optional) fields to anonymize and the anonymization strategy
            condition_on: (Optional[List[str]]): (optional) list of features to condition upon
        """

        logger.info(dataframe=X,
                    datatype=datatype.value,
                    method='synthesizer')

        if self._already_fitted():
            raise AlreadyFittedError()

        datatype = DataSourceType(datatype)

        dataset_attrs = self._init_datasource_attributes(
            sortbykey, entities, generate_cols, exclude_cols, dtypes)

        self._validate_datasource_attributes(X, dataset_attrs, datatype, target)

        # If the training data is a pandas dataframe, we first need to create a data source and then the instance
        if isinstance(X, pdDataFrame):
            from ydata.sdk.datasources import LocalDataSource
            if X.empty:
                raise EmptyDataError("The DataFrame is empty")
            self._logger.info('creating local connector with pandas dataframe')
            connector = LocalConnector.create(
                source=X, project=self._project, client=self._client)
            self._logger.info(
                f'created local connector. creating datasource with {connector}')
            _X = LocalDataSource(connector=connector, project=self._project,
                                 datatype=datatype, client=self._client)
            self._logger.info(f'created datasource {_X}')
        else:
            _X = X

        if dsState(_X.status.state) != dsState.AVAILABLE:
            raise DataSourceNotAvailableError(
                f"The datasource '{_X.uid}' is not available (status = {_X.status})")

        if isinstance(dataset_attrs, dict):
            dataset_attrs = DataSourceAttrs(**dataset_attrs)

        if datatype == DataSourceType.MULTITABLE:
            self._fit_from_datasource(_X, datatype=DataSourceType.MULTITABLE)
        else:
            self._fit_from_datasource(
                X=_X, datatype=datatype, dataset_attrs=dataset_attrs, target=target,
                anonymize=anonymize, privacy_level=privacy_level, condition_on=condition_on)

    @staticmethod
    def _init_datasource_attributes(
            sortbykey: Optional[Union[str, List[str]]],
            entities: Optional[Union[str, List[str]]],
            generate_cols: Optional[List[str]],
            exclude_cols: Optional[List[str]],
            dtypes: Optional[Dict[str, Union[str, DataType]]]) -> DataSourceAttrs:
        dataset_attrs = {
            'sortbykey': sortbykey if sortbykey is not None else [],
            'entities': entities if entities is not None else [],
            'generate_cols': generate_cols if generate_cols is not None else [],
            'exclude_cols': exclude_cols if exclude_cols is not None else [],
            'dtypes': {k: DataType(v) for k, v in dtypes.items()} if dtypes is not None else {}
        }
        return DataSourceAttrs(**dataset_attrs)

    @staticmethod
    def _validate_datasource_attributes(X, dataset_attrs: DataSourceAttrs, datatype: DataSourceType, target: Optional[str]):
        columns = []
        if isinstance(X, pdDataFrame):
            columns = X.columns
            if datatype is None:
                raise DataTypeMissingError(
                    "Argument `datatype` is mandatory for pandas.DataFrame training data")
        elif datatype == DataSourceType.MULTITABLE:
            tables = [t for t in X.tables.keys()]  # noqa: F841
            # Does it make sense to add more validations here?
        else:
            columns = [c.name for c in X.metadata.columns]

        if datatype != DataSourceType.MULTITABLE:
            if target is not None and target not in columns:
                raise DataSourceAttrsError(
                    "Invalid target: column '{target}' does not exist")

            if datatype == DataSourceType.TIMESERIES:
                if not dataset_attrs.sortbykey:
                    raise DataSourceAttrsError(
                        "The argument `sortbykey` is mandatory for timeseries datasource.")

            invalid_fields = {}
            for field, v in dataset_attrs.dict().items():
                field_columns = v if field != 'dtypes' else v.keys()
                not_in_cols = [c for c in field_columns if c not in columns]
                if len(not_in_cols) > 0:
                    invalid_fields[field] = not_in_cols

            if len(invalid_fields) > 0:
                error_msgs = ["\t- Field '{}': columns {} do not exist".format(
                    f, ', '.join(v)) for f, v in invalid_fields.items()]
                raise DataSourceAttrsError(
                    "The dataset attributes are invalid:\n {}".format('\n'.join(error_msgs)))

    @staticmethod
    def _metadata_to_payload(
        datatype: DataSourceType, ds_metadata: Metadata,
        dataset_attrs: Optional[DataSourceAttrs] = None, target: Optional[str] = None
    ) -> dict:
        """Transform a the metadata and dataset attributes into a valid
        payload.

        Arguments:
            datatype (DataSourceType): datasource type
            ds_metadata (Metadata): datasource metadata object
            dataset_attrs ( Optional[DataSourceAttrs] ): (optional) Dataset attributes
            target (Optional[str]): (optional) target column name

        Returns:
            metadata payload dictionary
        """

        columns = [
            {
                'name': c.name,
                'generation': True and c.name not in dataset_attrs.exclude_cols,
                'dataType': DataType(dataset_attrs.dtypes[c.name]).value if c.name in dataset_attrs.dtypes else c.datatype,
                'varType': c.vartype,
            }
            for c in ds_metadata.columns]

        metadata = {
            'columns': columns,
            'target': target
        }

        if dataset_attrs is not None:
            if datatype == DataSourceType.TIMESERIES:
                metadata['sortBy'] = [c for c in dataset_attrs.sortbykey]
                metadata['entity'] = [c for c in dataset_attrs.entities]

        return metadata

    def _fit_from_datasource(
        self,
        X,
        datatype: DataSourceType,
        privacy_level: Optional[PrivacyLevel] = None,
        dataset_attrs: Optional[DataSourceAttrs] = None,
        target: Optional[str] = None,
        anonymize: Optional[dict] = None,
        condition_on: Optional[List[str]] = None
    ) -> None:
        payload = self._create_payload()

        payload['dataSourceUID'] = X.uid

        if privacy_level:
            payload['privacyLevel'] = privacy_level.value

        if X.metadata is not None:
            payload['metadata'] = self._metadata_to_payload(
                datatype, X.metadata, dataset_attrs, target)

        payload['type'] = str(datatype.value)

        if anonymize is not None:
            # process and validated the anonymization config shared by the end user
            anonymize = build_and_validate_anonimization(
                anonimyze=anonymize, cols=[col.name for col in X.metadata.columns])
            payload["extraData"]["anonymize"] = anonymize
        if condition_on is not None:
            payload["extraData"]["condition_on"] = condition_on

        response = self._client.post(
            '/synthesizer/', json=payload, project=self._project)
        data = response.json()
        self._model = mSynthesizer(**data)
        while self._check_fitting_not_finished(self.status):
            self._logger.info('Training the synthesizer...')
            sleep(BACKOFF)

    def _create_payload(self) -> dict:
        payload = {
            'extraData': {}
        }

        if self._model and self._model.name:
            payload['name'] = self._model.name

        return payload

    def _check_fitting_not_finished(self, status: Status) -> bool:
        self._logger.debug(f'checking status {status}')

        if Status.State(status.state) in [Status.State.READY, Status.State.REPORT]:
            return False

        self._logger.debug(f'status not ready yet {status.state}')

        if status.prepare and PrepareState(status.prepare.state) == PrepareState.FAILED:
            raise FittingError('Could not train the synthesizer')

        if status.training and TrainingState(status.training.state) == TrainingState.FAILED:
            raise FittingError('Could not train the synthesizer')

        return True

    @abstractmethod
    def sample(self) -> pdDataFrame:
        """Abstract method to sample from a synthesizer."""

    def _sample(self, payload: Dict) -> pdDataFrame:
        """Sample from a synthesizer.

        Arguments:
            payload (dict): payload configuring the sample request

        Returns:
            pandas `DataFrame`
        """
        response = self._client.post(
            f"/synthesizer/{self.uid}/sample", json=payload, project=self._project)

        data: Dict = response.json()
        sample_uid = data.get('uid')
        sample_status = None
        while sample_status not in ['finished', 'failed']:
            self._logger.info('Sampling from the synthesizer...')
            response = self._client.get(
                f'/synthesizer/{self.uid}/history', project=self._project)
            history: Dict = response.json()
            sample_data = next((s for s in history if s.get('uid') == sample_uid), None)
            sample_status = sample_data.get('status', {}).get('state')
            sleep(BACKOFF)

        response = self._client.get_static_file(
            f'/synthesizer/{self.uid}/sample/{sample_uid}/sample.csv', project=self._project)
        data = StringIO(response.content.decode())
        return read_csv(data)

    @property
    def uid(self) -> UID:
        """Get the status of a synthesizer instance.

        Returns:
            Synthesizer status
        """
        if not self._is_initialized():
            return Status.State.NOT_INITIALIZED

        return self._model.uid

    @property
    def status(self) -> Status:
        """Get the status of a synthesizer instance.

        Returns:
            Synthesizer status
        """
        if not self._is_initialized():
            return Status.not_initialized()

        try:
            self = self.get()
            return self._model.status
        except Exception:  # noqa: PIE786
            return Status.unknown()

    def get(self):
        assert self._is_initialized() and self._model.uid, InputError(
            "Please provide the synthesizer `uid`")

        response = self._client.get(f'/synthesizer/{self.uid}', project=self._project)
        data = response.json()
        self._model = mSynthesizer(**data)

        return self

    @staticmethod
    @init_client
    def list(client: Optional[Client] = None) -> SynthesizersList:
        """List the synthesizer instances.

        Arguments:
            client (Client): (optional) Client to connect to the backend

        Returns:
            List of synthesizers
        """
        def __process_data(data: list) -> list:
            to_del = ['metadata', 'report', 'mode']
            for e in data:
                for k in to_del:
                    e.pop(k, None)
            return data

        response = client.get('/synthesizer')
        data: list = response.json()
        data = __process_data(data)

        return SynthesizersList(data)

    def _is_initialized(self) -> bool:
        """Determine if a synthesizer is instanciated or not.

        Returns:
            True if the synthesizer is instanciated
        """
        return self._model is not None

    def _already_fitted(self) -> bool:
        """Determine if a synthesizer is already fitted.

        Returns:
            True if the synthesizer is instanciated
        """

        return self._is_initialized() and \
            (self._model.status is not None
             and self._model.status.training is not None
             and self._model.status.training.state is not [TrainingState.PREPARING])

    @staticmethod
    def _resolve_api_status(api_status: Dict) -> Status:
        """Determine the status of the Synthesizer.

        The status of the synthesizer instance is determined by the state of
        its different components.

        Arguments:
            api_status (dict): json from the endpoint GET /synthesizer

        Returns:
            Synthesizer Status
        """
        status = Status(api_status.get('state', Status.UNKNOWN.name))
        if status == Status.PREPARE:
            if PrepareState(api_status.get('prepare', {}).get(
                    'state', PrepareState.UNKNOWN.name)) == PrepareState.FAILED:
                return Status.FAILED
        elif status == Status.TRAIN:
            if TrainingState(api_status.get('training', {}).get(
                    'state', TrainingState.UNKNOWN.name)) == TrainingState.FAILED:
                return Status.FAILED
        elif status == Status.REPORT:
            return Status.READY
        return status
