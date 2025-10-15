from typing import Optional
from pydantic import BaseModel

class KimaiCustomer(BaseModel):
  id: Optional[int] = None
  name: str
  number: str
  comment: Optional[str] = None
  visible: bool
  billable: bool
  color: Optional[str] = None

