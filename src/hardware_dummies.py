"""Simplified, non-printable hardware, connector, bend, and service envelopes."""

from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

import config as C
from .common import box_at, compound, cylinder_at
from .fans import fan_frame, rotor_disk


@dataclass(frozen=True)
class ReferenceModel:
    name: str
    shape: cq.Workplane
    color: tuple[float, float, float, float]
    category: str
    notes: str = ""


HARDWARE_COLORS = {
    "hdd": (0.15, 0.18, 0.22, 1.0),
    "pi": (0.55, 0.58, 0.62, 1.0),
    "hub": (0.08, 0.10, 0.12, 1.0),
    "fan": (0.05, 0.05, 0.06, 1.0),
    "connector": (0.15, 0.35, 0.75, 1.0),
    "clearance": (0.90, 0.20, 0.12, 0.35),
    "service": (0.98, 0.55, 0.08, 0.22),
    "airflow": (0.15, 0.70, 0.92, 0.20),
}


def _hdd(name: str, z: float) -> ReferenceModel:
    body = box_at(C.HDD_X, C.HDD_Y, z, C.HDD_W, C.HDD_L, C.HDD_H)
    return ReferenceModel(name, body, HARDWARE_COLORS["hdd"], "hardware")


def _fan(name: str, x: float, y: float, z: float, size: float, thickness: float) -> ReferenceModel:
    frame = fan_frame(x, y, z, size, thickness)
    rotor = rotor_disk(x, y, z, size, thickness)
    return ReferenceModel(
        name,
        cq.Workplane(obj=compound([frame, rotor])),
        HARDWARE_COLORS["fan"],
        "hardware",
    )


def nominal_hardware() -> dict[str, ReferenceModel]:
    return {
        "HDD_lower": _hdd("HDD_lower", C.HDD_LOWER_Z),
        "HDD_upper": _hdd("HDD_upper", C.HDD_UPPER_Z),
        "Pi_case": ReferenceModel(
            "Pi_case",
            box_at(C.PI_X, C.PI_Y, C.PI_Z, C.PI_CASE_W, C.PI_CASE_L, C.PI_CASE_H),
            HARDWARE_COLORS["pi"],
            "hardware",
        ),
        "USB_hub": ReferenceModel(
            "USB_hub",
            box_at(C.USB_HUB_X, C.USB_HUB_Y, C.USB_HUB_Z, C.USB_HUB_W, C.USB_HUB_H, C.USB_HUB_L),
            HARDWARE_COLORS["hub"],
            "hardware",
        ),
        "fan_120": _fan(
            "fan_120", C.FRONT_FAN_X, C.FRONT_FAN_Y, C.FRONT_FAN_Z, C.FRONT_FAN_SIZE, C.FRONT_FAN_THICKNESS
        ),
        "fan_80": _fan(
            "fan_80", C.REAR_FAN_X, C.REAR_FAN_Y, C.REAR_FAN_Z, C.REAR_FAN_SIZE, C.REAR_FAN_THICKNESS
        ),
    }


def connector_models() -> dict[str, ReferenceModel]:
    items: dict[str, ReferenceModel] = {}
    for label, z in (("lower", C.HDD_LOWER_Z), ("upper", C.HDD_UPPER_Z)):
        usb_x = C.HDD_X + C.HDD_USB_B_X_FROM_LEFT - C.HDD_USB_B_PLUG_W / 2.0
        usb_z = z + C.HDD_USB_B_Z_FROM_BOTTOM - C.HDD_USB_B_PLUG_H / 2.0
        items[f"HDD_{label}_USB_B_plug"] = ReferenceModel(
            f"HDD_{label}_USB_B_plug",
            box_at(usb_x, C.HDD_REAR_Y, usb_z, C.HDD_USB_B_PLUG_W, C.HDD_USB_B_PLUG_L, C.HDD_USB_B_PLUG_H),
            HARDWARE_COLORS["connector"],
            "connector",
        )
        dc_x = C.HDD_X + C.HDD_DC_X_FROM_LEFT - C.HDD_DC_PLUG_D / 2.0
        dc_z = z + C.HDD_DC_Z_FROM_BOTTOM - C.HDD_DC_PLUG_D / 2.0
        items[f"HDD_{label}_DC_plug"] = ReferenceModel(
            f"HDD_{label}_DC_plug",
            box_at(dc_x, C.HDD_REAR_Y, dc_z, C.HDD_DC_PLUG_D, C.HDD_DC_PLUG_L, C.HDD_DC_PLUG_D),
            HARDWARE_COLORS["connector"],
            "connector",
        )

    pi_rear = C.PI_Y + C.PI_CASE_L
    items["Pi_Ethernet_plug"] = ReferenceModel(
        "Pi_Ethernet_plug",
        box_at(
            C.PI_X + C.PI_ETHERNET_X_FROM_LEFT,
            pi_rear,
            C.PI_Z + C.PI_ETHERNET_Z_FROM_BOTTOM,
            C.PI_ETHERNET_PLUG_W,
            C.PI_ETHERNET_PLUG_L,
            C.PI_ETHERNET_PLUG_H,
        ),
        HARDWARE_COLORS["connector"],
        "connector",
    )
    items["Pi_USB_C_plug"] = ReferenceModel(
        "Pi_USB_C_plug",
        box_at(
            C.PI_X + C.PI_POWER_X_FROM_LEFT,
            pi_rear,
            C.PI_Z + C.PI_POWER_Z_FROM_BOTTOM,
            C.PI_POWER_PLUG_W,
            C.PI_POWER_PLUG_L,
            C.PI_POWER_PLUG_H,
        ),
        HARDWARE_COLORS["connector"],
        "connector",
    )
    items["Pi_USB_A_plug"] = ReferenceModel(
        "Pi_USB_A_plug",
        box_at(
            C.PI_X + C.PI_USB_X_FROM_LEFT,
            pi_rear,
            C.PI_Z + C.PI_USB_Z_FROM_BOTTOM,
            C.PI_USB_PLUG_W,
            C.PI_USB_PLUG_L,
            C.PI_USB_PLUG_H,
        ),
        HARDWARE_COLORS["connector"],
        "connector",
    )
    return items


def clearance_models() -> dict[str, ReferenceModel]:
    items: dict[str, ReferenceModel] = {}
    for label, z in (("lower", C.HDD_LOWER_Z), ("upper", C.HDD_UPPER_Z)):
        usb_x = C.HDD_X + C.HDD_USB_B_X_FROM_LEFT - C.HDD_USB_B_BEND_W / 2.0
        usb_z = z + C.HDD_USB_B_Z_FROM_BOTTOM - C.HDD_USB_B_BEND_H / 2.0
        items[f"HDD_{label}_USB_B_bend_zone"] = ReferenceModel(
            f"HDD_{label}_USB_B_bend_zone",
            box_at(usb_x, C.HDD_REAR_Y, usb_z, C.HDD_USB_B_BEND_W, C.HDD_USB_B_BEND_L, C.HDD_USB_B_BEND_H),
            HARDWARE_COLORS["clearance"],
            "clearance",
            "Straight plug plus gradual downward/side bend envelope.",
        )
        dc_x = C.HDD_X + C.HDD_DC_X_FROM_LEFT - C.HDD_DC_BEND_W / 2.0
        dc_z = z + C.HDD_DC_Z_FROM_BOTTOM - C.HDD_DC_BEND_H / 2.0
        items[f"HDD_{label}_DC_bend_zone"] = ReferenceModel(
            f"HDD_{label}_DC_bend_zone",
            box_at(dc_x, C.HDD_REAR_Y, dc_z, C.HDD_DC_BEND_W, C.HDD_DC_BEND_L, C.HDD_DC_BEND_H),
            HARDWARE_COLORS["clearance"],
            "clearance",
        )
        switch_x = C.HDD_X + C.HDD_SWITCH_X_FROM_LEFT - C.HDD_SWITCH_ACCESS_D / 2.0
        switch_z = z + C.HDD_SWITCH_Z_FROM_BOTTOM - C.HDD_SWITCH_ACCESS_D / 2.0
        items[f"HDD_{label}_switch_access"] = ReferenceModel(
            f"HDD_{label}_switch_access",
            box_at(
                switch_x,
                C.HDD_REAR_Y,
                switch_z,
                C.HDD_SWITCH_ACCESS_D,
                C.HDD_SWITCH_ACCESS_L,
                C.HDD_SWITCH_ACCESS_D,
            ),
            HARDWARE_COLORS["clearance"],
            "clearance",
        )

    # Pi connectors first extend rearward, then route left of the exhaust fan.
    pi_route1 = box_at(
        C.PI_X + C.PI_ROUTE_BODY_SIDE_INSET,
        C.PI_Y + C.PI_CASE_L,
        C.PI_Z + C.PI_ROUTE_BODY_Z_OFFSET,
        C.PI_CASE_W - 2.0 * C.PI_ROUTE_BODY_SIDE_INSET,
        C.PI_ROUTE_INITIAL_L,
        C.PI_ROUTE_INITIAL_H,
    )
    route_turn_y = C.REAR_FAN_Y - C.FAN_GUARD_DEPTH - C.PI_ROUTE_FAN_GUARD_GAP
    route2_y = C.PI_Y + C.PI_CASE_L + C.PI_ROUTE_INITIAL_L - C.PI_ROUTE_TURN_OVERLAP
    pi_route2 = box_at(
        C.PI_CABLE_ROUTE_X,
        route2_y,
        C.PI_CABLE_ROUTE_Z,
        C.PI_X + C.PI_CASE_W - C.PI_CABLE_ROUTE_X,
        route_turn_y - route2_y,
        C.PI_CABLE_ROUTE_H,
    )
    pi_route3 = box_at(
        C.PI_CABLE_ROUTE_X,
        route_turn_y,
        C.PI_CABLE_ROUTE_Z,
        C.PI_CABLE_ROUTE_W,
        C.NAS_EXTERNAL_D + C.ROUTE_REAR_PROJECTION - route_turn_y,
        C.PI_CABLE_ROUTE_H,
    )
    items["Pi_port_and_route_clearance"] = ReferenceModel(
        "Pi_port_and_route_clearance",
        cq.Workplane(obj=compound([pi_route1, pi_route2, pi_route3])),
        HARDWARE_COLORS["clearance"],
        "clearance",
    )

    hub_plug_shapes: list[cq.Workplane] = []
    plug_zone_w = C.USB_A_PLUG_W + 2.0 * C.USB_PLUG_ZONE_MARGIN
    plug_zone_h = C.USB_A_PLUG_H + 2.0 * C.USB_PLUG_ZONE_MARGIN
    for z_offset in C.USB_HUB_PORT_Z_OFFSETS:
        hub_plug_shapes.append(
            box_at(
                C.USB_HUB_X + (C.USB_HUB_W - plug_zone_w) / 2.0,
                C.USB_HUB_Y + C.USB_HUB_H,
                C.USB_HUB_Z + z_offset - plug_zone_h / 2.0,
                plug_zone_w,
                C.USB_PLUG_PROJECTION,
                plug_zone_h,
            )
        )
    hub_plugs = cq.Workplane(obj=compound(hub_plug_shapes))
    items["USB_hub_plug_clearance"] = ReferenceModel(
        "USB_hub_plug_clearance", hub_plugs, HARDWARE_COLORS["clearance"], "clearance"
    )
    for label, port_index in zip(("front", "rear"), C.FAN_USB_ADAPTER_PORT_INDICES):
        z_offset = C.USB_HUB_PORT_Z_OFFSETS[port_index]
        items[f"USB_hub_{label}_fan_USB_adapter"] = ReferenceModel(
            f"USB_hub_{label}_fan_USB_adapter",
            box_at(
                C.USB_HUB_X + (C.USB_HUB_W - C.FAN_USB_ADAPTER_W) / 2.0,
                C.USB_HUB_Y + C.USB_HUB_H,
                C.USB_HUB_Z + z_offset - C.FAN_USB_ADAPTER_H / 2.0,
                C.FAN_USB_ADAPTER_W,
                C.FAN_USB_ADAPTER_L,
                C.FAN_USB_ADAPTER_H,
            ),
            HARDWARE_COLORS["connector"],
            "clearance",
            "Provisional USB fan-adapter plug envelope; verify the real adapter body.",
        )
    items["USB_hub_host_cable_bend"] = ReferenceModel(
        "USB_hub_host_cable_bend",
        box_at(
            C.USB_HUB_X - C.USB_HUB_HOST_BEND_W / 2.0,
            C.USB_HUB_Y - C.USB_HUB_HOST_BEND_L,
            C.USB_HUB_Z - C.USB_HUB_HOST_BEND_H / 2.0,
            C.USB_HUB_HOST_BEND_W,
            C.USB_HUB_HOST_BEND_L,
            C.USB_HUB_HOST_BEND_H,
        ),
        HARDWARE_COLORS["clearance"],
        "clearance",
    )

    # Checked continuations through the two low rear cable openings.
    exit_y = C.NAS_EXTERNAL_D - C.WALL - C.REAR_EXIT_INNER_Y_OFFSET
    lower_exit = box_at(
        C.HDD_LOWER_EXIT_X,
        exit_y,
        C.HDD_LOWER_EXIT_Z,
        C.HDD_LOWER_EXIT_W,
        C.HDD_EXIT_ROUTE_DEPTH,
        C.HDD_LOWER_EXIT_H,
    )
    lower_feed_y = C.HDD_REAR_Y + C.HDD_LOWER_FEED_Y_OFFSET
    lower_feed = box_at(
        C.HDD_LOWER_FEED_X,
        lower_feed_y,
        C.HDD_LOWER_FEED_Z,
        C.HDD_LOWER_FEED_W,
        exit_y - lower_feed_y,
        C.HDD_LOWER_FEED_H,
    )
    lower_cross = box_at(
        C.HDD_LOWER_CROSS_X,
        C.HDD_REAR_Y + C.HDD_LOWER_CROSS_Y_OFFSET,
        C.HDD_LOWER_CROSS_Z,
        C.HDD_LOWER_CROSS_W,
        C.HDD_LOWER_CROSS_L,
        C.HDD_LOWER_CROSS_H,
    )
    items["HDD_lower_rear_exit_route"] = ReferenceModel(
        "HDD_lower_rear_exit_route",
        cq.Workplane(obj=compound([lower_cross, lower_feed, lower_exit])),
        HARDWARE_COLORS["clearance"],
        "clearance",
    )
    upper_drop = box_at(
        C.HDD_UPPER_DROP_X,
        C.HDD_REAR_Y + C.HDD_UPPER_DROP_Y_OFFSET,
        C.HDD_UPPER_DROP_Z,
        C.HDD_UPPER_DROP_W,
        C.HDD_UPPER_DROP_L,
        C.HDD_UPPER_DROP_H,
    )
    upper_exit = box_at(
        C.HDD_UPPER_EXIT_X,
        exit_y,
        C.HDD_UPPER_EXIT_Z,
        C.HDD_UPPER_EXIT_W,
        C.HDD_EXIT_ROUTE_DEPTH,
        C.HDD_UPPER_EXIT_H,
    )
    upper_usb_bend_xmax = (
        C.HDD_X + C.HDD_USB_B_X_FROM_LEFT + C.HDD_USB_B_BEND_W / 2.0
    )
    upper_usb_bridge = box_at(
        upper_usb_bend_xmax,
        C.HDD_REAR_Y + C.HDD_UPPER_USB_BRIDGE_Y_OFFSET,
        C.HDD_UPPER_USB_BRIDGE_Z,
        C.HDD_UPPER_DROP_X - upper_usb_bend_xmax,
        C.HDD_UPPER_USB_BRIDGE_L,
        C.HDD_UPPER_USB_BRIDGE_H,
    )
    items["HDD_upper_rear_exit_route"] = ReferenceModel(
        "HDD_upper_rear_exit_route",
        cq.Workplane(obj=compound([upper_drop, upper_exit, upper_usb_bridge])),
        HARDWARE_COLORS["clearance"],
        "clearance",
    )
    front_wire = box_at(
        C.FRONT_FAN_WIRE_X,
        C.FRONT_FAN_WIRE_Y,
        C.FRONT_FAN_WIRE_Z,
        C.FRONT_FAN_WIRE_W,
        C.USB_HUB_Y - C.FRONT_FAN_WIRE_Y,
        C.FRONT_FAN_WIRE_H,
    )
    front_elbow = box_at(
        C.FRONT_FAN_ELBOW_X,
        C.USB_HUB_Y,
        C.FRONT_FAN_WIRE_Z,
        C.FRONT_FAN_ELBOW_W,
        C.FRONT_FAN_ELBOW_L,
        C.FRONT_FAN_WIRE_H,
    )
    front_adapter_z0 = (
        C.USB_HUB_Z
        + C.USB_HUB_PORT_Z_OFFSETS[C.FAN_USB_ADAPTER_PORT_INDICES[0]]
        - C.FAN_USB_ADAPTER_H / 2.0
    )
    front_riser = box_at(
        C.FRONT_FAN_RISER_X,
        C.USB_HUB_Y + C.USB_HUB_H,
        C.FRONT_FAN_WIRE_Z,
        C.FRONT_FAN_RISER_W,
        C.FRONT_FAN_RISER_L,
        front_adapter_z0 + C.FAN_ROUTE_TOP_H - C.FRONT_FAN_WIRE_Z,
    )
    front_adapter_x0 = C.USB_HUB_X + (C.USB_HUB_W - C.FAN_USB_ADAPTER_W) / 2.0
    front_top = box_at(
        C.FRONT_FAN_RISER_X + C.FRONT_FAN_RISER_W,
        C.USB_HUB_Y + C.USB_HUB_H,
        front_adapter_z0,
        front_adapter_x0 - (C.FRONT_FAN_RISER_X + C.FRONT_FAN_RISER_W),
        C.FRONT_FAN_RISER_L,
        C.FAN_ROUTE_TOP_H,
    )
    items["front_fan_wire_route"] = ReferenceModel(
        "front_fan_wire_route",
        cq.Workplane(obj=compound([front_wire, front_elbow, front_riser, front_top])),
        HARDWARE_COLORS["clearance"],
        "clearance",
    )
    rear_link = box_at(
        C.REAR_FAN_LINK_X,
        C.REAR_FAN_Y - C.FAN_GUARD_DEPTH,
        C.REAR_FAN_WIRE_Z,
        C.FAN_WIRE_ZONE_W,
        C.FAN_GUARD_DEPTH,
        C.FAN_WIRE_ZONE_H,
    )
    rear_drop = box_at(
        C.REAR_FAN_LINK_X,
        C.REAR_FAN_ROUTE_UNDER_Y,
        C.REAR_FAN_ROUTE_UNDER_Z,
        C.FAN_WIRE_ZONE_W,
        C.REAR_FAN_Y - C.FAN_GUARD_DEPTH - C.REAR_FAN_ROUTE_UNDER_Y,
        C.REAR_FAN_WIRE_Z + C.FAN_WIRE_ZONE_H - C.REAR_FAN_ROUTE_UNDER_Z,
    )
    rear_under = box_at(
        C.REAR_FAN_ROUTE_UNDER_X,
        C.REAR_FAN_ROUTE_UNDER_Y,
        C.REAR_FAN_ROUTE_UNDER_Z,
        C.REAR_FAN_ROUTE_UNDER_W,
        C.REAR_FAN_ROUTE_UNDER_L,
        C.REAR_FAN_ROUTE_UNDER_H,
    )
    rear_adapter_z0 = (
        C.USB_HUB_Z
        + C.USB_HUB_PORT_Z_OFFSETS[C.FAN_USB_ADAPTER_PORT_INDICES[1]]
        - C.FAN_USB_ADAPTER_H / 2.0
    )
    rear_riser = box_at(
        C.REAR_FAN_RISER_X,
        C.REAR_FAN_RISER_Y,
        C.REAR_FAN_ROUTE_UNDER_Z,
        C.REAR_FAN_RISER_W,
        C.REAR_FAN_RISER_L,
        rear_adapter_z0 + C.FAN_ROUTE_TOP_H - C.REAR_FAN_ROUTE_UNDER_Z,
    )
    rear_under_link = box_at(
        C.REAR_FAN_RISER_X,
        C.REAR_FAN_ROUTE_UNDER_Y + C.REAR_FAN_ROUTE_UNDER_L,
        C.REAR_FAN_ROUTE_UNDER_Z,
        C.REAR_FAN_RISER_W,
        C.REAR_FAN_UNDER_LINK_L,
        C.REAR_FAN_ROUTE_UNDER_H,
    )
    rear_adapter_x1 = (
        C.USB_HUB_X + (C.USB_HUB_W + C.FAN_USB_ADAPTER_W) / 2.0
    )
    rear_top = box_at(
        rear_adapter_x1,
        C.REAR_FAN_RISER_Y,
        rear_adapter_z0,
        C.REAR_FAN_RISER_X + C.REAR_FAN_RISER_W - rear_adapter_x1,
        C.REAR_FAN_RISER_L,
        C.FAN_ROUTE_TOP_H,
    )
    items["rear_fan_wire_route"] = ReferenceModel(
        "rear_fan_wire_route",
        cq.Workplane(
            obj=compound(
                [rear_link, rear_drop, rear_under, rear_under_link, rear_riser, rear_top]
            )
        ),
        HARDWARE_COLORS["clearance"],
        "clearance",
    )

    hub_host_cross = box_at(
        C.HUB_HOST_ROUTE_CROSS_X,
        C.HUB_HOST_ROUTE_CROSS_Y,
        C.HUB_HOST_ROUTE_CROSS_Z,
        C.HUB_HOST_ROUTE_CROSS_W,
        C.HUB_HOST_ROUTE_CROSS_L,
        C.HUB_HOST_ROUTE_CROSS_H,
    )
    hub_host_riser = box_at(
        C.HUB_HOST_ROUTE_RISER_X,
        C.HUB_HOST_ROUTE_RISER_Y,
        C.HUB_HOST_ROUTE_RISER_Z,
        C.HUB_HOST_ROUTE_RISER_W,
        C.HUB_HOST_ROUTE_RISER_L,
        C.HUB_HOST_ROUTE_RISER_H,
    )
    items["USB_hub_host_cable_route"] = ReferenceModel(
        "USB_hub_host_cable_route",
        cq.Workplane(obj=compound([hub_host_cross, hub_host_riser])),
        HARDWARE_COLORS["clearance"],
        "clearance",
    )

    items["cable_chamber"] = ReferenceModel(
        "cable_chamber",
        box_at(
            C.WALL + C.MID_FRAME_RING,
            C.HDD_REAR_Y,
            C.WALL + 2.0,
            C.NAS_EXTERNAL_W - 2.0 * (C.WALL + C.MID_FRAME_RING),
            C.CABLE_CHAMBER_DEPTH,
            C.NAS_BODY_H - 2.0 * C.WALL - 4.0,
        ),
        HARDWARE_COLORS["airflow"],
        "clearance_display",
    )
    return items


def service_models() -> dict[str, ReferenceModel]:
    hdd_sweep_w = C.NAS_EXTERNAL_W + 22.0 - C.HDD_X
    items = {
        "HDD_lower_service_sweep": ReferenceModel(
            "HDD_lower_service_sweep",
            box_at(C.HDD_X, C.HDD_Y, C.HDD_LOWER_Z, hdd_sweep_w, C.HDD_L, C.HDD_H),
            HARDWARE_COLORS["service"],
            "service",
        ),
        "HDD_upper_service_sweep": ReferenceModel(
            "HDD_upper_service_sweep",
            box_at(C.HDD_X, C.HDD_Y, C.HDD_UPPER_Z, hdd_sweep_w, C.HDD_L, C.HDD_H),
            HARDWARE_COLORS["service"],
            "service",
        ),
        "Pi_vertical_service_sweep": ReferenceModel(
            "Pi_vertical_service_sweep",
            box_at(C.PI_X, C.PI_Y, C.PI_Z, C.PI_CASE_W, C.PI_CASE_L, C.NAS_BODY_H + 24.0 - C.PI_Z),
            HARDWARE_COLORS["service"],
            "service",
        ),
        "HDD_air_gap": ReferenceModel(
            "HDD_air_gap",
            box_at(C.HDD_X, C.HDD_Y, C.HDD_LOWER_Z + C.HDD_H, C.HDD_W, C.HDD_L, C.HDD_AIR_GAP),
            HARDWARE_COLORS["airflow"],
            "clearance_display",
        ),
    }
    return items


def all_references(include_clearances: bool = False, include_service: bool = False) -> dict[str, ReferenceModel]:
    items = nominal_hardware()
    items.update(connector_models())
    if include_clearances:
        items.update(clearance_models())
    if include_service:
        items.update(service_models())
    return items
