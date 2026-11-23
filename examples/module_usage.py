"""Generate the aircraft example artifacts through the Python API.

Run from the pyssp_dev workspace root:

    python repos/pyssp_sysml2/examples/module_usage.py

Pass ``--out`` to change the artifact directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pycps_sysml2

from pyssp_sysml2.artifacts.ssd import generate_ssd
from pyssp_sysml2.artifacts.ssv import generate_parameter_sets
from pyssp_sysml2.sysml.sync import sync_sysml_from_ssd

# The shared PysspCore vocabulary is an include root: pycps_sysml2 re-exports
# pyssp_sysml_definitions; no .sysml file is copied into this repository.
CORE_DEFINITIONS = (pycps_sysml2.core_definitions(),)
ARCHITECTURE = Path(__file__).resolve().parent / "aircraft_subset"
COMPOSITION = "AircraftComposition"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("build/examples/module_usage"),
        help="Output root directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ssd_path = args.out / "SystemStructure.ssd"
    parameter_set_dir = args.out / "parameter_sets"
    sync_dir = args.out / "synced_sysml"

    generate_ssd(
        ARCHITECTURE,
        ssd_path,
        COMPOSITION,
        includes=CORE_DEFINITIONS,
    )
    generate_parameter_sets(
        ARCHITECTURE,
        parameter_set_dir,
        COMPOSITION,
        includes=CORE_DEFINITIONS,
    )
    synced = sync_sysml_from_ssd(
        ARCHITECTURE,
        ssd_path,
        COMPOSITION,
        output_architecture_dir=sync_dir,
        includes=CORE_DEFINITIONS,
    )

    print(ssd_path)
    print(parameter_set_dir)
    for path in synced:
        print(path)


if __name__ == "__main__":
    main()
