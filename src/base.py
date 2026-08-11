"""Split ventilated base modules."""

import cadquery as cq

import config as C
from .common import PrintablePart, box_at, cylinder_at, slot_x, slot_y, trapezoid_tab_y


def _capture_rails(length: float) -> cq.Workplane:
    rail_y = C.WALL + C.FIT_CLEARANCE
    rail_len = max(length - 2.0 * rail_y, 1.0)
    left_x = C.WALL + C.FIT_CLEARANCE
    right_x = C.NAS_EXTERNAL_W - C.WALL - C.FIT_CLEARANCE - C.CAPTURE_RAIL_T
    rails = box_at(left_x, rail_y, C.WALL, C.CAPTURE_RAIL_T, rail_len, C.CAPTURE_RAIL_H)
    return rails.union(
        box_at(right_x, rail_y, C.WALL, C.CAPTURE_RAIL_T, rail_len, C.CAPTURE_RAIL_H)
    )


def _vent_base(shape: cq.Workplane, global_y0: float, length: float) -> cq.Workplane:
    center_xs = (C.NAS_EXTERNAL_W * 0.36, C.NAS_EXTERNAL_W * 0.50, C.NAS_EXTERNAL_W * 0.64)
    pitch = C.VENT_SLOT_L + C.VENT_WEB
    y = C.HDD_Y + C.VENT_SLOT_L / 2.0
    global_y1 = global_y0 + length
    while y < C.HDD_REAR_Y:
        if global_y0 + C.VENT_SLOT_L / 2.0 < y < global_y1 - C.VENT_SLOT_L / 2.0:
            local_y = y - global_y0
            for x in center_xs:
                shape = shape.cut(slot_y(C.VENT_SLOT_L, C.VENT_SLOT_W, C.WALL + 0.2, x, local_y, -0.1))
        y += pitch
    return shape


def _mounting_holes(shape: cq.Workplane, global_y0: float, length: float) -> cq.Workplane:
    global_y1 = global_y0 + length
    mount_points = [
        (C.FOOT_INSET, C.FOOT_INSET),
        (C.NAS_EXTERNAL_W - C.FOOT_INSET, C.FOOT_INSET),
        (C.FOOT_INSET, C.NAS_EXTERNAL_D - C.FOOT_INSET),
        (C.NAS_EXTERNAL_W - C.FOOT_INSET, C.NAS_EXTERNAL_D - C.FOOT_INSET),
        (C.CABLE_CLIP_X_LEFT, C.CABLE_CLIP_Y + C.CABLE_CLIP_WIDTH / 2.0),
        (C.CABLE_CLIP_X_RIGHT, C.CABLE_CLIP_Y + C.CABLE_CLIP_WIDTH / 2.0),
    ]
    for x, global_y in mount_points:
        if not (global_y0 <= global_y <= global_y1):
            continue
        shape = shape.cut(
            cylinder_at(
                C.M3_CLEARANCE_D / 2.0,
                C.WALL + 0.2,
                (x, global_y - global_y0, -0.1),
                (0.0, 0.0, 1.0),
            )
        )
    return shape


def _hdd_service_pedestal(
    shape: cq.Workplane,
    global_y0: float,
    post_global_y: float,
    ledge_global_y: float,
) -> cq.Workplane:
    """Add a fixed right-side post and two tray-support ledges."""
    local_y = post_global_y - global_y0
    ledge_local_y = ledge_global_y - global_y0
    post_h = C.HDD_UPPER_Z - C.TRAY_THICKNESS - C.WALL
    post = box_at(
        C.HDD_SERVICE_POST_X,
        local_y,
        C.WALL,
        C.HDD_SERVICE_POST_W,
        C.HDD_SERVICE_POST_DEPTH,
        post_h,
    )
    shape = shape.union(post)
    for drive_z in (C.HDD_LOWER_Z, C.HDD_UPPER_Z):
        tray_bottom = drive_z - C.TRAY_THICKNESS
        shape = shape.union(
            box_at(
                C.HDD_SERVICE_LEDGE_X,
                ledge_local_y,
                tray_bottom - C.HDD_SERVICE_LEDGE_T,
                C.HDD_SERVICE_LEDGE_W,
                C.TRAY_END_STOP_T,
                C.HDD_SERVICE_LEDGE_T,
            )
        )
    return shape


def make_base_front() -> cq.Workplane:
    length = C.MID_FRAME_FRONT_Y
    shape = box_at(0.0, 0.0, 0.0, C.NAS_EXTERNAL_W, length, C.WALL).union(_capture_rails(length))
    shape = _vent_base(shape, 0.0, length)
    shape = _mounting_holes(shape, 0.0, length)
    shape = _hdd_service_pedestal(shape, 0.0, C.HDD_SERVICE_FRONT_Y, C.TRAY_Y)
    key_xs = [C.NAS_EXTERNAL_W * ratio for ratio in C.BASE_JOINT_X_FRACTIONS]
    for x in key_xs:
        shape = shape.union(
            trapezoid_tab_y(x, length, C.JOINT_ENGAGEMENT, C.JOINT_THROAT, C.JOINT_HEAD, C.WALL)
        )
    return shape


def make_base_rear() -> cq.Workplane:
    length = C.NAS_EXTERNAL_D - C.MID_FRAME_REAR_Y
    shape = box_at(0.0, 0.0, 0.0, C.NAS_EXTERNAL_W, length, C.WALL).union(_capture_rails(length))
    shape = _vent_base(shape, C.MID_FRAME_REAR_Y, length)
    shape = _mounting_holes(shape, C.MID_FRAME_REAR_Y, length)
    shape = _hdd_service_pedestal(
        shape,
        C.MID_FRAME_REAR_Y,
        C.HDD_SERVICE_REAR_Y,
        C.HDD_SERVICE_REAR_Y,
    )
    key_xs = [C.NAS_EXTERNAL_W * ratio for ratio in C.BASE_JOINT_X_FRACTIONS]
    for x in key_xs:
        tab = trapezoid_tab_y(
            x,
            -C.JOINT_ENGAGEMENT,
            C.JOINT_ENGAGEMENT,
            C.JOINT_HEAD,
            C.JOINT_THROAT,
            C.WALL,
        )
        shape = shape.union(tab)
    # Cable-tie slots in the chamber floor.
    for y_fraction in C.BASE_CABLE_TIE_Y_FRACTIONS:
        y = length * y_fraction
        for x in (C.BASE_CABLE_TIE_X_INSET, C.NAS_EXTERNAL_W - C.BASE_CABLE_TIE_X_INSET):
            shape = shape.cut(
                slot_x(
                    C.BASE_CABLE_TIE_SLOT_L,
                    C.BASE_CABLE_TIE_SLOT_W,
                    C.WALL + 0.2,
                    x,
                    y,
                    -0.1,
                )
            )
    return shape


def make_foot() -> cq.Workplane:
    foot = cylinder_at(C.FOOT_RADIUS, C.FOOT_H, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    hole = cylinder_at(C.M3_CLEARANCE_D / 2.0, C.FOOT_H + 0.2, (0.0, 0.0, -0.1), (0.0, 0.0, 1.0))
    return foot.cut(hole)


def parts() -> list[PrintablePart]:
    return [
        PrintablePart("base_front", make_base_front(), notes="Front base module; keyed into mid-frame."),
        PrintablePart("base_rear", make_base_rear(), notes="Rear base/cable chamber module."),
        PrintablePart("foot", make_foot(), quantity=4, notes="Print four, preferably TPU; raises bottom vents 6 mm."),
    ]
