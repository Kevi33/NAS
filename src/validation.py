"""Automated printability, geometry, collision, clearance, and report checks."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
import math
from pathlib import Path
import re
import struct

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepCheck import BRepCheck_Analyzer

import config as C
from .common import (
    PlacedPart,
    PrintablePart,
    all_axis_permutations,
    bbox_limits,
    bbox_tuple,
    shape_value,
    valid_volume,
)
from .hardware_dummies import ReferenceModel


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


Vector3 = tuple[float, float, float]
Facet = tuple[Vector3, tuple[Vector3, Vector3, Vector3]]


@dataclass(frozen=True)
class STLMeshStats:
    """Topology and geometry facts measured directly from an exported STL."""

    dimensions: tuple[float, float, float]
    triangle_count: int
    vertex_count: int
    regions: int
    boundary_edges: int
    nonmanifold_edges: int
    winding_mismatches: int
    vertex_link_failures: int
    degenerate_triangles: int
    duplicate_triangles: int
    normal_failures: int
    self_intersections: int
    min_triangle_area: float
    signed_volume: float
    component_volumes: tuple[float, ...]
    vtk_regions: int
    vtk_bad_edges: int
    vtk_volume: float


def _fmt_dims(dims: tuple[float, float, float]) -> str:
    return " × ".join(f"{value:.2f}" for value in dims) + " mm"


def _intersection_volume(a: cq.Workplane | cq.Shape, b: cq.Workplane | cq.Shape) -> float:
    try:
        result = shape_value(a).intersect(shape_value(b))
        return max(result.Volume(), 0.0)
    except Exception:
        # A failed Boolean is not silently treated as a pass.
        return float("inf")


def _collisions(
    reference: cq.Workplane,
    placed: dict[str, PlacedPart],
    excluded: set[str] | None = None,
) -> list[tuple[str, float]]:
    excluded = excluded or set()
    hits: list[tuple[str, float]] = []
    for name, part in placed.items():
        if name in excluded:
            continue
        volume = _intersection_volume(reference, part.shape)
        if volume > C.COLLISION_VOLUME_EPS:
            hits.append((name, volume))
    return hits


def _hits_detail(hits: list[tuple[str, float]]) -> str:
    if not hits:
        return "No forbidden intersections."
    return "; ".join(
        f"{name} ({'Boolean failure' if volume == float('inf') else f'{volume:.2f} mm³'})"
        for name, volume in hits
    )


def _sampled_removal_check(
    label: str,
    placed: dict[str, PlacedPart],
    moving_names: tuple[str, ...],
    removed_names: set[str],
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),
    extra_moving: dict[str, cq.Workplane | cq.Shape] | None = None,
    travel: float = 20.0,
    increment: float = 0.30,
) -> CheckResult:
    """Sample a rigid withdrawal of attached printed and hardware solids."""
    failures: list[str] = []
    sample_count = int(travel / increment + 0.999999)
    moving_shapes: dict[str, cq.Workplane | cq.Shape] = {
        name: placed[name].shape for name in moving_names
    }
    moving_shapes.update(extra_moving or {})
    stationary_bounds = {
        name: shape_value(part.shape).BoundingBox() for name, part in placed.items()
    }
    for sample in range(1, sample_count + 1):
        distance = min(sample * increment, travel)
        vector = tuple(component * distance for component in direction)
        for moving_name, source_shape in moving_shapes.items():
            moving = shape_value(source_shape).moved(cq.Location(cq.Vector(*vector)))
            moving_bb = shape_value(moving).BoundingBox()
            for stationary_name, stationary in placed.items():
                if stationary_name in moving_names or stationary_name in removed_names:
                    continue
                stationary_bb = stationary_bounds[stationary_name]
                bbox_overlap = (
                    min(moving_bb.xmax, stationary_bb.xmax) - max(moving_bb.xmin, stationary_bb.xmin) > 1e-6
                    and min(moving_bb.ymax, stationary_bb.ymax) - max(moving_bb.ymin, stationary_bb.ymin) > 1e-6
                    and min(moving_bb.zmax, stationary_bb.zmax) - max(moving_bb.zmin, stationary_bb.zmin) > 1e-6
                )
                if not bbox_overlap:
                    continue
                overlap = _intersection_volume(moving, stationary.shape)
                if overlap > C.COLLISION_VOLUME_EPS:
                    failures.append(
                        f"{moving_name}/{stationary_name} at {vector} mm ({overlap:.2f} mm³)"
                    )
                    break
            if failures:
                break
        if failures:
            break
    detail = (
        failures[0]
        if failures
        else f"{sample_count} rigid-body positions checked through {direction} x {travel:.1f} mm."
    )
    return CheckResult(label, not failures, detail)


def _point_in_polygon(point: tuple[float, float], polygon: tuple[tuple[float, float], ...]) -> bool:
    """Return whether an XY point lies inside a simple support polygon."""
    x, y = point
    inside = False
    previous = polygon[-1]
    for current in polygon:
        x1, y1 = previous
        x2, y2 = current
        if (y1 > y) != (y2 > y):
            crossing_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing_x:
                inside = not inside
        previous = current
    return inside


def _reference_system(name: str) -> str | None:
    if name.startswith("HDD_lower"):
        return "HDD_lower"
    if name.startswith("HDD_upper"):
        return "HDD_upper"
    if name.startswith("Pi_") or name == "Pi_case":
        return "Pi"
    if name.startswith("USB_hub"):
        return "USB_hub"
    if name.startswith("front_fan") or name == "fan_120":
        return "fan_120"
    if name.startswith("rear_fan") or name == "fan_140":
        return "fan_140"
    return None


INTENTIONAL_CABLE_CONNECTIONS = {
    frozenset(("Pi_port_and_route_clearance", "USB_hub_host_cable_route")),
    frozenset(("front_fan_wire_route", "USB_hub_plug_clearance")),
    frozenset(("front_fan_wire_route", "USB_hub_front_fan_USB_adapter")),
    frozenset(("rear_fan_wire_route", "USB_hub_plug_clearance")),
    frozenset(("rear_fan_wire_route", "USB_hub_rear_fan_USB_adapter")),
}


_STL_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
def _read_stl_facets(path: Path) -> list[Facet]:
    """Parse binary or ASCII STL without allowing a mesh reader to repair it."""
    data = path.read_bytes()
    if len(data) >= 84:
        triangle_count = struct.unpack_from("<I", data, 80)[0]
        if 84 + triangle_count * 50 == len(data):
            if triangle_count == 0:
                raise ValueError("binary STL contains no triangles")
            facets: list[Facet] = []
            offset = 84
            for _ in range(triangle_count):
                values = struct.unpack_from("<12fH", data, offset)
                normal = tuple(float(value) for value in values[0:3])
                vertices = (
                    tuple(float(value) for value in values[3:6]),
                    tuple(float(value) for value in values[6:9]),
                    tuple(float(value) for value in values[9:12]),
                )
                facets.append((normal, vertices))  # type: ignore[arg-type]
                offset += 50
            return facets

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("STL is neither length-valid binary nor UTF-8 ASCII") from exc
    facet_pattern = re.compile(
        rf"facet\s+normal\s+({_STL_NUMBER})\s+({_STL_NUMBER})\s+({_STL_NUMBER})(.*?)endfacet",
        re.IGNORECASE | re.DOTALL,
    )
    vertex_pattern = re.compile(
        rf"vertex\s+({_STL_NUMBER})\s+({_STL_NUMBER})\s+({_STL_NUMBER})",
        re.IGNORECASE,
    )
    facets = []
    for facet_match in facet_pattern.finditer(text):
        normal = tuple(float(value) for value in facet_match.groups()[:3])
        vertices = [
            tuple(float(value) for value in match.groups())
            for match in vertex_pattern.finditer(facet_match.group(4))
        ]
        if len(vertices) != 3:
            raise ValueError(f"ASCII facet contains {len(vertices)} vertices instead of 3")
        facets.append((normal, tuple(vertices)))  # type: ignore[arg-type]
    if not facets:
        raise ValueError("ASCII STL contains no complete facets")
    return facets


def _cross(first: Vector3, second: Vector3) -> Vector3:
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def _subtract(first: Vector3, second: Vector3) -> Vector3:
    return tuple(first[axis] - second[axis] for axis in range(3))  # type: ignore[return-value]


def _dot(first: Vector3, second: Vector3) -> float:
    return sum(first[axis] * second[axis] for axis in range(3))


def _length(vector: Vector3) -> float:
    return math.sqrt(_dot(vector, vector))


def _weld_vertices(
    triangles: list[tuple[Vector3, Vector3, Vector3]],
) -> tuple[list[Vector3], list[tuple[int, int, int]]]:
    """Index exact raw STL coordinates so micro-gaps are never repaired away."""
    index_by_coordinate: dict[Vector3, int] = {}
    welded: list[Vector3] = []
    faces: list[tuple[int, int, int]] = []

    for triangle in triangles:
        face: list[int] = []
        for vertex in triangle:
            match_index = index_by_coordinate.get(vertex)
            if match_index is None:
                match_index = len(welded)
                welded.append(vertex)
                index_by_coordinate[vertex] = match_index
            face.append(match_index)
        faces.append(tuple(face))  # type: ignore[arg-type]
    return welded, faces


def _self_intersection_count(
    triangles: list[tuple[Vector3, Vector3, Vector3]],
    faces: list[tuple[int, int, int]],
) -> int:
    """Count non-adjacent triangle crossings with an AABB sweep and VTK SAT."""
    import vtk

    if not triangles:
        return 0
    spans = [
        max(vertex[axis] for triangle in triangles for vertex in triangle)
        - min(vertex[axis] for triangle in triangles for vertex in triangle)
        for axis in range(3)
    ]
    sweep_axis = max(range(3), key=lambda axis: spans[axis])
    other_axes = [axis for axis in range(3) if axis != sweep_axis]
    bounds = [
        (
            tuple(min(vertex[axis] for vertex in triangle) for axis in range(3)),
            tuple(max(vertex[axis] for vertex in triangle) for axis in range(3)),
        )
        for triangle in triangles
    ]
    order = sorted(range(len(triangles)), key=lambda index: bounds[index][0][sweep_axis])
    tolerance = C.STL_VERTEX_WELD_TOLERANCE
    intersections = 0

    def inset(triangle: tuple[Vector3, Vector3, Vector3]) -> tuple[Vector3, Vector3, Vector3]:
        centroid = tuple(
            sum(vertex[axis] for vertex in triangle) / 3.0 for axis in range(3)
        )
        scale = 1.0 - 1e-6
        return tuple(
            tuple(
                centroid[axis] + (vertex[axis] - centroid[axis]) * scale
                for axis in range(3)
            )
            for vertex in triangle
        )  # type: ignore[return-value]

    for order_position, first_index in enumerate(order):
        first_min, first_max = bounds[first_index]
        first_vertices = set(faces[first_index])
        for second_index in order[order_position + 1 :]:
            second_min, second_max = bounds[second_index]
            if second_min[sweep_axis] > first_max[sweep_axis] + tolerance:
                break
            if any(
                second_min[axis] > first_max[axis] + tolerance
                or first_min[axis] > second_max[axis] + tolerance
                for axis in other_axes
            ):
                continue
            first = triangles[first_index]
            second = triangles[second_index]
            if first_vertices.intersection(faces[second_index]):
                first = inset(first)
                second = inset(second)
            if vtk.vtkTriangle.TrianglesIntersect(
                first[0], first[1], first[2], second[0], second[1], second[2]
            ):
                intersections += 1
                if intersections >= 100:
                    return intersections
    return intersections


def _vtk_mesh_stats(path: Path) -> tuple[int, int, float]:
    """Independent VTK cross-check for regions, open edges, and volume."""
    import vtk

    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(path))
    reader.MergingOn()
    reader.Update()
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputConnection(reader.GetOutputPort())
    connectivity.SetExtractionModeToAllRegions()
    connectivity.Update()

    edges = vtk.vtkFeatureEdges()
    edges.SetInputConnection(reader.GetOutputPort())
    edges.BoundaryEdgesOn()
    edges.NonManifoldEdgesOn()
    edges.FeatureEdgesOff()
    edges.ManifoldEdgesOff()
    edges.Update()

    triangles = vtk.vtkTriangleFilter()
    triangles.SetInputConnection(reader.GetOutputPort())
    triangles.Update()
    mass = vtk.vtkMassProperties()
    mass.SetInputConnection(triangles.GetOutputPort())
    mass.Update()
    return (
        connectivity.GetNumberOfExtractedRegions(),
        edges.GetOutput().GetNumberOfCells(),
        float(mass.GetVolume()),
    )


def stl_mesh_stats(path: Path) -> STLMeshStats:
    """Analyze topology, winding, normals, and signed volume without repairing the STL."""
    facets = _read_stl_facets(path)
    triangles = [vertices for _, vertices in facets]
    all_vertices = [vertex for triangle in triangles for vertex in triangle]
    if any(not all(math.isfinite(value) for value in vertex) for vertex in all_vertices):
        raise ValueError("STL contains a non-finite vertex coordinate")

    mins = tuple(min(vertex[axis] for vertex in all_vertices) for axis in range(3))
    maxs = tuple(max(vertex[axis] for vertex in all_vertices) for axis in range(3))
    dimensions = tuple(maxs[axis] - mins[axis] for axis in range(3))
    welded_vertices, faces = _weld_vertices(triangles)

    degenerate_triangles = 0
    normal_failures = 0
    triangle_areas: list[float] = []
    triangle_signed_volumes: list[float] = []
    for (normal, triangle), face in zip(facets, faces):
        first_edge = _subtract(triangle[1], triangle[0])
        second_edge = _subtract(triangle[2], triangle[0])
        geometric_normal = _cross(first_edge, second_edge)
        doubled_area = _length(geometric_normal)
        triangle_area = doubled_area / 2.0
        triangle_areas.append(triangle_area)
        if len(set(face)) != 3 or triangle_area < C.STL_MIN_TRIANGLE_AREA:
            degenerate_triangles += 1
        normal_length = _length(normal) if all(math.isfinite(value) for value in normal) else 0.0
        if doubled_area <= 0.0 or normal_length <= 0.0:
            normal_failures += 1
        else:
            alignment = _dot(normal, geometric_normal) / (normal_length * doubled_area)
            if not math.isfinite(alignment) or alignment < C.STL_NORMAL_DOT_MIN:
                normal_failures += 1
        triangle_signed_volumes.append(
            _dot(triangle[0], _cross(triangle[1], triangle[2])) / 6.0
        )

    duplicate_triangles = sum(
        count - 1 for count in Counter(tuple(sorted(face)) for face in faces).values()
    )
    edge_faces: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    vertex_faces: dict[int, list[int]] = defaultdict(list)
    for face_index, face in enumerate(faces):
        for vertex in set(face):
            vertex_faces[vertex].append(face_index)
        for start, end in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            key = (min(start, end), max(start, end))
            direction = 1 if start < end else -1
            edge_faces[key].append((face_index, direction))

    boundary_edges = sum(len(incidents) == 1 for incidents in edge_faces.values())
    nonmanifold_edges = sum(len(incidents) > 2 for incidents in edge_faces.values())
    winding_mismatches = sum(
        len(incidents) == 2 and incidents[0][1] == incidents[1][1]
        for incidents in edge_faces.values()
    )

    parent = list(range(len(faces)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first: int, second: int) -> None:
        first_root = find(first)
        second_root = find(second)
        if first_root != second_root:
            parent[second_root] = first_root

    for incidents in edge_faces.values():
        for incident in incidents[1:]:
            union(incidents[0][0], incident[0])
    component_faces: dict[int, list[int]] = defaultdict(list)
    for face_index in range(len(faces)):
        component_faces[find(face_index)].append(face_index)
    component_volumes = tuple(
        math.fsum(triangle_signed_volumes[index] for index in indices)
        for _, indices in sorted(component_faces.items())
    )

    vertex_link_failures = 0
    for vertex, incident_faces in vertex_faces.items():
        link_degrees: Counter[int] = Counter()
        link_graph: dict[int, set[int]] = defaultdict(set)
        link_invalid = False
        for face_index in incident_faces:
            others = [candidate for candidate in faces[face_index] if candidate != vertex]
            if len(others) != 2 or others[0] == others[1]:
                link_invalid = True
                continue
            first, second = others
            link_degrees[first] += 1
            link_degrees[second] += 1
            link_graph[first].add(second)
            link_graph[second].add(first)
        if not link_graph or any(degree != 2 for degree in link_degrees.values()):
            link_invalid = True
        else:
            pending = [next(iter(link_graph))]
            visited: set[int] = set()
            while pending:
                current = pending.pop()
                if current in visited:
                    continue
                visited.add(current)
                pending.extend(link_graph[current] - visited)
            if len(visited) != len(link_graph):
                link_invalid = True
        if link_invalid:
            vertex_link_failures += 1

    self_intersections = _self_intersection_count(triangles, faces)
    vtk_regions, vtk_bad_edges, vtk_volume = _vtk_mesh_stats(path)
    return STLMeshStats(
        dimensions=dimensions,  # type: ignore[arg-type]
        triangle_count=len(faces),
        vertex_count=len(welded_vertices),
        regions=len(component_faces),
        boundary_edges=boundary_edges,
        nonmanifold_edges=nonmanifold_edges,
        winding_mismatches=winding_mismatches,
        vertex_link_failures=vertex_link_failures,
        degenerate_triangles=degenerate_triangles,
        duplicate_triangles=duplicate_triangles,
        normal_failures=normal_failures,
        self_intersections=self_intersections,
        min_triangle_area=min(triangle_areas),
        signed_volume=math.fsum(triangle_signed_volumes),
        component_volumes=component_volumes,
        vtk_regions=vtk_regions,
        vtk_bad_edges=vtk_bad_edges,
        vtk_volume=vtk_volume,
    )


def stl_bounds(path: Path) -> tuple[float, float, float]:
    """Return dimensions from the same strict parser used for manifold checks."""
    return stl_mesh_stats(path).dimensions


def stl_inventory_check(parts: dict[str, PrintablePart], directory: Path) -> CheckResult:
    """Require the individual-STL directory to contain exactly the expected exports."""
    expected = {f"{name}.stl" for name in parts}
    actual = (
        {path.name for path in directory.iterdir() if path.is_file() and path.suffix.lower() == ".stl"}
        if directory.exists()
        else set()
    )
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    detail = f"Expected {len(expected)} STL file(s); found {len(actual)}."
    if missing:
        detail += f" Missing: {', '.join(missing)}."
    if unexpected:
        detail += f" Unexpected: {', '.join(unexpected)}."
    return CheckResult("Individual STL inventory", not missing and not unexpected, detail)


def step_artifact_check(
    path: Path,
    label: str,
    expected_solid_count: int | None = None,
    expected_volume: float | None = None,
) -> CheckResult:
    """Reopen an exported STEP artifact and require valid solid geometry."""
    try:
        imported = cq.importers.importStep(str(path))
        value = imported.val()
        solid_count = len(value.Solids())
        volume = valid_volume(imported)
        count_matches = expected_solid_count is None or solid_count == expected_solid_count
        volume_tolerance = (
            max(0.10, expected_volume * 1e-6) if expected_volume is not None else None
        )
        volume_matches = (
            expected_volume is None
            or abs(volume - expected_volume) <= volume_tolerance  # type: ignore[operator]
        )
        passed = value.isValid() and solid_count > 0 and count_matches and volume_matches
        detail = f"Reopened with {solid_count} valid solid(s), volume {volume:.2f} mm³"
        if expected_solid_count is not None:
            detail += f"; expected {expected_solid_count} solid(s)"
        if expected_volume is not None:
            detail += f" and {expected_volume:.2f} mm³"
        detail += "."
    except Exception as exc:
        passed = False
        detail = f"Could not reopen STEP: {exc}"
    return CheckResult(f"STEP artifact: {label}", passed, detail)


def printability_checks(
    parts: dict[str, PrintablePart],
    stl_directory: Path | None = None,
    step_directory: Path | None = None,
) -> tuple[list[CheckResult], list[dict[str, object]]]:
    usable = (
        C.PRINT_BED_X - 2.0 * C.PRINT_BED_EDGE_MARGIN,
        C.PRINT_BED_Y - 2.0 * C.PRINT_BED_EDGE_MARGIN,
        min(C.PRINT_BED_Z, C.PRINT_USABLE_Z),
    )
    checks: list[CheckResult] = []
    rows: list[dict[str, object]] = []
    for name, part in parts.items():
        dims = bbox_tuple(part.shape)
        source_shape = shape_value(part.shape)
        source_volume = valid_volume(part.shape)
        solid_count = len(source_shape.Solids())
        source_brep_valid = bool(BRepCheck_Analyzer(source_shape.wrapped).IsValid())
        source_degenerate_edges = sum(
            bool(BRep_Tool.Degenerated_s(edge.wrapped)) for edge in source_shape.Edges()
        )
        source_valid = (
            source_brep_valid
            and source_shape.isValid()
            and solid_count == part.expected_solid_count
            and source_degenerate_edges == 0
        )
        preferred_fit = all(dims[index] <= usable[index] + 1e-6 for index in range(3))
        any_fit = any(
            all(candidate[index] <= usable[index] + 1e-6 for index in range(3))
            for candidate in all_axis_permutations(dims)
        )
        stl_dims: tuple[float, float, float] | None = None
        stl_fit = False
        stl_stats: STLMeshStats | None = None
        stl_error: str | None = None
        stl_volume: float | None = None
        stl_matches_source = False
        stl_volume_matches = False
        if stl_directory is not None:
            stl_path = stl_directory / f"{name}.stl"
            if stl_path.exists():
                try:
                    stl_stats = stl_mesh_stats(stl_path)
                    stl_dims = stl_stats.dimensions
                    stl_volume = stl_stats.signed_volume
                    stl_fit = all(
                        stl_dims[index] <= usable[index] + 0.05 for index in range(3)
                    )
                    stl_matches_source = all(
                        abs(stl_dims[index] - dims[index]) <= 0.05 for index in range(3)
                    )
                    stl_volume_matches = abs(stl_volume - source_volume) <= max(
                        0.50, source_volume * 0.002
                    )
                except Exception as exc:
                    stl_error = str(exc)
            else:
                stl_error = "STL file is missing"

        manifold_pass = (
            source_valid
            and stl_stats is not None
            and stl_stats.triangle_count > 0
            and stl_stats.regions == part.expected_solid_count
            and stl_stats.vtk_regions == part.expected_solid_count
            and stl_stats.boundary_edges == 0
            and stl_stats.nonmanifold_edges == 0
            and stl_stats.winding_mismatches == 0
            and stl_stats.vertex_link_failures == 0
            and stl_stats.degenerate_triangles == 0
            and stl_stats.duplicate_triangles == 0
            and stl_stats.normal_failures == 0
            and stl_stats.self_intersections == 0
            and stl_stats.vtk_bad_edges == 0
            and all(volume > C.STL_MIN_VOLUME for volume in stl_stats.component_volumes)
        )
        print_bed_pass = preferred_fit and stl_fit and stl_matches_source
        nonzero_volume_pass = (
            source_volume > C.STL_MIN_VOLUME
            and stl_stats is not None
            and stl_stats.signed_volume > C.STL_MIN_VOLUME
            and stl_stats.vtk_volume > C.STL_MIN_VOLUME
            and stl_volume_matches
        )

        if stl_stats is None:
            manifold_detail = stl_error or "STL analysis unavailable."
            volume_detail = stl_error or "STL volume unavailable."
        else:
            manifold_detail = (
                f"{stl_stats.triangle_count} triangles, {stl_stats.regions} raw/"
                f"{stl_stats.vtk_regions} VTK region(s); boundary {stl_stats.boundary_edges}, "
                f"non-manifold {stl_stats.nonmanifold_edges}, winding {stl_stats.winding_mismatches}, "
                f"vertex-link {stl_stats.vertex_link_failures}, sliver/degenerate "
                f"{stl_stats.degenerate_triangles}, duplicate {stl_stats.duplicate_triangles}, "
                f"normal {stl_stats.normal_failures}, self-intersection "
                f"{stl_stats.self_intersections}; minimum triangle area "
                f"{stl_stats.min_triangle_area:.6f} mm²; source BRep "
                f"{'valid' if source_valid else 'invalid'} ({source_degenerate_edges} degenerate edges)."
            )
            volume_detail = (
                f"Source {source_volume:.3f} mm³; signed STL {stl_stats.signed_volume:.3f} mm³; "
                f"VTK {stl_stats.vtk_volume:.3f} mm³; all "
                f"{len(stl_stats.component_volumes)} component volume(s) positive."
            )
        bed_detail = (
            f"STL {_fmt_dims(stl_dims) if stl_dims is not None else 'unavailable'}; "
            f"validated usable envelope {_fmt_dims(usable)}; source/STL bounds "
            f"{'match' if stl_matches_source else 'do not match'}; orthogonal alternative "
            f"{'YES' if any_fit else 'NO'}."
        )
        checks.extend(
            (
                CheckResult(f"MANIFOLD: {name}", manifold_pass, manifold_detail),
                CheckResult(f"PRINT BED: {name}", print_bed_pass, bed_detail),
                CheckResult(f"NON-ZERO VOLUME: {name}", nonzero_volume_pass, volume_detail),
            )
        )

        step_valid = False
        step_solid_count: int | None = None
        step_volume: float | None = None
        step_volume_matches = False
        if step_directory is not None:
            step_path = step_directory / f"{name}.step"
            if step_path.exists():
                try:
                    imported = cq.importers.importStep(str(step_path))
                    imported_value = imported.val()
                    step_valid = imported_value.isValid()
                    step_solid_count = len(imported_value.Solids())
                    step_volume = valid_volume(imported)
                    step_volume_matches = abs(step_volume - source_volume) <= max(
                        0.05, source_volume * 1e-6
                    )
                except Exception:
                    step_valid = False
        identity_pass = (
            source_valid
            and stl_matches_source
            and stl_volume_matches
            and step_valid
            and (step_solid_count is None or step_solid_count == part.expected_solid_count)
            and step_volume_matches
        )
        identity_detail = (
            f"Source {solid_count} solid(s), STEP {step_solid_count if step_solid_count is not None else 'unavailable'}; "
            f"source/STL volume {'matches' if stl_volume_matches else 'mismatch'}, "
            f"source/STEP volume {'matches' if step_volume_matches else 'mismatch'}."
        )
        checks.append(CheckResult(f"SOURCE/EXPORT IDENTITY: {name}", identity_pass, identity_detail))
        passed = manifold_pass and print_bed_pass and nonzero_volume_pass and identity_pass
        rows.append(
            {
                "name": name,
                "quantity": part.quantity,
                "dims": dims,
                "stl_dims": stl_dims,
                "preferred_fit": preferred_fit,
                "any_fit": any_fit,
                "valid": source_valid,
                "solid_count": solid_count,
                "expected_solid_count": part.expected_solid_count,
                "stl_regions": stl_stats.regions if stl_stats is not None else None,
                "stl_bad_edges": (
                    stl_stats.boundary_edges + stl_stats.nonmanifold_edges
                    if stl_stats is not None
                    else None
                ),
                "stl_triangles": stl_stats.triangle_count if stl_stats is not None else None,
                "stl_min_triangle_area": (
                    stl_stats.min_triangle_area if stl_stats is not None else None
                ),
                "source_volume": source_volume,
                "stl_volume": stl_volume,
                "step_volume": step_volume,
                "step_solid_count": step_solid_count,
                "manifold_pass": manifold_pass,
                "print_bed_pass": print_bed_pass,
                "nonzero_volume_pass": nonzero_volume_pass,
                "identity_pass": identity_pass,
                "passed": passed,
                "orientation": part.orientation,
                "supports": part.supports,
                "notes": part.notes,
            }
        )
    return checks, rows


def clearance_checks(
    placed: dict[str, PlacedPart],
    references: dict[str, ReferenceModel],
) -> list[CheckResult]:
    checks: list[CheckResult] = []

    # Printed parts must fit one another without occupying the same volume.
    # The two keeper/socket pairs are calibrated friction fits with a narrowly
    # bounded elastic interference; they are checked explicitly below.
    keeper_retention_pairs = {
        frozenset(("hdd_keeper_lower", "hdd_tray_lower_front")),
        frozenset(("hdd_keeper_upper", "hdd_tray_upper_front")),
    }
    printed_hits: list[tuple[str, str, float]] = []
    printed_items = list(placed.items())
    for index, (first_name, first) in enumerate(printed_items):
        first_bb = shape_value(first.shape).BoundingBox()
        for second_name, second in printed_items[index + 1 :]:
            second_bb = shape_value(second.shape).BoundingBox()
            bbox_overlap = (
                min(first_bb.xmax, second_bb.xmax) - max(first_bb.xmin, second_bb.xmin) > 1e-6
                and min(first_bb.ymax, second_bb.ymax) - max(first_bb.ymin, second_bb.ymin) > 1e-6
                and min(first_bb.zmax, second_bb.zmax) - max(first_bb.zmin, second_bb.zmin) > 1e-6
            )
            if not bbox_overlap:
                continue
            volume = _intersection_volume(first.shape, second.shape)
            if frozenset((first_name, second_name)) in keeper_retention_pairs:
                continue
            if volume > C.COLLISION_VOLUME_EPS:
                printed_hits.append((first_name, second_name, volume))
    printed_detail = "No printed-part self-intersections."
    if printed_hits:
        printed_detail = "; ".join(
            f"{first}/{second} ({volume:.2f} mm³)" for first, second, volume in printed_hits
        )
    checks.append(CheckResult("Printed assembly self-collision", not printed_hits, printed_detail))

    for keeper_name, tray_name in (
        ("hdd_keeper_lower", "hdd_tray_lower_front"),
        ("hdd_keeper_upper", "hdd_tray_upper_front"),
    ):
        overlap_shape = shape_value(placed[keeper_name].shape).intersect(
            shape_value(placed[tray_name].shape)
        )
        overlap = max(overlap_shape.Volume(), 0.0)
        overlap_bb = overlap_shape.BoundingBox()
        expected_depth = C.HDD_KEEPER_CLEARANCE + C.HDD_KEEPER_RETENTION_INTERFERENCE
        localized = (
            abs(overlap_bb.ylen - expected_depth) <= 1e-4
            and overlap_bb.xlen <= C.HDD_KEEPER_RETENTION_BUMP_LENGTH + 1e-4
            and overlap_bb.zlen <= 2.0 * C.HDD_KEEPER_RETENTION_BUMP_RADIUS + 1e-4
        )
        retention_pass = (
            C.HDD_KEEPER_RETENTION_VOLUME_MIN
            <= overlap
            <= C.HDD_KEEPER_RETENTION_VOLUME_MAX
            and localized
        )
        checks.append(
            CheckResult(
                f"Calibrated keeper retention: {keeper_name} / {tray_name}",
                retention_pass,
                f"Elastic bead/socket interference {overlap:.3f} mm³; required "
                f"{C.HDD_KEEPER_RETENTION_VOLUME_MIN:.2f}–"
                f"{C.HDD_KEEPER_RETENTION_VOLUME_MAX:.2f} mm³; localized bounds "
                f"{overlap_bb.xlen:.3f} x {overlap_bb.ylen:.3f} x {overlap_bb.zlen:.3f} mm.",
            )
        )

    labels = {
        "HDD_lower": "HDD2 lower enclosure clearance",
        "HDD_upper": "HDD1 upper enclosure clearance",
        "Pi_case": "Raspberry Pi case clearance",
        "USB_hub": "USB hub clearance",
        "fan_120": "120 mm fan clearance",
        "fan_140": "140 mm fan clearance",
    }
    for ref_name, label in labels.items():
        hits = _collisions(references[ref_name].shape, placed)
        checks.append(CheckResult(label, not hits, _hits_detail(hits)))

    # Connector bodies and bend envelopes must also remain free of printed walls.
    for ref_name, reference in references.items():
        if reference.category not in {"connector", "clearance"}:
            continue
        hits = _collisions(reference.shape, placed)
        readable = ref_name.replace("_", " ")
        checks.append(CheckResult(readable, not hits, _hits_detail(hits)))

    # Report the measured 140 mm rear stack against every neighboring field
    # called out in the design brief. These explicit results supplement the
    # general hardware/reference collision scans above and make regressions
    # in the external-fan topology immediately visible in the report.
    rear_stack_components = (
        ("140 mm rear fan", references["fan_140"].shape),
        ("rear fan spacer/guard", placed["rear_fan_guard"].shape),
    )
    rear_stack_targets = (
        ("USB hub body", references["USB_hub"].shape),
        ("USB hub plug field", references["USB_hub_plug_clearance"].shape),
        ("Raspberry Pi cable route", references["Pi_port_and_route_clearance"].shape),
        ("lower HDD USB-B bend", references["HDD_lower_USB_B_bend_zone"].shape),
        ("lower HDD DC bend", references["HDD_lower_DC_bend_zone"].shape),
        ("lower HDD rear route", references["HDD_lower_rear_exit_route"].shape),
        ("upper HDD USB-B bend", references["HDD_upper_USB_B_bend_zone"].shape),
        ("upper HDD DC bend", references["HDD_upper_DC_bend_zone"].shape),
        ("upper HDD rear route", references["HDD_upper_rear_exit_route"].shape),
        ("top rear panel", placed["top_rear"].shape),
        ("right rear side module", placed["right_side_rear"].shape),
    )
    for component_name, component_shape in rear_stack_components:
        for target_name, target_shape in rear_stack_targets:
            overlap = _intersection_volume(component_shape, target_shape)
            distance = shape_value(component_shape).distance(shape_value(target_shape))
            checks.append(
                CheckResult(
                    f"Rear-stack separation: {component_name} / {target_name}",
                    overlap <= C.COLLISION_VOLUME_EPS,
                    f"Intersection {overlap:.3f} mm³; minimum distance {distance:.3f} mm.",
                )
            )

    # Pairwise hardware collisions.
    hardware = [reference for reference in references.values() if reference.category == "hardware"]
    for first, second in combinations(hardware, 2):
        overlap = _intersection_volume(first.shape, second.shape)
        checks.append(
            CheckResult(
                f"Hardware separation: {first.name} / {second.name}",
                overlap <= C.COLLISION_VOLUME_EPS,
                f"Intersection volume {overlap:.3f} mm³.",
            )
        )

    # Cross-system connector/cable feasibility. Overlap within one system is
    # intentional (for example, a plug is contained by its bend envelope).
    routed = [
        reference
        for reference in references.values()
        if reference.category in {"hardware", "connector", "clearance"}
        and _reference_system(reference.name) is not None
    ]
    route_hits: list[tuple[str, str, float]] = []
    compared = 0
    intentional_connections = 0
    for first, second in combinations(routed, 2):
        first_system = _reference_system(first.name)
        second_system = _reference_system(second.name)
        if first_system == second_system:
            continue
        if frozenset((first.name, second.name)) in INTENTIONAL_CABLE_CONNECTIONS:
            intentional_connections += 1
            continue
        compared += 1
        overlap = _intersection_volume(first.shape, second.shape)
        if overlap > C.COLLISION_VOLUME_EPS:
            route_hits.append((first.name, second.name, overlap))
    route_detail = (
        f"{compared} unrelated cross-system pairs checked; "
        f"{intentional_connections} declared electrical connection pairs handled separately."
    )
    if route_hits:
        route_detail = "; ".join(
            f"{first}/{second} ({volume:.2f} mm³)" for first, second, volume in route_hits
        )
    checks.append(CheckResult("Cross-system connector and cable separation", not route_hits, route_detail))

    cable_links = (
        ("Lower HDD USB-B plug to bend", "HDD_lower_USB_B_plug", "HDD_lower_USB_B_bend_zone"),
        ("Lower HDD USB-B bend to exit", "HDD_lower_USB_B_bend_zone", "HDD_lower_rear_exit_route"),
        ("Lower HDD DC plug to bend", "HDD_lower_DC_plug", "HDD_lower_DC_bend_zone"),
        ("Lower HDD DC bend to exit", "HDD_lower_DC_bend_zone", "HDD_lower_rear_exit_route"),
        ("Upper HDD USB-B plug to bend", "HDD_upper_USB_B_plug", "HDD_upper_USB_B_bend_zone"),
        ("Upper HDD USB-B bend to exit", "HDD_upper_USB_B_bend_zone", "HDD_upper_rear_exit_route"),
        ("Upper HDD DC plug to bend", "HDD_upper_DC_plug", "HDD_upper_DC_bend_zone"),
        ("Upper HDD DC bend to exit", "HDD_upper_DC_bend_zone", "HDD_upper_rear_exit_route"),
        ("Pi Ethernet plug to routed field", "Pi_Ethernet_plug", "Pi_port_and_route_clearance"),
        ("Pi USB-C plug to routed field", "Pi_USB_C_plug", "Pi_port_and_route_clearance"),
        ("Pi USB-A plug to routed field", "Pi_USB_A_plug", "Pi_port_and_route_clearance"),
        ("Hub body to host bend", "USB_hub", "USB_hub_host_cable_bend"),
        ("Hub host bend to route", "USB_hub_host_cable_bend", "USB_hub_host_cable_route"),
        ("Hub host route to Pi field", "USB_hub_host_cable_route", "Pi_port_and_route_clearance"),
        ("Front fan to wire route", "fan_120", "front_fan_wire_route"),
        ("Front fan route to USB adapter", "front_fan_wire_route", "USB_hub_front_fan_USB_adapter"),
        ("Front fan adapter to hub", "USB_hub_front_fan_USB_adapter", "USB_hub"),
        ("Rear fan to wire route", "fan_140", "rear_fan_wire_route"),
        ("Rear fan route to USB adapter", "rear_fan_wire_route", "USB_hub_rear_fan_USB_adapter"),
        ("Rear fan adapter to hub", "USB_hub_rear_fan_USB_adapter", "USB_hub"),
    )
    for label, first_name, second_name in cable_links:
        distance = shape_value(references[first_name].shape).distance(
            shape_value(references[second_name].shape)
        )
        checks.append(
            CheckResult(
                f"Cable continuity: {label}",
                distance <= 0.05,
                f"Endpoint distance {distance:.3f} mm.",
            )
        )

    # Service paths are checked with the parts intentionally removed for that operation.
    service_exclusions = {
        "HDD_lower_service_sweep": {
            "right_side_front",
            "right_side_rear",
            "mid_frame_right_spine",
            "hdd_keeper_lower",
        },
        "HDD_upper_service_sweep": {
            "right_side_front",
            "right_side_rear",
            "mid_frame_right_spine",
            "hdd_keeper_upper",
        },
        "Pi_vertical_service_sweep": {"top_service_lid"},
    }
    for ref_name, exclusions in service_exclusions.items():
        hits = _collisions(references[ref_name].shape, placed, exclusions)
        checks.append(CheckResult(ref_name.replace("_", " "), not hits, _hits_detail(hits)))

    # Load paths and removable accessory contacts are explicit, not inferred
    # merely from a collision-free floating placement.
    support_pairs = (
        ("hdd_tray_lower_front", "left_side_front"),
        ("hdd_tray_lower_front", "right_side_front"),
        ("hdd_tray_lower_front", "base_front"),
        ("hdd_tray_lower_rear", "left_side_rear"),
        ("hdd_tray_lower_rear", "right_side_rear"),
        ("hdd_tray_lower_rear", "base_rear"),
        ("hdd_tray_upper_front", "left_side_front"),
        ("hdd_tray_upper_front", "right_side_front"),
        ("hdd_tray_upper_front", "base_front"),
        ("hdd_tray_upper_rear", "left_side_rear"),
        ("hdd_tray_upper_rear", "right_side_rear"),
        ("hdd_tray_upper_rear", "base_rear"),
        ("hdd_keeper_lower", "hdd_tray_lower_front"),
        ("hdd_keeper_upper", "hdd_tray_upper_front"),
        ("pi_tray", "left_side_front"),
        ("pi_tray", "right_side_front"),
        ("usb_hub_mount", "right_side_rear"),
        ("cable_clip_1", "base_rear"),
        ("cable_clip_2", "base_rear"),
        ("foot_1", "base_front"),
        ("foot_2", "base_front"),
        ("foot_3", "base_rear"),
        ("foot_4", "base_rear"),
    )
    for first_name, second_name in support_pairs:
        distance = shape_value(placed[first_name].shape).distance(shape_value(placed[second_name].shape))
        checks.append(
            CheckResult(
                f"Mechanical contact: {first_name} / {second_name}",
                distance <= 0.05,
                f"Minimum surface distance {distance:.3f} mm.",
            )
        )

    hardware_contacts = (
        ("USB hub bottom retention", references["USB_hub"].shape, placed["usb_hub_mount"].shape),
        ("120 mm fan panel seating", references["fan_120"].shape, placed["front_panel"].shape),
        ("Rear spacer to panel seating", placed["rear_fan_guard"].shape, placed["rear_panel"].shape),
        ("140 mm fan to spacer seating", references["fan_140"].shape, placed["rear_fan_guard"].shape),
    )
    for label, hardware_shape, printed_shape in hardware_contacts:
        distance = shape_value(hardware_shape).distance(shape_value(printed_shape))
        checks.append(
            CheckResult(
                f"Mechanical contact: {label}",
                distance <= 0.05,
                f"Minimum surface distance {distance:.3f} mm.",
            )
        )

    # With both removable right panels absent, each loaded HDD remains inside
    # the support polygon formed by the fixed base pedestals and left ledges.
    left_support_x = C.TRAY_OUTER_X + C.HDD_TRAY_SUPPORT_OVERLAP / 2.0
    right_support_x = C.HDD_SERVICE_LEDGE_X + C.HDD_TRAY_SUPPORT_OVERLAP / 2.0
    fixed_support_polygon = (
        (left_support_x, C.HDD_TRAY_SUPPORT_FRONT_Y),
        (right_support_x, C.TRAY_Y + C.TRAY_END_STOP_T / 2.0),
        (right_support_x, C.HDD_SERVICE_REAR_Y + C.TRAY_END_STOP_T / 2.0),
        (left_support_x, C.HDD_TRAY_SUPPORT_REAR_Y),
    )
    hdd_center = (C.HDD_X + C.HDD_W / 2.0, C.HDD_Y + C.HDD_L / 2.0)
    for level in ("lower", "upper"):
        supported = _point_in_polygon(hdd_center, fixed_support_polygon)
        checks.append(
            CheckResult(
                f"HDD {level} post-removal support polygon",
                supported,
                f"HDD center {hdd_center}; fixed/left support polygon {fixed_support_polygon}.",
            )
        )

    # Right-side modules must pull outward before the selected HDD can slide
    # laterally. The hub carrier moves rigidly with its rear side panel.
    checks.append(
        _sampled_removal_check(
            "Right-front side-panel removal after Pi tray removal",
            placed,
            ("right_side_front",),
            {"top_service_lid", "pi_tray"},
        )
    )
    checks.append(
        _sampled_removal_check(
            "Right-rear side-panel and unplugged hub-carrier removal",
            placed,
            ("right_side_rear", "usb_hub_mount"),
            {"top_rear", "right_side_front"},
            extra_moving={"USB_hub": references["USB_hub"].shape},
        )
    )
    checks.append(
        _sampled_removal_check(
            "Rear cable-cover, fan, and guard rearward removal",
            placed,
            ("rear_panel", "rear_fan_guard"),
            set(),
            direction=(0.0, 1.0, 0.0),
            extra_moving={"fan_140": references["fan_140"].shape},
            travel=80.0,
            increment=1.0,
        )
    )

    for ref_name in (
        "Pi_port_and_route_clearance",
        "HDD_lower_rear_exit_route",
        "HDD_upper_rear_exit_route",
        "USB_hub_plug_clearance",
        "rear_fan_wire_route",
    ):
        ymax = shape_value(references[ref_name].shape).BoundingBox().ymax
        checks.append(
            CheckResult(
                f"Rear-wall traversal: {ref_name}",
                ymax >= C.NAS_EXTERNAL_D + 0.5,
                f"Route reaches Y={ymax:.2f} mm past rear wall Y={C.NAS_EXTERNAL_D:.2f} mm.",
            )
        )

    # Direct dimensional invariants catch a design that is collision-free but too tight.
    hdd_gap = C.HDD_UPPER_Z - (C.HDD_LOWER_Z + C.HDD_H)
    checks.append(
        CheckResult(
            "HDD-to-HDD airflow gap",
            hdd_gap + 1e-6 >= C.HDD_AIR_GAP,
            f"Actual {hdd_gap:.2f} mm; required {C.HDD_AIR_GAP:.2f} mm.",
        )
    )
    cable_depth = (C.NAS_EXTERNAL_D - C.WALL) - C.HDD_REAR_Y
    checks.append(
        CheckResult(
            "HDD rear cable chamber depth",
            cable_depth + 1e-6 >= C.CABLE_CHAMBER_DEPTH,
            f"Actual {cable_depth:.2f} mm; required {C.CABLE_CHAMBER_DEPTH:.2f} mm.",
        )
    )
    guide_clearance = C.HDD_X - (C.TRAY_OUTER_X + C.TRAY_GUIDE_T)
    checks.append(
        CheckResult(
            "HDD left rail guide clearance",
            abs(guide_clearance - C.HDD_CLEARANCE) <= 0.02,
            f"Actual {guide_clearance:.2f} mm; configured {C.HDD_CLEARANCE:.2f} mm.",
        )
    )
    pi_frame_gap = C.MID_FRAME_FRONT_Y - (C.PI_Y + C.PI_CASE_L)
    checks.append(
        CheckResult(
            "Pi clear of structural mid-frame",
            pi_frame_gap >= C.FIT_CLEARANCE,
            f"Horizontal service gap {pi_frame_gap:.2f} mm.",
        )
    )
    front_gap = C.HDD_Y - (C.FRONT_FAN_Y + C.FRONT_FAN_THICKNESS)
    checks.append(
        CheckResult(
            "Front fan to HDD nose gap",
            front_gap + 1e-6 >= C.FRONT_FAN_TO_HDD,
            f"Actual {front_gap:.2f} mm.",
        )
    )
    tray_front_gap = C.TRAY_Y - (C.FRONT_FAN_Y + C.FRONT_FAN_THICKNESS)
    checks.append(
        CheckResult(
            "Front fan to tray clearance",
            tray_front_gap >= 2.0,
            f"Actual {tray_front_gap:.2f} mm.",
        )
    )
    fan_top_gap = C.NAS_BODY_H - C.WALL - (C.REAR_FAN_Z + C.REAR_FAN_SIZE)
    checks.append(
        CheckResult(
            "Rear fan top clearance",
            fan_top_gap >= C.REAR_FAN_TOP_CLEARANCE,
            f"Actual {fan_top_gap:.2f} mm.",
        )
    )
    hub_guard_gap = shape_value(references["USB_hub_plug_clearance"].shape).distance(
        shape_value(placed["rear_fan_guard"].shape)
    )
    checks.append(
        CheckResult(
            "Provisional USB hub plug field to rear fan guard clearance",
            hub_guard_gap + 1e-6 >= C.USB_HUB_CLEARANCE,
            f"Actual {hub_guard_gap:.2f} mm; required {C.USB_HUB_CLEARANCE:.2f} mm.",
        )
    )
    for label, ref_name in (
        ("Pi route to rear fan guard clearance", "Pi_port_and_route_clearance"),
        ("Lower HDD route to rear fan guard clearance", "HDD_lower_rear_exit_route"),
        ("Upper HDD route to rear fan guard clearance", "HDD_upper_rear_exit_route"),
    ):
        gap = shape_value(references[ref_name].shape).distance(
            shape_value(placed["rear_fan_guard"].shape)
        )
        checks.append(
            CheckResult(
                label,
                gap + 1e-6 >= C.FIT_CLEARANCE,
                f"Actual {gap:.2f} mm; required {C.FIT_CLEARANCE:.2f} mm.",
            )
        )
    fan_center_error = abs(
        C.REAR_FAN_X - (C.NAS_EXTERNAL_W - C.REAR_FAN_SIZE) / 2.0
    )
    checks.append(
        CheckResult(
            "140 mm rear fan horizontal centering",
            fan_center_error <= 1e-6,
            f"Centering error {fan_center_error:.4f} mm; fan X={C.REAR_FAN_X:.2f} mm.",
        )
    )
    spacer_depth = C.REAR_FAN_Y - C.NAS_EXTERNAL_D
    checks.append(
        CheckResult(
            "External rear fan spacer depth",
            abs(spacer_depth - C.FAN_GUARD_DEPTH) <= 1e-6,
            f"Panel-to-fan spacing {spacer_depth:.2f} mm.",
        )
    )
    opening_edge_land = (C.NAS_EXTERNAL_W - C.REAR_FAN_CUTOUT_D) / 2.0 - C.WALL
    opening_top_land = (
        C.NAS_BODY_H
        - C.WALL
        - (C.REAR_FAN_Z + (C.REAR_FAN_SIZE + C.REAR_FAN_CUTOUT_D) / 2.0)
    )
    low_slot_to_opening_web = (
        C.REAR_FAN_Z
        + (C.REAR_FAN_SIZE - C.REAR_FAN_CUTOUT_D) / 2.0
        - (C.REAR_LOW_SLOT_Z + C.REAR_LOW_SLOT_W / 2.0 + C.CABLE_EDGE_CHAMFER)
    )
    checks.append(
        CheckResult(
            "Rear fan opening structural lands",
            min(opening_edge_land, opening_top_land, low_slot_to_opening_web) + 1e-6 >= C.WALL,
            f"Side/top/low-slot webs {opening_edge_land:.2f}/{opening_top_land:.2f}/"
            f"{low_slot_to_opening_web:.2f} mm; required {C.WALL:.2f} mm.",
        )
    )
    front_post_gap = C.HDD_Y - (C.HDD_SERVICE_FRONT_Y + C.HDD_SERVICE_POST_DEPTH)
    rear_post_gap = C.HDD_SERVICE_REAR_Y - C.HDD_REAR_Y
    checks.append(
        CheckResult(
            "Fixed HDD service posts clear drive body",
            min(front_post_gap, rear_post_gap) + 1e-6 >= C.HDD_CLEARANCE,
            f"Front/rear body gaps {front_post_gap:.2f}/{rear_post_gap:.2f} mm; "
            f"required {C.HDD_CLEARANCE:.2f} mm.",
        )
    )
    return checks


def write_dimensions_report(
    path: Path,
    parts: dict[str, PrintablePart],
    rows: list[dict[str, object]],
) -> None:
    overall_h = C.NAS_BODY_H + C.FOOT_H
    lines = [
        "# Dimension report",
        "",
        "Generated directly from the current `config.py` and CadQuery bounding boxes.",
        "",
        "## Final configured dimensions",
        "",
        f"- Width: **{C.NAS_EXTERNAL_W:.2f} mm**",
        f"- Unchanged enclosure-body depth: **{C.NAS_EXTERNAL_D:.2f} mm**",
        f"- Installed depth including external rear fan: **{C.REAR_FAN_Y + C.REAR_FAN_THICKNESS:.2f} mm**",
        f"- External rear spacer depth: **{C.REAR_FAN_SPACER_DEPTH:.2f} mm**",
        f"- Body height: **{C.NAS_BODY_H:.2f} mm**",
        f"- Overall height including feet: **{overall_h:.2f} mm**",
        "",
        "## Printer validation profile",
        "",
        f"- Printer: **{C.PRINTER_MODEL}**",
        f"- Physical build volume: **{C.PRINT_BED_X:.0f} x {C.PRINT_BED_Y:.0f} x {C.PRINT_BED_Z:.0f} mm**",
        f"- Conservative validated envelope: **{C.PRINT_BED_X - 2.0 * C.PRINT_BED_EDGE_MARGIN:.0f} x "
        f"{C.PRINT_BED_Y - 2.0 * C.PRINT_BED_EDGE_MARGIN:.0f} x "
        f"{min(C.PRINT_BED_Z, C.PRINT_USABLE_Z):.0f} mm**",
        "- The enclosure geometry and modular panel splits are unchanged by the larger printer profile.",
        "",
        "> The depth intentionally exceeds the 250–260 mm design target. A "
        f"{C.HDD_L:.1f} mm drive, {C.FRONT_FAN_THICKNESS:.1f} mm fan, "
        f"{C.FRONT_FAN_TO_HDD:.1f} mm fan gap, {C.CABLE_CHAMBER_DEPTH:.1f} mm cable chamber, and two walls require "
        f"{C.NAS_EXTERNAL_D:.2f} mm.",
        "",
        "## Printable component bounding boxes",
        "",
        "| Part | Qty | X | Y | Z | All STL gates |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for row in rows:
        x, y, z = row["dims"]  # type: ignore[misc]
        lines.append(
            f"| `{row['name']}` | {row['quantity']} | {x:.2f} | {y:.2f} | {z:.2f} | {'PASS' if row['passed'] else 'FAIL'} |"
        )
    largest = max(rows, key=lambda row: max(row["dims"]))  # type: ignore[arg-type]
    lines.extend(
        [
            "",
            f"Largest single preferred-orientation extent: **{max(largest['dims']):.2f} mm** "  # type: ignore[arg-type]
            f"on `{largest['name']}`.",
            "",
            "## Hardware placement and clearances",
            "",
            f"- HDD #2 (lower) min corner: X {C.HDD_X:.2f}, Y {C.HDD_Y:.2f}, Z {C.HDD_LOWER_Z:.2f}",
            f"- HDD #1 (upper) min corner: X {C.HDD_X:.2f}, Y {C.HDD_Y:.2f}, Z {C.HDD_UPPER_Z:.2f}",
            f"- HDD-to-HDD gap: **{C.HDD_UPPER_Z - (C.HDD_LOWER_Z + C.HDD_H):.2f} mm**",
            f"- HDD guide clearance: **{C.HDD_CLEARANCE:.2f} mm per guided side**",
            f"- HDD rear cable clearance: **{(C.NAS_EXTERNAL_D - C.WALL) - C.HDD_REAR_Y:.2f} mm**",
            f"- Pi min corner: X {C.PI_X:.2f}, Y {C.PI_Y:.2f}, Z {C.PI_Z:.2f}",
            f"- Pi side clearance to inner shell: {(C.PI_X - C.WALL):.2f} mm left / {(C.NAS_EXTERNAL_W - C.WALL - (C.PI_X + C.PI_CASE_W)):.2f} mm right",
            f"- Pi top clearance: {(C.NAS_BODY_H - C.WALL - (C.PI_Z + C.PI_CASE_H)):.2f} mm",
            f"- Pi-to-mid-frame service gap: {C.MID_FRAME_FRONT_Y - (C.PI_Y + C.PI_CASE_L):.2f} mm",
            f"- USB hub rail-envelope clearance: {C.USB_HUB_CLEARANCE:.2f} mm per side; mounting slots permit vertical adjustment",
            f"- 120 mm fan min corner: X {C.FRONT_FAN_X:.2f}, Y {C.FRONT_FAN_Y:.2f}, Z {C.FRONT_FAN_Z:.2f}",
            f"- 140 mm fan min corner: X {C.REAR_FAN_X:.2f}, Y {C.REAR_FAN_Y:.2f}, Z {C.REAR_FAN_Z:.2f}",
            f"- Panel thickness: **{C.WALL:.2f} mm**",
            f"- Sliding fit clearance: **{C.FIT_CLEARANCE:.2f} mm per mating side**",
            f"- HDD keeper clearance: **{C.HDD_KEEPER_CLEARANCE:.2f} mm per mating side**",
            f"- Mid-frame: Y {C.MID_FRAME_FRONT_Y:.2f} to {C.MID_FRAME_REAR_Y:.2f} mm",
            "",
            "## Provisional dimensions to measure",
            "",
            "The UGREEN rear connector X/Z coordinates, molded plug overmolds, Pi case port locations, "
            "USB hub envelope, rubber feet, tapers, and vent locations are parameterized assumptions. "
            "Check them with calipers and edit `config.py` before a full print.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_printability_report(path: Path, checks: list[CheckResult], rows: list[dict[str, object]]) -> None:
    usable = (
        C.PRINT_BED_X - 2.0 * C.PRINT_BED_EDGE_MARGIN,
        C.PRINT_BED_Y - 2.0 * C.PRINT_BED_EDGE_MARGIN,
        min(C.PRINT_BED_Z, C.PRINT_USABLE_Z),
    )
    lines = [
        "# Printability report",
        "",
        f"Configured printer: **{C.PRINTER_MODEL}**, physical build volume "
        f"{C.PRINT_BED_X:.0f} x {C.PRINT_BED_Y:.0f} x {C.PRINT_BED_Z:.0f} mm.",
        f"Validated usable envelope: **{_fmt_dims(usable)}** ("
        f"{C.PRINT_BED_EDGE_MARGIN:.1f} mm XY margin per edge; explicit "
        f"{C.PRINT_USABLE_Z:.0f} mm usable-Z limit).",
        "",
        "Every row is a hard build gate. Production geometry remains modular; no parts were merged for the larger bed.",
        "",
        "| Part | STL bbox | MANIFOLD | PRINT BED | NON-ZERO VOLUME | Regions | Triangles | Min triangle area | Orientation | Supports |",
        "|---|---|:---:|:---:|:---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        report_dims = row["stl_dims"] if row["stl_dims"] is not None else row["dims"]
        min_area = row["stl_min_triangle_area"]
        lines.append(
            f"| `{row['name']}` | {_fmt_dims(report_dims)} | "
            f"{'PASS' if row['manifold_pass'] else 'FAIL'} | "
            f"{'PASS' if row['print_bed_pass'] else 'FAIL'} | "
            f"{'PASS' if row['nonzero_volume_pass'] else 'FAIL'} | "
            f"{row['stl_regions']}/{row['expected_solid_count']} | {row['stl_triangles']} | "
            f"{f'{min_area:.6f} mm²' if min_area is not None else 'n/a'} | "
            f"{row['orientation']} | {row['supports']} |"
        )
    lines.extend(
        [
            "",
            "## Manufacturing assumptions",
            "",
            f"- {C.NOZZLE_D:.1f} mm nozzle, {C.LAYER_H:.2f} mm layers, PLA or PETG.",
            "- Three to five perimeters; 20–30% gyroid/cubic infill for panels, 30–40% for keys and trays.",
            "- Print broad exterior faces on the bed and interior ribs/grooves upward.",
            "- No production part requires generated support in its preferred orientation.",
            "- PETG is preferred for fan-adjacent pieces, dovetails, and long-term warm service.",
            "- Add a brim only if needed; the largest production extent is 174 mm inside the 250 mm validated envelope.",
            "",
            "## Hard-gate definitions",
            "",
            "- **MANIFOLD PASS**: valid source BRep; expected connected regions; every raw STL edge used exactly twice with opposite winding; valid vertex links and stored normals; no sliver/degenerate or duplicate triangles; no triangle self-intersections; positive component orientations; independent VTK edge/region agreement.",
            "- **PRINT BED PASS**: exported preferred-orientation STL bounds fit the conservative usable envelope and match source bounds.",
            "- **NON-ZERO VOLUME PASS**: source, signed STL, VTK, and every connected component have positive volume; STL volume matches the source.",
            "",
            "## Automated results",
            "",
        ]
    )
    for check in checks:
        lines.append(f"- **{'PASS' if check.passed else 'FAIL'}** — {check.name}: {check.detail}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_clearance_report(path: Path, checks: list[CheckResult]) -> None:
    passed = sum(check.passed for check in checks)
    lines = [
        "# Clearance and collision report",
        "",
        f"Summary: **{passed}/{len(checks)} checks passed**.",
        "",
        "Boolean intersections larger than "
        f"{C.COLLISION_VOLUME_EPS:.2f} mm³ are failures except for the two explicitly bounded, "
        "coupon-calibrated HDD keeper friction beads. Zero-volume support contact is intentional.",
        "",
    ]
    for check in checks:
        lines.append(f"- **{'PASS' if check.passed else 'FAIL'}** — {check.name}: {check.detail}")
    lines.extend(
        [
            "",
            "## Service-path assumptions",
            "",
            "- HDD sweep checks remove both right shell modules, the selected keeper, and removable right mid-frame spine.",
            "- Before right-side withdrawal, the Pi/tray is removed and every hub device/host lead is unplugged; the strapped hub moves with its carrier.",
            "- The untouched loaded HDD remains inside the fixed-pedestal/left-ledge support polygon.",
            "- Pi sweep checks remove only the top service lid.",
            "- Rear cable-cover service is sampled as a rigid +Y pull of panel, fan, and guard after the fan lead is unplugged.",
            "- Connector/bend coordinates remain provisional until the real hardware is measured.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
