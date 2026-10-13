"""Unit tests for domain models — M1-T01.

TDD: test file written BEFORE models.py was confirmed working.
Uses exact field names from the models.
"""
# mypy: ignore-errors

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from hft_jev.domain.models import (
    Claim,
    Contradiction,
    DecisionScore,
    Evidence,
    FilingEvent,
    GateVerdict,
    ResearchArtifact,
    SourceReference,
)

# ── FilingEvent ───────────────────────────────────────────────────────────────


class TestFilingEvent:
    @pytest.mark.unit
    def test_valid_minimal(self) -> None:
        ev = FilingEvent(
            filing_date=date(2026, 10, 13),
            ticker="NVDA",
            url="https://www.sec.gov/Archives/edgar/data/1045810/000104581026000001/0001045810-26-000001-index.htm",  # type: ignore[arg-type]
            filing_type="10-Q",
        )
        assert ev.ticker == "NVDA"
        assert ev.filing_type == "10-Q"

    @pytest.mark.unit
    def test_invalid_missing_required(self) -> None:
        with pytest.raises(ValidationError):
            FilingEvent(
                ticker="NVDA",
                url="https://www.sec.gov/Archives/edgar/data/1045810/000104581026000001/0001045810-26-000001-index.htm",  # type: ignore[arg-type]
                filing_type="10-Q",
            )

    @pytest.mark.unit
    def test_invalid_extra_field(self) -> None:
        with pytest.raises(ValidationError):
            FilingEvent(
                filing_date=date(2026, 10, 13),
                ticker="NVDA",
                url="https://www.sec.gov/Archives/edgar/data/1045810/000104581026000001/0001045810-26-000001-index.htm",  # type: ignore[arg-type]
                filing_type="10-Q",
                not_a_field="intruder",  # type: ignore[call-arg]
            )

    @pytest.mark.unit
    def test_invalid_filing_type_not_allowed(self) -> None:
        with pytest.raises(ValidationError):
            FilingEvent(
                filing_date=date(2026, 10, 13),
                ticker="SPY",
                url="https://www.sec.gov/Archives/edgar/data/1045810/000104581026000001/0001045810-26-000001-index.htm",  # type: ignore[arg-type]
                filing_type="13F",
            )

    @pytest.mark.unit
    def test_invalid_ticker_lowercase(self) -> None:
        with pytest.raises(ValidationError):
            FilingEvent(
                filing_date=date(2026, 10, 13),
                ticker="nvda",
                url="https://www.sec.gov/Archives/edgar/data/1045810/000104581026000001/0001045810-26-000001-index.htm",  # type: ignore[arg-type]
                filing_type="8-K",
            )

    @pytest.mark.unit
    def test_invalid_ticker_too_long(self) -> None:
        with pytest.raises(ValidationError):
            FilingEvent(
                filing_date=date(2026, 10, 13),
                ticker="ABCDEF",
                url="https://www.sec.gov/Archives/edgar/data/1045810/000104581026000001/0001045810-26-000001-index.htm",  # type: ignore[arg-type]
                filing_type="8-K",
            )


# ── GateVerdict ───────────────────────────────────────────────────────────────


class TestGateVerdict:
    @pytest.mark.unit
    def test_valid_values(self) -> None:
        assert GateVerdict.PASS == "PASS"  # noqa: S105
        assert GateVerdict.FLAG == "FLAG"
        assert GateVerdict.BLOCK == "BLOCK"
        assert GateVerdict.NEEDS_DATA == "NEEDS_DATA"

    @pytest.mark.unit
    def test_invalid_value(self) -> None:
        with pytest.raises(ValueError):
            GateVerdict("INVALID")  # type: ignore[arg-type]

    @pytest.mark.unit
    def test_from_string(self) -> None:
        assert GateVerdict("PASS") == GateVerdict.PASS


# ── SourceReference ───────────────────────────────────────────────────────────


class TestSourceReference:
    @pytest.mark.unit
    def test_valid_minimal(self) -> None:
        now = datetime.now(UTC)
        sr = SourceReference(
            source_id="src-001",
            source_name="Bloomberg",
            retrieved_at=now,
            claims_supported=[],
        )
        assert sr.source_id == "src-001"
        assert sr.url is None

    @pytest.mark.unit
    def test_invalid_missing_source_id(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            SourceReference(
                source_name="SEC EDGAR",
                retrieved_at=now,
                claims_supported=[],
            )

    @pytest.mark.unit
    def test_invalid_extra_field(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            SourceReference(
                source_id="src-002",
                source_name="SEC",
                retrieved_at=now,
                claims_supported=[],
                ghost=True,  # type: ignoe[call-arg]
            )


# ── Evidence ──────────────────────────────────────────────────────────────────


class TestEvidence:
    @pytest.mark.unit
    def test_valid_minimal(self) -> None:
        now = datetime.now(UTC)
        ev = Evidence(
            evidence_id="ev-001",
            source_id="src-001",
            retrieved_at=now,
            excerpt="Revenue grew 15% YoY.",
            relevance="material",
        )
        assert ev.evidence_id == "ev-001"
        assert ev.relevance == "material"
        assert ev.published_at is None

    @pytest.mark.unit
    def test_invalid_missing_source_id(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            Evidence(
                evidence_id="ev-002",
                retrieved_at=now,
                excerpt="Some excerpt.",
                relevance="minor",
            )

    @pytest.mark.unit
    def test_invalid_extra_field(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            Evidence(
                evidence_id="ev-003",
                source_id="src-001",
                retrieved_at=now,
                excerpt="Data.",
                relevance="background",
                not_real=True,
            )

    @pytest.mark.unit
    def test_invalid_relevance_value(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            Evidence(
                evidence_id="ev-004",
                source_id="src-001",
                retrieved_at=now,
                excerpt="Data.",
                relevance="invalid_value",
            )


# ── Claim ─────────────────────────────────────────────────────────────────────


class TestClaim:
    @pytest.mark.unit
    def test_valid_minimal(self) -> None:
        c = Claim(
            claim_id="cl-001",
            source_ids=["ev-001"],
            text="NVDA reported record datacenter revenue.",
            verification_status="unverified",
        )
        assert c.claim_id == "cl-001"
        assert c.verification_status == "unverified"

    @pytest.mark.unit
    def test_invalid_missing_text(self) -> None:
        with pytest.raises(ValidationError):
            Claim(
                claim_id="cl-002",
                source_ids=[],
                verification_status="verified",
            )

    @pytest.mark.unit
    def test_invalid_extra_field(self) -> None:
        with pytest.raises(ValidationError):
            Claim(
                claim_id="cl-003",
                source_ids=["ev-001"],
                text="A claim.",
                verification_status="disputed",
                extra="nope",
            )


# ── Contradiction ─────────────────────────────────────────────────────────────


class TestContradiction:
    @pytest.mark.unit
    def test_valid_minimal(self) -> None:
        c = Contradiction(
            contradiction_id="cx-001",
            claim_a_id="cl-001",
            claim_b_id="cl-002",
            description="Internal estimates conflict with consensus.",
            resolution=None,
        )
        assert c.contradiction_id == "cx-001"
        assert c.resolution is None

    @pytest.mark.unit
    def test_valid_with_resolution(self) -> None:
        c = Contradiction(
            contradiction_id="cx-002",
            claim_a_id="cl-003",
            claim_b_id="cl-004",
            description="Minor discrepancy in QoQ growth.",
            resolution="minor",
        )
        assert c.resolution == "minor"

    @pytest.mark.unit
    def test_invalid_missing_claim_b(self) -> None:
        with pytest.raises(ValidationError):
            Contradiction(
                contradiction_id="cx-003",
                claim_a_id="cl-001",
                description="Incomplete.",
            )


# ── DecisionScore ─────────────────────────────────────────────────────────────


class TestDecisionScore:
    @pytest.mark.unit
    def test_valid_minimal(self) -> None:
        now = datetime.now(UTC)
        ds = DecisionScore(
            score=0.65,
            score_version="1",
            components={
                "evidence_strength": 0.8,
                "verification_coverage": 0.7,
                "contradictions_non_material": 0.9,
                "freshness": 0.6,
            },
            weights={
                "evidence_strength": 0.25,
                "verification_coverage": 0.25,
                "contradictions_non_material": 0.25,
                "freshness": 0.25,
            },
            mandatory_checks={
                "gate_passed": True,
                "signal_confirmed": True,
                "no_material_contradictions": True,
                "data_fresh": True,
                "asset_in_universe": True,
            },
            computed_at=now,
        )
        assert ds.score == 0.65
        assert ds.score_version == "1"
        assert ds.reject_threshold == 0.40
        assert ds.auto_threshold == 0.75

    @pytest.mark.unit
    def test_thresholds_present_and_versioned(self) -> None:
        """Thresholds 0.40 and 0.75 must be in defaults and versioned."""
        now = datetime.now(UTC)
        ds = DecisionScore(
            score=0.50,
            score_version="1",
            components={
                "evidence_strength": 0.5,
                "verification_coverage": 0.5,
                "contradictions_non_material": 1.0,
                "freshness": 0.5,
            },
            weights={
                "evidence_strength": 0.25,
                "verification_coverage": 0.25,
                "contradictions_non_material": 0.25,
                "freshness": 0.25,
            },
            mandatory_checks={
                "gate_passed": True,
                "signal_confirmed": True,
                "no_material_contradictions": True,
                "data_fresh": True,
                "asset_in_universe": True,
            },
            computed_at=now,
        )
        assert ds.reject_threshold == 0.40
        assert ds.auto_threshold == 0.75
        assert ds.score_version == "1"

    @pytest.mark.unit
    def test_invalid_score_out_of_range(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            DecisionScore(
                score=1.5,
                score_version="1",
                components={
                    "evidence_strength": 0.8,
                    "verification_coverage": 0.8,
                    "contradictions_non_material": 0.8,
                    "freshness": 0.8,
                },
                weights={
                    "evidence_strength": 0.25,
                    "verification_coverage": 0.25,
                    "contradictions_non_material": 0.25,
                    "freshness": 0.25,
                },
                mandatory_checks={
                    "gate_passed": True,
                    "signal_confirmed": True,
                    "no_material_contradictions": True,
                    "data_fresh": True,
                    "asset_in_universe": True,
                },
                computed_at=now,
            )

    @pytest.mark.unit
    def test_invalid_extra_field(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            DecisionScore(
                score=0.5,
                score_version="1",
                components={
                    "evidence_strength": 0.5,
                    "verification_coverage": 0.5,
                    "contradictions_non_material": 1.0,
                    "freshness": 0.5,
                },
                weights={
                    "evidence_strength": 0.25,
                    "verification_coverage": 0.25,
                    "contradictions_non_material": 0.25,
                    "freshness": 0.25,
                },
                mandatory_checks={
                    "gate_passed": True,
                    "signal_confirmed": True,
                    "no_material_contradictions": True,
                    "data_fresh": True,
                    "asset_in_universe": True,
                },
                computed_at=now,
                not_a_field=True,
            )


# ── ResearchArtifact ──────────────────────────────────────────────────────────


class TestResearchArtifact:
    @pytest.fixture
    def nvda_filing(self):
        return FilingEvent(
            filing_date=date(2026, 10, 13),
            ticker="NVDA",
            url="https://www.sec.gov/Archives/edgar/data/1045810/000104581026000001/0001045810-26-000001-index.htm",  # type: ignore[arg-type]
            filing_type="10-Q",
        )

    @pytest.mark.unit
    def test_roundtrip_json(self, nvda_filing) -> None:
        """Serialize to JSON and deserialize back — fields must match."""
        now = datetime(2026, 10, 14, 9, 0, 0, tzinfo=UTC)
        artifact = ResearchArtifact(
            research_id="R-20261014-001",
            event=nvda_filing,
            created_at=now,
            as_of_timestamp=now,
            assets_analyzed=["NVDA"],
            executive_summary="NVDA reported strong Q3 results driven by datacenter growth.",
            verified_facts=["Datacenter revenue reached $30.8B."],
            assumptions=["AI capex continues to grow."],
            potential_transmission_mechanisms=["Semiconductor sector rally."],
            risks=["Geopolitical restrictions on chip exports."],
            uncertainties=["Sustainability of AI capex trajectory."],
            invalidation_conditions=["AI capex growth slows below 20% YoY."],
            disclaimer="This is analytical research, not financial advice.",
        )
        json_str = artifact.model_dump_json()
        reloaded = ResearchArtifact.model_validate_json(json_str)
        assert reloaded.research_id == artifact.research_id
        assert reloaded.event.ticker == "NVDA"
        assert reloaded.schema_version == "1"
        assert reloaded.gate_verdict is None
        assert reloaded.decision_score is None
        assert reloaded.execution_status == "disabled"
        assert reloaded.ticket == "NO_TICKET"
        assert reloaded.created_at == now

    @pytest.mark.unit
    def test_valid_minimal(self, nvda_filing) -> None:
        """Minimal valid ResearchArtifact with only required fields."""
        now = datetime.now(UTC)
        artifact = ResearchArtifact(
            research_id="R-20261014-002",
            event=nvda_filing,
            created_at=now,
            as_of_timestamp=now,
            assets_analyzed=["SPY"],
            executive_summary="Minimal summary.",
            disclaimer="Not financial advice.",
        )
        assert artifact.research_id == "R-20261014-002"

    @pytest.mark.unit
    def test_invalid_extra_field(self, nvda_filing) -> None:
        """Extra field in ResearchArtifact → ValidationError."""
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            ResearchArtifact(
                research_id="R-20261014-003",
                event=nvda_filing,
                created_at=now,
                as_of_timestamp=now,
                assets_analyzed=["SPY"],
                executive_summary="Extra field test.",
                disclaimer="Not financial advice.",
                undocumented_field="sneak",
            )

    @pytest.mark.unit
    def test_with_gate_verdict_and_score(self, nvda_filing) -> None:
        """Artifact with PASS gate verdict and DecisionScore survives validation."""
        now = datetime.now(UTC)
        ds = DecisionScore(
            score=0.82,
            score_version="1",
            components={
                "evidence_strength": 0.9,
                "verification_coverage": 0.85,
                "contradictions_non_material": 1.0,
                "freshness": 0.7,
            },
            weights={
                "evidence_strength": 0.25,
                "verification_coverage": 0.25,
                "contradictions_non_material": 0.25,
                "freshness": 0.25,
            },
            mandatory_checks={
                "gate_passed": True,
                "signal_confirmed": True,
                "no_material_contradictions": True,
                "data_fresh": True,
                "asset_in_universe": True,
            },
            computed_at=now,
        )
        artifact = ResearchArtifact(
            research_id="R-20261014-004",
            event=nvda_filing,
            created_at=now,
            as_of_timestamp=now,
            assets_analyzed=["NVDA"],
            executive_summary="PASS gate artifact.",
            verified_facts=["All checks passed."],
            gate_verdict=GateVerdict.PASS,
            decision_score=ds,
            execution_status="submitted",
            ticket="T-20261014-001",
            disclaimer="Not financial advice.",
        )
        assert artifact.gate_verdict == GateVerdict.PASS
        assert artifact.decision_score is not None
        assert artifact.decision_score.score == 0.82
        assert artifact.execution_status == "submitted"
