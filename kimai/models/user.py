from typing import Any
from pydantic import BaseModel, model_validator

class KimaiUserEntity(BaseModel):
  language: str
  timezone: str
  preferences: Any

class KimaiUser(BaseModel):
  id: int
  alias: str
  username: str
  account_number: str
  enabled: str
  color: str

  @model_validator(mode="before")
  @classmethod
  def map_account_number(cls, data: Any):
    cls.account_number = data.accountNumber

    return data
