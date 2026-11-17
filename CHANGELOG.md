# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `pyssp validate` reports dialect problems, FMU interface names, and an
  optional `fmu_meta.implementation` mismatch without writing an artifact. Its
  `--base-index` option checks parameter arrays against the indices the
  generator will emit.
- `pyssp_sysml2.check_fmu_interfaces` compares every leaf component's expected
  SSD connector names with its FMU's `variable_names`, taking the same
  `base_index` as the generator.

## [0.5.0] - 2026-11-09

### Added

- Accept definition roots and merge the core definitions when loading a model.

### Changed

- Handle parameter `base_index` across the SSP artifacts and the CLI.
- Remove the vendored `experimental_pyssp_standard` submodule; consume it as a
  release wheel.
- Add a `CHANGELOG.md`, split `requirements-dev.txt`, and refresh the docs.

