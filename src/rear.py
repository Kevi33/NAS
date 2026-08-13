"""Removable rear access panel and external 140 mm fan spacer/guard."""

import cadquery as cq

import config as C
from .common import PrintablePart, box_at, chamfered_slot_cutter, cylinder_at


PANEL_W = C.NAS_EXTERNAL_W - 2.0 * C.WALL
PANEL_H = C.NAS_BODY_H - 2.0 * C.WALL


def _edge_tongues(shape: cq.Workplane) -> cq.Workplane:
    usable = PANEL_H - 2.0 * C.PANEL_TONGUE_SEGMENT_H
    step = usable / max(C.PANEL_TONGUE_COUNT - 1, 1)
    for index in range(C.PANEL_TONGUE_COUNT):
        y = index * step
        shape = shape.union(
            box_at(-C.PANEL_EDGE_TONGUE, y, 0.0, C.PANEL_EDGE_TONGUE, C.PANEL_TONGUE_SEGMENT_H, C.WALL)
        )
        shape = shape.union(
            box_at(PANEL_W, y, 0.0, C.PANEL_EDGE_TONGUE, C.PANEL_TONGUE_SEGMENT_H, C.WALL)
        )
    return shape


def make_rear_panel() -> cq.Workplane:
    shape = box_at(0.0, 0.0, 0.0, PANEL_W, PANEL_H, C.WALL)
    cx = C.REAR_FAN_X + C.REAR_FAN_SIZE / 2.0 - C.WALL
    cy = C.REAR_FAN_Z + C.REAR_FAN_SIZE / 2.0 - C.WALL
    opening = cylinder_at(C.REAR_FAN_CUTOUT_D / 2.0, C.WALL + 0.2, (cx, cy, -0.1), (0.0, 0.0, 1.0))
    shape = shape.cut(opening)
    disk = cylinder_at(
        C.REAR_FAN_CUTOUT_D / 2.0 + C.REAR_GRILLE_RING_EXTRA,
        C.WALL,
        (cx, cy, 0.0),
        (0.0, 0.0, 1.0),
    )
    for offset in C.REAR_GRILLE_BAR_X_OFFSETS:
        bar = box_at(
            cx + offset - C.GRILLE_BAR / 2.0,
            cy - C.REAR_FAN_CUTOUT_D / 2.0,
            0.0,
            C.GRILLE_BAR,
            C.REAR_FAN_CUTOUT_D,
            C.WALL,
        )
        shape = shape.union(bar.intersect(disk))

    half = C.REAR_FAN_HOLE_SPACING / 2.0
    for x in (cx - half, cx + half):
        for y in (cy - half, cy + half):
            shape = shape.cut(
                cylinder_at(C.FAN_MOUNT_HOLE_D / 2.0, C.WALL + 0.2, (x, y, -0.1), (0.0, 0.0, 1.0))
            )

    # Low-voltage cable exits. The complete cover withdraws rearward for service.
    openings = (
        chamfered_slot_cutter(
            C.REAR_LOW_SLOT_L,
            C.REAR_LOW_SLOT_W,
            C.WALL + 0.2,
            C.REAR_LOW_SLOT_LEFT_X - C.WALL,
            C.REAR_LOW_SLOT_Z - C.WALL,
            -0.1,
            C.CABLE_EDGE_CHAMFER,
        ),
        chamfered_slot_cutter(
            C.REAR_LOW_SLOT_L,
            C.REAR_LOW_SLOT_W,
            C.WALL + 0.2,
            C.REAR_LOW_SLOT_RIGHT_X - C.WALL,
            C.REAR_LOW_SLOT_Z - C.WALL,
            -0.1,
            C.CABLE_EDGE_CHAMFER,
        ),
        chamfered_slot_cutter(
            C.REAR_PI_SLOT_H,
            C.REAR_PI_SLOT_W,
            C.WALL + 0.2,
            C.REAR_PI_SLOT_X - C.WALL,
            C.REAR_PI_SLOT_Z - C.WALL,
            -0.1,
            C.CABLE_EDGE_CHAMFER,
            90.0,
        ),
        chamfered_slot_cutter(
            C.USB_HUB_REAR_ACCESS_H,
            C.USB_HUB_REAR_ACCESS_W,
            C.WALL + 0.2,
            C.USB_HUB_REAR_ACCESS_X - C.WALL,
            C.USB_HUB_REAR_ACCESS_Z - C.WALL,
            -0.1,
            C.CABLE_EDGE_CHAMFER,
            90.0,
        ),
        chamfered_slot_cutter(
            C.REAR_FAN_WIRE_SLOT_L,
            C.REAR_FAN_WIRE_SLOT_W,
            C.WALL + 0.2,
            C.REAR_FAN_WIRE_SLOT_X - C.WALL,
            C.REAR_FAN_WIRE_SLOT_Z - C.WALL,
            -0.1,
            C.CABLE_EDGE_CHAMFER,
            90.0,
        ),
    )
    for opening_shape in openings:
        shape = shape.cut(opening_shape)
    return _edge_tongues(shape).clean()


def make_rear_fan_guard() -> cq.Workplane:
    size = C.REAR_FAN_SIZE
    outer = box_at(0.0, 0.0, 0.0, size, size, C.FAN_GUARD_DEPTH)
    inner = box_at(
        C.FAN_GUARD_FRAME,
        C.FAN_GUARD_FRAME,
        -0.1,
        size - 2.0 * C.FAN_GUARD_FRAME,
        size - 2.0 * C.FAN_GUARD_FRAME,
        C.FAN_GUARD_DEPTH + 0.2,
    )
    guard = outer.cut(inner)
    half = C.REAR_FAN_HOLE_SPACING / 2.0
    hole_centers = tuple(
        (x, y)
        for x in (size / 2.0 - half, size / 2.0 + half)
        for y in (size / 2.0 - half, size / 2.0 + half)
    )
    # Full-depth bosses keep the wide 124.5 mm mounting pattern connected to
    # the perimeter instead of leaving the screw holes in the open duct.
    for x, y in hole_centers:
        guard = guard.union(
            cylinder_at(
                C.FAN_GUARD_BOSS_R,
                C.FAN_GUARD_DEPTH,
                (x, y, 0.0),
                (0.0, 0.0, 1.0),
            )
        )
    # Cable-retaining crossbars sit at the fan side of the external spacer.
    guard = guard.union(
        box_at(
            size / 2.0 - C.FAN_GUARD_CROSSBAR_W / 2.0,
            0.0,
            0.0,
            C.FAN_GUARD_CROSSBAR_W,
            size,
            C.FAN_GUARD_CROSSBAR_T,
        )
    )
    guard = guard.union(
        box_at(
            0.0,
            size / 2.0 - C.FAN_GUARD_CROSSBAR_W / 2.0,
            0.0,
            size,
            C.FAN_GUARD_CROSSBAR_W,
            C.FAN_GUARD_CROSSBAR_T,
        )
    )
    for x, y in hole_centers:
        guard = guard.cut(
            cylinder_at(
                C.FAN_MOUNT_HOLE_D / 2.0,
                C.FAN_GUARD_DEPTH + 0.2,
                (x, y, -0.1),
                (0.0, 0.0, 1.0),
            )
        )
    return guard.clean()


def parts() -> list[PrintablePart]:
    return [
        PrintablePart(
            "rear_panel",
            make_rear_panel(),
            orientation="exterior face on bed; grille and tongues upward",
            notes="Rearward-pull cable cover with centered 140 mm exhaust and protected cable openings.",
        ),
        PrintablePart(
            "rear_fan_guard",
            make_rear_fan_guard(),
            orientation="fan-side crossbar face on bed; spacer walls upward",
            notes="External 10 mm spacer and broad cable guard for the 140 mm exhaust fan.",
        ),
    ]
