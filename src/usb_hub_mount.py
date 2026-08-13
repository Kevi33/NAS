"""Tolerant rail-style USB hub carrier."""

import cadquery as cq

import config as C
from .common import PrintablePart, box_at, slot_y


def make_usb_hub_mount() -> cq.Workplane:
    # Local print axes map to assembly Y, Z, X respectively.
    shape = box_at(0.0, 0.0, 0.0, C.HUB_MOUNT_W, C.HUB_MOUNT_L, C.HUB_MOUNT_BACK_T)
    # Remove the centre to create two compliant rails and short end bridges.
    window = box_at(
        C.HUB_MOUNT_EDGE,
        C.HUB_MOUNT_EDGE,
        -0.1,
        C.HUB_MOUNT_W - 2.0 * C.HUB_MOUNT_EDGE,
        C.HUB_MOUNT_L - 2.0 * C.HUB_MOUNT_EDGE,
        C.HUB_MOUNT_BACK_T + 0.2,
    )
    shape = shape.cut(window)
    # A central bridge keeps the two compliant rails one connected print.
    bridge_y = C.HUB_MOUNT_L / 2.0 - C.HUB_MOUNT_CENTER_BRIDGE_W / 2.0
    shape = shape.union(
        box_at(
            0.0,
            bridge_y,
            0.0,
            C.HUB_MOUNT_W,
            C.HUB_MOUNT_CENTER_BRIDGE_W,
            C.HUB_MOUNT_BACK_T,
        )
    )
    # Full-width back bridges give the two M3 adjustment slots real bearing
    # material. Without these, both slots lie entirely inside the large center
    # window and the carrier merely touches the side wall without being
    # fastenable.
    for fastener_y in (C.HUB_MOUNT_SLOT_INSET, C.HUB_MOUNT_L - C.HUB_MOUNT_SLOT_INSET):
        shape = shape.union(
            box_at(
                0.0,
                fastener_y - C.HUB_MOUNT_FASTENER_BRIDGE_W / 2.0,
                0.0,
                C.HUB_MOUNT_W,
                C.HUB_MOUNT_FASTENER_BRIDGE_W,
                C.HUB_MOUNT_BACK_T,
            )
        )
    # Edge lips wrap only the hub corners; all four port faces remain clear.
    for x in (0.0, C.HUB_MOUNT_W - C.HUB_MOUNT_EDGE):
        for y in (0.0, C.HUB_MOUNT_L - C.HUB_MOUNT_END_LIP_L):
            shape = shape.union(
                box_at(
                    x,
                    y,
                    0.0,
                    C.HUB_MOUNT_EDGE,
                    C.HUB_MOUNT_END_LIP_L,
                    C.HUB_MOUNT_LIP + C.HUB_MOUNT_BACK_T,
                )
            )
    # A full-width lower flange supports the vertical hub under gravity. The
    # configured 1.5 mm envelope seats on its top face without interference.
    shape = shape.union(
        box_at(
            C.HUB_MOUNT_EDGE,
            0.0,
            0.0,
            C.HUB_MOUNT_W - 2.0 * C.HUB_MOUNT_EDGE,
            C.HUB_MOUNT_BOTTOM_STOP_H,
            C.HUB_MOUNT_BOTTOM_STOP_REACH,
        )
    )
    # Two Velcro/printed-strap stations retain the hub against inward motion.
    for fraction in C.HUB_MOUNT_STRAP_Y_FRACTIONS:
        strap_y = C.HUB_MOUNT_L * fraction
        for strap_x in (C.HUB_MOUNT_EDGE / 2.0, C.HUB_MOUNT_W - C.HUB_MOUNT_EDGE / 2.0):
            shape = shape.cut(
                slot_y(
                    C.HUB_MOUNT_STRAP_SLOT_L,
                    C.HUB_MOUNT_STRAP_SLOT_W,
                    C.HUB_MOUNT_BACK_T + 0.2,
                    strap_x,
                    strap_y,
                    -0.1,
                )
            )
    # Long mounting slots permit vertical adjustment after measuring the hub.
    for y in (C.HUB_MOUNT_SLOT_INSET, C.HUB_MOUNT_L - C.HUB_MOUNT_SLOT_INSET):
        shape = shape.cut(
            slot_y(
                12.0,
                C.M3_CLEARANCE_D,
                C.HUB_MOUNT_BACK_T + 0.2,
                C.HUB_MOUNT_W / 2.0,
                y,
                -0.1,
            )
        )
    return shape


def parts() -> list[PrintablePart]:
    return [
        PrintablePart(
            "usb_hub_mount",
            make_usb_hub_mount(),
            notes="Mirrorable open rail carrier with 1.5 mm nominal clearance and slotted adjustment.",
        ),
    ]
