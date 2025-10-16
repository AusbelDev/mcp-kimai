from pydantic import BaseModel

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
