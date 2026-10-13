"""Domain models — Pydantic v2, frozen, extra=forbid. M1-T01.

References:
- master_prompt.md §5.1, §9, §10
- ADR-004 (DecisionScore thresholds, mandatory checks)
- ADR-011 (GateVerdict: PASS/FLAG/BLOCK/NEEDS_DATA)
- ADR-012 (only 8-K, 10-Q, 10-K trigger)
"""

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class GateVerdict(StrEnum):
    """Deterministic gate verdict per ADR-011.

    ADR-011 amended ADR-004: hard requirement is gate ∈ {PASS, FLAG}.
    FLAG never auto-submits (even if score ≥ auto_threshold).
    """

    PASS = "PASS"  # noqa: S105
    FLAG = "FLAG"
    BLOCK = "BLOCK"
    NEEDS_DATA = "NEEDS_DATA"


class FilingEvent(BaseModel):
    """SEC filing that triggers a research run.

    ADR-012: only 8-K, 10-Q, 10-K trigger.
    Universe validation (SPY/NVDA) is the gate's job, not the model's.
    """

    model_config = {"extra": "forbid", "frozen": True}

    filing_date: date = Field(..., description="Date the filing was submitted")
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=5,
        pattern=r"^[A-Z]{1,5}$",
        description="Issuer ticker, uppercase, 1-5 chars",
    )
    url: HttpUrl = Field(..., description="Link to the filing on sec.gov or equivalent")
    filing_type: Literal["8-K", "10-Q", "10-K"] = Field(..., description="Filing type per ADR-012")


class SourceReference(BaseModel):
    """Bibliographic metadata for one source."""

    model_config = {"extra": "forbid", "frozen": True}

    source_id: str = Field(..., min_length=1, description="Unique source identifier")
    url: HttpUrl | None = Field(default=None, description="URL of the source, if available")
    published_at: date | None = Field(default=None, description="Publication date, if known")
    retrieved_at: datetime = Field(..., description="When the source was fetched")
    source_name: str = Field(
        ..., min_length=1, max_length=256, description="Human-readable source name"
    )
    claims_supported: list[str] = Field(
        default_factory=list, description="IDs of claims this source backs"
    )


class Evidence(BaseModel):
    """Excerpt from a source that backs a claim."""

    model_config = {"extra": "forbid", "frozen": True}

    evidence_id: str = Field(..., min_length=1, description="Unique evidence identifier")
    source_id: str = Field(
        ..., min_length=1, description="Cross-references SourceReference.source_id"
    )
    url: HttpUrl | None = Field(default=None, description="Direct link to the passage")
    retrieved_at: datetime = Field(..., description="When this evidence was fetched")
    published_at: date | None = Field(default=None, description="Original publication date")
    excerpt: str = Field(..., max_length=2000, description="Relevant excerpt from the source")
    relevance: Literal["material", "minor", "background"] = Field(
        ..., description="Materiality classification of this evidence"
    )


class Claim(BaseModel):
    """Verifiable assertion extracted from evidence."""

    model_config = {"extra": "forbid", "frozen": True}

    claim_id: str = Field(..., min_length=1, description="Unique claim identifier")
    source_ids: list[str] = Field(
        default_factory=list, description="Maps to Evidence.evidence_id entries"
    )
    text: str = Field(..., max_length=1000, description="The assertion text")
    verification_status: Literal["verified", "unverified", "disputed", "unverifiable"] = Field(
        ..., description="Verification state of this claim"
    )


class Contradiction(BaseModel):
    """Two claims that conflict."""

    model_config = {"extra": "forbid", "frozen": True}

    contradiction_id: str = Field(..., min_length=1, description="Unique contradiction identifier")
    claim_a_id: str = Field(..., min_length=1, description="First conflicting claim")
    claim_b_id: str = Field(..., min_length=1, description="Second conflicting claim")
    description: str = Field(..., max_length=1000, description="What the conflict is about")
    resolution: Literal["material", "minor"] | None = Field(
        default=None, description="None = unresolved per §10"
    )


class DecisionScore(BaseModel):
    """Stores the scored result. Does NOT compute the score (gate's job).

    ADR-004 §1: mandatory checks + weighted sum.
    """

    model_config = {"extra": "forbid", "frozen": True}

    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0 and 1")
    score_version: str = Field(..., description="Version of the scoring formula")
    components: dict[str, float] = Field(
        ..., description="Normalised component values (e.g. evidence_strength: 0.8)"
    )
    weights: dict[str, float] = Field(
        ..., description="Weights used in the weighted sum (sum ~= 1.0)"
    )
    reject_threshold: float = Field(
        default=0.40, ge=0.0, le=1.0, description="ADR-004 reject threshold"
    )
    auto_threshold: float = Field(
        default=0.75, ge=0.0, le=1.0, description="ADR-004 auto-submit threshold"
    )
    mandatory_checks: dict[str, bool] = Field(
        ..., description="All must be True for score > 0 (ADR-004 §1)"
    )
    computed_at: datetime = Field(..., description="When the score was computed")


class ResearchArtifact(BaseModel):
    """Published research memo — the output of the entire research flow.

    All fields from master_prompt.md §9.
    """

    model_config = {"extra": "forbid", "frozen": True}

    research_id: str = Field(
        ..., min_length=1, max_length=64, description="Unique research identifier"
    )
    schema_version: Literal["1"] = Field(default="1", description="Schema version")
    event: FilingEvent = Field(..., description="The triggering filing")
    event_category: str | None = Field(default=None, description="Set by Event Analyst (M2)")
    created_at: datetime = Field(..., description="When the artifact was created")
    as_of_timestamp: datetime = Field(..., description="Cutoff timestamp for data")
    assets_analyzed: list[str] = Field(..., description="Tickers examined")
    executive_summary: str = Field(..., max_length=5000, description="Executive summary")
    verified_facts: list[str] = Field(
        default_factory=list, description="Verified factual statements"
    )
    evidence: list[Evidence] = Field(default_factory=list, description="Evidence items")
    source_references: list[SourceReference] = Field(
        default_factory=list, description="Source metadata"
    )
    bull_case: str | None = Field(default=None, description="Bull case scenario")
    base_case: str | None = Field(default=None, description="Base case scenario")
    bear_case: str | None = Field(default=None, description="Bear case scenario")
    assumptions: list[str] = Field(default_factory=list, description="Key assumptions")
    potential_transmission_mechanisms: list[str] = Field(
        default_factory=list, description="How the event transmits to assets"
    )
    risks: list[str] = Field(default_factory=list, description="Identified risks")
    contradictions: list[Contradiction] = Field(
        default_factory=list, description="Conflicting claims"
    )
    uncertainties: list[str] = Field(default_factory=list, description="Areas of uncertainty")
    invalidation_conditions: list[str] = Field(
        default_factory=list, description="Conditions that would invalidate the thesis"
    )
    quantitative_analysis: str | None = Field(default=None, description="Numeric analysis")
    verification_results: dict[str, bool] = Field(
        default_factory=dict, description="Gate check name → passed?"
    )
    gate_verdict: GateVerdict | None = Field(
        default=None, description="Set by deterministic gate (M1-T02)"
    )
    decision_score: DecisionScore | None = Field(
        default=None, description="Set by gate (M1-T02) after PASS/FLAG"
    )
    retry_count: int = Field(default=0, ge=0, description="Number of retry attempts")
    review_status: str = Field(default="pending", description="Human review state")
    execution_status: str = Field(
        default="disabled", description="Execution state per §5.1 / ADR-003"
    )
    ticket: str | None = Field(default="NO_TICKET", description="Order ticket when proposed")
    disclaimer: str = Field(..., max_length=1000, description="Mandatory legal disclaimer")
