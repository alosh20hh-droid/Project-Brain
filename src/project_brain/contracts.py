from __future__ import annotations
from enum import Enum
from typing import Any, Protocol
from pydantic import BaseModel, Field, model_validator

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
    operation_id: str | None = None
    hypothesis: str | None = None
    constraints: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    evidence_required: list[EvidenceRequirement] = Field(default_factory=list)
    risk: RiskLevel = RiskLevel.LOW
    timeout_seconds: int = 600

    @model_validator(mode="after")
    def validate_execution_boundary(self):
        if not self.task_id.strip(): raise ValueError("task_id is required")
        if not self.goal.strip(): raise ValueError("goal is required")
        if self.timeout_seconds <= 0: raise ValueError("timeout_seconds must be positive")
        if self.risk in {RiskLevel.SENSITIVE,RiskLevel.IRREVERSIBLE} and not (self.operation_id and self.operation_id.strip()):
            raise ValueError("operation_id is required for sensitive or irreversible execution")
        return self

class Evidence(BaseModel):
    kind: str
    uri: str | None = None
    content: Any | None = None
    source: str
    content_hash: str | None = None
    strength: str = "weak"
    collected_at: str | None = None

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
