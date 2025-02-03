from typing import List, Optional

from pydantic import Field

from ydata.sdk.common.model import BaseModel, Config
from ydata.sdk.common.pydantic_utils import to_camel


class BaseConfig(Config):
    alias_generator = to_camel


class TableColumn(BaseModel):
    """Class to store the information of a Column table."""
    model_config = BaseConfig()

    name: str
    variable_type: str  # change this to the datatypes
    primary_key: Optional[bool]
    is_foreign_key: Optional[bool]
    foreign_keys: list
    nullable: bool


class Table(BaseModel):
    """Class to store the table columns information."""
    model_config = BaseConfig()

    name: str
    columns: List[TableColumn]
    primary_keys: List[TableColumn]
    foreign_keys: List[TableColumn]


class Schema(BaseModel):
    """Class to store the database schema information."""
    model_config = BaseConfig()

    name: str
    tables: Optional[List[Table]] = Field(None)
