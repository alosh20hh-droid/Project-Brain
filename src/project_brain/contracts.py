from __future__ import annotations
from enum import Enum
from typing import Any, Protocol
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "low"
    SENSITIVE = "sensitive"
    IRREVERSIBLE = "irreversible"

class EvidenceRequirement(BaseModel):
    kind: str
    description: str
    required: bool = True

class ExecutionRequest(BaseModel):
    task_id: str
    goal: str
    hypothesis: str | None = None
    constraints: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    evidence_required: list[EvidenceRequirement] = Field(default_factory=list)
    risk: RiskLevel = RiskLevel.LOW
    timeout_seconds: int = 600

class Evidence(BaseModel):
    kind: str
    uri: str | None = None
    content: Any | None = None
    source: str

class ExecutionResult(BaseModel):
    task_id: str
    completed: bool
    summary: str
    evidence: list[Evidence] = Field(default_factory=list)
    error: str | None = None

class VerificationResult(BaseModel):
    task_id: str
    accepted: bool
    reasons: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)

class ModelProvider(Protocol):
    async def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> dict[str, Any]: ...

class Executor(Protocol):
    async def execute(self, request: ExecutionRequest) -> ExecutionResult: ...

class Verifier(Protocol):
    async def verify(self, request: ExecutionRequest, result: ExecutionResult) -> VerificationResult: ...
