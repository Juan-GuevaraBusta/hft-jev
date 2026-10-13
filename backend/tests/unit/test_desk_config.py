"""Unit tests for the desk YAML loader (DeskConfig). No network, no LLMs."""

import re
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]  # PyYAML ships no py.typed; tests use safe_load only

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_YAML = REPO_ROOT / "config" / "desk.example.yaml"


def _example_data() -> dict[str, object]:
    with EXAMPLE_YAML.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    assert isinstance(loaded, dict)
    return loaded


def _write_yaml(tmp_path: Path, data: dict[str, object], name: str = "desk.yaml") -> Path:
    target = tmp_path / name
    with target.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle)
    return target


@pytest.mark.unit
def test_loads_example_yaml_without_error() -> None:
    """The real config/desk.example.yaml must validate against DeskConfig."""
    from hft_jev.desk_config import load_desk_config

    config = load_desk_config(EXAMPLE_YAML)

    assert config.desk.name == "hft-jev-research-desk"
    assert config.execution.reject_threshold == 0.40
    assert config.execution.auto_threshold == 0.75


@pytest.mark.unit
def test_unknown_root_field_fails_naming_the_key(tmp_path: Path) -> None:
    """A YAML with an unknown root key must fail and name the key."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    data = _example_data()
    data["bogus_section"] = {"enabled": True}

    with pytest.raises(DeskConfigError, match="bogus_section"):
        load_desk_config(_write_yaml(tmp_path, data))


@pytest.mark.unit
def test_unknown_nested_field_fails_naming_the_key(tmp_path: Path) -> None:
    """A YAML with an unknown nested key must fail and name the key."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    data = _example_data()
    execution = data["execution"]
    assert isinstance(execution, dict)
    execution["bogus_limit"] = 123

    with pytest.raises(DeskConfigError, match="bogus_limit"):
        load_desk_config(_write_yaml(tmp_path, data))


def _mutate(tmp_path: Path, dotted: str, value: object) -> Path:
    """Return a tmp YAML copy of the example with dotted key set to value."""
    data = _example_data()
    node: dict[str, object] = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        child = node[part]
        assert isinstance(child, dict)
        node = child
    node[parts[-1]] = value
    return _write_yaml(tmp_path, data)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("dotted", "bad_value"),
    [
        ("execution.reject_threshold", 1.5),
        ("execution.auto_threshold", -0.1),
        ("execution.max_daily_loss_pct", 2.0),
        ("money_rules.max_new_order_pct", 1.01),
        ("desk_limits.material_pct_threshold", -0.5),
        ("execution.max_orders_per_day", 0),
        ("desk_limits.max_artifacts_for_review_per_day", 0),
        ("money_rules.staleness_hours", 0),
    ],
)
def test_out_of_range_limit_fails_naming_field_and_value(
    tmp_path: Path, dotted: str, bad_value: object
) -> None:
    """Out-of-range thresholds/limits must fail naming the field and the value."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    field = dotted.split(".")[-1]
    with pytest.raises(DeskConfigError, match=re.escape(f"{field}={bad_value!r}")):
        load_desk_config(_mutate(tmp_path, dotted, bad_value))


@pytest.mark.unit
@pytest.mark.parametrize("reject", [0.75, 0.9])
def test_reject_threshold_gte_auto_threshold_fails(tmp_path: Path, reject: float) -> None:
    """ADR-004 invariant: reject_threshold < auto_threshold (0.40 / 0.75)."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    data = _example_data()
    execution = data["execution"]
    assert isinstance(execution, dict)
    execution["reject_threshold"] = reject
    execution["auto_threshold"] = 0.75

    with pytest.raises(
        DeskConfigError,
        match=re.escape(f"reject_threshold={reject!r} must be < auto_threshold="),
    ):
        load_desk_config(_write_yaml(tmp_path, data))


@pytest.mark.unit
def test_unknown_shift_key_fails_with_clear_message(tmp_path: Path) -> None:
    """A shift other than night_ingest/morning_desk must fail naming the key."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    data = _example_data()
    schedule = data["schedule"]
    assert isinstance(schedule, dict)
    schedule["evening_desk"] = {"enabled": True}

    with pytest.raises(DeskConfigError, match="evening_desk"):
        load_desk_config(_write_yaml(tmp_path, data))


@pytest.mark.unit
@pytest.mark.parametrize("bad_cron", ["not a cron", "30 16 * *", "30 16 * * 1-5 extra"])
def test_invalid_cron_fails_with_clear_message(tmp_path: Path, bad_cron: str) -> None:
    """night_ingest.cron must be a 5-field cron expression."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    with pytest.raises(DeskConfigError, match=re.escape(f"cron={bad_cron!r}")):
        load_desk_config(_mutate(tmp_path, "schedule.night_ingest.cron", bad_cron))


@pytest.mark.unit
@pytest.mark.parametrize("bad_time", ["9am", "25:00", "09-00"])
def test_invalid_morning_time_fails_with_clear_message(tmp_path: Path, bad_time: str) -> None:
    """morning_desk.local_time must be HH:MM in 24h format."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    with pytest.raises(DeskConfigError, match=re.escape(f"local_time={bad_time!r}")):
        load_desk_config(_mutate(tmp_path, "schedule.morning_desk.local_time", bad_time))


@pytest.mark.unit
def test_loader_routes_through_safe_load(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The loader must call yaml.safe_load (never yaml.load)."""
    from hft_jev.desk_config import load_desk_config

    calls: list[str] = []
    real_safe_load = yaml.safe_load

    def spy(text: str) -> object:
        calls.append(text)
        return real_safe_load(text)

    target = _write_yaml(tmp_path, _example_data())
    monkeypatch.setattr(yaml, "safe_load", spy)
    load_desk_config(target)

    assert len(calls) == 1


@pytest.mark.unit
def test_malicious_yaml_tag_is_rejected(tmp_path: Path) -> None:
    """A !!python/object tag must fail: proof the loader never yaml.loads it."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    evil = tmp_path / "evil.yaml"
    evil.write_text('desk: !!python/object/apply:os.system ["echo pwned"]\n', encoding="utf-8")

    with pytest.raises(DeskConfigError):
        load_desk_config(evil)


@pytest.mark.unit
def test_unreadable_file_fails_with_path_in_message(tmp_path: Path) -> None:
    """A missing file must fail naming the path."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    missing = tmp_path / "no-such-desk.yaml"
    with pytest.raises(DeskConfigError, match=re.escape(str(missing))):
        load_desk_config(missing)


@pytest.mark.unit
def test_malformed_yaml_fails_with_clear_message(tmp_path: Path) -> None:
    """Syntactically invalid YAML must fail, not parse halfway."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    broken = tmp_path / "broken.yaml"
    broken.write_text("desk: [unclosed\n  - bad indent:\n", encoding="utf-8")

    with pytest.raises(DeskConfigError, match="not valid YAML"):
        load_desk_config(broken)


@pytest.mark.unit
def test_non_mapping_root_fails_with_clear_message(tmp_path: Path) -> None:
    """A YAML document whose root is not a mapping must fail."""
    from hft_jev.desk_config import DeskConfigError, load_desk_config

    target = tmp_path / "list-root.yaml"
    target.write_text("- just\n- a\n- list\n", encoding="utf-8")

    with pytest.raises(DeskConfigError, match="root must be a mapping"):
        load_desk_config(target)


@pytest.mark.unit
def test_example_pins_approved_contract_decisions() -> None:
    """Q3/Q4: the example reuses the tope-3 field (=3) with both shifts enabled."""
    from hft_jev.desk_config import load_desk_config

    config = load_desk_config(EXAMPLE_YAML)

    assert config.desk_limits.max_artifacts_for_review_per_day == 3
    assert config.schedule.night_ingest.enabled is True
    assert config.schedule.morning_desk.enabled is True
