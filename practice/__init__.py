# practice/
#
# Human-facing exercises, as opposed to the sensors, which are
# machine-facing. Everything here is meant to be run BY a person ON an
# article, with the sensor suite used only as a second opinion after
# the person has committed to a read.
#
# Kept out of schema_contract deliberately: this is pedagogy, not a
# published interface, and it should be free to change without a
# SCHEMA_VERSION bump. Its stability is documented by __all__.

from .article_check import (
    LayerQuestion,
    OpenQuestion,
    LAYER_QUESTIONS,
    OPEN_QUESTIONS,
    RATING_SCALE,
    HumanRead,
    MachineRead,
    Divergence,
    tier_rank,
    machine_read,
    compare,
    format_report,
    blank_worksheet,
)

__all__ = [
    "LayerQuestion",
    "OpenQuestion",
    "LAYER_QUESTIONS",
    "OPEN_QUESTIONS",
    "RATING_SCALE",
    "HumanRead",
    "MachineRead",
    "Divergence",
    "tier_rank",
    "machine_read",
    "compare",
    "format_report",
    "blank_worksheet",
]
