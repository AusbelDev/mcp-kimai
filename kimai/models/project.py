from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from kimai.models.customer import KimaiProjectCustomer
from kimai.models.misc import KimaiMetaPairValue
# TODO: Find a way to add KimaiTeam to projects.
# WARNING: If imported, it adds circular imports
# from kimai.models.team import KimaiTeam

class KimaiProjectCollection(BaseModel):
  parentTitle: Optional[str] = None
  customer: Optional[int] = None
  id: Optional[int] = None
  name: str
  start: Optional[datetime] = None
  end: Optional[datetime] = None
  comment: Optional[str] = None
  visible: bool
  billable: bool
  meta_fields: List[KimaiMetaPairValue] = []
  # teams: List[KimaiTeam] = []
  globalActivities: bool
  color: Optional[str] = None

class KimaiProject(BaseModel):
  customer: Optional[KimaiProjectCustomer] = None
  id: Optional[int] = None
  name: str
  comment: Optional[str] = None
  visible: bool
  billable: bool
  globalActivities: bool
  color: Optional[str] = None
