"""Skeletal, split HDD cradle and removable side keeper."""

import cadquery as cq

import config as C
from .common import PrintablePart, box_at, trapezoid_tab_y


def _rails(length: float) -> cq.Workplane:
    left = box_at(0.0, 0.0, 0.0, C.TRAY_RAIL_W, length, C.TRAY_THICKNESS)
    right = box_at(C.TRAY_OUTER_W - C.TRAY_RAIL_W, 0.0, 0.0, C.TRAY_RAIL_W, length, C.TRAY_THICKNESS)
    return left.union(right)


def _locator_sockets(shape: cq.Workplane, support_local_y: float) -> cq.Workplane:
    socket_w = C.HDD_TRAY_LOCATOR_W + 2.0 * C.FIT_CLEARANCE
    socket_l = C.HDD_TRAY_LOCATOR_L + 2.0 * C.FIT_CLEARANCE
    socket_h = C.HDD_TRAY_LOCATOR_H + C.JOINT_EXTRA_DEPTH
    for index, cx in enumerate(
        (C.HDD_TRAY_LOCATOR_CENTER_INSET, C.TRAY_OUTER_W - C.HDD_TRAY_LOCATOR_CENTER_INSET)
    ):
        x0 = cx - socket_w / 2.0
        # The right shell module withdraws toward +X for HDD service. Its
        # locator therefore uses an outward-open notch; the closed left socket
        # retains the tray after that module and its ledge are removed.
        width = socket_w if index == 0 else C.TRAY_OUTER_W - x0 + 0.1
        shape = shape.cut(
            box_at(
                x0,
                support_local_y - socket_l / 2.0,
                -0.1,
                width,
                socket_l,
                socket_h + 0.1,
            )
        )
    return shape


def make_tray_front() -> cq.Workplane:
    shape = _rails(C.TRAY_HALF_L)
    shape = shape.union(box_at(0.0, 0.0, 0.0, C.TRAY_OUTER_W, C.TRAY_END_STOP_T, C.TRAY_THICKNESS))
    # Front stops contact only the lower corner zones and leave the vented centre open.
    shape = shape.union(box_at(0.0, 0.0, C.TRAY_THICKNESS, C.TRAY_RAIL_W, C.TRAY_END_STOP_T, C.TRAY_GUIDE_H))
    shape = shape.union(
        box_at(
            C.TRAY_OUTER_W - C.TRAY_RAIL_W,
            0.0,
            C.TRAY_THICKNESS,
            C.TRAY_RAIL_W,
            C.TRAY_END_STOP_T,
            C.TRAY_GUIDE_H,
        )
    )
    # Left lateral guide.  The right side remains open for service.
    shape = shape.union(box_at(0.0, C.TRAY_END_STOP_T, C.TRAY_THICKNESS, C.TRAY_GUIDE_T, C.TRAY_HALF_L - C.TRAY_END_STOP_T, C.TRAY_GUIDE_H))
    for x in (C.TRAY_RAIL_W / 2.0, C.TRAY_OUTER_W - C.TRAY_RAIL_W / 2.0):
        shape = shape.union(
            trapezoid_tab_y(
                x,
                C.TRAY_HALF_L,
                C.TRAY_JOIN_LENGTH,
                C.TRAY_JOIN_THROAT,
                C.TRAY_JOIN_HEAD,
                C.TRAY_THICKNESS,
            )
        )
    # Replaceable keeper socket in the right rail.
    keeper_socket = box_at(
        C.TRAY_OUTER_W - C.TRAY_RAIL_W - 0.1,
        C.HDD_KEEPER_SLOT_Y - 0.1,
        -0.1,
        C.TRAY_RAIL_W + 0.2,
        C.HDD_KEEPER_SLOT_L + 0.2,
        C.TRAY_THICKNESS + 0.2,
    )
    shape = shape.cut(keeper_socket)
    # Inboard bypass rib preserves a single connected cradle around the socket.
    right_rail_x = C.TRAY_OUTER_W - C.TRAY_RAIL_W
    shape = shape.union(
        box_at(
            right_rail_x - C.HDD_KEEPER_BYPASS_INSET,
            C.HDD_KEEPER_SLOT_Y - C.HDD_KEEPER_BYPASS_END_OVERLAP,
            0.0,
            C.HDD_KEEPER_BYPASS_W,
            C.HDD_KEEPER_SLOT_L + 2.0 * C.HDD_KEEPER_BYPASS_END_OVERLAP,
            C.TRAY_THICKNESS,
        )
    )
    front_support_local_y = C.HDD_TRAY_SUPPORT_FRONT_Y - C.TRAY_Y
    shape = _locator_sockets(shape, front_support_local_y)
    return shape


def make_tray_rear() -> cq.Workplane:
    shape = _rails(C.TRAY_HALF_L)
    shape = shape.union(
        box_at(
            0.0,
            C.TRAY_HALF_L - C.TRAY_END_STOP_T,
            0.0,
            C.TRAY_OUTER_W,
            C.TRAY_END_STOP_T,
            C.TRAY_THICKNESS,
        )
    )
    shape = shape.union(
        box_at(0.0, C.TRAY_HALF_L - C.TRAY_END_STOP_T, C.TRAY_THICKNESS, C.TRAY_RAIL_W, C.TRAY_END_STOP_T, C.TRAY_GUIDE_H)
    )
    # Deliberately omit a right-rear stop: the provisional power switch and
    # connector finger zone occupy this corner.
    shape = shape.union(box_at(0.0, 0.0, C.TRAY_THICKNESS, C.TRAY_GUIDE_T, C.TRAY_HALF_L - C.TRAY_END_STOP_T, C.TRAY_GUIDE_H))
    for x in (C.TRAY_RAIL_W / 2.0, C.TRAY_OUTER_W - C.TRAY_RAIL_W / 2.0):
        pocket = trapezoid_tab_y(
            x,
            -C.FIT_CLEARANCE,
            C.TRAY_JOIN_LENGTH + C.FIT_CLEARANCE + C.JOINT_EXTRA_DEPTH,
            C.TRAY_JOIN_THROAT + 2.0 * C.FIT_CLEARANCE,
            C.TRAY_JOIN_HEAD + 2.0 * C.FIT_CLEARANCE,
            C.TRAY_THICKNESS + 0.2,
            -0.1,
        )
        shape = shape.cut(pocket)
    rear_support_local_y = C.HDD_TRAY_SUPPORT_REAR_Y - (C.TRAY_Y + C.TRAY_HALF_L)
    shape = _locator_sockets(shape, rear_support_local_y)
    return shape


def make_keeper() -> cq.Workplane:
    # The base replaces a short rail segment; the outer wall retains the HDD.
    base_w = C.TRAY_RAIL_W - 2.0 * C.FIT_CLEARANCE
    base_l = C.HDD_KEEPER_SLOT_L - 2.0 * C.FIT_CLEARANCE
    body = box_at(0.0, 0.0, 0.0, base_w, base_l, C.TRAY_THICKNESS)
    guide_x = C.TRAY_RAIL_W - C.TRAY_GUIDE_T - C.FIT_CLEARANCE
    guide = box_at(
        guide_x,
        0.0,
        C.TRAY_THICKNESS - C.HDD_KEEPER_GUIDE_EMBED,
        C.TRAY_GUIDE_T,
        base_l,
        C.TRAY_GUIDE_H + C.HDD_KEEPER_GUIDE_EMBED,
    )
    keeper = body.union(guide)
    # Two shoulders rest on the uncut rail beside the socket, preventing the
    # replacement segment from dropping through under HDD load.
    for y in (-C.HDD_KEEPER_SHOULDER_L, base_l):
        keeper = keeper.union(
            box_at(
                guide_x,
                y,
                C.TRAY_THICKNESS,
                C.TRAY_GUIDE_T,
                C.HDD_KEEPER_SHOULDER_L,
                C.HDD_KEEPER_SHOULDER_T,
            )
        )
    return keeper


def make_rail_fit_test() -> cq.Workplane:
    depth = C.HDD_RAIL_FIT_TEST_DEPTH
    shape = _rails(depth)
    shape = shape.union(box_at(0.0, 0.0, 0.0, C.TRAY_OUTER_W, C.TRAY_END_STOP_T, C.TRAY_THICKNESS))
    shape = shape.union(box_at(0.0, 0.0, C.TRAY_THICKNESS, C.TRAY_GUIDE_T, depth, C.TRAY_GUIDE_H))
    # A short rear stop makes the configured fore/aft clearance tangible.
    shape = shape.union(box_at(0.0, 0.0, C.TRAY_THICKNESS, C.TRAY_RAIL_W, C.TRAY_END_STOP_T, C.TRAY_GUIDE_H))
    shape = shape.union(
        box_at(C.TRAY_OUTER_W - C.TRAY_RAIL_W, 0.0, C.TRAY_THICKNESS, C.TRAY_RAIL_W, C.TRAY_END_STOP_T, C.TRAY_GUIDE_H)
    )
    return shape


def parts() -> list[PrintablePart]:
    return [
        PrintablePart("hdd_tray_front", make_tray_front(), quantity=2, notes="Print two; skeletal front cradle halves."),
        PrintablePart("hdd_tray_rear", make_tray_rear(), quantity=2, notes="Print two; skeletal rear cradle halves."),
        PrintablePart("hdd_keeper", make_keeper(), quantity=2, notes="Remove before sliding an HDD out the right side."),
    ]
