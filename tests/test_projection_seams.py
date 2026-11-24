"""Emission seams accept plain projection records, never a SysML fixture.

Each test builds the records by hand, writes one artifact, and reads it back
through the ``pyssp_standard`` facade. A static check keeps the emit package
free of parser imports so the seam cannot silently regress.
"""

from __future__ import annotations

import ast
import json
import zipfile
from pathlib import Path

import pytest
from pyssp_standard import SSD, SSM, SSV

from pyssp_sysml.emit.analysis import build_analysis
from pyssp_sysml.emit.ssd import build_ssd
from pyssp_sysml.emit.ssm import build_ssm
from pyssp_sysml.emit.ssp import build_ssp
from pyssp_sysml.emit.ssv import build_ssv
from pyssp_sysml.projection.model import (
    AnalysisModel,
    Attribute,
    AttributeDef,
    Connection,
    Experiment,
    MappingSpec,
    PartDef,
    PartUsage,
    PortDef,
    PortUsage,
    SystemModel,
)

PROJECT = Path(__file__).resolve().parents[1]
EMIT = PROJECT / "src" / "pyssp_sysml" / "emit"


def _part_def() -> PartDef:
    signal = PortDef(
        name="Signal",
        attributes={"value": Attribute("value", "Real")},
        scalar=True,
    )
    input_port = PortUsage(
        name="u",
        type_name="Signal",
        direction="in",
        member_directions={"value": "in"},
        definition=signal,
    )
    output_port = PortUsage(
        name="y",
        type_name="Signal",
        direction="out",
        member_directions={"value": "out"},
        definition=signal,
    )
    return PartDef(
        name="Comp",
        ports={"u": input_port, "y": output_port},
        resource_name="Comp.fmu",
    )


def _system_model() -> SystemModel:
    comp = _part_def()
    root = PartDef(
        name="Root",
        parts={"comp": PartUsage("comp", "Comp", comp)},
    )
    return SystemModel(name="Root", root=root, components=(comp,))


def test_build_ssd_accepts_projection(tmp_path: Path) -> None:
    output = tmp_path / "SystemStructure.ssd"
    with SSD(output, mode="w") as ssd:
        build_ssd(ssd, _system_model())

    with SSD(output, mode="r") as ssd:
        assert ssd.system is not None
        [component] = ssd.system.elements
        assert component.name == "comp"
        assert [connector.name for connector in component.connectors] == ["u", "y"]
        assert [connector.kind for connector in component.connectors] == [
            "input",
            "output",
        ]


def test_build_ssd_accepts_a_resolved_connection(tmp_path: Path) -> None:
    comp = _part_def()
    source = PartUsage("source", "Comp", comp)
    destination = PartUsage("destination", "Comp", comp)
    root = PartDef(
        name="Root",
        ports={},
        parts={"source": source, "destination": destination},
        connections=(
            Connection(
                key="source.y->destination.u",
                source_part="source",
                source_port="y",
                destination_part="destination",
                destination_port="u",
                source=comp.ports["y"],
                destination=comp.ports["u"],
            ),
        ),
    )
    model = SystemModel(name="Root", root=root, components=(comp,))
    output = tmp_path / "SystemStructure.ssd"
    with SSD(output, mode="w") as ssd:
        build_ssd(ssd, model)

    with SSD(output, mode="r") as ssd:
        assert ssd.system is not None
        [connection] = ssd.system.connections
        assert (
            connection.start_element,
            connection.start_connector,
            connection.end_element,
            connection.end_connector,
        ) == ("source", "y", "destination", "u")


def test_build_ssv_accepts_projection(tmp_path: Path) -> None:
    definition = AttributeDef(
        name="Nominal",
        attributes={
            "gain": Attribute("gain", "Real", value=2.5),
            "xs": Attribute(
                "xs", "Real", multiplicity="2", value=(0.0, 10.0)
            ),
        },
    )
    output = tmp_path / "Nominal.ssv"
    with SSV(output, mode="w") as ssv:
        build_ssv(ssv, definition)

    with SSV(output, mode="r") as ssv:
        assert ssv.xml.name == "Nominal"
        assert {
            (parameter.name, parameter.attributes["value"])
            for parameter in ssv.xml.parameters
        } == {("gain", "2.5"), ("xs[0]", "0"), ("xs[1]", "10")}


def test_build_ssm_accepts_projection(tmp_path: Path) -> None:
    mapping = MappingSpec(
        set_name="Nominal",
        identity=False,
        component_name="comp",
        entries=(("gain", "comp.gain"),),
    )
    output = tmp_path / "Nominal_comp.ssm"
    with SSM(output, mode="w") as ssm:
        build_ssm(ssm, mapping)

    with SSM(output, mode="r") as ssm:
        [entry] = ssm.xml.mappings
        assert (entry.source, entry.target) == ("gain", "comp.gain")


def test_build_ssp_accepts_projection(tmp_path: Path) -> None:
    model = _system_model()
    model = SystemModel(
        name=model.name,
        root=model.root,
        components=model.components,
        parameter_sets=(
            AttributeDef(
                name="Nominal",
                attributes={"gain": Attribute("gain", "Real", value=2.0)},
            ),
        ),
    )
    output = tmp_path / "model.ssp"
    with pytest.warns(UserWarning):
        build_ssp(
            model,
            output,
            allow_missing_fmus=True,
            validate_fmus=False,
        )

    with zipfile.ZipFile(output, "r") as archive:
        assert set(archive.namelist()) == {
            "SystemStructure.ssd",
            "resources/parameter_sets/Nominal.ssv",
        }


def test_build_analysis_accepts_projection(tmp_path: Path) -> None:
    model = AnalysisModel(
        model_name="System",
        analysis_name="Scenario",
        model_composition="Model",
        sut="sut",
        target_ssd="SystemStructure.ssd",
        description="A study",
        experiment=Experiment(
            name="default", start_time=0.0, stop_time=10.0, step_size=0.1
        ),
        scenario_set=AttributeDef(
            name="Nominal",
            attributes={"gain": Attribute("gain", "Real", value=2.0)},
        ),
        scenario_mapping=MappingSpec(
            set_name="Nominal",
            identity=False,
            component_name="sut",
            entries=(("gain", "gain"),),
        ),
    )
    artifacts = build_analysis(model, tmp_path / "analysis")

    assert artifacts.ssv is not None and artifacts.ssv.is_file()
    assert artifacts.ssm is not None and artifacts.ssm.is_file()
    descriptor = json.loads(artifacts.descriptor.read_text(encoding="utf-8"))
    assert descriptor["composition"] == "Model"
    assert descriptor["sut"] == "sut"
    assert descriptor["scenario"]["set"] == "Nominal"
    assert descriptor["experiment"]["step_size"] == 0.1


def test_emit_modules_import_no_parser() -> None:
    violations: list[str] = []
    for path in sorted(EMIT.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if name == "pycps_sysml" or name.startswith("pycps_sysml."):
                    violations.append(f"{path.name}:{node.lineno} imports {name}")
    assert not violations, "emit must stay parser-free:\n" + "\n".join(violations)
