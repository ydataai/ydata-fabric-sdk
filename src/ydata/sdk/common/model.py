from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class Config(ConfigDict):
    populate_by_name = True
    extra = 'allow'
    use_enum_values = True


class BaseModel(PydanticBaseModel):
    """BaseModel replacement from pydantic.

    All datamodel from YData SDK inherits from this class.
    """
    model_config = Config()
