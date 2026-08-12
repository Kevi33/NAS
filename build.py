"""Regenerate every printable, assembly, fit-test, preview, and report artifact."""

from __future__ import annotations

from pathlib import Path
import sys
import time
import traceback

import cadquery as cq

import config as C
from src.assembly import (
    cadquery_assembly,
    clearance_references,
    placed_printable_parts,
    printable_parts,
    standard_references,
)
from src.common import PrintablePart, move_to_origin, shape_value, valid_volume
from src.fit_tests import fit_test_models
from src.preview import render_stl
from src.validation import (
    clearance_checks,
    printability_checks,
    stl_inventory_check,
    write_clearance_report,
    write_dimensions_report,
    write_printability_report,
    step_artifact_check,
)


ROOT = Path(__file__).resolve().parent
STL_DIR = ROOT / "exports" / "individual" / "STL"
STEP_DIR = ROOT / "exports" / "individual" / "STEP"
ASSEMBLY_DIR = ROOT / "exports" / "assembly"
FIT_DIR = ROOT / "exports" / "fit_tests"
REPORT_DIR = ROOT / "reports"
INTERNAL_PREVIEW_EXCLUSIONS = {
    "front_panel",
    "right_side_front",
    "right_side_rear",
    "top_service_lid",
    "top_rear",
}


def _ensure_directories() -> None:
    for directory in (STL_DIR, STEP_DIR, ASSEMBLY_DIR, FIT_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def _clear_generated_files() -> None:
    """Remove generator-owned artifacts while preserving slicer project files."""
    generated_suffixes = {".stl", ".step", ".png", ".md"}
    focused_report = REPORT_DIR / "hdd_keeper_retention_test_validation.md"
    for directory in (STL_DIR, STEP_DIR, ASSEMBLY_DIR, FIT_DIR, REPORT_DIR):
        for path in directory.iterdir():
            if (
                path.is_file()
                and path.suffix.lower() in generated_suffixes
                and path != focused_report
            ):
                path.unlink()


def _export_shape(shape: cq.Workplane | cq.Shape, path: Path) -> None:
    cq.exporters.export(
        shape,
        str(path),
        tolerance=C.STL_LINEAR_TOLERANCE,
        angularTolerance=C.STL_ANGULAR_TOLERANCE,
    )


def _export_individuals(parts) -> None:
    print(f"[1/6] Exporting {len(parts)} individual printable source parts ...")
    for name, part in parts.items():
        printable = move_to_origin(part.shape)
        _export_shape(printable, STEP_DIR / f"{name}.step")
        _export_shape(printable, STL_DIR / f"{name}.stl")


def _export_fit_tests(models: dict[str, cq.Workplane]) -> None:
    print("[2/6] Exporting fit-test coupons ...")
    for name, shape in models.items():
        printable = move_to_origin(shape)
        _export_shape(printable, FIT_DIR / f"{name}.step")
        _export_shape(printable, FIT_DIR / f"{name}.stl")


def _save_assembly(assembly: cq.Assembly, basename: str, save_stl: bool = False) -> None:
    assembly.save(str(ASSEMBLY_DIR / f"{basename}.step"), exportType="STEP", mode="default")
    if save_stl:
        assembly.save(
            str(ASSEMBLY_DIR / f"{basename}.stl"),
            exportType="STL",
            mode="default",
            tolerance=C.STL_LINEAR_TOLERANCE,
            angularTolerance=C.STL_ANGULAR_TOLERANCE,
        )


def _export_assemblies(placed, standard_refs, clearance_refs) -> None:
    print("[3/6] Exporting complete, exploded, cutaway, and clearance-check assemblies ...")
    assembled = cadquery_assembly(placed, standard_refs, exploded=False)
    exploded = cadquery_assembly(placed, standard_refs, exploded=True)
    internal = cadquery_assembly(
        {
            name: item
            for name, item in placed.items()
            if name not in INTERNAL_PREVIEW_EXCLUSIONS
        },
        standard_refs,
        exploded=False,
    )
    checking = cadquery_assembly(placed, clearance_refs, exploded=False)
    _save_assembly(assembled, "NAS_Assembly", save_stl=True)
    _save_assembly(exploded, "NAS_Exploded", save_stl=True)
    _save_assembly(internal, "NAS_Internal_Inspection", save_stl=True)
    _save_assembly(checking, "NAS_Clearance_Check", save_stl=False)


def _render_previews() -> list[str]:
    print("[4/6] Rendering headless assembly previews ...")
    warnings: list[str] = []
    for basename in ("NAS_Assembly", "NAS_Exploded", "NAS_Internal_Inspection"):
        try:
            render_stl(ASSEMBLY_DIR / f"{basename}.stl", ASSEMBLY_DIR / f"{basename}_preview.png")
        except Exception as exc:
            warnings.append(f"Preview {basename}: {exc}")
    for basename, size in (
        ("dovetail_fit_test", (1400, 700)),
        ("panel_key_fit_test", (1400, 650)),
        ("hdd_rail_fit_test", (1000, 600)),
        ("hdd_keeper_fit_test", (900, 600)),
        ("hdd_keeper_retention_test", (1400, 650)),
    ):
        try:
            render_stl(FIT_DIR / f"{basename}.stl", FIT_DIR / f"{basename}_preview.png", size)
        except Exception as exc:
            warnings.append(f"Preview {basename}: {exc}")
    return warnings


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    started = time.perf_counter()
    _ensure_directories()
    try:
        _clear_generated_files()
        parts = printable_parts()
        placed = placed_printable_parts(parts)
        standard_refs = standard_references()
        clearance_refs = clearance_references()
        fit_models = {name: move_to_origin(shape) for name, shape in fit_test_models().items()}
        fit_parts = {
            name: PrintablePart(
                name=name,
                shape=shape,
                quantity=1,
                orientation="flat coupon base on bed; labels and joint openings upward",
                supports="none",
                notes="Calibration artifact; print before committing to the production joints.",
                expected_solid_count=len(shape_value(shape).Solids()),
            )
            for name, shape in fit_models.items()
        }

        _export_individuals(parts)
        _export_fit_tests(fit_models)
        _export_assemblies(placed, standard_refs, clearance_refs)
        preview_warnings = _render_previews()

        print("[5/6] Validating source, STL mesh, STEP, and print-bed geometry ...")
        production_checks, production_rows = printability_checks(parts, STL_DIR, STEP_DIR)
        print_checks = [stl_inventory_check(parts, STL_DIR), *production_checks]
        print_rows = list(production_rows)
        fit_checks, fit_rows = printability_checks(fit_parts, FIT_DIR, FIT_DIR)
        print_checks.extend(fit_checks)
        print_rows.extend(fit_rows)
        placed_solid_count = sum(len(shape_value(item.shape).Solids()) for item in placed.values())
        placed_volume = sum(valid_volume(item.shape) for item in placed.values())
        standard_solid_count = sum(
            len(shape_value(reference.shape).Solids()) for reference in standard_refs.values()
        )
        standard_volume = sum(valid_volume(reference.shape) for reference in standard_refs.values())
        clearance_solid_count = sum(
            len(shape_value(reference.shape).Solids()) for reference in clearance_refs.values()
        )
        clearance_volume = sum(valid_volume(reference.shape) for reference in clearance_refs.values())
        internal_placed = {
            name: item
            for name, item in placed.items()
            if name not in INTERNAL_PREVIEW_EXCLUSIONS
        }
        internal_solid_count = sum(
            len(shape_value(item.shape).Solids()) for item in internal_placed.values()
        )
        internal_volume = sum(valid_volume(item.shape) for item in internal_placed.values())
        assembly_expectations = {
            "NAS_Assembly": (
                placed_solid_count + standard_solid_count,
                placed_volume + standard_volume,
            ),
            "NAS_Exploded": (
                placed_solid_count + standard_solid_count,
                placed_volume + standard_volume,
            ),
            "NAS_Internal_Inspection": (
                internal_solid_count + standard_solid_count,
                internal_volume + standard_volume,
            ),
            "NAS_Clearance_Check": (
                placed_solid_count + clearance_solid_count,
                placed_volume + clearance_volume,
            ),
        }
        for basename, (expected_solids, expected_volume) in assembly_expectations.items():
            print_checks.append(
                step_artifact_check(
                    ASSEMBLY_DIR / f"{basename}.step",
                    basename,
                    expected_solids,
                    expected_volume,
                )
            )
        print("[6/6] Running hardware, cable-zone, and service-sweep collision checks ...")
        clearance_results = clearance_checks(placed, clearance_refs)

        write_dimensions_report(REPORT_DIR / "dimensions.md", parts, print_rows)
        write_printability_report(REPORT_DIR / "printability.md", print_checks, print_rows)
        write_clearance_report(REPORT_DIR / "clearance_report.md", clearance_results)

        failed_print = [check for check in print_checks if not check.passed]
        failed_clearance = [check for check in clearance_results if not check.passed]
        elapsed = time.perf_counter() - started
        print()
        print("=" * 72)
        print(f"PRINTABLE SOURCE PARTS: {len(parts)} ({sum(part.quantity for part in parts.values())} physical pieces)")
        print(f"PLACED PRINTED INSTANCES: {len(placed)}")
        manifold_count = sum(bool(row["manifold_pass"]) for row in production_rows)
        bed_count = sum(bool(row["print_bed_pass"]) for row in production_rows)
        volume_count = sum(bool(row["nonzero_volume_pass"]) for row in production_rows)
        print(f"INDIVIDUAL STL MANIFOLD: {manifold_count}/{len(production_rows)} PASS")
        print(f"INDIVIDUAL STL PRINT BED: {bed_count}/{len(production_rows)} PASS")
        print(f"INDIVIDUAL STL NON-ZERO VOLUME: {volume_count}/{len(production_rows)} PASS")
        print(f"PRINT/EXPORT CHECKS: {len(print_checks) - len(failed_print)}/{len(print_checks)} PASS")
        print(f"CLEARANCE CHECKS: {len(clearance_results) - len(failed_clearance)}/{len(clearance_results)} PASS")
        if preview_warnings:
            for warning in preview_warnings:
                print(f"WARNING: {warning}")
        if failed_print or failed_clearance:
            print("BUILD RESULT: FAIL")
            for check in failed_print + failed_clearance:
                print(f"  FAIL - {check.name}: {check.detail}")
            print(f"Elapsed: {elapsed:.1f} s")
            return 1
        print("BUILD RESULT: SUCCESS")
        print(f"Final body: {C.NAS_EXTERNAL_W:.1f} x {C.NAS_EXTERNAL_D:.1f} x {C.NAS_BODY_H:.1f} mm")
        print(f"Overall height with feet: {C.NAS_BODY_H + C.FOOT_H:.1f} mm")
        print(f"Elapsed: {elapsed:.1f} s")
        return 0
    except Exception:
        print("BUILD RESULT: ERROR")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
