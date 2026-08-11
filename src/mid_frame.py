"""Structural C-frame and removable right service spine."""

import cadquery as cq

import config as C
from .common import PrintablePart, box_at


def _extrude_polygon(points: list[cq.Vector], vector: cq.Vector) -> cq.Solid:
    wire = cq.Wire.makePolygon(points, close=True)
    return cq.Solid.extrudeLinear(wire, [], vector)


def _horizontal_key_pocket(
    cx: float,
    assembly_z0: float,
    assembly_z_len: float,
    front_face: bool,
) -> cq.Workplane:
    throat = C.JOINT_THROAT + 2.0 * C.FIT_CLEARANCE
    head = C.JOINT_HEAD + 2.0 * C.FIT_CLEARANCE
    depth = C.JOINT_ENGAGEMENT + C.JOINT_EXTRA_DEPTH
    face_z = C.MID_FRAME_DEPTH + 0.1 if front_face else -0.1
    inner_z = C.MID_FRAME_DEPTH - depth if front_face else depth
    points = [
        cq.Vector(cx - throat / 2.0, assembly_z0, face_z),
        cq.Vector(cx + throat / 2.0, assembly_z0, face_z),
        cq.Vector(cx + head / 2.0, assembly_z0, inner_z),
        cq.Vector(cx - head / 2.0, assembly_z0, inner_z),
    ]
    solid = _extrude_polygon(points, cq.Vector(0.0, assembly_z_len, 0.0))
    return cq.Workplane(obj=solid)


def _left_side_key_pocket(assembly_z: float, front_face: bool) -> cq.Workplane:
    throat = C.JOINT_THROAT + 2.0 * C.FIT_CLEARANCE
    head = C.JOINT_HEAD + 2.0 * C.FIT_CLEARANCE
    depth = C.JOINT_ENGAGEMENT + C.JOINT_EXTRA_DEPTH
    face_z = C.MID_FRAME_DEPTH + 0.1 if front_face else -0.1
    inner_z = C.MID_FRAME_DEPTH - depth if front_face else depth
    x0 = -C.FIT_CLEARANCE
    points = [
        cq.Vector(x0, assembly_z - throat / 2.0, face_z),
        cq.Vector(x0, assembly_z + throat / 2.0, face_z),
        cq.Vector(x0, assembly_z + head / 2.0, inner_z),
        cq.Vector(x0, assembly_z - head / 2.0, inner_z),
    ]
    solid = _extrude_polygon(points, cq.Vector(C.WALL + 2.0 * C.FIT_CLEARANCE, 0.0, 0.0))
    return cq.Workplane(obj=solid)


def _joint_pockets(frame: cq.Workplane, front_face: bool) -> cq.Workplane:
    # Base module keys: cross-section lies in frame X/Z plane.
    for ratio in C.BASE_JOINT_X_FRACTIONS:
        x = C.NAS_EXTERNAL_W * ratio
        pocket = _horizontal_key_pocket(
            x, -C.FIT_CLEARANCE, C.WALL + 2.0 * C.FIT_CLEARANCE, front_face
        )
        frame = frame.cut(pocket)
    # Top module keys use the same X positions as the base keys.
    for ratio in C.TOP_JOINT_X_FRACTIONS:
        x = C.NAS_EXTERNAL_W * ratio
        pocket = _horizontal_key_pocket(
            x,
            C.NAS_BODY_H - C.WALL - C.FIT_CLEARANCE,
            C.WALL + 2.0 * C.FIT_CLEARANCE,
            front_face,
        )
        frame = frame.cut(pocket)
    # Left-side module keys: local frame Y is assembly Z.
    panel_h = C.NAS_BODY_H - 2.0 * C.WALL
    for ratio in C.SIDE_JOINT_Z_FRACTIONS:
        assembly_z = C.WALL + panel_h * ratio
        pocket = _left_side_key_pocket(assembly_z, front_face)
        frame = frame.cut(pocket)
    return frame


def make_mid_frame() -> cq.Workplane:
    # Local print axes: X=case X, Y=case Z, Z=case depth.
    outer = box_at(0.0, 0.0, 0.0, C.NAS_EXTERNAL_W, C.NAS_BODY_H, C.MID_FRAME_DEPTH)
    # Opening reaches the right edge.  The separate spine closes it in service.
    opening = box_at(
        C.MID_FRAME_RING,
        C.MID_FRAME_RING,
        -0.1,
        C.NAS_EXTERNAL_W - C.MID_FRAME_RING + 0.1,
        C.NAS_BODY_H - 2.0 * C.MID_FRAME_RING,
        C.MID_FRAME_DEPTH + 0.2,
    )
    frame = outer.cut(opening)
    frame = _joint_pockets(frame, True)
    frame = _joint_pockets(frame, False)

    # Female pockets for the removable right-spine nibs.
    spine_pocket_x = C.NAS_EXTERNAL_W - C.MID_FRAME_RING
    for y in (C.MID_FRAME_RING - 3.0, C.NAS_BODY_H - C.MID_FRAME_RING):
        frame = frame.cut(
            box_at(
                spine_pocket_x,
                y - C.FIT_CLEARANCE,
                -0.1,
                C.MID_FRAME_RING + 0.1,
                3.0 + 2.0 * C.FIT_CLEARANCE,
                C.MID_FRAME_DEPTH + 0.2,
            )
        )

    return frame


def make_right_spine() -> cq.Workplane:
    height = C.NAS_BODY_H - 2.0 * C.MID_FRAME_RING
    spine = box_at(0.0, 0.0, 0.0, C.MID_FRAME_RING, height, C.MID_FRAME_DEPTH)
    # Keyed end nibs engage shallow pockets in the top/bottom bars.
    nib_w = C.MID_FRAME_RING - 2.0 * C.FIT_CLEARANCE
    spine = spine.union(box_at(C.FIT_CLEARANCE, -3.0, C.FIT_CLEARANCE, nib_w, 3.0, C.MID_FRAME_DEPTH - 2.0 * C.FIT_CLEARANCE))
    spine = spine.union(box_at(C.FIT_CLEARANCE, height, C.FIT_CLEARANCE, nib_w, 3.0, C.MID_FRAME_DEPTH - 2.0 * C.FIT_CLEARANCE))
    # Receiving pockets for the keyed right-side shell modules.
    panel_h = C.NAS_BODY_H - 2.0 * C.WALL
    for ratio in C.SIDE_JOINT_Z_FRACTIONS:
        assembly_z = C.WALL + panel_h * ratio
        local_y = assembly_z - C.MID_FRAME_RING
        for local_z in (-0.1, C.MID_FRAME_DEPTH - C.JOINT_ENGAGEMENT - C.JOINT_EXTRA_DEPTH):
            pocket = box_at(
                C.MID_FRAME_RING - C.WALL - C.FIT_CLEARANCE,
                local_y - C.JOINT_HEAD / 2.0 - C.FIT_CLEARANCE,
                local_z,
                C.WALL + C.FIT_CLEARANCE + 0.1,
                C.JOINT_HEAD + 2.0 * C.FIT_CLEARANCE,
                C.JOINT_ENGAGEMENT + C.JOINT_EXTRA_DEPTH + 0.2,
            )
            spine = spine.cut(pocket)
    return spine


def parts() -> list[PrintablePart]:
    return [
        PrintablePart(
            "mid_frame",
            make_mid_frame(),
            orientation="broad face on bed",
            notes="Structural C-frame; open right side is the HDD service path.",
        ),
        PrintablePart(
            "mid_frame_right_spine",
            make_right_spine(),
            notes="Remove after right side panels to slide either HDD out laterally.",
        ),
    ]
