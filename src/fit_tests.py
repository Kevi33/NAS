"""Small calibration prints for production joints and the HDD cradle."""

from __future__ import annotations

import cadquery as cq

import config as C
from .common import box_at, compound, trapezoid_tab_y
from .hdd_tray import make_keeper, make_rail_fit_test


_PIXEL_DIGITS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
}


def _emboss_numeric_label(
    shape: cq.Workplane,
    text_value: str,
    cx: float,
    cy: float,
    base_z: float,
) -> cq.Workplane:
    """Fuse a deterministic 3x5-pixel label with generous printable features."""
    pixel = C.FIT_TEST_LABEL_PIXEL
    gap = C.FIT_TEST_LABEL_GAP
    digit_w = 3.0 * pixel + 2.0 * gap
    digit_h = 5.0 * pixel + 4.0 * gap
    total_w = len(text_value) * digit_w + (len(text_value) - 1) * C.FIT_TEST_LABEL_DIGIT_GAP
    x_origin = cx - total_w / 2.0
    y_origin = cy - digit_h / 2.0
    for digit_index, digit in enumerate(text_value):
        pattern = _PIXEL_DIGITS[digit]
        digit_x = x_origin + digit_index * (digit_w + C.FIT_TEST_LABEL_DIGIT_GAP)
        for row_index, row in enumerate(reversed(pattern)):
            for column_index, enabled in enumerate(row):
                if enabled != "1":
                    continue
                shape = shape.union(
                    box_at(
                        digit_x + column_index * (pixel + gap),
                        y_origin + row_index * (pixel + gap),
                        base_z - C.FIT_TEST_LABEL_EMBED,
                        pixel,
                        pixel,
                        C.FIT_TEST_LABEL_H + C.FIT_TEST_LABEL_EMBED,
                    )
                )
    return shape.clean()


def _rail_prism(length: float, throat: float, head: float, depth: float) -> cq.Workplane:
    profile = (
        cq.Workplane("XZ")
        .moveTo(-throat / 2.0, 0.0)
        .lineTo(throat / 2.0, 0.0)
        .lineTo(head / 2.0, depth)
        .lineTo(-head / 2.0, depth)
        .close()
        .extrude(length)
    )
    # XZ extrusion advances toward -Y; normalize it to Y=0..length.
    return profile.translate((0.0, length, 0.0))


def _female_coupon(clearance: float) -> cq.Workplane:
    block_w = 18.0
    block_l = C.FIT_TEST_RAIL_LENGTH
    block_h = C.FIT_TEST_DOVETAIL_DEPTH + 3.0
    block = box_at(0.0, 0.0, 0.0, block_w, block_l, block_h)
    slot = _rail_prism(
        block_l + 0.2,
        C.FIT_TEST_DOVETAIL_THROAT + 2.0 * clearance,
        C.FIT_TEST_DOVETAIL_HEAD + 2.0 * clearance,
        C.FIT_TEST_DOVETAIL_DEPTH + 0.2,
    ).translate((block_w / 2.0, 0.1, block_h - C.FIT_TEST_DOVETAIL_DEPTH - 0.1))
    coupon = block.cut(slot)

    # Connected label tab with deterministic solid pixel digits.
    tab = box_at(block_w, block_l - 12.0, 0.0, 12.0, 12.0, 2.0)
    coupon = coupon.union(tab)
    label = f"{int(round(clearance * 100)):02d}"
    return _emboss_numeric_label(coupon, label, block_w + 6.0, block_l - 6.0, 2.0)


def _male_coupon() -> cq.Workplane:
    rail = _rail_prism(
        C.FIT_TEST_RAIL_LENGTH - 4.0,
        C.FIT_TEST_DOVETAIL_THROAT,
        C.FIT_TEST_DOVETAIL_HEAD,
        C.FIT_TEST_DOVETAIL_DEPTH,
    )
    handle = box_at(
        -9.0,
        -4.0,
        0.0,
        18.0,
        5.0,
        C.FIT_TEST_DOVETAIL_DEPTH,
    )
    return rail.union(handle)


def make_dovetail_fit_test() -> cq.Workplane:
    cell_pitch = 31.0
    shapes: list[cq.Workplane] = []
    for index, clearance in enumerate(C.FIT_TEST_CLEARANCES):
        x = index * cell_pitch
        shapes.append(_female_coupon(clearance).translate((x, 0.0, 0.0)))
        shapes.append(_male_coupon().translate((x + 9.0, 40.0, 0.0)))
    return cq.Workplane(obj=compound(shapes))


def make_panel_key_fit_test() -> cq.Workplane:
    """Exact planar production-key profile at the five configured clearances."""
    cell_pitch = 31.0
    shapes: list[cq.Workplane] = []
    plate_w = 28.0
    plate_l = 20.0
    plate_h = C.WALL
    for index, clearance in enumerate(C.FIT_TEST_CLEARANCES):
        x0 = index * cell_pitch
        female = box_at(x0, 0.0, 0.0, plate_w, plate_l, plate_h)
        pocket = trapezoid_tab_y(
            x0 + plate_w / 2.0,
            plate_l - C.JOINT_ENGAGEMENT - C.JOINT_EXTRA_DEPTH,
            C.JOINT_ENGAGEMENT + C.JOINT_EXTRA_DEPTH + 0.1,
            C.JOINT_THROAT + 2.0 * clearance,
            C.JOINT_HEAD + 2.0 * clearance,
            plate_h + 0.2,
            -0.1,
        )
        female = female.cut(pocket)
        female = _emboss_numeric_label(
            female,
            f"{int(round(clearance * 100)):02d}",
            x0 + plate_w / 2.0,
            5.0,
            plate_h,
        )
        male = box_at(x0 + 5.0, 36.0, 0.0, 18.0, 10.0, plate_h)
        male = male.union(
            trapezoid_tab_y(
                x0 + plate_w / 2.0,
                46.0,
                C.JOINT_ENGAGEMENT,
                C.JOINT_THROAT,
                C.JOINT_HEAD,
                plate_h,
            )
        )
        shapes.extend((female, male))
    return cq.Workplane(obj=compound(shapes))


def make_keeper_fit_test() -> cq.Workplane:
    rail = _keeper_retention_socket(
        f"{int(round(C.HDD_KEEPER_CLEARANCE * 100)):02d}"
    )
    slot_y = (C.HDD_KEEPER_TEST_RAIL_LENGTH - C.HDD_KEEPER_SLOT_L) / 2.0
    keeper = make_keeper().translate((16.0, slot_y + C.HDD_KEEPER_CLEARANCE, 0.0))
    return cq.Workplane(obj=compound([rail, keeper]))


def _keeper_retention_socket(label: str) -> cq.Workplane:
    """Production-faithful rail socket with a fused clearance label."""
    rail_length = C.HDD_KEEPER_TEST_RAIL_LENGTH
    slot_y = (rail_length - C.HDD_KEEPER_SLOT_L) / 2.0
    socket = box_at(0.0, 0.0, 0.0, C.TRAY_RAIL_W, rail_length, C.TRAY_THICKNESS)
    socket = socket.union(
        box_at(
            -C.HDD_KEEPER_BYPASS_INSET,
            slot_y - C.HDD_KEEPER_BYPASS_END_OVERLAP,
            0.0,
            C.HDD_KEEPER_BYPASS_W,
            C.HDD_KEEPER_SLOT_L + 2.0 * C.HDD_KEEPER_BYPASS_END_OVERLAP,
            C.TRAY_THICKNESS,
        )
    )
    socket = socket.cut(
        box_at(
            0.0,
            slot_y,
            -C.JOINT_EXTRA_DEPTH,
            C.TRAY_RAIL_W + C.JOINT_EXTRA_DEPTH,
            C.HDD_KEEPER_SLOT_L,
            C.TRAY_THICKNESS + 2.0 * C.JOINT_EXTRA_DEPTH,
        )
    )
    return _emboss_numeric_label(socket, label, C.TRAY_RAIL_W / 2.0, slot_y / 2.0, C.TRAY_THICKNESS)


def _retained_keeper_variant(clearance: float, label: str) -> cq.Workplane:
    """Production keeper at one test clearance, with a matching numeric ID."""
    keeper = make_keeper(clearance)

    # Repeat the numeric ID on the loose keeper so variants cannot be mixed up
    # after removal from the print plate. The label sits inside the socket plan.
    pixel = C.FIT_TEST_LABEL_PIXEL
    gap = C.FIT_TEST_LABEL_GAP
    digit_w = 3.0 * pixel + 2.0 * gap
    label_w = 2.0 * digit_w + C.FIT_TEST_LABEL_DIGIT_GAP
    base_l = C.HDD_KEEPER_SLOT_L - 2.0 * clearance
    return _emboss_numeric_label(
        keeper,
        label,
        label_w / 2.0,
        base_l / 2.0,
        C.TRAY_THICKNESS,
    )


def make_keeper_retention_test() -> cq.Workplane:
    """Five separately labeled socket/keeper retention pairs."""
    shapes: list[cq.Workplane] = []
    slot_y = (C.HDD_KEEPER_TEST_RAIL_LENGTH - C.HDD_KEEPER_SLOT_L) / 2.0
    for index, clearance in enumerate(C.HDD_KEEPER_TEST_CLEARANCES):
        label = f"{int(round(clearance * 100)):02d}"
        cell_x = index * C.HDD_KEEPER_TEST_CELL_PITCH
        socket = _keeper_retention_socket(label).translate((cell_x, 0.0, 0.0))
        keeper = _retained_keeper_variant(clearance, label).translate(
            (cell_x + C.HDD_KEEPER_TEST_LOOSE_X, slot_y, 0.0)
        )
        shapes.extend((socket, keeper))
    return cq.Workplane(obj=compound(shapes))


def fit_test_models() -> dict[str, cq.Workplane]:
    return {
        "dovetail_fit_test": make_dovetail_fit_test(),
        "panel_key_fit_test": make_panel_key_fit_test(),
        "hdd_rail_fit_test": make_rail_fit_test(),
        "hdd_keeper_fit_test": make_keeper_fit_test(),
        "hdd_keeper_retention_test": make_keeper_retention_test(),
    }
