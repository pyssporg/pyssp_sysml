"""Pure analysis-descriptor emission from the parser-free model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pyssp_standard import SSM

from pyssp_sysml2.core.paths import ensure_directory
from pyssp_sysml2.emit.ssm import build_ssm
from pyssp_sysml2.emit.ssv import write_parameter_set
from pyssp_sysml2.projection.model import AnalysisModel


@dataclass(frozen=True)
class AnalysisArtifacts:
    """Paths written by :func:`build_analysis`."""

    ssv: Path | None
    ssm: Path | None
    descriptor: Path
    scenario_set: str | None
    model_usage: str


def _relative_name(path: Path, output_dir: Path) -> str:
    return path.relative_to(output_dir).as_posix()


def build_analysis(
    model: AnalysisModel,
    output_dir: Path,
    *,
    base_index: int = 0,
) -> AnalysisArtifacts:
    """Write ``analysis.json`` and, for one applied set, its SSV and SSM."""
    ensure_directory(output_dir)

    set_definition = model.scenario_set
    ssv_path: Path | None = None
    ssm_path: Path | None = None
    scenario: dict[str, str] | None = None
    if set_definition is not None:
        ssv_path = write_parameter_set(
            set_definition,
            output_dir / f"{set_definition.name}.ssv",
            base_index=base_index,
        )

        ssm_path = output_dir / f"{model.analysis_name}.ssm"
        with SSM(ssm_path, mode="w") as ssm:
            assert model.scenario_mapping is not None
            build_ssm(ssm, model.scenario_mapping)

        scenario = {
            "set": set_definition.name,
            "ssv": _relative_name(ssv_path, output_dir),
            "ssm": _relative_name(ssm_path, output_dir),
        }

    experiment: dict[str, object] = {
        "name": model.experiment.name,
        "start_time": model.experiment.start_time,
        "stop_time": model.experiment.stop_time,
        "step_size": model.experiment.step_size,
    }
    if model.experiment.tolerance is not None:
        experiment["tolerance"] = model.experiment.tolerance

    descriptor: dict[str, object] = {
        "model": model.model_name,
        "composition": model.model_composition,
        "sut": model.sut,
        "target_ssd": model.target_ssd,
        "analysis": model.analysis_name,
        "experiment": experiment,
    }
    if model.description:
        descriptor["description"] = model.description
    if scenario is not None:
        descriptor["scenario"] = scenario
    if model.model_source is not None:
        descriptor["model_source"] = model.model_source
    descriptor_path = output_dir / "analysis.json"
    descriptor_path.write_text(
        json.dumps(descriptor, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return AnalysisArtifacts(
        ssv=ssv_path,
        ssm=ssm_path,
        descriptor=descriptor_path,
        scenario_set=set_definition.name if set_definition is not None else None,
        model_usage=model.sut,
    )
