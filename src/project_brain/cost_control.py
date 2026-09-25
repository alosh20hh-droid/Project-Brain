from __future__ import annotations
from decimal import Decimal
from dataclasses import dataclass

@dataclass
class CostLedger:
 limit:Decimal
 spent:Decimal=Decimal("0")
 reserved:Decimal=Decimal("0")

 @property
 def available(self)->Decimal:
  return self.limit-self.spent-self.reserved

 def reserve(self,amount:Decimal)->bool:
  if amount<0 or amount>self.available:return False
  self.reserved+=amount
  return True

 def settle(self,reserved_amount:Decimal,actual_amount:Decimal)->None:
  if reserved_amount<0 or actual_amount<0:
   raise ValueError("amount cannot be negative")
  if reserved_amount>self.reserved:
   raise ValueError("reservation exceeds ledger")
  projected_reserved=self.reserved-reserved_amount
  projected_spent=self.spent+actual_amount
  if projected_spent+projected_reserved>self.limit:
   raise RuntimeError("actual cost exceeds budget")
  self.reserved=projected_reserved
  self.spent=projected_spent

 def release(self,amount:Decimal)->None:
  if amount<0 or amount>self.reserved:raise ValueError("invalid release")
  self.reserved-=amount
