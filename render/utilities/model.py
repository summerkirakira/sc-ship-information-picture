from pydantic import BaseModel
from ..models import Ship as ErkulShip


class ShipGroup(BaseModel):
    class ShipInfo(BaseModel):
        local_name: str
        name: str
        alias: list[str]
        manufacturer: str
        price: int
    ships: list[ShipInfo]