"""Flattening is an SSD export option, not model data.

The same architecture is exported twice: the default emits one
``port.member`` connector per port member, and ``flat_connector=True`` emits a
single connector named for the port. Nothing in the SysML document records the
choice.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_standard import SSD

from pyssp_sysml2.artifacts.ssd import generate_ssd
from tests.fixture_files import fixture_text, render_fixture
from tests.testhelpers import COMPOSITION_NAME, write_model


def _architecture(tmp_path: Path) -> Path:
    root = tmp_path / "arch"
    root.mkdir(parents=True)
    write_model(root / "ports.sysml", fixture_text("flat-connector/ports.sysml"))
    write_model(root / "parts.sysml", fixture_text("flat-connector/parts.sysml"))
    write_model(
        root / "composition.sysml",
        render_fixture(
            "flat-connector/composition.sysml", COMPOSITION_NAME=COMPOSITION_NAME
        ),
    )
    return root


def _ssd_summary(ssd_path: Path) -> dict[str, object]:
    with SSD(ssd_path, mode="r") as ssd:
        assert ssd.system is not None
        connectors = {
            component.name: sorted(
                connector.name for connector in component.connectors
            )
            for component in ssd.system.elements
        }
        connections = sorted(
            (
                connection.start_element,
                connection.start_connector,
                connection.end_element,
                connection.end_connector,
            )
            for connection in ssd.system.connections
        )
    return {"connectors": connectors, "connections": connections}


def _generate(tmp_path: Path, *, flat_connector: bool) -> dict[str, object]:
    architecture_dir = _architecture(tmp_path / "arch")
    ssd_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(
        architecture_dir,
        ssd_path,
        COMPOSITION_NAME,
        flat_connector=flat_connector,
    )
    return _ssd_summary(ssd_path)


def _assert_endpoints_are_connectors(summary: dict[str, object]) -> None:
    connectors = summary["connectors"]
    assert isinstance(connectors, dict)
    for start, start_connector, end, end_connector in summary["connections"]:
        assert start_connector in connectors[start]
        assert end_connector in connectors[end]


def test_default_keeps_per_member_connectors(tmp_path: Path) -> None:
    """Without the option every port member gets its own connector."""
    summary = _generate(tmp_path, flat_connector=False)

    assert summary["connectors"] == {"src": ["sig.x"], "dst": ["sigIn.x"]}
    assert summary["connections"] == [("src", "sig.x", "dst", "sigIn.x")]
    _assert_endpoints_are_connectors(summary)


def test_flat_connector_option_emits_one_connector_per_port(
    tmp_path: Path,
) -> None:
    """``flat_connector=True`` names the connector for the port alone."""
    summary = _generate(tmp_path, flat_connector=True)

    assert summary["connectors"] == {"src": ["sig"], "dst": ["sigIn"]}
    assert summary["connections"] == [("src", "sig", "dst", "sigIn")]
    _assert_endpoints_are_connectors(summary)
