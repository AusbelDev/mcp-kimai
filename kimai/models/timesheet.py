from typing import Any, Dict, List, Optional
from pydantic import BaseModel, model_validator
from datetime import datetime

from kimai.models.misc import KimaiMetaPairValue

class KimaiTimesheetEntity(BaseModel):
  activity: Optional[int] = None
  project: Optional[int] = None
  user: Optional[int] = None
  tags: List[str] = []
  id: Optional[int] = None
  begin: datetime
  end: Optional[datetime] = None
  duration: Optional[int] = None
  description: Optional[str] = None
  rate: Optional[int] = None
  internal_rate: Optional[int] = None
  fixed_rate: Optional[int] = None
  hourly_rate: Optional[int] = None
  exported: bool
  billable: bool
  meta_fields: List[KimaiMetaPairValue] = []

class KimaiTimesheetCollection(BaseModel):
  activity: Optional[int] = None
  project: Optional[int] = None
  user: Optional[int] = None
  tags: List[str] = []
  id: Optional[int] = None
  begin: datetime
  end: Optional[datetime] = None
  duration: Optional[int] = None
  description: Optional[str] = None
  rate: Optional[int] = None
  internal_rate: Optional[int] = None
  exported: bool
  billable: bool
  meta_fields: List[KimaiMetaPairValue] = []

  # TODO: Find a way to map camelCase fields to their snake_case equivalents
  @model_validator(mode = "before")
  @classmethod
  def map_to_snake_case(cls, data: Any):
    if("internalRate" not in data): raise Exception(f'No field called "internalRate" in data')
    if("metaFields" not in data): raise Exception(f'No field called "metaFields" in data')

    print(data)

    cls.internal_rate = data.get("internalRate")
    cls.meta_fields = data.get("metaFields")

    return data

class KimaiTimesheetCollectionDetails(BaseModel):
  user: Optional[int] = None

class KimaiTimesheet(BaseModel):
  begin: datetime
  end: datetime
  project: int
  activity: int
  description: str
  fixed_rate: int
  hourly_rate: int
  user: int
  exported: bool
  billable: bool
  tags: List[str]

  def format_to_submit(self) -> Dict[str, Any]:
    return {
      "begin": self.begin.isoformat(),
      "end": self.end.isoformat(),
      "project": self.project,
      "activity": self.activity,
      "description": self.description,
      "fixedRate": self.fixed_rate,
      "hourlyRate": self.hourly_rate,
      "user": self.user,
      "exported": self.exported,
      "billable": self.billable,
      "tags": ",".join(self.tags)
    }
