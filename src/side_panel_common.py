"""Shared split-side-panel geometry."""

import cadquery as cq

import config as C
from .common import box_at, cylinder_at, slot_x, trapezoid_tab_x


PANEL_H = C.NAS_BODY_H - 2.0 * C.WALL


def _edge_tongue_grooves(shape: cq.Workplane, length: float, front: bool) -> cq.Workplane:
    edge_x = 0.0 if front else length - C.WALL
    groove_x = edge_x - C.FIT_CLEARANCE if front else edge_x - C.FIT_CLEARANCE
    groove_len = C.WALL + 2.0 * C.FIT_CLEARANCE
    usable = PANEL_H - 2.0 * C.PANEL_TONGUE_SEGMENT_H
    step = usable / max(C.PANEL_TONGUE_COUNT - 1, 1)
    for index in range(C.PANEL_TONGUE_COUNT):
        cy = C.PANEL_TONGUE_SEGMENT_H / 2.0 + index * step
        groove = box_at(
            groove_x,
            cy - C.PANEL_TONGUE_SEGMENT_H / 2.0 - C.FIT_CLEARANCE,
            C.WALL - C.PANEL_EDGE_TONGUE - C.FIT_CLEARANCE,
            groove_len,
            C.PANEL_TONGUE_SEGMENT_H + 2.0 * C.FIT_CLEARANCE,
            C.PANEL_EDGE_TONGUE + 2.0 * C.FIT_CLEARANCE,
        )
        shape = shape.cut(groove)
    return shape


def _vents(shape: cq.Workplane, global_x0: float, length: float) -> cq.Workplane:
    global_x1 = global_x0 + length
    global_y_positions = (
        C.HDD_LOWER_Z + C.HDD_H / 2.0 - C.WALL,
        C.HDD_UPPER_Z + C.HDD_H / 2.0 - C.WALL,
        C.PI_Z + C.PI_CASE_H / 2.0 - C.WALL,
    )
    x = max(global_x0 + 22.0, C.HDD_Y + 22.0)
    while x < min(global_x1 - 22.0, C.HDD_REAR_Y - 8.0):
        local_x = x - global_x0
        for cy in global_y_positions:
            shape = shape.cut(slot_x(C.VENT_SLOT_L, C.VENT_SLOT_W, C.WALL + 0.2, local_x, cy, -0.1))
        x += C.VENT_SLOT_L + C.VENT_WEB
    return shape


def _hardware_ledges(shape: cq.Workplane, global_y0: float, length: float) -> cq.Workplane:
    global_y1 = global_y0 + length
    ledge_z0 = C.WALL - 0.3

    # Two keyed support shelves per HDD level. Right panels are mirrored at
    # placement time, so the same local geometry supports both tray rails.
    hdd_reach = C.TRAY_OUTER_X + C.HDD_TRAY_SUPPORT_OVERLAP
    for support_y in (C.HDD_TRAY_SUPPORT_FRONT_Y, C.HDD_TRAY_SUPPORT_REAR_Y):
        if not (global_y0 <= support_y <= global_y1):
            continue
        local_x = support_y - global_y0 - C.HDD_TRAY_SUPPORT_DEPTH / 2.0
        for drive_z in (C.HDD_LOWER_Z, C.HDD_UPPER_Z):
            tray_bottom = drive_z - C.TRAY_THICKNESS
            local_y = tray_bottom - C.WALL - C.HDD_TRAY_SUPPORT_LEDGE_T
            ledge = box_at(
                local_x,
                local_y,
                ledge_z0,
                C.HDD_TRAY_SUPPORT_DEPTH,
                C.HDD_TRAY_SUPPORT_LEDGE_T,
                hdd_reach - ledge_z0,
            )
            shape = shape.union(ledge)
            locator = box_at(
                support_y - global_y0 - C.HDD_TRAY_LOCATOR_L / 2.0,
                tray_bottom - C.WALL - 0.3,
                C.TRAY_OUTER_X + 0.8,
                C.HDD_TRAY_LOCATOR_L,
                C.HDD_TRAY_LOCATOR_H + 0.3,
                C.HDD_TRAY_LOCATOR_W,
            )
            shape = shape.union(locator)

    # Pi tray lifts vertically from four keyed ledges, all in the front module.
    pi_reach = C.PI_TRAY_X + C.PI_LEDGE_OVERLAP
    for support_y in (C.PI_LEDGE_FRONT_Y, C.PI_LEDGE_REAR_Y):
        if not (global_y0 <= support_y <= global_y1):
            continue
        local_x = support_y - global_y0 - C.PI_LEDGE_DEPTH / 2.0
        local_y = C.PI_TRAY_Z - C.WALL - C.PI_LEDGE_T
        shape = shape.union(
            box_at(
                local_x,
                local_y,
                ledge_z0,
                C.PI_LEDGE_DEPTH,
                C.PI_LEDGE_T,
                pi_reach - ledge_z0,
            )
        )
        shape = shape.union(
            box_at(
                support_y - global_y0 - C.PI_LOCATOR_L / 2.0,
                C.PI_TRAY_Z - C.WALL - 0.3,
                C.PI_TRAY_X + 0.8,
                C.PI_LOCATOR_L,
                C.PI_LOCATOR_H + 0.3,
                C.PI_LOCATOR_W,
            )
        )
    return shape


def _hub_mount_holes(shape: cq.Workplane, global_y0: float, length: float) -> cq.Workplane:
    mount_y = C.USB_HUB_Y - C.USB_HUB_CLEARANCE - C.HUB_MOUNT_EDGE
    hole_global_y = mount_y + C.HUB_MOUNT_W / 2.0
    if not (global_y0 <= hole_global_y <= global_y0 + length):
        return shape
    mount_z = C.USB_HUB_Z - C.USB_HUB_CLEARANCE - C.HUB_MOUNT_EDGE
    for z in (
        mount_z + C.HUB_MOUNT_SLOT_INSET,
        mount_z + C.HUB_MOUNT_L - C.HUB_MOUNT_SLOT_INSET,
    ):
        hole = cylinder_at(
            C.M3_CLEARANCE_D / 2.0,
            C.WALL + 0.2,
            (hole_global_y - global_y0, z - C.WALL, -0.1),
            (0.0, 0.0, 1.0),
        )
        shape = shape.cut(hole)
    return shape


def make_side_front() -> cq.Workplane:
    length = C.MID_FRAME_FRONT_Y
    shape = box_at(0.0, 0.0, 0.0, length, PANEL_H, C.WALL)
    shape = _edge_tongue_grooves(shape, length, True)
    shape = _vents(shape, 0.0, length)
    shape = _hardware_ledges(shape, 0.0, length)
    shape = _hub_mount_holes(shape, 0.0, length)
    for ratio in C.SIDE_JOINT_Z_FRACTIONS:
        cy = PANEL_H * ratio
        shape = shape.union(
            trapezoid_tab_x(cy, length, C.JOINT_ENGAGEMENT, C.JOINT_THROAT, C.JOINT_HEAD, C.WALL)
        )
    return shape


def make_side_rear() -> cq.Workplane:
    length = C.NAS_EXTERNAL_D - C.MID_FRAME_REAR_Y
    shape = box_at(0.0, 0.0, 0.0, length, PANEL_H, C.WALL)
    shape = _edge_tongue_grooves(shape, length, False)
    shape = _vents(shape, C.MID_FRAME_REAR_Y, length)
    shape = _hardware_ledges(shape, C.MID_FRAME_REAR_Y, length)
    shape = _hub_mount_holes(shape, C.MID_FRAME_REAR_Y, length)
    for ratio in C.SIDE_JOINT_Z_FRACTIONS:
        cy = PANEL_H * ratio
        tab = trapezoid_tab_x(
            cy,
            -C.JOINT_ENGAGEMENT,
            C.JOINT_ENGAGEMENT,
            C.JOINT_HEAD,
            C.JOINT_THROAT,
            C.WALL,
        )
        shape = shape.union(tab)
    return shape
