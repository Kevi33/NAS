"""Open Raspberry Pi case tray with keyed integrated-side supports."""

import cadquery as cq

import config as C
from .common import PrintablePart, box_at, slot_y


def make_pi_tray() -> cq.Workplane:
    # Open perimeter plus two narrow support rails; no solid shelf below the Pi case.
    frame_w = C.PI_TRAY_FRAME_W
    shape = box_at(0.0, 0.0, 0.0, C.PI_TRAY_W, frame_w, C.PI_TRAY_T)
    shape = shape.union(box_at(0.0, C.PI_TRAY_L - frame_w, 0.0, C.PI_TRAY_W, frame_w, C.PI_TRAY_T))
    shape = shape.union(box_at(0.0, 0.0, 0.0, frame_w, C.PI_TRAY_L, C.PI_TRAY_T))
    shape = shape.union(box_at(C.PI_TRAY_W - frame_w, 0.0, 0.0, frame_w, C.PI_TRAY_L, C.PI_TRAY_T))

    pi_local_x = (C.PI_TRAY_W - C.PI_CASE_W) / 2.0
    rail_w = C.PI_TRAY_RAIL_W
    for x in (pi_local_x, pi_local_x + C.PI_CASE_W - rail_w):
        shape = shape.union(
            box_at(
                x,
                frame_w - C.PI_TRAY_RAIL_END_OVERLAP,
                0.0,
                rail_w,
                C.PI_TRAY_L - 2.0 * frame_w + 2.0 * C.PI_TRAY_RAIL_END_OVERLAP,
                C.PI_TRAY_T,
            )
        )

    # Short guides provide configured clearance while leaving ports exposed.
    left_guide_x = pi_local_x - C.PI_CASE_CLEARANCE - C.PI_TRAY_GUIDE_T
    right_guide_x = pi_local_x + C.PI_CASE_W + C.PI_CASE_CLEARANCE
    shape = shape.union(
        box_at(
            left_guide_x,
            C.PI_TRAY_GUIDE_Y,
            C.PI_TRAY_T - C.PI_TRAY_GUIDE_EMBED,
            C.PI_TRAY_GUIDE_T,
            C.PI_TRAY_GUIDE_L,
            C.PI_TRAY_GUIDE_H,
        )
    )
    shape = shape.union(
        box_at(
            right_guide_x,
            C.PI_TRAY_GUIDE_Y,
            C.PI_TRAY_T - C.PI_TRAY_GUIDE_EMBED,
            C.PI_TRAY_GUIDE_T,
            C.PI_TRAY_GUIDE_L,
            C.PI_TRAY_GUIDE_H,
        )
    )
    # Floor-level bridges fuse each guide to its nearest load rail while ending
    # exactly at the Pi body envelope; support contact remains zero-volume.
    shape = shape.union(
        box_at(
            left_guide_x,
            C.PI_TRAY_GUIDE_Y,
            0.0,
            pi_local_x - left_guide_x,
            C.PI_TRAY_GUIDE_L,
            C.PI_TRAY_T,
        )
    )
    shape = shape.union(
        box_at(
            pi_local_x + C.PI_CASE_W,
            C.PI_TRAY_GUIDE_Y,
            0.0,
            right_guide_x + C.PI_TRAY_GUIDE_T - (pi_local_x + C.PI_CASE_W),
            C.PI_TRAY_GUIDE_L,
            C.PI_TRAY_T,
        )
    )
    # Adjustable strap slots; the strap itself can be Velcro or a printed band.
    for x in (
        pi_local_x - C.PI_TRAY_STRAP_X_OFFSET,
        pi_local_x + C.PI_CASE_W + C.PI_TRAY_STRAP_X_OFFSET,
    ):
        shape = shape.cut(
            slot_y(
                C.PI_TRAY_STRAP_SLOT_L,
                C.PI_TRAY_STRAP_SLOT_W,
                C.PI_TRAY_T + 0.2,
                x,
                C.PI_TRAY_L / 2.0,
                -0.1,
            )
        )
    # Four shallow underside pockets register on the integrated side-panel ledges.
    socket_w = C.PI_LOCATOR_W + 2.0 * C.FIT_CLEARANCE
    socket_l = C.PI_LOCATOR_L + 2.0 * C.FIT_CLEARANCE
    socket_h = C.PI_LOCATOR_H + C.JOINT_EXTRA_DEPTH
    for global_y in (C.PI_LEDGE_FRONT_Y, C.PI_LEDGE_REAR_Y):
        local_y = global_y - C.PI_TRAY_Y
        for index, cx in enumerate(
            (C.PI_LOCATOR_CENTER_INSET, C.PI_TRAY_W - C.PI_LOCATOR_CENTER_INSET)
        ):
            x0 = cx - socket_w / 2.0
            # The closed left pocket retains the tray; the right notch opens
            # toward +X so the service-side panel can withdraw laterally.
            width = socket_w if index == 0 else C.PI_TRAY_W - x0 + 0.1
            shape = shape.cut(
                box_at(
                    x0,
                    local_y - socket_l / 2.0,
                    -0.1,
                    width,
                    socket_l,
                    socket_h + 0.1,
                )
            )
    return shape


def parts() -> list[PrintablePart]:
    return [
        PrintablePart("pi_tray", make_pi_tray(), notes="Open lift-out tray with strap slots."),
    ]
