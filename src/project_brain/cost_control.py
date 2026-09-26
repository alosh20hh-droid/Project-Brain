from __future__ import annotations
from decimal import Decimal
from dataclasses import dataclass
import json
from .persistence import SQLiteProjectStore

@dataclass
class CostLedger:
 limit:Decimal
 spent:Decimal=Decimal("0")
 reserved:Decimal=Decimal("0")
 store:SQLiteProjectStore|None=None
 ledger_id:str="default"

 def __post_init__(self):
  self.limit=Decimal(str(self.limit));self.spent=Decimal(str(self.spent));self.reserved=Decimal(str(self.reserved))
  if self.store:
   self.store.put_if_absent("budget",self.ledger_id,{"limit":str(self.limit),"spent":str(self.spent),"reserved":str(self.reserved)})
   self._refresh()

 def _refresh(self):
  if self.store:
   raw=self.store.get("budget",self.ledger_id)
   if raw is None:raise RuntimeError("budget ledger missing")
   self.limit=Decimal(raw["limit"]);self.spent=Decimal(raw["spent"]);self.reserved=Decimal(raw["reserved"])

 @property
 def available(self)->Decimal:
  self._refresh()
  return self.limit-self.spent-self.reserved

 def reserve(self,amount:Decimal)->bool:
  amount=Decimal(str(amount))
  if amount<0:return False
  if not self.store:
   if amount>self.available:return False
   self.reserved+=amount;return True
  with self.store.connect() as db:
   db.execute("BEGIN IMMEDIATE")
   row=db.execute("SELECT value_json FROM kv WHERE namespace='budget' AND key=?",(self.ledger_id,)).fetchone()
   if row is None:return False
   current=json.loads(row[0]);limit=Decimal(current["limit"]);spent=Decimal(current["spent"]);reserved=Decimal(current["reserved"])
   if amount>limit-spent-reserved:return False
   current["reserved"]=str(reserved+amount)
   db.execute("UPDATE kv SET value_json=? WHERE namespace='budget' AND key=?",(json.dumps(current,sort_keys=True),self.ledger_id))
  self._refresh();return True

 def settle(self,reserved_amount:Decimal,actual_amount:Decimal)->None:
  reserved_amount=Decimal(str(reserved_amount));actual_amount=Decimal(str(actual_amount))
  if reserved_amount<0 or actual_amount<0:raise ValueError("amount cannot be negative")
  if not self.store:
   if reserved_amount>self.reserved:raise ValueError("reservation exceeds ledger")
   projected_reserved=self.reserved-reserved_amount;projected_spent=self.spent+actual_amount
   if projected_spent+projected_reserved>self.limit:raise RuntimeError("actual cost exceeds budget")
   self.reserved=projected_reserved;self.spent=projected_spent;return
  with self.store.connect() as db:
   db.execute("BEGIN IMMEDIATE")
   row=db.execute("SELECT value_json FROM kv WHERE namespace='budget' AND key=?",(self.ledger_id,)).fetchone()
   if row is None:raise RuntimeError("budget ledger missing")
   current=json.loads(row[0]);limit=Decimal(current["limit"]);spent=Decimal(current["spent"]);reserved=Decimal(current["reserved"])
   if reserved_amount>reserved:raise ValueError("reservation exceeds ledger")
   projected_reserved=reserved-reserved_amount;projected_spent=spent+actual_amount
   if projected_spent+projected_reserved>limit:raise RuntimeError("actual cost exceeds budget")
   current["reserved"]=str(projected_reserved);current["spent"]=str(projected_spent)
   db.execute("UPDATE kv SET value_json=? WHERE namespace='budget' AND key=?",(json.dumps(current,sort_keys=True),self.ledger_id))
  self._refresh()

 def release(self,amount:Decimal)->None:
  amount=Decimal(str(amount))
  if amount<0:raise ValueError("invalid release")
  if not self.store:
   if amount>self.reserved:raise ValueError("invalid release")
   self.reserved-=amount;return
  with self.store.connect() as db:
   db.execute("BEGIN IMMEDIATE")
   row=db.execute("SELECT value_json FROM kv WHERE namespace='budget' AND key=?",(self.ledger_id,)).fetchone()
   if row is None:raise RuntimeError("budget ledger missing")
   current=json.loads(row[0]);reserved=Decimal(current["reserved"])
   if amount>reserved:raise ValueError("invalid release")
   current["reserved"]=str(reserved-amount)
   db.execute("UPDATE kv SET value_json=? WHERE namespace='budget' AND key=?",(json.dumps(current,sort_keys=True),self.ledger_id))
  self._refresh()
