from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Reflection:
 lesson:str
 should_change_plan:bool

def reflect(completed:bool,verified:bool,repeated_failure:bool)->Reflection:
 if repeated_failure:return Reflection("Do not repeat the same failed approach; change the plan.",True)
 if completed and not verified:return Reflection("Execution claimed completion but evidence did not verify it.",True)
 if not completed:return Reflection("Execution did not complete; inspect failure before retrying.",True)
 return Reflection("Verified outcome can be retained as project knowledge.",False)
