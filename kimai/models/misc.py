from pydantic import BaseModel

class KimaiMetaPairValue(BaseModel):
  name: str
  value: str
