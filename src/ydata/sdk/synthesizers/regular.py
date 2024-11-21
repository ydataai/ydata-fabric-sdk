from typing import Dict, List, Optional, Union

from pandas import DataFrame as pdDataFrame

from ydata.datascience.common import PrivacyLevel
from ydata.sdk.common.exceptions import InputError
from ydata.sdk.datasources import DataSource
from ydata.sdk.datasources._models.datatype import DataSourceType
from ydata.sdk.datasources._models.metadata.data_types import DataType
from ydata.sdk.synthesizers.synthesizer import BaseSynthesizer


class RegularSynthesizer(BaseSynthesizer):

    def sample(self, n_samples: int = 1, condition_on: Optional[dict] = None) -> pdDataFrame:
        """Sample from a [`RegularSynthesizer`][ydata.sdk.synthesizers.RegularSynthesizer]
        instance.

        Arguments:
            n_samples (int): number of rows in the sample
            condition_on: (Optional[dict]): (optional) conditional sampling parameters

        Returns:
            synthetic data
        """
        if n_samples < 1:
            raise InputError("Parameter 'n_samples' must be greater than 0")

        payload = {"numberOfRecords": n_samples}
        if condition_on is not None:
            payload["extraData"] = {
                "condition_on": condition_on
            }
        return self._sample(payload=payload)

    def fit(self, X,
            privacy_level: PrivacyLevel = PrivacyLevel.HIGH_FIDELITY,
            entities: Optional[Union[str, List[str]]] = None,
            generate_cols: Optional[List[str]] = None,
            exclude_cols: Optional[List[str]] = None,
            dtypes: Optional[Dict[str, Union[str, DataType]]] = None,
            target: Optional[str] = None,
            anonymize: Optional[dict] = None,
            condition_on: Optional[List[str]] = None) -> None:
        """Fit the synthesizer.

        The synthesizer accepts as training dataset either a pandas [`DataFrame`][pandas.DataFrame] directly or a YData [`DataSource`][ydata.sdk.datasources.DataSource].

        Arguments:
            X (Union[DataSource, pandas.DataFrame]): Training dataset
            privacy_level (PrivacyLevel): Synthesizer privacy level (defaults to high fidelity)
            entities (Union[str, List[str]]): (optional) columns representing entities ID
            generate_cols (List[str]): (optional) columns that should be synthesized
            exclude_cols (List[str]): (optional) columns that should not be synthesized
            dtypes (Dict[str, Union[str, DataType]]): (optional) datatype mapping that will overwrite the datasource metadata column datatypes
            target (Optional[str]): (optional) Target column
            name (Optional[str]): (optional) Synthesizer instance name
            anonymize (Optional[str]): (optional) fields to anonymize and the anonymization strategy
            condition_on: (Optional[List[str]]): (optional) list of features to condition upon
        """
        BaseSynthesizer.fit(self, X=X, datatype=DataSourceType.TABULAR, entities=entities,
                            generate_cols=generate_cols, exclude_cols=exclude_cols, dtypes=dtypes,
                            target=target, anonymize=anonymize, privacy_level=privacy_level,
                            condition_on=condition_on)

    def __repr__(self):
        if self._model is not None:
            return self._model.__repr__()
        else:
            return "RegularSynthesizer(Not Initialized)"
