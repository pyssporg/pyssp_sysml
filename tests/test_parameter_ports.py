from __future__ import annotations

from pathlib import Path

import pytest
from pycps_sysml2 import core_definitions
from pyssp_standard import SSD

from pycps_sysml2.parameters.dialect.composition import validate_parameter_dialect
from pycps_sysml2.parameters.policy import SSP_POLICY
from pyssp_sysml2.parameters.dialect.declarations import (
    parameter_declarations,
    parameter_interface,
)
from pyssp_sysml2.parameters.dialect.markers import validate_marker_definitions
from pyssp_sysml2.parameters.synthesis.interfaces import ensure_component_interface
from pyssp_sysml2.artifacts.ssd import generate_ssd
from pyssp_sysml2.model import load
from tests.fixture_files import render_fixture
from tests.testhelpers import COMPOSITION_NAME, write_model


#: The template imports the shipped vocabulary; a test may shadow a marker.
INCLUDES = (core_definitions(),)


def _model(
    *,
    port: str = "in port parameters : Params;",
    imports: str = "private import PysspCore::*;",
    markers: str = "",
    interface_decl: str = "port def Params :> ParameterInterface",
    interface_members: str = (
        "attribute gain : Real = 2.0;\n"
        "    attribute count : Integer;\n"
        "    attribute xs : Real[2];"
    ),
) -> str:
    return render_fixture(
        "parameter-ports/template.sysml",
        imports=imports,
        port=port,
        markers=markers,
        interface_decl=interface_decl,
        interface_members=interface_members,
        COMPOSITION_NAME=COMPOSITION_NAME,
    )


def _load(tmp_path: Path, text: str, *, includes: bool = True):
    architecture_dir = tmp_path / "arch"
    write_model(architecture_dir / "model.sysml", text)
    roots = INCLUDES if includes else ()
    return architecture_dir, load(architecture_dir, *roots)


@pytest.mark.parametrize(
    "port",
    ["in port parameters : Params;", "port parameters : Params;"],
)
def test_parameter_interface_is_a_port(tmp_path, port: str) -> None:
    """The parameter port is an input (or undirected) port typed by a marked port def."""
    _, architecture = _load(tmp_path, _model(port=port))
    part_def = architecture.get_part_def("Comp")

    interface = parameter_interface(architecture, part_def)

    assert interface is not None
    assert interface.specializes == ("ParameterInterface",)
    assert list(interface.attributes) == ["gain", "count", "xs"]
    assert part_def.ports["parameters"].direction in (None, "in")
    assert part_def.attributes == {}
    assert [attribute.name for attribute in parameter_declarations(architecture, part_def)] == [
        "gain",
        "count",
        "xs",
    ]


def test_out_direction_is_rejected(tmp_path) -> None:
    """A parameter port is not an output signal."""
    _, architecture = _load(
        tmp_path, _model(port="out port parameters : Params;")
    )

    with pytest.raises(ValueError, match="undirected or 'in'"):
        parameter_interface(architecture, architecture.get_part_def("Comp"))


def test_conjugated_parameter_interface_is_rejected(tmp_path) -> None:
    """SSD parameter synthesis refuses a conjugated parameter interface."""
    _, architecture = _load(
        tmp_path, _model(port="in port parameters : ~Params;")
    )
    part_def = architecture.get_part_def("Comp")

    ssd_path = tmp_path / "SystemStructure.ssd"
    with SSD(ssd_path, mode="w") as ssd:
        top = ssd.new_system(COMPOSITION_NAME)
        component = top.add_component("comp", source="resources/Comp.fmu")
        component.add_connector(name="gain", kind="parameter", type_name="Real")

    with SSD(ssd_path, mode="r") as ssd:
        with pytest.raises(ValueError, match="conjugated definition '~Params'"):
            ensure_component_interface(
                architecture,
                part_def,
                ssd.system.elements[0],
                source_file="architecture.sysml",
            )


def test_attribute_bag_is_rejected(tmp_path) -> None:
    """The retired attribute carrier fails with a migration hint."""
    _, architecture = _load(
        tmp_path, _model(port="attribute parameters : Params;")
    )

    with pytest.raises(ValueError, match="attribute bag"):
        parameter_interface(architecture, architecture.get_part_def("Comp"))


def test_attribute_marker_is_rejected(tmp_path) -> None:
    """ParameterInterface must be a port def, not an attribute def."""
    _, architecture = _load(
        tmp_path,
        _model(
            imports="",
            markers=(
                "attribute def ParameterInterface;\n"
                "  attribute def ParameterSet;"
            ),
        ),
        includes=False,
    )

    with pytest.raises(ValueError, match="defined as an attribute def"):
        validate_marker_definitions(architecture)


def test_retired_flat_connector_attribute_is_rejected(tmp_path) -> None:
    """Flattening is an export option; the model attribute was removed."""
    _, architecture = _load(
        tmp_path,
        _model(
            interface_members=(
                "attribute pyssp_flat_connector : Boolean = true;\n"
                "    attribute gain : Real;"
            ),
        ),
    )

    with pytest.raises(ValueError, match="--flat-connector"):
        validate_parameter_dialect(
            architecture,
            architecture.get_part_def("Comp"),
            policy=SSP_POLICY,
        )


def test_parameter_port_cannot_be_connected(tmp_path) -> None:
    """Parameter ports are bound, not wired with 'connect'."""
    model = render_fixture(
        "parameter-ports/connected-ports.sysml", COMPOSITION_NAME=COMPOSITION_NAME
    )
    architecture_dir, _ = _load(tmp_path, model)

    with pytest.raises(ValueError, match="cannot be connected"):
        generate_ssd(
            architecture_dir,
            tmp_path / "SystemStructure.ssd",
            COMPOSITION_NAME,
            includes=INCLUDES,
        )


def test_interface_port_must_use_the_reserved_usage_name(tmp_path) -> None:
    """The reserved name is enforced: a marked port under 'gains' is an error."""
    architecture_dir, _ = _load(tmp_path, _model(port="in port gains : Params;"))

    with pytest.raises(ValueError, match="must be named 'parameters'"):
        generate_ssd(
            architecture_dir,
            tmp_path / "SystemStructure.ssd",
            COMPOSITION_NAME,
            includes=INCLUDES,
        )


def test_ssd_connectors_are_flat_parameter_connectors(tmp_path) -> None:
    """The parameter port does not leak into signal connectors."""
    architecture_dir, _ = _load(tmp_path, _model())
    output_path = tmp_path / "SystemStructure.ssd"

    generate_ssd(architecture_dir, output_path, COMPOSITION_NAME, includes=INCLUDES)

    with SSD(output_path, mode="r") as ssd:
        component = ssd.system.elements[0]
        assert sorted(
            (connector.name, connector.kind, connector.type_name)
            for connector in component.connectors
        ) == [
            ("count", "parameter", "Integer"),
            ("gain", "parameter", "Real"),
            ("xs[0]", "parameter", "Real"),
            ("xs[1]", "parameter", "Real"),
        ]
