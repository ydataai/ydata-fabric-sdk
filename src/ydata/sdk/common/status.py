from typing import Generic, Optional, TypeVar

from pydantic import ConfigDict, Field

from .model import BaseModel

T = TypeVar("T")


class GenericStateErrorStatus(BaseModel, Generic[T]):
    model_config = ConfigDict(
        use_enum_values=True
    )
    state: Optional[T] = Field(None)
