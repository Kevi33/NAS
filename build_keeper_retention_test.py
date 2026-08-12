"""Generate and validate only the dedicated HDD keeper retention coupon."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import traceback

import cadquery as cq

import config as C
from src.common import PrintablePart, move_to_origin, shape_value
from src.fit_tests import make_keeper_retention_test
from src.preview import render_stl
from src.validation import printability_checks


ROOT = Path(__file__).resolve().parent
FIT_DIR = ROOT / "exports" / "fit_tests"
REPORT_DIR = ROOT / "reports"
BASENAME = "hdd_keeper_retention_test"
ALLOWED_OUTPUTS = {
    FIT_DIR / f"{BASENAME}.stl",
    FIT_DIR / f"{BASENAME}.step",
    FIT_DIR / f"{BASENAME}_preview.png",
    REPORT_DIR / f"{BASENAME}_validation.md",
}


def _fingerprint(path: Path) -> tuple[int, int, str]:
    stat = path.stat()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return stat.st_size, stat.st_mtime_ns, digest


def _protected_snapshot() -> dict[Path, tuple[int, int, str]]:
    snapshot: dict[Path, tuple[int, int, str]] = {}
    for directory in (ROOT / "exports", REPORT_DIR):
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path not in ALLOWED_OUTPUTS:
                snapshot[path] = _fingerprint(path)
    return snapshot


def _export(shape: cq.Workplane, path: Path) -> None:
    cq.exporters.export(
        shape,
        str(path),
        tolerance=C.STL_LINEAR_TOLERANCE,
        angularTolerance=C.STL_ANGULAR_TOLERANCE,
    )


def _write_report(checks, row: dict[str, object]) -> None:
    report_path = REPORT_DIR / f"{BASENAME}_validation.md"
    clearances = C.HDD_KEEPER_TEST_CLEARANCES
    lines = [
        "# HDD keeper retention test validation",
        "",
        "This focused build does not regenerate or modify enclosure artifacts.",
        "",
        "## Test matrix",
        "",
        "| Label | Clearance per side | Friction-bead projection | Net positive interference |",
        "|---:|---:|---:|---:|",
    ]
    for clearance in clearances:
        projection = 2.0 * clearance + C.HDD_KEEPER_RETENTION_INTERFERENCE
        lines.append(
            f"| {int(round(clearance * 100)):02d} | {clearance:.2f} mm | "
            f"{projection:.2f} mm | {C.HDD_KEEPER_RETENTION_INTERFERENCE:.2f} mm |"
        )
    stl_dims = row["stl_dims"]
    dims_text = "unavailable"
    if isinstance(stl_dims, tuple):
        dims_text = " x ".join(f"{value:.2f}" for value in stl_dims) + " mm"
    lines.extend(
        [
            "",
            "The broad rounded bead is fused into the keeper body; there are no thin snap tabs. "
            "Each variant has the same nominal 0.10 mm positive preload after its opposite flat "
            "face shifts against the socket wall.",
            "",
            "## Export validation",
            "",
            f"- Exported bounds: **{dims_text}**",
            f"- Expected connected solids: **{row['expected_solid_count']}**",
        ]
    )
    for check in checks:
        lines.append(f"- **{'PASS' if check.passed else 'FAIL'}** — {check.name}: {check.detail}")
    lines.extend(
        [
            "",
            "## Physical test",
            "",
            "1. Print the exported STL flat with labels and keeper guides upward, using the final filament/profile.",
            "2. Match each loose keeper to the socket with the same 00/05/10/15/20 label.",
            "3. Face the guide toward the open/outboard side and press vertically until both shoulders seat.",
            "4. After cooling, invert and lightly shake; reject any variant that drops or rattles noticeably.",
            "5. Confirm the keeper can still be removed by hand without tools or damage.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    protected_before = _protected_snapshot()
    FIT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        expected_matrix = (0.00, 0.05, 0.10, 0.15, 0.20)
        if tuple(C.HDD_KEEPER_TEST_CLEARANCES) != expected_matrix:
            raise ValueError(f"Unexpected keeper test matrix: {C.HDD_KEEPER_TEST_CLEARANCES!r}")

        model = move_to_origin(make_keeper_retention_test())
        expected_solids = 2 * len(expected_matrix)
        actual_solids = len(shape_value(model).Solids())
        if actual_solids != expected_solids:
            raise ValueError(f"Expected {expected_solids} separate test pieces, got {actual_solids}")

        _export(model, FIT_DIR / f"{BASENAME}.step")
        _export(model, FIT_DIR / f"{BASENAME}.stl")
        render_stl(
            FIT_DIR / f"{BASENAME}.stl",
            FIT_DIR / f"{BASENAME}_preview.png",
            (1400, 650),
        )

        part = PrintablePart(
            name=BASENAME,
            shape=model,
            quantity=1,
            orientation="flat socket rails and keeper bases on bed; labels and guides upward",
            supports="none",
            notes="Five labeled keeper-retention clearance pairs; print with the production profile.",
            expected_solid_count=expected_solids,
        )
        checks, rows = printability_checks({BASENAME: part}, FIT_DIR, FIT_DIR)
        _write_report(checks, rows[0])

        protected_after = _protected_snapshot()
        if protected_after != protected_before:
            changed = sorted(
                str(path.relative_to(ROOT))
                for path in set(protected_before) | set(protected_after)
                if protected_before.get(path) != protected_after.get(path)
            )
            raise RuntimeError(f"Focused build changed protected artifacts: {changed}")

        failures = [check for check in checks if not check.passed]
        print(f"HDD keeper retention variants: {len(expected_matrix)}")
        print(f"Separate printable pieces: {actual_solids}")
        print(f"VALIDATION CHECKS: {len(checks) - len(failures)}/{len(checks)} PASS")
        if failures:
            for check in failures:
                print(f"FAIL - {check.name}: {check.detail}")
            print("FOCUSED BUILD RESULT: FAIL")
            return 1
        print("FOCUSED BUILD RESULT: SUCCESS")
        return 0
    except Exception:
        print("FOCUSED BUILD RESULT: ERROR")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
