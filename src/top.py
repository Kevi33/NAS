"""Two-piece top with a removable Pi service lid."""

import cadquery as cq

import config as C
from .common import PrintablePart, box_at, slot_x, slot_y, trapezoid_tab_y


def _capture_rails(length: float) -> cq.Workplane:
    rail_y = C.WALL + C.FIT_CLEARANCE
    rail_len = max(length - 2.0 * rail_y, 1.0)
    left_x = C.WALL + C.FIT_CLEARANCE
    right_x = C.NAS_EXTERNAL_W - C.WALL - C.FIT_CLEARANCE - C.CAPTURE_RAIL_T
    rails = box_at(left_x, rail_y, C.WALL, C.CAPTURE_RAIL_T, rail_len, C.CAPTURE_RAIL_H)
    return rails.union(
        box_at(right_x, rail_y, C.WALL, C.CAPTURE_RAIL_T, rail_len, C.CAPTURE_RAIL_H)
    )


def _vent(shape: cq.Workplane, global_y0: float, length: float) -> cq.Workplane:
    pitch = C.VENT_SLOT_L + C.VENT_WEB
    y = global_y0 + 18.0
    while y < global_y0 + length - 18.0:
        for x in (C.NAS_EXTERNAL_W * 0.38, C.NAS_EXTERNAL_W * 0.50, C.NAS_EXTERNAL_W * 0.62):
            shape = shape.cut(slot_y(C.VENT_SLOT_L, C.VENT_SLOT_W, C.WALL + 0.2, x, y - global_y0, -0.1))
        y += pitch
    return shape


def make_service_lid() -> cq.Workplane:
    length = C.TOP_SERVICE_REAR_Y
    shape = box_at(0.0, 0.0, 0.0, C.NAS_EXTERNAL_W, length, C.WALL).union(_capture_rails(length))
    shape = _vent(shape, 0.0, length)
    for ratio in C.TOP_JOINT_X_FRACTIONS:
        x = C.NAS_EXTERNAL_W * ratio
        shape = shape.union(
            trapezoid_tab_y(x, length, C.JOINT_ENGAGEMENT, C.JOINT_THROAT, C.JOINT_HEAD, C.WALL)
        )
    # Finger relief at the front edge.
    finger = slot_x(
        C.TOP_FINGER_RELIEF_L,
        C.TOP_FINGER_RELIEF_W,
        C.WALL + 0.2,
        C.NAS_EXTERNAL_W / 2.0,
        C.TOP_FINGER_RELIEF_Y,
        -0.1,
    )
    return shape.cut(finger)


def make_top_rear() -> cq.Workplane:
    length = C.NAS_EXTERNAL_D - C.TOP_REAR_FRONT_Y
    shape = box_at(0.0, 0.0, 0.0, C.NAS_EXTERNAL_W, length, C.WALL).union(_capture_rails(length))
    shape = _vent(shape, C.TOP_REAR_FRONT_Y, length)
    for ratio in C.TOP_JOINT_X_FRACTIONS:
        x = C.NAS_EXTERNAL_W * ratio
        tab = trapezoid_tab_y(
            x,
            -C.JOINT_ENGAGEMENT,
            C.JOINT_ENGAGEMENT,
            C.JOINT_HEAD,
            C.JOINT_THROAT,
            C.WALL,
        )
        shape = shape.union(tab)
    return shape


def parts() -> list[PrintablePart]:
    return [
        PrintablePart(
            "top_service_lid",
            make_service_lid(),
            notes="Lift-off Pi service lid; front half of top shell.",
        ),
        PrintablePart("top_rear", make_top_rear(), notes="Rear top/cable-chamber cover."),
    ]
