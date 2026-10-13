"""Langfuse tracing setup (ADR-001: Langfuse Cloud, Python SDK v4).

Usage, once per process and AFTER environment variables are loaded:

    langfuse = init_langfuse()
    with research_trace(research_id, name="run-research"):
        with langfuse.start_as_current_observation(as_type="agent", name="run-research") as root:
            root.update(input=question)
            result = graph.invoke(state, config={"callbacks": langchain_callbacks()})
            root.update(output=result)
    langfuse.flush()  # short-lived processes only

Credentials come only from the environment (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`,
`LANGFUSE_BASE_URL`); never pass keys as literals.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from functools import lru_cache

from langchain_core.callbacks import BaseCallbackHandler
from langfuse import Langfuse, propagate_attributes
from langfuse.langchain import CallbackHandler
from langfuse.types import (
    MaskOtelSpansParams,
    MaskOtelSpansResult,
    OtelSpanIdentifier,
    OtelSpanPatch,
)

from hft_jev import __version__

DEFAULT_ENVIRONMENT = "development"
SERVICE_NAME = "hft-jev"

# Trace payloads leave the machine (Langfuse Cloud). Anything matching these patterns is
# replaced before export, even if a caller accidentally puts it into an input/output.
_REDACTIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(?:sk|pk)-[A-Za-z0-9_-]{16,}"), "[REDACTED_API_KEY]"),
    (re.compile(r"\blsv2_[A-Za-z0-9_]{20,}"), "[REDACTED_API_KEY]"),
    (re.compile(r"\b(?:PK|AK|CK)[A-Z0-9]{16,}\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{16,}"), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b"), "[REDACTED_EMAIL]"),
)


def redact_text(value: str) -> str:
    """Return `value` with API keys, bearer tokens and emails replaced by placeholders."""
    for pattern, replacement in _REDACTIONS:
        value = pattern.sub(replacement, value)
    return value


def mask_otel_spans(*, params: MaskOtelSpansParams) -> MaskOtelSpansResult | None:
    """Langfuse export hook: redact string span attributes before they are sent.

    Must stay fast and must not raise: an exception drops the whole export batch.
    """
    patches: dict[OtelSpanIdentifier, OtelSpanPatch] = {}
    for identifier, span in params.spans.items():
        replacements: dict[str, str] = {}
        for key, value in span.attributes.items():
            if isinstance(value, str):
                masked = redact_text(value)
                if masked != value:
                    replacements[key] = masked
        if replacements:
            patches[identifier] = OtelSpanPatch(set_attributes=replacements)
    if not patches:
        return None
    return MaskOtelSpansResult(span_patches=patches)


@lru_cache(maxsize=1)
def init_langfuse() -> Langfuse:
    """Create the process-wide Langfuse client with masking, environment and release.

    Call before any `get_client()`/`CallbackHandler()` use: the SDK reuses the first
    client created for a public key and ignores later constructor arguments.
    """
    os.environ.setdefault("OTEL_SERVICE_NAME", SERVICE_NAME)
    has_credentials = bool(
        os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")
    )
    return Langfuse(
        tracing_enabled=has_credentials,
        environment=os.environ.get("LANGFUSE_TRACING_ENVIRONMENT", DEFAULT_ENVIRONMENT),
        release=__version__,
        mask_otel_spans=mask_otel_spans,
    )


def langchain_callbacks() -> list[BaseCallbackHandler]:
    """Callbacks for LangChain/LangGraph `config={"callbacks": ...}`.

    The handler nests under the active Langfuse observation and records each model call as
    a `generation` with model name and token usage.
    """
    init_langfuse()
    return [CallbackHandler()]


@contextmanager
def research_trace(
    research_id: str,
    *,
    name: str,
    tags: list[str] | None = None,
    metadata: Mapping[str, str] | None = None,
) -> Iterator[None]:
    """Propagate trace attributes for one research run to every child observation.

    `research_id` becomes the Langfuse `session_id` so all traces of a research (chief,
    sub-agents, evals) group together. `name` must be stable (no ids or model names):
    evaluators and dashboards filter on it.
    """
    with propagate_attributes(
        session_id=research_id,
        trace_name=name,
        tags=tags,
        metadata={"research_id": research_id, **(metadata or {})},
    ):
        yield
