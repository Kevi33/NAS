"""Part registry, exact assembly placements, and exploded transforms."""

from __future__ import annotations

import cadquery as cq

import config as C
from . import base, cable_clips, front, hdd_tray, left_panel, mid_frame, pi_tray, rear, right_panel, top, usb_hub_mount
from .common import PlacedPart, PrintablePart, color
from .hardware_dummies import ReferenceModel, all_references


PRINT_COLOR = (0.72, 0.74, 0.78, 1.0)
ACCENT_COLOR = (0.20, 0.23, 0.28, 1.0)


def printable_parts() -> dict[str, PrintablePart]:
    entries: list[PrintablePart] = []
    for module in (base, front, rear, left_panel, right_panel, top, mid_frame, hdd_tray, pi_tray, usb_hub_mount, cable_clips):
        entries.extend(module.parts())
    return {entry.name: entry for entry in entries}


def _place_side_left(shape: cq.Workplane, y: float) -> cq.Workplane:
    return (
        shape.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0)
        .translate((0.0, y, C.WALL))
    )


def _place_side_right(shape: cq.Workplane, y: float) -> cq.Workplane:
    mirrored = shape.mirror("XY")
    return (
        mirrored.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0)
        .translate((C.NAS_EXTERNAL_W, y, C.WALL))
    )


def _place_end_panel(shape: cq.Workplane, rear_panel: bool = False) -> cq.Workplane:
    y = C.NAS_EXTERNAL_D if rear_panel else C.WALL
    return shape.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0).translate((C.WALL, y, C.WALL))


def _place_mid_frame(shape: cq.Workplane, x: float = 0.0, z: float = 0.0) -> cq.Workplane:
    return shape.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0).translate((x, C.MID_FRAME_REAR_Y, z))


def placed_printable_parts(parts: dict[str, PrintablePart] | None = None) -> dict[str, PlacedPart]:
    if parts is None:
        parts = printable_parts()
    placed: dict[str, PlacedPart] = {}

    def add(name: str, source: str, shape: cq.Workplane, accent: bool = False) -> None:
        placed[name] = PlacedPart(name, source, shape, ACCENT_COLOR if accent else PRINT_COLOR)

    add("base_front", "base_front", parts["base_front"].shape)
    add("base_rear", "base_rear", parts["base_rear"].shape.translate((0.0, C.MID_FRAME_REAR_Y, 0.0)))

    add("top_service_lid", "top_service_lid", parts["top_service_lid"].shape.mirror("XY").translate((0.0, 0.0, C.NAS_BODY_H)))
    add("top_rear", "top_rear", parts["top_rear"].shape.mirror("XY").translate((0.0, C.TOP_REAR_FRONT_Y, C.NAS_BODY_H)))

    add("left_side_front", "left_side_front", _place_side_left(parts["left_side_front"].shape, 0.0))
    add("left_side_rear", "left_side_rear", _place_side_left(parts["left_side_rear"].shape, C.MID_FRAME_REAR_Y))
    add("right_side_front", "right_side_front", _place_side_right(parts["right_side_front"].shape, 0.0))
    add("right_side_rear", "right_side_rear", _place_side_right(parts["right_side_rear"].shape, C.MID_FRAME_REAR_Y))

    add("front_panel", "front_panel", _place_end_panel(parts["front_panel"].shape, False), True)
    add("rear_panel", "rear_panel", _place_end_panel(parts["rear_panel"].shape, True), True)
    add("mid_frame", "mid_frame", _place_mid_frame(parts["mid_frame"].shape), True)
    add(
        "mid_frame_right_spine",
        "mid_frame_right_spine",
        _place_mid_frame(parts["mid_frame_right_spine"].shape, C.NAS_EXTERNAL_W - C.MID_FRAME_RING, C.MID_FRAME_RING),
        True,
    )

    # HDD cradle halves and service keepers, duplicated at two Z levels.
    for label, drive_z in (("lower", C.HDD_LOWER_Z), ("upper", C.HDD_UPPER_Z)):
        tray_z = drive_z - C.TRAY_THICKNESS
        add(
            f"hdd_tray_{label}_front",
            "hdd_tray_front",
            parts["hdd_tray_front"].shape.translate((C.TRAY_OUTER_X, C.TRAY_Y, tray_z)),
            True,
        )
        add(
            f"hdd_tray_{label}_rear",
            "hdd_tray_rear",
            parts["hdd_tray_rear"].shape.translate((C.TRAY_OUTER_X, C.TRAY_Y + C.TRAY_HALF_L, tray_z)),
            True,
        )
        keeper_x = C.TRAY_OUTER_X + C.TRAY_OUTER_W - C.TRAY_RAIL_W
        keeper_y = C.TRAY_Y + C.HDD_KEEPER_SLOT_Y + C.FIT_CLEARANCE
        add(
            f"hdd_keeper_{label}",
            "hdd_keeper",
            parts["hdd_keeper"].shape.translate((keeper_x + C.FIT_CLEARANCE, keeper_y, tray_z)),
            True,
        )

    add("pi_tray", "pi_tray", parts["pi_tray"].shape.translate((C.PI_TRAY_X, C.PI_TRAY_Y, C.PI_TRAY_Z)), True)
    mount_y = C.USB_HUB_Y - C.USB_HUB_CLEARANCE - C.HUB_MOUNT_EDGE
    mount_z = C.USB_HUB_Z - C.USB_HUB_CLEARANCE - C.HUB_MOUNT_EDGE
    mount_x = C.NAS_EXTERNAL_W - C.WALL
    hub_mount = (
        parts["usb_hub_mount"].shape.mirror("XY")
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0)
        .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0)
        .translate((mount_x, mount_y, mount_z))
    )
    add("usb_hub_mount", "usb_hub_mount", hub_mount, True)
    guard = parts["rear_fan_guard"].shape.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 90.0).translate(
        (C.REAR_FAN_X, C.REAR_FAN_Y, C.REAR_FAN_Z)
    )
    add("rear_fan_guard", "rear_fan_guard", guard, True)

    # Four raised feet; their bottom defines Z=-FOOT_H.
    for idx, (x, y) in enumerate(
        (
            (C.FOOT_INSET, C.FOOT_INSET),
            (C.NAS_EXTERNAL_W - C.FOOT_INSET, C.FOOT_INSET),
            (C.FOOT_INSET, C.NAS_EXTERNAL_D - C.FOOT_INSET),
            (C.NAS_EXTERNAL_W - C.FOOT_INSET, C.NAS_EXTERNAL_D - C.FOOT_INSET),
        ),
        start=1,
    ):
        foot = parts["foot"].shape.translate((x, y, -C.FOOT_H))
        add(f"foot_{idx}", "foot", foot, True)

    # Representative cable clips in the rear chamber; more may be printed.
    clip_z = C.WALL + C.CABLE_CLIP_INNER_D / 2.0 + 2.0 * C.CABLE_CLIP_WALL
    for idx, x in enumerate((C.CABLE_CLIP_X_LEFT, C.CABLE_CLIP_X_RIGHT), start=1):
        clip = parts["cable_clip"].shape.translate((x, C.CABLE_CLIP_Y, clip_z))
        add(f"cable_clip_{idx}", "cable_clip", clip, True)
    return placed


def _exploded_shape(item: PlacedPart) -> cq.Workplane:
    name = item.name
    vector = (0.0, 0.0, 0.0)
    if name == "base_front":
        vector = (0.0, -12.0, -8.0)
    elif name == "base_rear":
        vector = (0.0, 12.0, -8.0)
    elif name in {"foot_1", "foot_2"}:
        vector = (0.0, -12.0, -8.0)
    elif name in {"foot_3", "foot_4"} or name.startswith("cable_clip_"):
        vector = (0.0, 12.0, -8.0)
    elif name.startswith("left_side"):
        vector = (-24.0, -10.0 if name.endswith("front") else 10.0, 0.0)
    elif name.startswith("right_side"):
        vector = (30.0, -10.0 if name.endswith("front") else 10.0, 0.0)
    elif name == "front_panel":
        vector = (0.0, -28.0, 0.0)
    elif name == "rear_panel":
        vector = (0.0, 32.0, 0.0)
    elif name == "top_service_lid":
        vector = (0.0, -8.0, 24.0)
    elif name == "top_rear":
        vector = (0.0, 8.0, 24.0)
    elif name.startswith("hdd_tray") or name.startswith("hdd_keeper"):
        vector = (18.0, 0.0, 0.0)
    elif name.startswith("pi_"):
        vector = (0.0, 0.0, 18.0)
    elif name.startswith("usb_hub"):
        vector = (18.0, 0.0, 0.0)
    elif name == "mid_frame_right_spine":
        vector = (20.0, 0.0, 0.0)
    elif name == "rear_fan_guard":
        vector = (0.0, -16.0, 0.0)
    return item.shape.translate(vector)


def cadquery_assembly(
    placed: dict[str, PlacedPart],
    references: dict[str, ReferenceModel] | None = None,
    exploded: bool = False,
) -> cq.Assembly:
    assembly = cq.Assembly(name="NAS")
    for item in placed.values():
        shape = _exploded_shape(item) if exploded else item.shape
        assembly.add(shape, name=item.name, color=color(item.color))
    if references:
        for reference in references.values():
            ref_shape = reference.shape
            if exploded:
                if reference.name.startswith("HDD_lower") or reference.name.startswith("HDD_upper"):
                    ref_shape = ref_shape.translate((18.0, 0.0, 0.0))
                elif reference.name.startswith("Pi_") or reference.name == "Pi_case":
                    ref_shape = ref_shape.translate((0.0, 0.0, 18.0))
                elif reference.name.startswith("USB_hub"):
                    ref_shape = ref_shape.translate((18.0, 0.0, 0.0))
                elif reference.name == "fan_120":
                    ref_shape = ref_shape.translate((0.0, -20.0, 0.0))
                elif reference.name == "fan_80":
                    ref_shape = ref_shape.translate((0.0, 20.0, 0.0))
            assembly.add(ref_shape, name=reference.name, color=color(reference.color))
    return assembly


def standard_references() -> dict[str, ReferenceModel]:
    return all_references(include_clearances=False, include_service=False)


def clearance_references() -> dict[str, ReferenceModel]:
    return all_references(include_clearances=True, include_service=True)
