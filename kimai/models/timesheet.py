import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

import pytz
from models.activity import KimaiActivityDetails
from models.misc import KimaiMetaPairValue
from pydantic import BaseModel, field_serializer, model_validator

logger = logging.getLogger(__name__)


# FIXME: Doesnt load the dotenv variables here, so MCP_TIMEZONE is not found
# TODO: Again, find a way to map camelCase to snake_case
# Hint: Use Pydantic Config (?)
class KimaiTimesheetEntity(BaseModel):
    activity: Optional[int] = None
    project: Optional[int] = None
    id: Optional[int] = None
    begin: datetime
    end: Optional[datetime] = None
    duration: Optional[int] = None
    description: Optional[str] = None
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

    # @field_serializer("tags")
    # def join_tags(self, value) -> str:
    #     return ",".join(value)

    @field_serializer("begin", "end")
    def datetimes_to_iso(self, value: Optional[datetime]) -> Optional[str]:
        _timezone = os.environ.get("MCP_TIMEZONE", "America/Mexico_City")
        local_dt = datetime.now(pytz.timezone(_timezone))
        utco = local_dt.utcoffset() or timedelta(0)
        hours_offset = int(utco.total_seconds() // 3600)

        logger.info(
            f"TZ: {_timezone}, Timezone offset hours: {hours_offset}, UTC time: {datetime.now(timezone.utc)}, Local time: {datetime.now(pytz.timezone(_timezone))}"
        )
        if value:
            return (value - timedelta(hours=hours_offset)).isoformat()
        return None
