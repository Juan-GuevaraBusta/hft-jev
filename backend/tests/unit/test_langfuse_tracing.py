"""Unit tests for Langfuse tracing helpers (no network, no credentials)."""

from types import MappingProxyType

import pytest
from langfuse.types import MaskOtelSpansParams, OtelSpanData, OtelSpanIdentifier

from hft_jev.observability import mask_otel_spans, redact_text


def _span(attributes: dict[str, str | int]) -> OtelSpanData:
    return OtelSpanData(
        trace_id="t1",
        span_id="s",
        parent_span_id=None,
        name="span",
        instrumentation_scope_name="langfuse-sdk",
        instrumentation_scope_version=None,
        attributes=MappingProxyType(attributes),
        resource_attributes=MappingProxyType({}),
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("key sk-or-v1-abcdef0123456789abcdef", "key [REDACTED_API_KEY]"),
        ("sk-lf-1234abcd-1234-abcd-1234-abcdef", "[REDACTED_API_KEY]"),
        ("lsv2_pt_abcdefghijklmnopqrstuvwxyz", "[REDACTED_API_KEY]"),
        ("alpaca PKABCDEFGHIJKLMNOP12", "alpaca [REDACTED_API_KEY]"),
        ("Authorization: Bearer abc.def-ghi_jkl.mnop", "Authorization: Bearer [REDACTED_TOKEN]"),
        ("contact jane.doe@example.com now", "contact [REDACTED_EMAIL] now"),
        ("ACME revenue +12% vs consensus", "ACME revenue +12% vs consensus"),
    ],
)
def test_redact_text(raw: str, expected: str) -> None:
    assert redact_text(raw) == expected


@pytest.mark.unit
def test_mask_otel_spans_patches_only_sensitive_string_attributes() -> None:
    sensitive = OtelSpanIdentifier(trace_id="t1", span_id="s1")
    clean = OtelSpanIdentifier(trace_id="t1", span_id="s2")
    params = MaskOtelSpansParams(
        spans=MappingProxyType(
            {
                sensitive: _span({"input": "use sk-or-v1-abcdef0123456789abcdef", "n": 3}),
                clean: _span({"input": "ACME beat consensus"}),
            }
        )
    )

    result = mask_otel_spans(params=params)

    assert result is not None
    assert set(result.span_patches) == {sensitive}
    patch = result.span_patches[sensitive]
    assert patch is not None
    assert patch.set_attributes == {"input": "use [REDACTED_API_KEY]"}


@pytest.mark.unit
def test_mask_otel_spans_returns_none_when_nothing_to_redact() -> None:
    params = MaskOtelSpansParams(
        spans=MappingProxyType(
            {OtelSpanIdentifier(trace_id="t1", span_id="s1"): _span({"output": "neutral"})}
        )
    )

    assert mask_otel_spans(params=params) is None
