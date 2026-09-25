from decimal import Decimal
import pytest
from project_brain.cost_control import CostLedger

def test_reservation_prevents_oversubscription():
 l=CostLedger(Decimal("10"))
 assert l.reserve(Decimal("7"))
 assert not l.reserve(Decimal("4"))

def test_settlement_moves_reserved_to_spent():
 l=CostLedger(Decimal("10"));l.reserve(Decimal("5"));l.settle(Decimal("5"),Decimal("4"))
 assert l.spent==Decimal("4");assert l.reserved==Decimal("0")
