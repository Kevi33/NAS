"""Removable right shell modules used for HDD service."""

from .common import PrintablePart
from .side_panel_common import make_side_front, make_side_rear


def parts() -> list[PrintablePart]:
    return [
        PrintablePart(
            "right_side_front",
            make_side_front(),
            notes="Remove with right mid-frame spine for HDD service.",
        ),
        PrintablePart(
            "right_side_rear",
            make_side_rear(),
            notes="Remove with right mid-frame spine for HDD service.",
        ),
    ]

