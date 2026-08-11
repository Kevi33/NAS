"""Left shell modules."""

from .common import PrintablePart
from .side_panel_common import make_side_front, make_side_rear


def parts() -> list[PrintablePart]:
    return [
        PrintablePart("left_side_front", make_side_front(), notes="Front left shell module."),
        PrintablePart("left_side_rear", make_side_rear(), notes="Rear left shell module."),
    ]

