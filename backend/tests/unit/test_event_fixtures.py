"""Unit tests for synthetic filing-event fixtures. No network, no EDGAR calls."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "events"

VALID_FIXTURES = {
    "8k-nvda-synthetic.json": "8-K",
    "10q-nvda-synthetic.json": "10-Q",
    "10k-nvda-synthetic.json": "10-K",
}

INVALID_FIXTURES = [
    "invalid-missing-form.json",
    "invalid-form-4.json",
]


def _load_fixture(name: str) -> dict[str, object]:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


@pytest.mark.unit
@pytest.mark.parametrize(("name", "form"), sorted(VALID_FIXTURES.items()))
def test_valid_fixtures_parse_to_filing_event(name: str, form: str) -> None:
    """Each material form (8-K, 10-Q, 10-K) has a fixture parsing to FilingEvent."""
    from hft_jev.events import FilingEvent

    event = FilingEvent.model_validate(_load_fixture(name))

    assert event.form == form
    assert event.symbol == "NVDA"
    assert event.synthetic is True


@pytest.mark.unit
def test_valid_fixtures_are_labeled_synthetic_in_raw_json() -> None:
    """Synthetic data must carry its label in the file, not just the model."""
    for name in VALID_FIXTURES:
        assert _load_fixture(name)["synthetic"] is True


@pytest.mark.unit
@pytest.mark.parametrize("name", INVALID_FIXTURES)
def test_invalid_fixtures_fail_validation_with_clear_error(name: str) -> None:
    """Invalid fixtures must not parse to FilingEvent."""
    from hft_jev.events import FilingEvent

    with pytest.raises(ValidationError):
        FilingEvent.model_validate(_load_fixture(name))
