from typing import Any, Dict, List, Optional
from pydantic import BaseModel, field_serializer, model_validator
from datetime import datetime

from kimai.models.activity import KimaiActivityDetails
from kimai.models.misc import KimaiMetaPairValue
from kimai.models.project import KimaiProject


# TODO: Again, find a way to map camelCase to snake_case
# Hint: Use Pydantic Config (?)
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
    rate: Optional[float] = None
    internalRate: Optional[float] = None
    fixedRate: Optional[int] = None
    hourlyRate: Optional[float] = None
    exported: bool
    billable: bool
    metaFields: List[KimaiMetaPairValue] = []


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
    @model_validator(mode="before")
    @classmethod
    def map_to_snake_case(cls, data: Any):
        mapping = {
            "internalRate": "internal_rate",
            "metaFields": "meta_fields",
        }
        for camel_case, snake_case in mapping.items():
            if camel_case in data:
                data[snake_case] = data.pop(camel_case)

        return data


class KimaiTimesheetCollectionDetails(BaseModel):
    user: Optional[int] = None
    tags: List[str] = []
    id: Optional[int] = None
    begin: datetime
    end: Optional[datetime] = None
    duration: Optional[int] = None
    activity: KimaiActivityDetails
    description: Optional[str] = None
    rate: Optional[float] = None
    internalRate: Optional[float] = None
    exported: bool
    billable: bool
    metaFields: List[KimaiMetaPairValue] = []


class KimaiTimesheet(BaseModel):
    begin: datetime
    end: Optional[datetime] = None
    project: int
    activity: int
    description: Optional[str] = None
    fixedRate: Optional[str] = None
    hourlyRate: Optional[str] = None
    user: Optional[int] = None
    exported: Optional[bool] = None
    billable: Optional[bool] = None
    tags: List[str] = []

    @field_serializer("tags")
    def join_tags(self, value) -> str:
        return ",".join(value)

    @field_serializer("begin", "end")
    def datetimes_to_iso(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.isoformat()
        return None
