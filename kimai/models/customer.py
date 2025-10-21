from typing import Any, List, Optional
from pydantic import BaseModel

from models.misc import KimaiMetaPairValue


class KimaiProjectCustomer(BaseModel):
    id: Optional[int] = None
    name: str
    number: Optional[int] = None
    comment: Optional[str] = None
    visible: bool
    billable: bool
    color: Optional[str] = None


class KimaiCustomer(BaseModel):
    id: Optional[int] = None
    name: str
    number: Optional[int] = None
    comment: Optional[str] = None
    visible: bool
    billable: bool
    currency: str
    metaFields: List[KimaiMetaPairValue] = []
    teams: List[Any]  # TODO:
    color: Optional[str] = None
