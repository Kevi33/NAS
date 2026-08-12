# HDD keeper retention test validation

This focused build does not regenerate or modify enclosure artifacts.

## Test matrix

| Label | Clearance per side | Friction-bead projection | Net positive interference |
|---:|---:|---:|---:|
| 00 | 0.00 mm | 0.10 mm | 0.10 mm |
| 05 | 0.05 mm | 0.20 mm | 0.10 mm |
| 10 | 0.10 mm | 0.30 mm | 0.10 mm |
| 15 | 0.15 mm | 0.40 mm | 0.10 mm |
| 20 | 0.20 mm | 0.50 mm | 0.10 mm |

The broad rounded bead is fused into the keeper body; there are no thin snap tabs. Each variant has the same nominal 0.10 mm positive preload after its opposite flat face shifts against the socket wall.

## Export validation

- Exported bounds: **122.20 x 32.00 x 9.00 mm**
- Expected connected solids: **10**
- **PASS** — MANIFOLD: hdd_keeper_retention_test: 4120 triangles, 10 raw/10 VTK region(s); boundary 0, non-manifold 0, winding 0, vertex-link 0, sliver/degenerate 0, duplicate 0, normal 0, self-intersection 0; minimum triangle area 0.001690 mm²; source BRep valid (0 degenerate edges).
- **PASS** — PRINT BED: hdd_keeper_retention_test: STL 122.20 × 32.00 × 9.00 mm; validated usable envelope 250.00 × 250.00 × 250.00 mm; source/STL bounds match; orthogonal alternative YES.
- **PASS** — NON-ZERO VOLUME: hdd_keeper_retention_test: Source 5305.564 mm³; signed STL 5305.563 mm³; VTK 5305.563 mm³; all 10 component volume(s) positive.
- **PASS** — SOURCE/EXPORT IDENTITY: hdd_keeper_retention_test: Source 10 solid(s), STEP 10; source/STL volume matches, source/STEP volume matches.

## Physical test

1. Print the exported STL flat with labels and keeper guides upward, using the final filament/profile.
2. Match each loose keeper to the socket with the same 00/05/10/15/20 label.
3. Face the guide toward the open/outboard side and press vertically until both shoulders seat.
4. After cooling, invert and lightly shake; reject any variant that drops or rattles noticeably.
5. Confirm the keeper can still be removed by hand without tools or damage.
