from datetime import datetime
import os

from typing import Any, List, Optional
from pydantic import BaseModel, field_serializer
from kimai.models.misc import OrderByOptions, OrderDirectionOptions, VisibilityOptions

class KimaiRequestHeaders:
  user_token: str
  user_password: str
  cookies: str

  def __init__(self):
    KIMAI_USER = os.getenv("KIMAI_USER")
    KIMAI_TOKEN = os.getenv("KIMAI_TOKEN")

    if(not(KIMAI_USER and KIMAI_TOKEN)):
      raise Exception("Cannot instantiate headers without crucial data")

    self.user_token = KIMAI_USER
    self.user_password = KIMAI_TOKEN

  def as_headers(self) -> Any:
    return {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'X-AUTH-USER': self.user_token,
      'X-AUTH-TOKEN': self.user_password
    }

class IKimaiFetchActivitiesParams(BaseModel):
  project: Optional[str] = None
  projects: Optional[List[str]] = None
  visible: Optional[VisibilityOptions] = None
  globals: Optional[bool] = None
  orderBy: Optional[OrderByOptions] = "name"
  order: Optional[OrderDirectionOptions] = "ASC"
  term: Optional[str] = None

  @field_serializer('projects')
  def join_lists(self, value) -> str:
    return ",".join(value)

class IKimaiFetchRecentTimesheetsParams(BaseModel):
  user: Optional[str] = None
  begin: Optional[datetime] = None
  size: Optional[int] = None

  @field_serializer('begin')
  def to_html5_date(self, value) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S")

class IKimaiFetchTimesheetsParams(BaseModel):
  user: Optional[str] = None
  customers: Optional[List[str]] = None
  projects: Optional[List[str]] = None
  activities: Optional[List[str]] = None
  page: Optional[int] = None # 1
  size: Optional[int] = None # 50
  tags: Optional[str] = None
  orderBy: Optional[OrderByOptions] = None # "name"
  order: Optional[OrderDirectionOptions] = None # "ASC"
  begin: Optional[datetime] = None
  end: Optional[datetime] = None
  active: Optional[bool] = None
  billable: Optional[bool] = None
  full: Optional[bool] = None # False
  term: Optional[str] = None
  modified_after: Optional[datetime] = None

  @field_serializer('begin', 'end', 'modified_after')
  def to_html5_date(self, value) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S")

  @field_serializer('customers', 'projects', 'activities')
  def join_lists(self, value) -> str:
    return ",".join(value)
