# Dimension report

Generated directly from the current `config.py` and CadQuery bounding boxes.

## Final NAS external dimensions

- Width: **146.00 mm**
- Depth: **291.10 mm**
- Body height: **174.00 mm**
- Overall height including feet: **180.00 mm**

## Printer validation profile

- Printer: **Bambu Lab P1S**
- Physical build volume: **256 x 256 x 256 mm**
- Conservative validated envelope: **250 x 250 x 250 mm**
- The enclosure geometry and modular panel splits are unchanged by the larger printer profile.

> The depth intentionally exceeds the 250–260 mm design target. A 194.0 mm drive, 25.0 mm fan, 6.5 mm fan gap, 60.0 mm cable chamber, and two walls require 291.10 mm.

## Printable component bounding boxes

| Part | Qty | X | Y | Z | All STL gates |
|---|---:|---:|---:|---:|:---:|
| `base_front` | 1 | 146.00 | 145.55 | 60.00 | PASS |
| `base_rear` | 1 | 146.00 | 145.55 | 60.00 | PASS |
| `foot` | 4 | 16.00 | 16.00 | 6.00 | PASS |
| `front_panel` | 1 | 143.20 | 168.40 | 2.80 | PASS |
| `rear_panel` | 1 | 143.20 | 168.40 | 2.80 | PASS |
| `rear_fan_guard` | 1 | 80.00 | 80.00 | 8.00 | PASS |
| `left_side_front` | 1 | 145.55 | 168.40 | 13.85 | PASS |
| `left_side_rear` | 1 | 145.55 | 168.40 | 13.85 | PASS |
| `right_side_front` | 1 | 145.55 | 168.40 | 13.85 | PASS |
| `right_side_rear` | 1 | 145.55 | 168.40 | 13.85 | PASS |
| `top_service_lid` | 1 | 146.00 | 145.55 | 6.80 | PASS |
| `top_rear` | 1 | 146.00 | 145.55 | 6.80 | PASS |
| `mid_frame` | 1 | 146.00 | 174.00 | 8.00 | PASS |
| `mid_frame_right_spine` | 1 | 8.00 | 164.00 | 8.00 | PASS |
| `hdd_tray_front` | 2 | 124.30 | 107.25 | 9.00 | PASS |
| `hdd_tray_rear` | 2 | 124.30 | 101.25 | 9.00 | PASS |
| `hdd_keeper` | 2 | 7.70 | 15.40 | 9.00 | PASS |
| `pi_tray` | 1 | 128.00 | 95.00 | 8.00 | PASS |
| `usb_hub_mount` | 1 | 19.00 | 119.00 | 7.00 | PASS |
| `cable_clip` | 2 | 12.80 | 10.00 | 15.20 | PASS |
| `dovetail_fit_test` | 1 | 154.00 | 66.00 | 6.50 | PASS |
| `panel_key_fit_test` | 1 | 152.00 | 50.00 | 3.30 | PASS |
| `hdd_rail_fit_test` | 1 | 124.30 | 32.00 | 9.00 | PASS |
| `hdd_keeper_fit_test` | 1 | 26.10 | 32.00 | 9.00 | PASS |

Largest single preferred-orientation extent: **174.00 mm** on `mid_frame`.

## Hardware placement and clearances

- HDD #2 (lower) min corner: X 14.50, Y 34.30, Z 13.00
- HDD #1 (upper) min corner: X 14.50, Y 34.30, Z 63.00
- HDD-to-HDD gap: **12.00 mm**
- HDD guide clearance: **1.25 mm per guided side**
- HDD rear cable clearance: **60.00 mm**
- Pi min corner: X 40.00, Y 44.30, Z 113.00
- Pi side clearance to inner shell: 37.20 mm left / 37.20 mm right
- Pi top clearance: 18.20 mm
- Pi-to-mid-frame service gap: 5.25 mm
- USB hub rail-envelope clearance: 1.50 mm per side; mounting slots permit vertical adjustment
- 120 mm fan min corner: X 13.00, Y 2.80, Z 27.00
- 80 mm fan min corner: X 26.50, Y 263.30, Z 89.20
- Panel thickness: **2.80 mm**
- Sliding fit clearance: **0.30 mm per mating side**
- Mid-frame: Y 141.55 to 149.55 mm

## Provisional dimensions to measure

The UGREEN rear connector X/Z coordinates, molded plug overmolds, Pi case port locations, USB hub envelope, rubber feet, tapers, and vent locations are parameterized assumptions. Check them with calipers and edit `config.py` before a full print.
