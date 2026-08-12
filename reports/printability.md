# Printability report

Configured printer: **Bambu Lab P1S**, physical build volume 256 x 256 x 256 mm.
Validated usable envelope: **250.00 × 250.00 × 250.00 mm** (3.0 mm XY margin per edge; explicit 250 mm usable-Z limit).

Every row is a hard build gate. Production geometry remains modular; no parts were merged for the larger bed.

| Part | STL bbox | MANIFOLD | PRINT BED | NON-ZERO VOLUME | Regions | Triangles | Min triangle area | Orientation | Supports |
|---|---|:---:|:---:|:---:|---:|---:|---:|---|---|
| `base_front` | 146.00 × 145.55 × 60.00 mm | PASS | PASS | PASS | 1/1 | 2912 | 0.126908 mm² | largest flat face on bed; detail side up | none |
| `base_rear` | 146.00 × 145.55 × 60.00 mm | PASS | PASS | PASS | 1/1 | 4984 | 0.076438 mm² | largest flat face on bed; detail side up | none |
| `foot` | 16.00 × 16.00 × 6.00 mm | PASS | PASS | PASS | 1/1 | 672 | 0.381389 mm² | largest flat face on bed; detail side up | none |
| `front_panel` | 143.20 × 168.40 × 2.80 mm | PASS | PASS | PASS | 1/1 | 1840 | 0.235548 mm² | exterior grille face on bed; interior face up | none |
| `rear_panel` | 143.20 × 168.40 × 2.80 mm | PASS | PASS | PASS | 1/1 | 4600 | 0.207570 mm² | exterior face on bed; grille and tongues upward | none |
| `rear_fan_guard` | 80.00 × 80.00 × 8.00 mm | PASS | PASS | PASS | 1/1 | 1052 | 0.046946 mm² | largest flat face on bed; detail side up | none |
| `left_side_front` | 145.55 × 168.40 × 13.85 mm | PASS | PASS | PASS | 1/1 | 2336 | 0.126908 mm² | largest flat face on bed; detail side up | none |
| `left_side_rear` | 145.55 × 168.40 × 13.85 mm | PASS | PASS | PASS | 1/1 | 2952 | 0.177968 mm² | largest flat face on bed; detail side up | none |
| `right_side_front` | 145.55 × 168.40 × 13.85 mm | PASS | PASS | PASS | 1/1 | 2336 | 0.126908 mm² | largest flat face on bed; detail side up | none |
| `right_side_rear` | 145.55 × 168.40 × 13.85 mm | PASS | PASS | PASS | 1/1 | 2952 | 0.177968 mm² | largest flat face on bed; detail side up | none |
| `top_service_lid` | 146.00 × 145.55 × 6.80 mm | PASS | PASS | PASS | 1/1 | 3264 | 0.038662 mm² | largest flat face on bed; detail side up | none |
| `top_rear` | 146.00 × 145.55 × 6.80 mm | PASS | PASS | PASS | 1/1 | 3224 | 0.126908 mm² | largest flat face on bed; detail side up | none |
| `mid_frame` | 146.00 × 174.00 × 8.00 mm | PASS | PASS | PASS | 1/1 | 548 | 0.071106 mm² | broad face on bed | none |
| `mid_frame_right_spine` | 8.00 × 164.00 × 8.00 mm | PASS | PASS | PASS | 1/1 | 92 | 0.759999 mm² | largest flat face on bed; detail side up | none |
| `hdd_tray_front` | 124.30 × 107.25 × 9.00 mm | PASS | PASS | PASS | 1/1 | 148 | 1.200000 mm² | largest flat face on bed; detail side up | none |
| `hdd_tray_rear` | 124.30 × 101.25 × 9.00 mm | PASS | PASS | PASS | 1/1 | 110 | 0.080000 mm² | largest flat face on bed; detail side up | none |
| `hdd_keeper` | 8.00 × 16.00 × 9.00 mm | PASS | PASS | PASS | 1/1 | 76 | 0.001689 mm² | largest flat face on bed; detail side up | none |
| `pi_tray` | 128.00 × 95.00 × 8.00 mm | PASS | PASS | PASS | 1/1 | 184 | 1.619998 mm² | largest flat face on bed; detail side up | none |
| `usb_hub_mount` | 19.00 × 119.00 × 7.00 mm | PASS | PASS | PASS | 1/1 | 1484 | 0.036454 mm² | largest flat face on bed; detail side up | none |
| `cable_clip` | 12.80 × 10.00 × 15.20 mm | PASS | PASS | PASS | 1/1 | 384 | 0.157981 mm² | either broad XZ face on bed; cable opening visible from above | none |
| `dovetail_fit_test` | 154.00 × 66.00 × 6.50 mm | PASS | PASS | PASS | 10/10 | 2116 | 0.011250 mm² | flat coupon base on bed; labels and joint openings upward | none |
| `panel_key_fit_test` | 152.00 × 50.00 × 3.30 mm | PASS | PASS | PASS | 10/10 | 2056 | 0.011250 mm² | flat coupon base on bed; labels and joint openings upward | none |
| `hdd_rail_fit_test` | 124.30 × 32.00 × 9.00 mm | PASS | PASS | PASS | 1/1 | 52 | 7.200000 mm² | flat coupon base on bed; labels and joint openings upward | none |
| `hdd_keeper_fit_test` | 26.40 × 32.00 × 9.00 mm | PASS | PASS | PASS | 2/2 | 504 | 0.001690 mm² | flat coupon base on bed; labels and joint openings upward | none |
| `hdd_keeper_retention_test` | 122.20 × 32.00 × 9.00 mm | PASS | PASS | PASS | 10/10 | 4120 | 0.001690 mm² | flat coupon base on bed; labels and joint openings upward | none |

## Manufacturing assumptions

- 0.4 mm nozzle, 0.20 mm layers, PLA or PETG.
- Three to five perimeters; 20–30% gyroid/cubic infill for panels, 30–40% for keys and trays.
- Print broad exterior faces on the bed and interior ribs/grooves upward.
- No production part requires generated support in its preferred orientation.
- PETG is preferred for fan-adjacent pieces, dovetails, and long-term warm service.
- Add a brim only if needed; the largest production extent is 174 mm inside the 250 mm validated envelope.

## Hard-gate definitions

- **MANIFOLD PASS**: valid source BRep; expected connected regions; every raw STL edge used exactly twice with opposite winding; valid vertex links and stored normals; no sliver/degenerate or duplicate triangles; no triangle self-intersections; positive component orientations; independent VTK edge/region agreement.
- **PRINT BED PASS**: exported preferred-orientation STL bounds fit the conservative usable envelope and match source bounds.
- **NON-ZERO VOLUME PASS**: source, signed STL, VTK, and every connected component have positive volume; STL volume matches the source.

## Automated results

- **PASS** — Individual STL inventory: Expected 20 STL file(s); found 20.
- **PASS** — MANIFOLD: base_front: 2912 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.126908 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: base_front: STL 146.00 × 145.55 × 60.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: base_front: Source 60069.908 mm³; signed STL 60070.393 mm³; VTK 60070.393 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: base_front: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: base_rear: 4984 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.076438 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: base_rear: STL 146.00 × 145.55 × 60.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: base_rear: Source 59430.321 mm³; signed STL 59430.985 mm³; VTK 59430.985 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: base_rear: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: foot: 672 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.381389 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: foot: STL 16.00 × 16.00 × 6.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: foot: Source 1151.896 mm³; signed STL 1150.823 mm³; VTK 1150.823 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: foot: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: front_panel: 1840 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.235548 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: front_panel: STL 143.20 × 168.40 × 2.80 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: front_panel: Source 46208.734 mm³; signed STL 46223.722 mm³; VTK 46223.722 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: front_panel: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: rear_panel: 4600 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.207570 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: rear_panel: STL 143.20 × 168.40 × 2.80 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: rear_panel: Source 44734.924 mm³; signed STL 44748.367 mm³; VTK 44748.367 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: rear_panel: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: rear_fan_guard: 1052 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.046946 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: rear_fan_guard: STL 80.00 × 80.00 × 8.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: rear_fan_guard: Source 10728.222 mm³; signed STL 10728.562 mm³; VTK 10728.562 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: rear_fan_guard: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: left_side_front: 2336 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.126908 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: left_side_front: STL 145.55 × 168.40 × 13.85 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: left_side_front: Source 64939.447 mm³; signed STL 64939.888 mm³; VTK 64939.888 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: left_side_front: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: left_side_rear: 2952 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.177968 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: left_side_rear: STL 145.55 × 168.40 × 13.85 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: left_side_rear: Source 64090.204 mm³; signed STL 64090.691 mm³; VTK 64090.691 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: left_side_rear: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: right_side_front: 2336 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.126908 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: right_side_front: STL 145.55 × 168.40 × 13.85 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: right_side_front: Source 64939.447 mm³; signed STL 64939.888 mm³; VTK 64939.888 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: right_side_front: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: right_side_rear: 2952 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.177968 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: right_side_rear: STL 145.55 × 168.40 × 13.85 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: right_side_rear: Source 64090.204 mm³; signed STL 64090.691 mm³; VTK 64090.691 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: right_side_rear: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: top_service_lid: 3264 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.038662 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: top_service_lid: STL 146.00 × 145.55 × 6.80 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: top_service_lid: Source 55597.935 mm³; signed STL 55598.632 mm³; VTK 55598.632 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: top_service_lid: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: top_rear: 3224 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.126908 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: top_rear: STL 146.00 × 145.55 × 6.80 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: top_rear: Source 55858.087 mm³; signed STL 55858.748 mm³; VTK 55858.748 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: top_rear: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: mid_frame: 548 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.071106 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: mid_frame: STL 146.00 × 174.00 × 8.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: mid_frame: Source 26165.120 mm³; signed STL 26165.120 mm³; VTK 26165.120 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: mid_frame: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: mid_frame_right_spine: 92 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.759999 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: mid_frame_right_spine: STL 8.00 × 164.00 × 8.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: mid_frame_right_spine: Source 9565.760 mm³; signed STL 9565.760 mm³; VTK 9565.760 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: mid_frame_right_spine: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: hdd_tray_front: 148 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 1.200000 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: hdd_tray_front: STL 124.30 × 107.25 × 9.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: hdd_tray_front: Source 7485.820 mm³; signed STL 7485.820 mm³; VTK 7485.820 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: hdd_tray_front: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: hdd_tray_rear: 110 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.080000 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: hdd_tray_rear: STL 124.30 × 101.25 × 9.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: hdd_tray_rear: Source 7125.383 mm³; signed STL 7125.383 mm³; VTK 7125.383 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: hdd_tray_rear: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: hdd_keeper: 76 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.001689 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: hdd_keeper: STL 8.00 × 16.00 × 9.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: hdd_keeper: Source 468.685 mm³; signed STL 468.685 mm³; VTK 468.685 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: hdd_keeper: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: pi_tray: 184 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 1.619998 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: pi_tray: STL 128.00 × 95.00 × 8.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: pi_tray: Source 11835.840 mm³; signed STL 11835.840 mm³; VTK 11835.840 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: pi_tray: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: usb_hub_mount: 1484 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.036454 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: usb_hub_mount: STL 19.00 × 119.00 × 7.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: usb_hub_mount: Source 3384.844 mm³; signed STL 3384.872 mm³; VTK 3384.872 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: usb_hub_mount: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: cable_clip: 384 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.157981 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: cable_clip: STL 12.80 × 10.00 × 15.20 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: cable_clip: Source 1166.020 mm³; signed STL 1166.061 mm³; VTK 1166.061 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: cable_clip: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: dovetail_fit_test: 2116 triangles, 10 raw/10 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.011250 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: dovetail_fit_test: STL 154.00 × 66.00 × 6.50 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: dovetail_fit_test: Source 19392.067 mm³; signed STL 19392.067 mm³; VTK 19392.067 mm³; all 10 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: dovetail_fit_test: Source 10 solid(s), STEP 10; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: panel_key_fit_test: 2056 triangles, 10 raw/10 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.011250 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: panel_key_fit_test: STL 152.00 × 50.00 × 3.30 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: panel_key_fit_test: Source 10296.973 mm³; signed STL 10296.973 mm³; VTK 10296.973 mm³; all 10 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: panel_key_fit_test: Source 10 solid(s), STEP 10; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: hdd_rail_fit_test: 52 triangles, 1 raw/1 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 7.200000 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: hdd_rail_fit_test: STL 124.30 × 32.00 × 9.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: hdd_rail_fit_test: Source 3216.300 mm³; signed STL 3216.300 mm³; VTK 3216.300 mm³; all 1 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: hdd_rail_fit_test: Source 1 solid(s), STEP 1; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: hdd_keeper_fit_test: 504 triangles, 2 raw/2 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.001690 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: hdd_keeper_fit_test: STL 26.40 × 32.00 × 9.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: hdd_keeper_fit_test: Source 1069.765 mm³; signed STL 1069.765 mm³; VTK 1069.765 mm³; all 2 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: hdd_keeper_fit_test: Source 2 solid(s), STEP 2; source/STL volume matches, source/STEP volume matches.
- **PASS** — MANIFOLD: hdd_keeper_retention_test: 4120 triangles, 10 raw/10 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.001690 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: hdd_keeper_retention_test: STL 122.20 × 32.00 × 9.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: hdd_keeper_retention_test: Source 5305.564 mm³; signed STL 5305.563 mm³; VTK 5305.563 mm³; all 10 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: hdd_keeper_retention_test: Source 10 solid(s), STEP 10; source/STL volume matches, source/STEP volume matches.
- **PASS** — STEP artifact: NAS_Assembly: Reopened with 42 valid solid(s), volume 2997185.73 mm³; expected 42 solid(s) and 2997185.73 mm³.
- **PASS** — STEP artifact: NAS_Exploded: Reopened with 42 valid solid(s), volume 2997185.73 mm³; expected 42 solid(s) and 2997185.73 mm³.
- **PASS** — STEP artifact: NAS_Internal_Inspection: Reopened with 37 valid solid(s), volume 2710491.32 mm³; expected 37 solid(s) and 2710491.32 mm³.
- **PASS** — STEP artifact: NAS_Clearance_Check: Reopened with 81 valid solid(s), volume 7724697.89 mm³; expected 81 solid(s) and 7724697.89 mm³.
