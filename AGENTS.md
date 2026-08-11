# CAD project working notes

- Use `config.py` for all hardware, fit, printer, cable, and structural dimensions.
- The configured printer is a Bambu Lab P1S (256 mm physical cube); validate with 3 mm XY margins and a conservative 250 mm usable Z height without merging the modular panels.
- Run the complete generator with `.venv/Scripts/python.exe build.py` on Windows.
- Do not hand-edit generated files under `exports/` or `reports/`.
- A successful CadQuery export is not sufficient: every individual STL must report MANIFOLD PASS, PRINT BED PASS, and NON-ZERO VOLUME PASS, and the clearance suite must also pass.
- Keep the right mid-frame spine and both right side modules removable; that is the HDD service path.
- Keep the Pi wholly in front of the structural mid-frame so it can lift through the top service lid.
- Treat all connector coordinates and the USB-hub envelope as provisional until measured.
