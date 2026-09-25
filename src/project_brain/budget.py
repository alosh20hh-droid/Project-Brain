from __future__ import annotations
from decimal import Decimal
from pydantic import BaseModel

class Budget(BaseModel):
    limit: Decimal = Decimal("0")
    spent: Decimal = Decimal("0")
    reserved: Decimal = Decimal("0")

    @property
    def available(self)->Decimal:
        return self.limit-self.spent-self.reserved

    def can_reserve(self, amount: Decimal)->bool:
        return amount >= 0 and amount <= self.available
