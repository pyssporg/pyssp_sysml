"""SSP-family composition wrappers.

Each module owns one artifact: SSD, SSV, SSM, SSP, or the analysis descriptor.
Its ``generate_*`` function loads, selects, and projects the SysML architecture,
then calls the parser-free emitter in :mod:`pyssp_sysml2.emit`. The ``build_*``
seams accept projection records; ``build_ssd``'s legacy
``(ssd, part_def, architecture)`` form projects on the fly for callers that
already hold a loaded architecture.
"""
