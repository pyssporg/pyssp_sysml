"""Small value rules shared by the emitters.

``fixed_count`` and ``format_value`` are the SSP wire rules, not model data.
Keeping them here lets the emitters stay free of the SysML parser while the
error text still names the port or parameter that failed.
"""

from __future__ import annotations


def fixed_count(multiplicity: str, name: str) -> int:
    """Number of elements for a fixed multiplicity, or error when variable."""
    if multiplicity == "*" or multiplicity.endswith("..*"):
        raise ValueError(
            f"Parameter '{name}' has unbounded multiplicity '[{multiplicity}]'; "
            "SSP parameters need a fixed length"
        )
    if ".." in multiplicity:
        lower, upper = multiplicity.split("..", 1)
        if lower != upper:
            raise ValueError(
                f"Parameter '{name}' has variable multiplicity '[{multiplicity}]'; "
                "SSP parameters need a fixed length"
            )
        multiplicity = lower
    try:
        return int(multiplicity)
    except ValueError:
        raise ValueError(
            f"Parameter '{name}' has unsupported multiplicity '[{multiplicity}]'"
        ) from None


def format_value(tag: str, literal):
    if literal is None:
        return ""
    if tag == "Real":
        number = float(literal)
        if number.is_integer():
            return f"{number:g}"
        # Shortest representation that round-trips to the same float: a value
        # authored at full precision must reach the artifact unchanged.
        return repr(number)
    if tag == "Integer":
        return str(int(literal))
    if tag == "Boolean":
        return "true" if bool(literal) else "false"
    if tag == "String":
        return str(literal)
    raise Exception("[format_value] Unknown tag")
