"""Small open cable-management clips."""

import cadquery as cq

import config as C
from .common import PrintablePart, cylinder_at


def make_cable_clip() -> cq.Workplane:
    """Create one extruded C-profile with no tangent/coplanar fused shells."""
    outer_r = C.CABLE_CLIP_INNER_D / 2.0 + C.CABLE_CLIP_WALL
    inner_r = C.CABLE_CLIP_INNER_D / 2.0
    opening_half = C.CABLE_CLIP_OPENING / 2.0
    foot_bottom = -outer_r - C.CABLE_CLIP_WALL

    # A single closed XZ outline is extruded through the clip width. This
    # avoids the coincident/tangent Boolean seams produced by the former
    # cylinder + foot + quadrant-cut construction.
    profile = (
        (-opening_half, outer_r),
        (-outer_r, outer_r),
        (-outer_r, foot_bottom),
        (outer_r, foot_bottom),
        (outer_r, outer_r),
        (opening_half, outer_r),
        (opening_half, inner_r),
        (inner_r, inner_r),
        (inner_r, -inner_r),
        (-inner_r, -inner_r),
        (-inner_r, inner_r),
        (-opening_half, inner_r),
    )
    clip = cq.Workplane("XZ").polyline(profile).close().extrude(-C.CABLE_CLIP_WIDTH)

    # The mounting hole continues into the open cable cavity, making it a
    # true through-hole without leaving a zero-thickness blind cap.
    hole_depth = inner_r - foot_bottom + 0.2
    clip = clip.cut(
        cylinder_at(
            C.M3_CLEARANCE_D / 2.0,
            hole_depth,
            (0.0, C.CABLE_CLIP_WIDTH / 2.0, foot_bottom - 0.1),
            (0.0, 0.0, 1.0),
        )
    )
    return clip.clean()


def parts() -> list[PrintablePart]:
    return [
        PrintablePart(
            "cable_clip",
            make_cable_clip(),
            quantity=2,
            orientation="either broad XZ face on bed; cable opening visible from above",
            notes="Two floor-mounted clips are supplied; reprint extras as needed.",
        )
    ]
