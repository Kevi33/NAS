# Parametric Raspberry Pi 5 NAS enclosure

This repository is an executable CadQuery project for a modular, FDM-printable mini-NAS. It is configured for two UGREEN 50422 / US222 drive enclosures, a Raspberry Pi 5 in a provisional GeeekPi metal case, a provisional UGREEN 25851 USB hub, a 120 mm front intake fan, and a measured 140 mm rear exhaust fan.

The build creates real solids rather than a rendering-only mock-up: individual STEP/STL print files, named assembled/exploded/checking STEP models, fit coupons, automated geometry reports, and PNG previews.

## Current configured envelope

- Body: **146.0 x 291.1 x 174.0 mm** (W x D x H)
- Installed depth including the external rear fan: **326.1 mm**
- External rear fan spacer: **10.0 mm**
- Height including 6 mm feet: **180.0 mm**
- Drive rear cable chamber: **60.0 mm**
- HDD guide clearance: **1.25 mm per guided side**
- HDD-to-HDD airflow gap: **12.0 mm**
- Production joint clearance: **0.20 mm per mating side**, calibrated from the printed P1S fit coupon
- HDD keeper clearance: **0.00 mm per side**, calibrated from the printed retention coupon and isolated from the panel/dovetail setting

The 291.1 mm depth is deliberate. Two 2.8 mm walls, a 25 mm fan, a 6.5 mm fan/drive gap, a 194 mm drive, and a 60 mm cable chamber cannot fit the initial 250-260 mm styling target without sacrificing cable bend space.

The configured printer is a **Bambu Lab P1S** with a physical 256 x 256 x 256 mm build volume. Validation uses a conservative 3 mm XY margin and a 250 mm usable Z limit. The enclosure remains intentionally split and modular; the larger printer profile does not merge or enlarge any enclosure part.

## Install and regenerate

CadQuery 2.6.1 with 64-bit CPython 3.12 is the tested toolchain.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe build.py
```

To generate only the dedicated keeper-retention calibration model without touching enclosure exports, use:

```powershell
.\.venv\Scripts\python.exe build_keeper_retention_test.py
```

To regenerate only the two rear-fan printable parts plus affected assemblies and reports, while hash-protecting every unrelated export and slicer project, use:

```powershell
.\.venv\Scripts\python.exe build_rear_fan_update.py
```

On Linux/macOS, use `.venv/bin/python`. A good run ends with `BUILD RESULT: SUCCESS`; any source-solid, exported-mesh, STEP-reopen, print-bed, collision, cable-route, or service-path failure returns a non-zero exit code. The generator deletes only old files in its known output directories before rebuilding, so renamed artifacts cannot remain stale.

## Generated artifacts

```text
exports/
  individual/
    STL/                  # one printable source part per file
    STEP/
  assembly/
    NAS_Assembly.step
    NAS_Assembly.stl
    NAS_Assembly_preview.png
    NAS_Exploded.step
    NAS_Exploded.stl
    NAS_Exploded_preview.png
    NAS_Internal_Inspection.step
    NAS_Internal_Inspection.stl
    NAS_Internal_Inspection_preview.png
    NAS_Clearance_Check.step
  fit_tests/
    dovetail_fit_test.{stl,step}
    panel_key_fit_test.{stl,step}
    hdd_rail_fit_test.{stl,step}
    hdd_keeper_fit_test.{stl,step}
    hdd_keeper_retention_test.{stl,step}
    *_preview.png
reports/
  dimensions.md
  printability.md
  clearance_report.md
  hdd_keeper_retention_test_validation.md
```

The assembly, exploded, and cutaway `NAS_Internal_Inspection` STL files are disconnected inspection models containing printed and hardware solids. The cutaway omits the front, right side, and top shell modules to expose the internal relationships. Do not slice these inspection models as one print job. Use the individual STL files in the quantities listed in the dimension report.

## Parametric changes

Edit `config.py`, then rerun `build.py`; never hand-edit generated exports. Important uncertain dimensions are exposed centrally, including:

- `HDD_L`, `HDD_W`, `HDD_H`, clearances, and rear connector X/Z offsets
- `PI_CASE_L`, `PI_CASE_W`, `PI_CASE_H`, and Pi port/plug offsets
- `USB_HUB_L`, `USB_HUB_W`, `USB_HUB_H`, clearance, port offsets, and rear access envelope
- USB-B, DC, USB-A, Ethernet, USB-C, fan-adapter, and cable-bend envelopes
- `FIT_CLEARANCE`, the independent `HDD_KEEPER_CLEARANCE`, and all panel-key dimensions
- `PRINTER_MODEL`, `PRINT_BED_X`, `PRINT_BED_Y`, `PRINT_BED_Z`, `PRINT_USABLE_Z`, and `PRINT_BED_EDGE_MARGIN`

The case depth, module split, frame pockets, carrier locations, cable chamber, service sweeps, exports, and reports derive from these values. Because the real molded housings and plugs have not been measured, print the coupons and verify the report against caliper measurements before a full enclosure print.

## Mechanical layout and airflow

The 120 mm fan occupies the front/lower-middle region and blows rearward. Each HDD rests only on narrow edge rails, keeping the enclosure's underside heat-emission area open. Keyed side-panel ledges carry the split HDD cradles and the Pi tray; fixed front/rear base pedestals preserve a stable HDD support polygon while the right service panels are absent. Locator pockets prevent the carriers from wandering without permanently clamping the hardware.

The Pi sits above the drives and entirely ahead of the transverse structural C-frame. Air continues through the large frame opening into the rear cable chamber, then leaves through the centered 140 mm exhaust and passive base/side/top vents. The rear fan sits outside the original enclosure body on a shallow printed spacer/guard, preserving the fixed hub and cable chamber while keeping loose leads clear of the rotor.

The hub mounts vertically on a slotted rail carrier with a positive bottom stop and two strap stations in the right-rear chamber. Its four provisional rear-facing USB plug envelopes pass through a chamfered rear service opening, including two explicitly modeled fan USB-adapter bodies. If physical measurement shows the real port face differs, change the hub/port parameters before printing.

## Assembly and service order

1. Print all four calibration models first. Select the panel/joint clearance and confirm the real HDD nose in the rail slice.
2. Key `base_front` and `base_rear` into the structural `mid_frame`, then install the two left side modules. Leave the right service side open.
3. Join the lower front/rear skeletal cradle pair below its sliding surface, seat it on the left ledges and fixed base pedestals, install the lower HDD, and fit its load-shouldered keeper.
4. Repeat for the upper cradle and HDD. This lower-first order avoids trying to pass the lower drive through an installed upper tray.
5. Fasten the empty hub carrier to the right-rear module with M3 hardware and feed a removable strap through its slots. Slide both right modules into their capture rails and frame pockets, then fit the removable right frame spine.
6. Slide the front intake panel into its interrupted tongues. Insert the rear cable cover from behind in the forward direction. Install fans with proper fan screws or M4 through-bolts; do not rely on threads in a 2.8 mm panel.
7. Fit the fan guard, feet, and two floor cable clips. Lower the open Pi tray onto its four side ledges, then install and strap the Pi case.
8. Seat the USB hub against the carrier's bottom stop, secure its strap, and connect the low-voltage wiring. Keep every AC adapter outside the printed enclosure.
9. Fit `top_rear`, then the lift-off `top_service_lid` last to capture the side rails.

For Pi service, unplug it, remove only the front top service lid, and lift the case and tray vertically. For rear cable service, disconnect the 140 mm fan lead and pull the rear panel, external spacer/guard, and fan straight rearward (+Y); do not lift the panel against its interrupted tongues. Neither HDD needs to move.

For HDD service, remove both top modules, unplug and lift out the Pi and its tray, then disconnect all four hub device plugs and the hub host lead. The strapped hub may remain in its carrier. Remove both right side modules, the removable frame spine, and the selected drive's keeper; the selected HDD slides laterally to the right. The untouched loaded tray remains inside the support polygon formed by its left ledges and the fixed front/rear base pedestals.

## Fit coupons

- `dovetail_fit_test.stl`: five conventional long sliding-dovetail pairs at 0.20/0.25/0.30/0.35/0.40 mm per side.
- `panel_key_fit_test.stl`: the exact short planar key/pocket profile used by the production shell, at the same five clearances.
- `hdd_rail_fit_test.stl`: a 32 mm-deep full-width cradle slice for inserting the real UGREEN nose.
- `hdd_keeper_fit_test.stl`: the removable keeper and its supported rail socket.
- `hdd_keeper_retention_test.stl`: five production-faithful keeper/socket pairs at 0.00/0.05/0.10/0.15/0.20 mm keeper clearance, each with a broad rounded friction bead for light positive retention.

Labels give hundredths of a millimetre per mating side. On the keeper-retention coupon, match each loose keeper to the socket with the same label, orient its guide toward the open/outboard edge, and press it vertically down until both shoulders seat. After cooling, invert and lightly shake the pair, then confirm hand removal without tools. Use the smallest variant that seats by hand, does not rattle, and remains captured under gravity and light shaking.

The physically tested `00` variant is the current production keeper: its broad R1.0 friction bead provides light positive retention while remaining removable by hand. The HDD rail profile and the global panel/dovetail clearance remain independently calibrated and unchanged.

## Recommended FDM settings

- 0.4 mm nozzle; 0.20 mm layers
- 3-5 walls/perimeters; use 5 on frame, carrier, and joint-heavy parts
- 5 top and bottom layers
- 20-30% gyroid/cubic infill for panels; 30-40% for trays, frame, and keys
- PLA for cool prototypes; PETG preferred for joints, warm service, and fan-adjacent parts
- Use each part's preferred orientation in `reports/printability.md`; broad exterior faces go on the plate and internal ribs/open grooves face upward
- Generated supports: none in the preferred orientations
- Add a brim only if warping requires it; the largest production extent is 174 mm inside the conservative 250 mm usable envelope

## Automated validation

The build checks every production and fit-test model in its preferred orientation against the P1S profile: physical 256 x 256 x 256 mm, conservative validated envelope 250 x 250 x 250 mm. It does not use the larger bed to change the enclosure geometry or modular splits.

Every printable STL receives three independent hard gates in `reports/printability.md`: **MANIFOLD**, **PRINT BED**, and **NON-ZERO VOLUME**. The manifold audit checks connected regions, welded edge incidence, shared-edge winding, vertex-link topology, stored facet normals, degenerate and duplicate triangles, and the validity of the source BRep. Bounds, signed mesh volume, source/STEP volume identity, and the exact expected individual-STL inventory are also verified. Any failed gate makes `build.py` return a non-zero result.

The clearance suite checks printed-part self-intersections, hardware and cable volumes against printed parts, unrelated cross-system cable conflicts, intended endpoint continuity, positive fan/tray gaps, rear-wall route traversal, keyed mechanical contacts, loaded-HDD support polygons after panel removal, and sampled HDD/Pi/side/rear-cover service sweeps with only explicitly removable or unplugged items excluded. Details are in the three Markdown reports.

## Measurement cautions

The drive envelope and connector types follow the supplied brief. Public US222 documentation identifies USB 3.0 Type-B, a 5.5 mm 12 V DC input, a power control, and underside heat-emission openings. Reference pages: [US222 manual mirror](https://device.report/manual/6657570), [UGREEN Singapore product page](https://ugreen.com.sg/products/ugreen-usb-3-0-3-5inch-hard-drive-box-uk-plug), and [UGREEN 25851 page](https://www.ugreen.com/en-au/products/au-25851).

These sources do not replace caliper checks. Connector coordinates, plug overmolds, rubber feet, molded tapers, exact GeeekPi port locations, the hub's true port face, and fan-adapter bodies remain provisional. Treat the first build as an engineering prototype.

Verify each fan's nameplate voltage and current before powering it. Many PC fans are 12 V; a USB fan adapter must provide the fan's required voltage/current rather than merely adapting the connector shape.

## Source map

- `src/base.py`, `front.py`, `rear.py`, `left_panel.py`, `right_panel.py`, `top.py`: shell modules
- `src/mid_frame.py`: structural split hoop and removable HDD service spine
- `src/hdd_tray.py`, `pi_tray.py`, `usb_hub_mount.py`: removable hardware carriers
- `src/hardware_dummies.py`, `fans.py`: non-printable hardware, connector, cable, airflow, and service references
- `src/assembly.py`: exact placements, quantities, colors, and exploded transforms
- `src/validation.py`: source/export/bed/mesh/STEP/collision/service checks and reports
- `src/fit_tests.py`: calibration prints
- `build.py`: one-command artifact generator
