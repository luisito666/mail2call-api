from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SystemStatsBase(BaseModel):
    metric_name: str
    metric_value: Dict[str, Any]


class SystemStatsCreate(SystemStatsBase):
    pass


class SystemStatsUpdate(BaseModel):
    metric_name: Optional[str] = None
    metric_value: Optional[Dict[str, Any]] = None


class SystemStatsResponse(SystemStatsBase):
    id: int
    recorded_at: datetime