"""TEMPORARY STUB — FilingEvent (approved exception, Refs #47 M1-T01).

The user approved a minimal stub ("apruebo el stub minimo y a reemplazar"):
this model exists only so PR-M1-T02 (#48) fixtures have a parse target.
M1-T01 MUST replace this file with the real domain model; do not extend it.

Rules for this stub:
- Synthetic data only. Every valid fixture carries synthetic=true.
- Never present stub data as a real EDGAR filing.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FilingForm = Literal["8-K", "10-Q", "10-K"]


class FilingEvent(BaseModel):
    """Minimal material-filing event (STUB — replaced by M1-T01, issue #47)."""

    model_config = ConfigDict(extra="forbid", strict=True)

    form: FilingForm
    symbol: str = Field(min_length=1)
    title: str = ""
    synthetic: bool = True
