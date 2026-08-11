"""Shared CadQuery helpers and lightweight part metadata."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Iterable

import cadquery as cq


@dataclass(frozen=True)
class PrintablePart:
    name: str
    shape: cq.Workplane
    quantity: int = 1
    orientation: str = "largest flat face on bed; detail side up"
    supports: str = "none"
    notes: str = ""
    expected_solid_count: int = 1


@dataclass(frozen=True)
class PlacedPart:
    name: str
    source_name: str
    shape: cq.Workplane
    color: tuple[float, float, float, float]


def box_at(x: float, y: float, z: float, dx: float, dy: float, dz: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(dx, dy, dz, centered=(False, False, False))
        .translate((x, y, z))
    )


def cylinder_at(
    radius: float,
    height: float,
    origin: tuple[float, float, float],
    direction: tuple[float, float, float],
) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(radius, height, cq.Vector(*origin), cq.Vector(*direction))
    return cq.Workplane(obj=solid)


def slot_x(length: float, width: float, depth: float, cx: float, cy: float, z: float = 0.0) -> cq.Workplane:
    straight = max(length - width, 0.01)
    shape = box_at(cx - straight / 2.0, cy - width / 2.0, z, straight, width, depth)
    radius = width / 2.0
    for x in (cx - straight / 2.0, cx + straight / 2.0):
        shape = shape.union(cylinder_at(radius, depth, (x, cy, z), (0.0, 0.0, 1.0)))
    return shape


def slot_y(length: float, width: float, depth: float, cx: float, cy: float, z: float = 0.0) -> cq.Workplane:
    straight = max(length - width, 0.01)
    shape = box_at(cx - width / 2.0, cy - straight / 2.0, z, width, straight, depth)
    radius = width / 2.0
    for y in (cy - straight / 2.0, cy + straight / 2.0):
        shape = shape.union(cylinder_at(radius, depth, (cx, y, z), (0.0, 0.0, 1.0)))
    return shape


def chamfered_slot_cutter(
    length: float,
    width: float,
    depth: float,
    cx: float,
    cy: float,
    z: float,
    chamfer: float,
    angle: float = 0.0,
) -> cq.Workplane:
    """Capsule cutter enlarged at both faces to bevel a cable-contact rim."""
    nominal_low = z + 0.1 + chamfer
    nominal_high = z + depth - 0.1 - chamfer
    sections = (
        (z, length + 2.0 * chamfer, width + 2.0 * chamfer),
        (nominal_low, length, width),
        (nominal_high, length, width),
        (z + depth, length + 2.0 * chamfer, width + 2.0 * chamfer),
    )
    wires = [
        cq.Workplane("XY")
        .slot2D(section_length, section_width, angle)
        .val()
        .translate((cx, cy, section_z))
        for section_z, section_length, section_width in sections
    ]
    return cq.Workplane(obj=cq.Solid.makeLoft(wires, True))


def trapezoid_tab_y(
    cx: float,
    y0: float,
    length: float,
    throat: float,
    head: float,
    height: float,
    z: float = 0.0,
) -> cq.Workplane:
    points = [
        (cx - throat / 2.0, y0),
        (cx + throat / 2.0, y0),
        (cx + head / 2.0, y0 + length),
        (cx - head / 2.0, y0 + length),
    ]
    return cq.Workplane("XY").polyline(points).close().extrude(height).translate((0.0, 0.0, z))


def trapezoid_tab_x(
    cy: float,
    x0: float,
    length: float,
    throat: float,
    head: float,
    height: float,
    z: float = 0.0,
) -> cq.Workplane:
    points = [
        (x0, cy - throat / 2.0),
        (x0, cy + throat / 2.0),
        (x0 + length, cy + head / 2.0),
        (x0 + length, cy - head / 2.0),
    ]
    return cq.Workplane("XY").polyline(points).close().extrude(height).translate((0.0, 0.0, z))


def shape_value(shape: cq.Workplane | cq.Shape) -> cq.Shape:
    return shape.val() if isinstance(shape, cq.Workplane) else shape


def compound(shapes: Iterable[cq.Workplane | cq.Shape]) -> cq.Compound:
    values = [shape_value(shape) for shape in shapes]
    return cq.Compound.makeCompound(values)


def bbox_tuple(shape: cq.Workplane | cq.Shape) -> tuple[float, float, float]:
    bb = shape_value(shape).BoundingBox()
    return (bb.xlen, bb.ylen, bb.zlen)


def bbox_limits(shape: cq.Workplane | cq.Shape) -> tuple[float, float, float, float, float, float]:
    bb = shape_value(shape).BoundingBox()
    return (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)


def move_to_origin(shape: cq.Workplane) -> cq.Workplane:
    bb = shape.val().BoundingBox()
    return shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def all_axis_permutations(dimensions: tuple[float, float, float]) -> list[tuple[float, float, float]]:
    return sorted(set(permutations(dimensions, 3)))


def color(rgba: tuple[float, float, float, float]) -> cq.Color:
    return cq.Color(*rgba)


def valid_volume(shape: cq.Workplane | cq.Shape) -> float:
    value = shape_value(shape)
    return value.Volume() if value.isValid() else -1.0
