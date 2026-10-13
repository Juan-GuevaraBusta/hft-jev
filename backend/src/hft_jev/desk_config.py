"""Desk configuration: Pydantic validation for config/desk.yaml documents.

The YAML example (config/desk.example.yaml) is the contract for M2: this
module validates shape, types and ranges, but never executes turns, cron,
workers or queues. YAML is parsed exclusively with yaml.safe_load.
"""

import re
from pathlib import Path
from typing import Literal

import yaml  # type: ignore[import-untyped]  # PyYAML ships no py.typed; only safe_load is used
from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

_STRICT_FORBID = ConfigDict(extra="forbid", strict=True)

_CRON_FIELD = r"(?:\*(?:/\d+)?|\d+(?:-\d+)?(?:/\d+)?(?:,\d+(?:-\d+)?(?:/\d+)?)*)"
_CRON_RE = r"^" + r"\s+".join([_CRON_FIELD] * 5) + r"$"
_LOCAL_TIME_RE = r"^(?:[01]\d|2[0-3]):[0-5]\d$"


def _check_unit_interval(name: str, value: float) -> float:
    """Validate a [0, 1] fraction (ADR-004 percentages); message names field+value."""
    if not 0.0 <= value <= 1.0:
        raise PydanticCustomError(
            "desk_config_out_of_range",
            f"{name}={value!r} is out of range: expected a fraction in [0, 1] (ADR-004)",
            {"name": name, "value": value},
        )
    return value


def _check_positive_int(name: str, value: int) -> int:
    """Validate a count >= 1; message names field+value."""
    if value < 1:
        raise PydanticCustomError(
            "desk_config_out_of_range",
            f"{name}={value!r} is out of range: expected an integer >= 1",
            {"name": name, "value": value},
        )
    return value


class DeskMeta(BaseModel):
    """The [desk] section: desk identity and timezone."""

    model_config = _STRICT_FORBID

    name: str
    timezone: str


class Universe(BaseModel):
    """The [universe] section: allowed symbols for research and orders."""

    model_config = _STRICT_FORBID

    description: str
    symbols: list[str]


class NightIngest(BaseModel):
    """The [schedule.night_ingest] shift: shape only, no scheduling here."""

    model_config = _STRICT_FORBID

    enabled: bool
    cron: str
    tasks: list[str]

    @field_validator("cron")
    @classmethod
    def _validate_cron(cls, value: str) -> str:
        if re.match(_CRON_RE, value) is None:
            raise PydanticCustomError(
                "desk_config_invalid_cron",
                f"cron={value!r} is invalid: expected a 5-field cron expression",
                {"value": value},
            )
        return value


class MorningDesk(BaseModel):
    """The [schedule.morning_desk] shift: shape only, no scheduling here."""

    model_config = _STRICT_FORBID

    enabled: bool
    local_time: str
    combine_night_intel: bool

    @field_validator("local_time")
    @classmethod
    def _validate_local_time(cls, value: str) -> str:
        if re.match(_LOCAL_TIME_RE, value) is None:
            raise PydanticCustomError(
                "desk_config_invalid_time",
                f"local_time={value!r} is invalid: expected HH:MM in 24h format",
                {"value": value},
            )
        return value


class Schedule(BaseModel):
    """The [schedule] section: exactly the known shifts, nothing else."""

    model_config = _STRICT_FORBID

    night_ingest: NightIngest
    morning_desk: MorningDesk


class DeskLimits(BaseModel):
    """The [desk_limits] section: analytical desk limits (not orders)."""

    model_config = _STRICT_FORBID

    max_deep_dives_per_day: int
    max_artifacts_for_review_per_day: int
    review_horizon_trading_days: int
    material_pct_threshold: float

    @field_validator("material_pct_threshold")
    @classmethod
    def _validate_pct(cls, value: float) -> float:
        return _check_unit_interval("material_pct_threshold", value)

    @field_validator(
        "max_deep_dives_per_day",
        "max_artifacts_for_review_per_day",
        "review_horizon_trading_days",
    )
    @classmethod
    def _validate_counts(cls, value: int, info: ValidationInfo) -> int:
        return _check_positive_int(info.field_name or "value", value)


class MoneyRules(BaseModel):
    """The [money_rules] section: consumed by the Deterministic Gate."""

    model_config = _STRICT_FORBID

    minimum_cash_reserve_pct: float
    max_single_name_exposure_pct: float
    max_new_order_pct: float
    investment_horizon: str | None
    portfolio_fixture_path: str | None
    staleness_hours: int

    @field_validator(
        "minimum_cash_reserve_pct",
        "max_single_name_exposure_pct",
        "max_new_order_pct",
    )
    @classmethod
    def _validate_pcts(cls, value: float, info: ValidationInfo) -> float:
        return _check_unit_interval(info.field_name or "value", value)

    @field_validator("staleness_hours")
    @classmethod
    def _validate_staleness(cls, value: int) -> int:
        return _check_positive_int("staleness_hours", value)


class SecContact(BaseModel):
    """The [sec_contact] section: SEC EDGAR User-Agent contact.

    Placeholder strings (e.g. {{SEC_CONTACT_NAME}}) are accepted as-is:
    requiring a real email is deferred (user decision Q7, option a).
    """

    model_config = _STRICT_FORBID

    name: str
    email: str


class ModelTiers(BaseModel):
    """The [model_tiers] section: OpenRouter model ids (empty = fail-closed)."""

    model_config = _STRICT_FORBID

    fast: str
    mid: str
    strong: str


TierName = Literal["fast", "mid", "strong"]


class NodeTierMap(BaseModel):
    """The [node_tier_map] section: research node to model tier mapping."""

    model_config = _STRICT_FORBID

    event_analyst: TierName
    evidence_researcher: TierName
    market_impact: TierName
    risk_contradiction: TierName
    thesis_synthesizer: TierName


class Execution(BaseModel):
    """The [execution] section: Alpaca routing (ADR-003) and limits (ADR-004)."""

    model_config = _STRICT_FORBID

    broker: Literal["alpaca"]
    mode: Literal["paper", "live"]
    kill_switch: bool
    ticket_default: str
    score_version: str
    reject_threshold: float
    auto_threshold: float
    shadow_tracking: bool
    max_daily_loss_pct: float
    max_orders_per_day: int

    @field_validator("reject_threshold", "auto_threshold", "max_daily_loss_pct")
    @classmethod
    def _validate_pcts(cls, value: float, info: ValidationInfo) -> float:
        return _check_unit_interval(info.field_name or "value", value)

    @field_validator("max_orders_per_day")
    @classmethod
    def _validate_max_orders(cls, value: int) -> int:
        return _check_positive_int("max_orders_per_day", value)

    @model_validator(mode="after")
    def _validate_threshold_order(self) -> "Execution":
        if not self.reject_threshold < self.auto_threshold:
            raise PydanticCustomError(
                "desk_config_threshold_order",
                f"reject_threshold={self.reject_threshold!r} must be < "
                f"auto_threshold={self.auto_threshold!r} (ADR-004)",
                {"reject": self.reject_threshold, "auto": self.auto_threshold},
            )
        return self


class DeskConfig(BaseModel):
    """Root model of a desk.yaml document. Unknown keys fail everywhere."""

    model_config = _STRICT_FORBID

    desk: DeskMeta
    universe: Universe
    benchmark: str
    schedule: Schedule
    desk_limits: DeskLimits
    money_rules: MoneyRules
    sec_contact: SecContact
    model_tiers: ModelTiers
    node_tier_map: NodeTierMap
    execution: Execution


class DeskConfigError(ValueError):
    """Raised when a desk YAML document cannot be loaded or validated."""


def load_desk_config(path: Path | str) -> DeskConfig:
    """Load and validate a desk YAML document.

    The file is parsed exclusively with yaml.safe_load; yaml.load (and any
    explicit Loader) is never used. Any failure raises DeskConfigError with
    a message naming the offending field.
    """
    source = Path(path)
    try:
        raw_text = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise DeskConfigError(f"desk config file is not readable: {source}") from exc
    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise DeskConfigError(f"desk config is not valid YAML: {source}: {exc}") from exc
    if not isinstance(data, dict):
        raise DeskConfigError(
            f"desk config root must be a mapping, got {type(data).__name__}: {source}"
        )
    try:
        return DeskConfig.model_validate(data)
    except ValidationError as exc:
        raise DeskConfigError(f"desk config is invalid: {source}\n{exc}") from exc
