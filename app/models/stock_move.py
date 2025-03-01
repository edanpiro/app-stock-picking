from pydantic import BaseModel


class StockMove(BaseModel):
    product_id: int
    product_uom_qty: float
    description_picking: str = None
    quantity: float = None
