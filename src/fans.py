"""Fan footprint helpers used by the reference model."""

import cadquery as cq

from .common import box_at, cylinder_at


def fan_frame(x: float, y: float, z: float, size: float, thickness: float) -> cq.Workplane:
    outer = box_at(x, y, z, size, thickness, size)
    rotor_clearance = cylinder_at(size * 0.42, thickness + 0.2, (x + size / 2.0, y - 0.1, z + size / 2.0), (0.0, 1.0, 0.0))
    return outer.cut(rotor_clearance)


def rotor_disk(x: float, y: float, z: float, size: float, thickness: float) -> cq.Workplane:
    return cylinder_at(size * 0.38, max(thickness * 0.16, 2.0), (x + size / 2.0, y + thickness * 0.42, z + size / 2.0), (0.0, 1.0, 0.0))

