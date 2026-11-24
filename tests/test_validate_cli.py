"""``pyssp validate`` reports every problem and writes no artifact."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from pyssp_sysml.cli import main
from tests.fixture_files import fixture_text
from tests.test_generate_ssp import (
    _build_fmu,
    _write_architecture,
    _write_mismatched_fmu,
)
from tests.testhelpers import COMPOSITION_NAME, write_model

def _validate(
    architecture_dir: Path,
    capsys: pytest.CaptureFixture,
    *extra: str,
) -> tuple[int, str]:
    code = main(
        [
            "validate",
            "--architecture",
            str(architecture_dir),
            "--composition",
            COMPOSITION_NAME,
            *extra,
        ]
    )
    return code, capsys.readouterr().out


def _write_array_architecture(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    write_model(
        root / "model.sysml",
        fixture_text("validate/array-parameters.sysml"),
    )
    return root


def _build_array_fmu(path: Path) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "modelDescription.xml",
            fixture_text("validate/array-model-description.xml"),
        )
    return path


def test_validate_passes_when_every_check_agrees(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    architecture_dir = _write_architecture(
        tmp_path / "arch", source=str(tmp_path / "Comp.fmu")
    )
    _build_fmu(tmp_path / "Comp.fmu")

    code, output = _validate(architecture_dir, capsys)

    assert code == 0
    assert "PASS role-markers" in output
    assert "PASS fmu-interfaces" in output
    assert "check(s) failed" not in output


def test_validate_reports_a_port_member_absent_from_the_fmu(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """A declared connector name the FMU does not carry fails the interface."""
    architecture_dir = _write_architecture(
        tmp_path / "arch",
        source=str(tmp_path / "Comp.fmu"),
        parameterized=False,
    )
    _write_mismatched_fmu(tmp_path / "Comp.fmu")

    code, output = _validate(architecture_dir, capsys)

    assert code == 1
    assert "FAIL fmu-interfaces:" in output
    assert "missing variable 'output.y'" in output
    assert "1 check(s) failed" in output


def test_validate_reports_an_implementation_mismatch(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    architecture_dir = _write_architecture(
        tmp_path / "arch",
        source=str(tmp_path / "Comp.fmu"),
        implementation="CoSimulation",
    )
    _build_fmu(tmp_path / "Comp.fmu")

    code, output = _validate(
        architecture_dir, capsys, "--implementation", "ModelExchange"
    )

    assert code == 1
    assert "PASS fmu-interfaces" in output
    assert "FAIL fmu-implementation:" in output
    assert "1 check(s) failed" in output


def test_validate_no_fmu_skips_the_interface_check(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    architecture_dir = _write_architecture(
        tmp_path / "arch",
        source=str(tmp_path / "Comp.fmu"),
        parameterized=False,
    )

    code, output = _validate(architecture_dir, capsys, "--no-fmu")

    assert code == 0
    assert "fmu-interfaces" not in output


def test_validate_reports_a_missing_declared_fmu_source(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    architecture_dir = _write_architecture(
        tmp_path / "arch",
        source=str(tmp_path / "Missing.fmu"),
        parameterized=False,
    )

    code, output = _validate(architecture_dir, capsys)

    assert code == 1
    assert "FAIL fmu-interfaces:" in output
    assert "Comp: FMU source does not exist" in output


def test_validate_reports_an_unreadable_fmu(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    architecture_dir = _write_architecture(
        tmp_path / "arch",
        source=str(tmp_path / "Comp.fmu"),
        parameterized=False,
    )
    (tmp_path / "Comp.fmu").write_text("not an FMU archive", encoding="utf-8")

    code, output = _validate(architecture_dir, capsys)

    assert code == 1
    assert "FAIL fmu-interfaces:" in output
    assert "cannot read FMU" in output


def test_validate_array_parameter_uses_the_generators_base_index(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """``--base-index 1`` matches OMC-built FMUs and the generated names."""
    architecture_dir = _write_array_architecture(tmp_path / "arch")
    _build_array_fmu(tmp_path / "Comp.fmu")

    code, output = _validate(
        architecture_dir,
        capsys,
        "--fmu-root",
        str(tmp_path),
        "--base-index",
        "1",
    )

    assert code == 0
    assert "PASS fmu-interfaces" in output


def test_validate_array_parameter_defaults_to_zero_and_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """The default 0-based check disagrees with a 1-based array FMU."""
    architecture_dir = _write_array_architecture(tmp_path / "arch")
    _build_array_fmu(tmp_path / "Comp.fmu")

    code, output = _validate(
        architecture_dir, capsys, "--fmu-root", str(tmp_path)
    )

    assert code == 1
    assert "missing variable 'waypointX_km[0]'" in output
    assert "1 check(s) failed" in output


def test_validate_reports_an_unknown_composition_as_an_argument_error(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    architecture_dir = _write_architecture(
        tmp_path / "arch", source=str(tmp_path / "Comp.fmu")
    )

    code = main(
        [
            "validate",
            "--architecture",
            str(architecture_dir),
            "--composition",
            "MissingComposition",
        ]
    )

    assert code == 1
    assert "[error] Unknown composition" in capsys.readouterr().out
