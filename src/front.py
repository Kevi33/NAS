"""Front intake panel with integrated high-free-area grille."""

import cadquery as cq

import config as C
from .common import PrintablePart, box_at, cylinder_at
from .side_panel_common import end_panel_tongue_shapes


PANEL_W = C.NAS_EXTERNAL_W - 2.0 * C.WALL
PANEL_H = C.NAS_BODY_H - 2.0 * C.WALL


def _edge_tongues(shape: cq.Workplane) -> cq.Workplane:
    for tongue in end_panel_tongue_shapes():
        shape = shape.union(tongue)
    return shape


def make_front_panel() -> cq.Workplane:
    shape = box_at(0.0, 0.0, 0.0, PANEL_W, PANEL_H, C.WALL)
    cx = C.FRONT_FAN_X + C.FRONT_FAN_SIZE / 2.0 - C.WALL
    cy = C.FRONT_FAN_Z + C.FRONT_FAN_SIZE / 2.0 - C.WALL
    opening = cylinder_at(C.FRONT_FAN_CUTOUT_D / 2.0, C.WALL + 0.2, (cx, cy, -0.1), (0.0, 0.0, 1.0))
    shape = shape.cut(opening)

    # Extend bars into the surrounding panel by 1.2 mm so each is a fused solid,
    # not merely a floating grille element inside the cutout.
    disk = cylinder_at(C.FRONT_FAN_CUTOUT_D / 2.0 + 1.2, C.WALL, (cx, cy, 0.0), (0.0, 0.0, 1.0))
    grille = None
    x = cx - C.FRONT_FAN_CUTOUT_D / 2.0 + C.GRILLE_PITCH
    while x < cx + C.FRONT_FAN_CUTOUT_D / 2.0:
        bar = box_at(x - C.GRILLE_BAR / 2.0, cy - C.FRONT_FAN_CUTOUT_D / 2.0, 0.0, C.GRILLE_BAR, C.FRONT_FAN_CUTOUT_D, C.WALL)
        bar = bar.intersect(disk)
        grille = bar if grille is None else grille.union(bar)
        x += C.GRILLE_PITCH
    if grille is not None:
        shape = shape.union(grille)

    half = C.FRONT_FAN_HOLE_SPACING / 2.0
    for x in (cx - half, cx + half):
        for y in (cy - half, cy + half):
            hole = cylinder_at(C.FAN_MOUNT_HOLE_D / 2.0, C.WALL + 0.2, (x, y, -0.1), (0.0, 0.0, 1.0))
            shape = shape.cut(hole)
    return _edge_tongues(shape)


def parts() -> list[PrintablePart]:
    return [
        PrintablePart(
            "front_panel",
            make_front_panel(),
            orientation="exterior grille face on bed; interior face up",
            notes="120 mm intake; vertical grille exceeds 65% nominal open area.",
        )
    ]
