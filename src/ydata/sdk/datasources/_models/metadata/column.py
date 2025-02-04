from pydantic import Field, ConfigDict

from ydata.sdk.common.model import BaseModel
from ydata.sdk.datasources._models.metadata.data_types import DataType, VariableType


class Column(BaseModel):
    model_config = ConfigDict(
        use_enum_values = True
    )

    name: str
    datatype: DataType = Field(alias='dataType')
    vartype: VariableType = Field(alias='varType')

    def __repr__(self) -> str:
        return f"Column(name={self.name}, datatype={self.datatype}, vartype={self.vartype})"

    def __str__(self) -> str:
        return super().__repr__()
