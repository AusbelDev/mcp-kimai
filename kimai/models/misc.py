from typing import Literal, TypeAlias
from pydantic import BaseModel

VisibilityOptions: TypeAlias = Literal["visible", "hidden", "all"]
OrderByOptions: TypeAlias = Literal["id", "name", "project"]
OrderDirectionOptions: TypeAlias = Literal["ASC", "DESC"]

class KimaiVersion(BaseModel):
  version: str
  versionId: int
  candidate: str
  semver: str
  name: str
  copyright: str

class KimaiMetaPairValue(BaseModel):
  name: str
  value: str
