from typing import Any, List, Optional
from pydantic import BaseModel

from models.misc import KimaiMetaPairValue
from models.project import KimaiProject


class KimaiActivityDetails(BaseModel):
    id: Optional[int] = None
    project: Optional[KimaiProject] = None
    name: str
    comment: Optional[str] = None
    visible: bool
    billable: bool
    color: Optional[str] = None


class KimaiActivityForm(BaseModel):
    name: str
    comment: Optional[str] = None
    invoiceText: Optional[str] = None
    project: Optional[int] = None
    color: Optional[str] = None
    visible: Optional[bool] = None
    billable: Optional[bool] = None


class KimaiActivity(BaseModel):
    parentTitle: Optional[str] = None
    project: Optional[int] = None
    id: Optional[int] = None
    name: str
    comment: Optional[str] = None
    visible: bool
    billable: bool
    metaFields: List[KimaiMetaPairValue] = []
    teams: List[Any] = []
    color: Optional[str] = None


class KimaiActivityEntity(BaseModel):
    parentTitle: Optional[str] = None
    project: Optional[int] = None
    id: Optional[int] = None
    name: str
    comment: Optional[str] = None
    visible: bool
    billable: bool
    metaFields: List[KimaiMetaPairValue] = []
    teams: List[Any] = []  # TODO:
    budget: float
    timeBudget: int
    budgetType: Optional[str] = None
    color: Optional[str] = None
