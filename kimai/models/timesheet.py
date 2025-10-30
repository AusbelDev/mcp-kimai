import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

import pytz
from models.activity import KimaiActivityDetails
from models.misc import KimaiMetaPairValue
from pydantic import BaseModel, field_serializer, model_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _to_utc_iso(dt: datetime, env_tz: str) -> str:
    """Normalize a datetime (naive or aware) to UTC and return ISO-8601."""
    if dt.tzinfo is None:
        tz = pytz.timezone(env_tz)
        # Localize with DST awareness
        try:
            aware = tz.localize(
                dt, is_dst=None
            )  # let pytz determine DST; raises on edge cases
        except pytz.AmbiguousTimeError:
            # Fall back to standard time (is_dst=False) if time is ambiguous (fall-back hour)
            aware = tz.localize(dt, is_dst=False)
        except pytz.NonExistentTimeError:
            # If the time never occurred (spring-forward gap), bump 1 hour and mark DST
            aware = tz.localize(dt + timedelta(hours=1), is_dst=True)
    else:
        aware = dt

    utc_dt = aware.astimezone(timezone.utc)
    return utc_dt.isoformat()


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
        if value is None:
            return None

        tz_env = os.environ.get("MCP_TIMEZONE", "America/Mexico_City")

        try:
            iso_utc = _to_utc_iso(value, tz_env)

            tz = pytz.timezone(tz_env)
            local_now = datetime.now(tz)
            utc_now = datetime.now(timezone.utc)
            utcoffset = local_now.utcoffset() or timedelta(0)
            hours_offset = int(utcoffset.total_seconds() // 3600)

            iso_utc_dt = datetime.fromisoformat(iso_utc)
            if abs(hours_offset) > 0:
                if hours_offset > 0:
                    corrected_value = iso_utc_dt - timedelta(hours=hours_offset)
                elif hours_offset < 0:
                    corrected_value = iso_utc_dt + timedelta(hours=abs(hours_offset))
            else:
                corrected_value = iso_utc_dt

            logger.info(
                "Serialized datetime to UTC. "
                f"ENV_TZ={tz_env}, offset_hours={hours_offset}, "
                f"input={value!r}, output_utc={iso_utc}, "
                f"now_utc={utc_now.isoformat()}, now_local={local_now.isoformat()}, "
                f"Corrected value={corrected_value if abs(hours_offset) > 0 else 'N/A'}"
            )

            return corrected_value.isoformat() if abs(hours_offset) > 0 else iso_utc

        except Exception:
            logger.exception(
                "Failed to convert datetime to UTC; returning best-effort value."
            )
            # Best-effort fallback: if value is aware, at least convert that to UTC
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).isoformat()
            return None
