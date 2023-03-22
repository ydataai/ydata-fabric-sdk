from typing import Dict, List, Optional, Union

from pandas import DataFrame as pdDataFrame

from ydata.sdk.common.exceptions import InputError
from ydata.sdk.datasources import DataSource
from ydata.sdk.datasources._models.datatype import DataSourceType
from ydata.sdk.datasources._models.metadata.data_types import DataType
from ydata.sdk.synthesizers.synthesizer import BaseSynthesizer


class TimeSeriesSynthesizer(BaseSynthesizer):

    def sample(self, n_entities: Optional[int] = None) -> pdDataFrame:
        """Sample from a [`TimeSeriesSynthesizer`][ydata.sdk.synthesizers.TimeS
        eriesSynthesizer] instance.

        If a training dataset was not using any `entity` column, the Synthesizer assumes a single entity.
        A [`TimeSeriesSynthesizer`][ydata.sdk.synthesizers.TimeSeriesSynthesizer] always sample the full trajectory of its entities.

        Arguments:
            n_entities (int): (optional) number of entities to sample. If `None`, uses the same number of entities as in the original dataset.

        Returns:
            synthetic data
        """
        if n_entities is not None and n_entities < 1:
            raise InputError("Parameter 'n_entities' must be greater than 0")

        return self._sample(payload={"numberOfRecords": n_entities})

    def fit(self, X: Union[DataSource, pdDataFrame],
            sortbykey: Optional[Union[str, List[str]]],
            entity_id_cols: Optional[Union[str, List[str]]] = None,
            generate_cols: Optional[List[str]] = None,
            exclude_cols: Optional[List[str]] = None,
            dtypes: Optional[Dict[str, Union[str, DataType]]] = None,
            target: Optional[str] = None,
            name: Optional[str] = None,
            anonymize: Optional[dict] = None) -> None:
        """Fit the synthesizer.

        The synthesizer accepts as training dataset either a pandas [`DataFrame`][pandas.DataFrame] directly or a YData [`DataSource`][ydata.sdk.datasources.DataSource].

        Arguments:
            X (Union[DataSource, pandas.DataFrame]): Training dataset
            sortbykey (Union[str, List[str]]): column(s) to use to sort timeseries datasets
            entity_id_cols (Union[str, List[str]]): (optional) columns representing entities ID
            generate_cols (List[str]): (optional) columns that should be synthesized
            exclude_cols (List[str]): (optional) columns that should not be synthesized
            dtypes (Dict[str, Union[str, DataType]]): (optional) datatype mapping that will overwrite the datasource metadata column datatypes
            target (Optional[str]): (optional) Metadata associated to the datasource
            name (Optional[str]): (optional) Synthesizer instance name
            anonymize (Optional[str]): (optional) fields to anonymize and the anonymization strategy
        """
        BaseSynthesizer.fit(self, X=X, datatype=DataSourceType.TIMESERIES, sortbykey=sortbykey, entity_id_cols=entity_id_cols,
                            generate_cols=generate_cols, exclude_cols=exclude_cols, dtypes=dtypes,  target=target,
                            name=name, anonymize=anonymize)

    def __repr__(self):
        if self._model is not None:
            return self._model.__repr__()
        else:
            return "TimeSeriesSynthesizer(Not Initialized)"
