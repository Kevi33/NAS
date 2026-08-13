"""Left shell modules."""

from .common import PrintablePart
from .side_panel_common import make_side_front, make_side_rear


def parts() -> list[PrintablePart]:
    return [
        PrintablePart(
            "left_side_front",
            make_side_front(right_hand=False),
            notes="Physical left-hand front shell module.",
        ),
        PrintablePart(
            "left_side_rear",
            make_side_rear(right_hand=False),
            notes="Physical left-hand rear shell module; no USB hub carrier holes.",
        ),
    ]
