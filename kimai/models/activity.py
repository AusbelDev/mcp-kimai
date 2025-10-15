from typing import Any, List, Optional
from pydantic import BaseModel

from kimai.models.misc import KimaiMetaPairValue

class KimaiActivity(BaseModel):
  parentTitle: Optional[str] = None
  project: Optional[int] = None
  id: Optional[int] = None
  name: str
  comment: Optional[str] = None
  visible: bool
  billable: bool
  meta_fields: List[KimaiMetaPairValue] = []
  teams: List[Any] = []
  color: str
