from pydantic import BaseModel, validator
from datetime import datetime
from typing import List
from .stock_move import StockMove


class StockPicking(BaseModel):
    partner_id: int
    scheduled_date: datetime
    picking_type: str
    origin: str = None
    moves: List[StockMove]

    @validator("picking_type", pre=True, always=True)
    def picking_type_code(cls, value):
        allowed_values = ["incoming", "outgoing", "internal"]
        if value and value not in allowed_values:
            raise ValueError(f"Must be one of: {allowed_values}")
        return value