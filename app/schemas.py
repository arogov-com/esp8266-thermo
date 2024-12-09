from pydantic import BaseModel, Field, EmailStr, ConfigDict


class ThermoAddSchema(BaseModel):
    sid: str = Field(max_length=64)
    mac: str = Field(max_length=17)
    temp: float
    pres: float
    hum: float
    adc: float
    sha1: str
    update: bool | None
    model_config = ConfigDict(extra='forbid')


class KeyAddSchema(BaseModel):
    name: str = Field(max_length=64)
    email: str = EmailStr()
    perm_add_key: bool
    perm_delete_key: bool
    perm_delete_thermo: bool
    perm_read_key: bool
    perm_read_thermo: bool
    perm_add_thermo: bool
    model_config = ConfigDict(extra='forbid')


class KeySchema(KeyAddSchema):
    id: int
    key: str
    enabled: bool
    created: int


class ResponseSchema(BaseModel):
    status: bool
    reason: str


class DeleteSchema(BaseModel):
    id: int = Field(ge=0)
    model_config = ConfigDict(extra='forbid')
