from __future__ import annotations

from pathlib import Path

import pytest
from pyssp_standard import SSD, System

from pycps_sysml2 import core_definitions
from pyssp_sysml2.artifacts.preflight import _expected_connector_names
from pyssp_sysml2.artifacts.ssd import build_ssd, generate_ssd
from pyssp_sysml2.model import load
from tests.fixture_files import fixture_path, fixture_text, render_fixture
from tests.testhelpers import COMPOSITION_NAME, write_model



def _ssd_summary(ssd_path) -> list[str]:
    with SSD(ssd_path, mode="r") as ssd:
        assert ssd.system is not None

        lines = []
        for component in sorted(ssd.system.elements, key=lambda element: element.name):
            connector_summaries = sorted(
                f"{connector.kind}:{connector.name}:{connector.type_name}"
                for connector in component.connectors
            )
            lines.append(f"component {component.name}")
            lines.extend(f"  {summary}" for summary in connector_summaries)

        for connection in sorted(
            ssd.system.connections,
            key=lambda conn: (
                conn.start_element,
                conn.start_connector,
                conn.end_element,
                conn.end_connector,
            ),
        ):
            lines.append(
                "connection "
                f"{connection.start_element}.{connection.start_connector}"
                f" -> {connection.end_element}.{connection.end_connector}"
            )

        return lines


def test_generate_ssd_from_small_snippet(tmp_path) -> None:
    """Generated SSD contains expected connectors, parameters, and expanded connections."""
    architecture_dir = tmp_path / "arch"
    architecture_dir.mkdir(parents=True, exist_ok=True)

    write_model(
        architecture_dir / "ports.sysml",
        fixture_text("generate-ssd/ports.sysml"),
    )

    write_model(
        architecture_dir / "parts.sysml",
        fixture_text("generate-ssd/parts.sysml"),
    )

    write_model(
        architecture_dir / "composition.sysml",
        render_fixture("generate-ssd/composition.sysml", COMPOSITION_NAME=COMPOSITION_NAME),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    architecture = load(architecture_dir)
    system = architecture.get_part_def(COMPOSITION_NAME)

    with SSD(output_path, mode="w") as ssd:
        build_ssd(ssd, system, architecture)

    assert _ssd_summary(output_path) == [
        "component dst",
        "  input:sigIn.mode:Integer",
        "  input:sigIn.x:Real",
        "component src",
        "  output:sig.mode:Integer",
        "  output:sig.x:Real",
        "  parameter:gains[0]:Real",
        "  parameter:gains[1]:Real",
        "connection src.sig.mode -> dst.sigIn.mode",
        "connection src.sig.x -> dst.sigIn.x",
    ]


def test_generate_ssd_writes_core_ssd_metadata(tmp_path: Path) -> None:
    """Generated SSD sets the expected top-level metadata and component fields."""
    architecture_dir = tmp_path / "arch"
    architecture_dir.mkdir(parents=True, exist_ok=True)

    write_model(
        architecture_dir / "model.sysml",
        render_fixture("generate-ssd/core-metadata.sysml", COMPOSITION_NAME=COMPOSITION_NAME),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    architecture = load(architecture_dir)
    system = architecture.get_part_def(COMPOSITION_NAME)

    with SSD(output_path, mode="w") as ssd:
        build_ssd(ssd, system, architecture)

    assert _ssd_summary(output_path) == [
        "component src",
        "  output:outSig.x:Real",
    ]

    with SSD(output_path, mode="r") as ssd:
        assert ssd.xml.name == COMPOSITION_NAME
        assert 'version="1.0"' in output_path.read_text()
        assert ssd.default_experiment is not None
        assert ssd.default_experiment.start_time == 0
        assert ssd.default_experiment.stop_time == 3600
        assert ssd.system is not None
        assert len(ssd.system.elements) == 1
        component = ssd.system.elements[0]
        assert component.name == "src"
        assert component.component_type == "application/x-fmu-sharedlibrary"
        assert component.source == ""


def test_generate_ssd_reads_the_experiment_container(tmp_path: Path) -> None:
    """A typed DefaultExperiment container supplies the SSD start and stop."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        render_fixture(
            "generate-ssd/default-experiment.sysml",
            COMPOSITION_NAME=COMPOSITION_NAME,
        ),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, COMPOSITION_NAME)

    with SSD(output_path, mode="r") as ssd:
        assert ssd.default_experiment is not None
        assert ssd.default_experiment.start_time == 2.0
        assert ssd.default_experiment.stop_time == 8.0


def test_generate_ssd_rejects_retired_experiment_attributes(tmp_path: Path) -> None:
    """The removed start/stop attributes name the container replacement."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/retired-default-experiment.sysml"),
    )

    with pytest.raises(
        ValueError,
        match=r"pyssp_default_start_time .*DefaultExperiment",
    ):
        generate_ssd(
            architecture_dir, tmp_path / "SystemStructure.ssd", "Model"
        )


def test_generate_ssd_rejects_the_retired_flat_connector_attribute(
    tmp_path: Path,
) -> None:
    """Flattening is an export option and no longer model data."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/retired-flat-connector.sysml"),
    )

    with pytest.raises(ValueError, match="--flat-connector"):
        generate_ssd(
            architecture_dir, tmp_path / "SystemStructure.ssd", "Model"
        )


def test_generate_ssd_rejects_retired_parameter_set_attribute(tmp_path: Path) -> None:
    """The legacy external SSV pointer is replaced by SysML-defined sets."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        render_fixture(
            "generate-ssd/retired-parameter-set.sysml", COMPOSITION_NAME=COMPOSITION_NAME
        ),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    with pytest.raises(ValueError, match=r"pyssp_parameter_set .*ParameterSet"):
        generate_ssd(architecture_dir, output_path, COMPOSITION_NAME)


def test_generate_ssd_wires_system_boundary(tmp_path: Path) -> None:
    """A bare connection end emits an SSD connection without an element."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        render_fixture("generate-ssd/boundary.sysml", COMPOSITION_NAME=COMPOSITION_NAME),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, COMPOSITION_NAME)

    with SSD(output_path, mode="r") as ssd:
        top = ssd.system
        assert [(connector.name, connector.kind) for connector in top.connectors] == [
            ("y.x", "output")
        ]
        assert [
            (c.start_element, c.start_connector, c.end_element, c.end_connector)
            for c in top.connections
        ] == [("inner", "v.x", None, "y.x")]

        inner = top.elements[0]
        assert isinstance(inner, System)
        assert [(connector.name, connector.kind) for connector in inner.connectors] == [
            ("u.x", "input"),
            ("v.x", "output"),
        ]
        assert [
            (c.start_element, c.start_connector, c.end_element, c.end_connector)
            for c in inner.connections
        ] == [
            (None, "u.x", "src", "sig.x"),
            ("src", "sig.x", "dst", "sigIn.x"),
            ("dst", "sig.x", None, "v.x"),
        ]


def test_generate_ssd_rejects_boundary_port_wrong_direction(tmp_path: Path) -> None:
    """A boundary port used as the start of a connection must be an input."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        render_fixture(
            "generate-ssd/boundary-wrong-direction.sysml",
            COMPOSITION_NAME=COMPOSITION_NAME,
        ),
    )

    with pytest.raises(ValueError, match="used as the end of a connection"):
        generate_ssd(
            architecture_dir, tmp_path / "SystemStructure.ssd", COMPOSITION_NAME
        )


def test_generate_ssd_rejects_boundary_to_boundary_connection(tmp_path: Path) -> None:
    """A connection between two boundary ports does not cross a subpart."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        render_fixture(
            "generate-ssd/boundary-to-boundary.sysml",
            COMPOSITION_NAME=COMPOSITION_NAME,
        ),
    )

    with pytest.raises(ValueError, match="links two boundary ports"):
        generate_ssd(
            architecture_dir, tmp_path / "SystemStructure.ssd", COMPOSITION_NAME
        )


def test_quoted_attribute_names_become_plain_ssd_connectors(tmp_path) -> None:
    """Quoted SysML names keep their characters in the SSD connector name."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "quoted.sysml",
        fixture_text("quoted-names/composition.sysml"),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, "System")

    assert _ssd_summary(output_path) == [
        "component sink",
        "  input:feed.X[1]:Real",
        "  input:feed.X[2]:Real",
        "  input:feed.p:Real",
        "component source",
        "  output:feed.X[1]:Real",
        "  output:feed.X[2]:Real",
        "  output:feed.p:Real",
        "connection source.feed.X[1] -> sink.feed.X[1]",
        "connection source.feed.X[2] -> sink.feed.X[2]",
        "connection source.feed.p -> sink.feed.p",
    ]


def test_port_multiplicity_expands_connectors_and_connections(tmp_path) -> None:
    """One fixed-multiplicity port expands to one indexed connector per element."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "arrays.sysml",
        fixture_text("arrays/ports.sysml"),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(
        architecture_dir, output_path, "System", flat_connector=True
    )

    assert _ssd_summary(output_path) == [
        "component sink",
        "  input:feed.X[1]:Real",
        "  input:feed.X[2]:Real",
        "  input:feed.X[3]:Real",
        "component source",
        "  output:feed.X[1]:Real",
        "  output:feed.X[2]:Real",
        "  output:feed.X[3]:Real",
        "connection source.feed.X[1] -> sink.feed.X[1]",
        "connection source.feed.X[2] -> sink.feed.X[2]",
        "connection source.feed.X[3] -> sink.feed.X[3]",
    ]


def test_generate_ssd_uses_member_directions_on_a_mixed_port(tmp_path) -> None:
    """A member's direction overrides its usage; unmarked members fall back to input."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/member-directions.sysml"),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, COMPOSITION_NAME)

    assert _ssd_summary(output_path) == [
        "component widget",
        "  input:fallback.n:Real",
        # sig.p[1..3]: one connector per array element.
        "  input:sig.p[1]:Real",
        "  input:sig.p[2]:Real",
        "  input:sig.p[3]:Real",
        "  output:sig.m:Real",
    ]


def test_array_attribute_connection_expands_per_element(tmp_path) -> None:
    """Two matching array members connect element by element."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/array-attribute.sysml"),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, "System")

    assert _ssd_summary(output_path) == [
        "component sink",
        "  input:sigIn.p[1]:Real",
        "  input:sigIn.p[2]:Real",
        "  input:sigIn.p[3]:Real",
        "component source",
        "  output:sig.p[1]:Real",
        "  output:sig.p[2]:Real",
        "  output:sig.p[3]:Real",
        "connection source.sig.p[1] -> sink.sigIn.p[1]",
        "connection source.sig.p[2] -> sink.sigIn.p[2]",
        "connection source.sig.p[3] -> sink.sigIn.p[3]",
    ]


def test_array_attributes_with_unequal_lengths_are_rejected(tmp_path) -> None:
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/array-attribute-mismatch.sysml"),
    )

    with pytest.raises(ValueError, match="attributes with different multiplicity"):
        generate_ssd(
            architecture_dir,
            tmp_path / "out.ssd",
            "System",
            type_check=False,
        )


def test_variable_array_attribute_is_rejected(tmp_path) -> None:
    """A variable range cannot become a fixed set of connectors."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/array-attribute-variable.sysml"),
    )

    with pytest.raises(ValueError, match="Port attribute 'sig.p'.*multiplicity"):
        generate_ssd(architecture_dir, tmp_path / "out.ssd", "System")


def test_boundary_array_attribute_expands_per_element(tmp_path) -> None:
    """A boundary port with an array member wires each element like a component."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/boundary-array.sysml"),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, "System")

    with SSD(output_path, mode="r") as ssd:
        top = ssd.system
        assert [connector.name for connector in top.connectors] == [
            "u.p[1]",
            "u.p[2]",
            "u.p[3]",
        ]
        assert [
            (c.start_element, c.start_connector, c.end_element, c.end_connector)
            for c in top.connections
        ] == [
            (None, "u.p[1]", "inner", "u.p[1]"),
            (None, "u.p[2]", "inner", "u.p[2]"),
            (None, "u.p[3]", "inner", "u.p[3]"),
        ]


def test_derived_part_definition_emits_effective_members(tmp_path) -> None:
    """A derived def emits inherited connectors and connections before its own."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/inheritance.sysml"),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, "System")

    with SSD(output_path, mode="r") as ssd:
        top = ssd.system
        assert top is not None
        [link] = top.elements
        assert isinstance(link, System)
        assert [element.name for element in link.elements] == ["sink", "probe"]
        assert [
            (connector.name, connector.kind, connector.type_name)
            for connector in link.connectors
        ] == [
            ("u", "input", "Real"),
            ("y", "output", "Real"),
            ("extra.value", "output", "Real"),
            ("extra.flag", "output", "Integer"),
        ]
        assert [
            (
                connection.start_element,
                connection.start_connector,
                connection.end_element,
                connection.end_connector,
            )
            for connection in link.connections
        ] == [
            (None, "u", "sink", "u"),
            ("probe", "u.value", None, "extra.value"),
            ("probe", "u.flag", None, "extra.flag"),
        ]


def test_preflight_expects_effective_connectors(tmp_path) -> None:
    """Preflight reads the same inherited member view as the SSD writer."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/inheritance.sysml"),
    )

    architecture = load(architecture_dir)
    derived = architecture.get_part_def("DerivedLink")

    assert _expected_connector_names(
        architecture,
        derived,
        parameter_model=False,
        base_index=0,
        flat=False,
    ) == ["u", "y", "extra.value", "extra.flag"]


def test_flat_connector_rejects_an_array_attribute(tmp_path) -> None:
    """Flat naming has no slot for a per-element index."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/array-attribute.sysml"),
    )

    with pytest.raises(ValueError, match="Flat connector naming cannot represent"):
        generate_ssd(
            architecture_dir,
            tmp_path / "out.ssd",
            "System",
            flat_connector=True,
        )


def test_connection_with_mismatched_multiplicity_is_rejected(tmp_path) -> None:
    architecture_dir = tmp_path / "mismatch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("arrays/mismatch.sysml"),
    )

    with pytest.raises(ValueError, match="different multiplicity"):
        generate_ssd(architecture_dir, tmp_path / "out.ssd", "System")


def test_generate_ssd_merges_core_definitions_on_request(tmp_path: Path) -> None:
    """A marker-free model fails by default and generates with the core defs."""
    architecture = fixture_path("core-definitions/marker-user.sysml")
    output_path = tmp_path / "SystemStructure.ssd"

    with pytest.raises(ValueError, match="SspModel"):
        generate_ssd(architecture, output_path, "MarkerSystem")

    generate_ssd(
        architecture,
        output_path,
        "MarkerSystem",
        includes=[core_definitions()],
    )

    assert _ssd_summary(output_path) == [
        "component dst",
        "  input:inSig.x:Real",
        "component src",
        "  output:outSig.x:Real",
        "connection src.outSig.x -> dst.inSig.x",
    ]


def test_mirrored_port_definitions_connect_by_member(tmp_path) -> None:
    """Direction is flow, not type: mirrored definitions are compatible ends."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/mirrored-ports.sysml"),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, "System")

    assert _ssd_summary(output_path) == [
        "component sink",
        "  input:feed.p:Real",
        "  output:feed.m:Real",
        "component source",
        "  input:feed.m:Real",
        "  output:feed.p:Real",
        "connection source.feed.m -> sink.feed.m",
        "connection source.feed.p -> sink.feed.p",
    ]


def test_conjugated_port_definition_serves_both_ends(tmp_path) -> None:
    """One definition used as ``P`` and ``~P`` emits flipped connector kinds."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/conjugated-ports.sysml"),
    )
    architecture = load(architecture_dir)
    assert list(architecture.port_definitions) == ["Feed"]
    assert architecture.part_definitions["Source"].ports["feed"].conjugated is False
    assert architecture.part_definitions["Sink"].ports["feed"].conjugated is True

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, "System")

    assert _ssd_summary(output_path) == [
        "component sink",
        "  input:feed.p:Real",
        "  output:feed.m:Real",
        "component source",
        "  input:feed.m:Real",
        "  output:feed.p:Real",
        "connection source.feed.m -> sink.feed.m",
        "connection source.feed.p -> sink.feed.p",
    ]


def test_single_value_member_exports_as_a_scalar_connector(tmp_path) -> None:
    """A port whose only member is ``value`` keeps the FMU variable name."""
    architecture_dir = tmp_path / "arch"
    write_model(
        architecture_dir / "model.sysml",
        fixture_text("generate-ssd/scalar-port.sysml"),
    )

    output_path = tmp_path / "SystemStructure.ssd"
    generate_ssd(architecture_dir, output_path, "System")

    assert _ssd_summary(output_path) == [
        "component sink",
        "  input:AltIn:Real",
        "component source",
        "  output:Alt:Real",
        "connection source.Alt -> sink.AltIn",
    ]
