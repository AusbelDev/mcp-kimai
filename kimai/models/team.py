from typing import List, Optional
from pydantic import BaseModel

from kimai.models.activity import KimaiActivity
from kimai.models.customer import KimaiCustomer
from kimai.models.project import KimaiProjectCollection
from kimai.models.user import KimaiUser

class TeamMember(BaseModel):
  user: KimaiUser
  teamlead: bool

class KimaiTeamCollection(BaseModel):
  id: Optional[int] = None
  name: str
  color: str

class KimaiTeam(KimaiTeamCollection):
  teamlead: KimaiUser
  users: List[KimaiUser] = []
  members: List[TeamMember] = []
  customers: List[KimaiCustomer] = []
  # projects: List[KimaiProjectCollection] = []
  activities: List[KimaiActivity] = []

