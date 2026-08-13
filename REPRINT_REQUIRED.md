# Production reprint decision

This decision applies to parts printed before the 2026-08-13 full production-export audit. The authoritative manufacturing files are the regenerated files in `exports/individual/STL/`; preserved slicer-project (`.3mf`) files are not regenerated or covered by the production identity gate.

## Must reprint

| Part | Decision | Reason |
|---|---|---|
| `right_side_front` | **REPRINT REQUIRED** | The old STL was the left-hand part. It reached the intended right-side assembly pose only through a forbidden reflection in `assembly.py`. The new STL contains the physical right hand. |
| `right_side_rear` | **REPRINT REQUIRED** | The old STL was not the physical right hand. The new STL contains the right-hand ledges/keys plus the two USB-hub carrier holes. |
| `usb_hub_mount` | **REPRINT REQUIRED** | The audit found both former M3 slots entirely inside the open center window, leaving no carrier bearing material at either screw. The corrected carrier adds two compact, slotted back bridges without moving the hub or fastener axes. |

## Previously printed parts that remain valid

| Part | Decision | Compatibility note |
|---|---|---|
| `base_front` | Valid | Production geometry unchanged. |
| `base_rear` | Valid | Production geometry unchanged. |
| `front_panel` | Valid | 120 mm intake geometry unchanged. |
| `rear_panel` | Valid | Current 140 mm production geometry unchanged by this audit. |
| `rear_fan_guard` | Valid if it is the current 140 mm part | Current production geometry remains 140 x 140 x 10 mm. See the stale-3MF warning below. |
| `left_side_front` | Valid | Production geometry unchanged. |
| `left_side_rear` | Valid, including the earlier holed print | The new source omits two unused hub holes. The earlier holed left panel is a strict material subset with unchanged mating envelopes, keys, and ledges, so it remains compatible. |
| `top_service_lid` | Valid | STL geometry unchanged; assembly placement now expresses the same pose with a physical 180-degree rotation. |
| `top_rear` | Valid | STL geometry unchanged; assembly placement now expresses the same pose with a physical 180-degree rotation. |
| `mid_frame` | Valid | Production geometry unchanged. |
| `mid_frame_right_spine` | Valid | Production geometry unchanged. |
| `hdd_tray_front` | Valid | Rail and tray geometry unchanged. |
| `hdd_tray_rear` | Valid | Rail and tray geometry unchanged. |
| `hdd_keeper` | Valid | Calibrated 0.00 mm keeper geometry unchanged. |
| `pi_tray` | Valid | Production geometry unchanged. |
| `cable_clip` | Valid | Production geometry unchanged. |
| `foot` | Valid | Production geometry unchanged. |

## Preserved slicer-project warning

- `exports/individual/STL/rear_fan_guard.3mf` contains the obsolete 80 x 80 x 8 mm guard, not the current 140 x 140 x 10 mm production part. A guard printed from that file must be reprinted from `rear_fan_guard.stl`.
- `exports/individual/STL/usb_hub_mount.3mf` contains the old carrier without usable fastener bridges. Do not print it; use the regenerated `usb_hub_mount.stl`.
- `exports/individual/STL/hdd_tray_front.3mf` is a multi-object slicer project that also embeds the old hub-carrier mesh. It is not an authoritative single-part export.

In total, 3 of the 20 production part types require replacement; the other 17 remain compatible under the conditions above.
