"""Selectively rebuild the rear-fan artifacts while validating the whole project.

This entry point intentionally leaves every unrelated individual export and fit
coupon untouched.  It also treats slicer-owned 3MF files and the focused HDD
keeper report as protected artifacts.  Run it only after the rear-fan source
changes are complete::

    .venv/Scripts/python.exe build_rear_fan_update.py
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import sys
import time
import traceback
from typing import Callable
from uuid import uuid4

import cadquery as cq

import config as C
from build import (
    ASSEMBLY_DIR,
    FIT_DIR,
    INTERNAL_PREVIEW_EXCLUSIONS,
    REPORT_DIR,
    ROOT,
    STEP_DIR,
    STL_DIR,
    _ensure_directories,
    _export_shape,
)
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
    CheckResult,
    clearance_checks,
    printability_checks,
    step_artifact_check,
    stl_inventory_check,
    write_clearance_report,
    write_dimensions_report,
    write_printability_report,
)


TARGET_PARTS = frozenset({"rear_panel", "rear_fan_guard"})
EXPECTED_PRODUCTION_PARTS = 20
ASSEMBLY_STEP_BASENAMES = (
    "NAS_Assembly",
    "NAS_Exploded",
    "NAS_Internal_Inspection",
    "NAS_Clearance_Check",
)
ASSEMBLY_MESH_BASENAMES = (
    "NAS_Assembly",
    "NAS_Exploded",
    "NAS_Internal_Inspection",
)
CORE_REPORT_NAMES = (
    "dimensions.md",
    "printability.md",
    "clearance_report.md",
)


@dataclass(frozen=True)
class FileState:
    """Content and timestamp state used by the selective-build scope guard."""

    size: int
    mtime_ns: int
    digest: str


def _path_key(path: Path) -> str:
    """Return a stable, case-insensitive repository-relative path key."""

    relative = path.resolve().relative_to(ROOT.resolve())
    return relative.as_posix().casefold()


def _allowed_paths() -> frozenset[str]:
    paths: set[Path] = set()
    for name in TARGET_PARTS:
        paths.add(STL_DIR / f"{name}.stl")
        paths.add(STEP_DIR / f"{name}.step")
    for basename in ASSEMBLY_STEP_BASENAMES:
        paths.add(ASSEMBLY_DIR / f"{basename}.step")
    for basename in ASSEMBLY_MESH_BASENAMES:
        paths.add(ASSEMBLY_DIR / f"{basename}.stl")
        paths.add(ASSEMBLY_DIR / f"{basename}_preview.png")
    for name in CORE_REPORT_NAMES:
        paths.add(REPORT_DIR / name)
    return frozenset(_path_key(path) for path in paths)


ALLOWED_PATHS = _allowed_paths()


def _stable_file_state(path: Path) -> FileState:
    """Hash a file only when its size and mtime remain stable during the read."""

    for _ in range(3):
        before = path.stat()
        digest = sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        after = path.stat()
        if before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns:
            return FileState(after.st_size, after.st_mtime_ns, digest.hexdigest())
    raise RuntimeError(f"Artifact changed while it was being snapshotted: {path}")


def _snapshot_artifacts() -> dict[str, FileState]:
    """Snapshot every file under exports/ and reports/, including all 3MFs."""

    snapshot: dict[str, FileState] = {}
    for directory in (ROOT / "exports", REPORT_DIR):
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                snapshot[_path_key(path)] = _stable_file_state(path)
    return snapshot


def _scope_violations(
    before: dict[str, FileState], after: dict[str, FileState]
) -> list[str]:
    """Describe every created, removed, re-timestamped, or rehashed protected file."""

    violations: list[str] = []
    for key in sorted(set(before) | set(after)):
        if key in ALLOWED_PATHS:
            continue
        old = before.get(key)
        new = after.get(key)
        if old is None:
            violations.append(f"created protected artifact: {key}")
        elif new is None:
            violations.append(f"removed protected artifact: {key}")
        elif old.digest != new.digest:
            violations.append(f"changed protected artifact content: {key}")
        elif old.mtime_ns != new.mtime_ns:
            violations.append(f"changed protected artifact mtime: {key}")
        elif old.size != new.size:
            violations.append(f"changed protected artifact size: {key}")
    return violations


def _temporary_path(target: Path) -> Path:
    """Create a same-directory temporary name whose final suffix stays usable."""

    return target.with_name(f".{target.stem}.{uuid4().hex}.tmp{target.suffix}")


def _atomic_export_shape(shape: cq.Workplane | cq.Shape, target: Path) -> None:
    temporary = _temporary_path(target)
    try:
        _export_shape(shape, temporary)
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_save_assembly(
    assembly: cq.Assembly,
    target: Path,
    export_type: str,
) -> None:
    temporary = _temporary_path(target)
    try:
        if export_type == "STL":
            assembly.save(
                str(temporary),
                exportType="STL",
                mode="default",
                tolerance=C.STL_LINEAR_TOLERANCE,
                angularTolerance=C.STL_ANGULAR_TOLERANCE,
            )
        else:
            assembly.save(str(temporary), exportType=export_type, mode="default")
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_render(source: Path, target: Path) -> None:
    temporary = _temporary_path(target)
    try:
        render_stl(source, temporary)
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_report(writer: Callable[..., None], target: Path, *args: object) -> None:
    temporary = _temporary_path(target)
    try:
        writer(temporary, *args)
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _export_target_parts(parts: dict[str, PrintablePart]) -> None:
    missing = sorted(TARGET_PARTS - set(parts))
    if missing:
        raise RuntimeError(f"Selective target part(s) missing from registry: {', '.join(missing)}")
    print(f"[1/6] Exporting only: {', '.join(sorted(TARGET_PARTS))} ...")
    for name in sorted(TARGET_PARTS):
        printable = move_to_origin(parts[name].shape)
        _atomic_export_shape(printable, STEP_DIR / f"{name}.step")
        _atomic_export_shape(printable, STL_DIR / f"{name}.stl")


def _assembly_models(placed, standard_refs, clearance_refs) -> dict[str, cq.Assembly]:
    internal = {
        name: item
        for name, item in placed.items()
        if name not in INTERNAL_PREVIEW_EXCLUSIONS
    }
    return {
        "NAS_Assembly": cadquery_assembly(placed, standard_refs, exploded=False),
        "NAS_Exploded": cadquery_assembly(placed, standard_refs, exploded=True),
        "NAS_Internal_Inspection": cadquery_assembly(internal, standard_refs, exploded=False),
        "NAS_Clearance_Check": cadquery_assembly(placed, clearance_refs, exploded=False),
    }


def _export_affected_assemblies(assemblies: dict[str, cq.Assembly]) -> None:
    print("[2/6] Regenerating affected assembly STEP/STL artifacts ...")
    for basename in ASSEMBLY_STEP_BASENAMES:
        _atomic_save_assembly(
            assemblies[basename], ASSEMBLY_DIR / f"{basename}.step", "STEP"
        )
    for basename in ASSEMBLY_MESH_BASENAMES:
        _atomic_save_assembly(
            assemblies[basename], ASSEMBLY_DIR / f"{basename}.stl", "STL"
        )


def _render_affected_previews() -> None:
    print("[3/6] Regenerating assembly previews only ...")
    for basename in ASSEMBLY_MESH_BASENAMES:
        _atomic_render(
            ASSEMBLY_DIR / f"{basename}.stl",
            ASSEMBLY_DIR / f"{basename}_preview.png",
        )


def _fit_parts() -> dict[str, PrintablePart]:
    models = {name: move_to_origin(shape) for name, shape in fit_test_models().items()}
    return {
        name: PrintablePart(
            name=name,
            shape=shape,
            quantity=1,
            orientation="flat coupon base on bed; labels and joint openings upward",
            supports="none",
            notes="Calibration artifact; print before committing to the production joints.",
            expected_solid_count=len(shape_value(shape).Solids()),
        )
        for name, shape in models.items()
    }


def _fit_artifact_inventory_check(fit_parts: dict[str, PrintablePart]) -> CheckResult:
    """Require every existing fit STL/STEP to belong to the validated model set."""

    expected_stl = {f"{name}.stl" for name in fit_parts}
    expected_step = {f"{name}.step" for name in fit_parts}
    actual_stl = {
        path.name
        for path in FIT_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".stl"
    }
    actual_step = {
        path.name
        for path in FIT_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".step"
    }
    missing = sorted((expected_stl - actual_stl) | (expected_step - actual_step))
    unexpected = sorted((actual_stl - expected_stl) | (actual_step - expected_step))
    passed = not missing and not unexpected
    detail = (
        f"Expected and found {len(expected_stl)} STL plus {len(expected_step)} STEP fit artifacts."
    )
    if missing:
        detail += f" Missing: {', '.join(missing)}."
    if unexpected:
        detail += f" Unexpected/unvalidated: {', '.join(unexpected)}."
    return CheckResult("Fit-test STL/STEP inventory", passed, detail)


def _assembly_expectations(placed, standard_refs, clearance_refs) -> dict[str, tuple[int, float]]:
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
    return {
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


def _run_selective_build() -> int:
    started = time.perf_counter()
    _ensure_directories()

    parts = printable_parts()
    if len(parts) != EXPECTED_PRODUCTION_PARTS:
        raise RuntimeError(
            f"Expected {EXPECTED_PRODUCTION_PARTS} production source parts; found {len(parts)}."
        )
    placed = placed_printable_parts(parts)
    standard_refs = standard_references()
    clearance_refs = clearance_references()
    fit_parts = _fit_parts()

    _export_target_parts(parts)
    assemblies = _assembly_models(placed, standard_refs, clearance_refs)
    _export_affected_assemblies(assemblies)
    _render_affected_previews()

    print("[4/6] Validating all production and existing fit-test STL/STEP artifacts ...")
    production_checks, production_rows = printability_checks(parts, STL_DIR, STEP_DIR)
    print_checks: list[CheckResult] = [
        stl_inventory_check(parts, STL_DIR),
        *production_checks,
    ]
    print_rows = list(production_rows)
    fit_checks, fit_rows = printability_checks(fit_parts, FIT_DIR, FIT_DIR)
    print_checks.append(_fit_artifact_inventory_check(fit_parts))
    print_checks.extend(fit_checks)
    print_rows.extend(fit_rows)

    for basename, (expected_solids, expected_volume) in _assembly_expectations(
        placed, standard_refs, clearance_refs
    ).items():
        print_checks.append(
            step_artifact_check(
                ASSEMBLY_DIR / f"{basename}.step",
                basename,
                expected_solids,
                expected_volume,
            )
        )

    print("[5/6] Running the complete collision, cable-route, hardware, and service suite ...")
    clearance_results = clearance_checks(placed, clearance_refs)

    print("[6/6] Regenerating the three core reports ...")
    _atomic_report(
        write_dimensions_report,
        REPORT_DIR / "dimensions.md",
        parts,
        print_rows,
    )
    _atomic_report(
        write_printability_report,
        REPORT_DIR / "printability.md",
        print_checks,
        print_rows,
    )
    _atomic_report(
        write_clearance_report,
        REPORT_DIR / "clearance_report.md",
        clearance_results,
    )

    failed_print = [check for check in print_checks if not check.passed]
    failed_clearance = [check for check in clearance_results if not check.passed]
    manifold_count = sum(bool(row["manifold_pass"]) for row in production_rows)
    bed_count = sum(bool(row["print_bed_pass"]) for row in production_rows)
    volume_count = sum(bool(row["nonzero_volume_pass"]) for row in production_rows)
    elapsed = time.perf_counter() - started

    print()
    print("=" * 72)
    print(f"PRODUCTION SOURCE PARTS VALIDATED: {len(parts)}")
    print(f"FIT-TEST MODELS VALIDATED: {len(fit_parts)}")
    print(f"INDIVIDUAL STL MANIFOLD: {manifold_count}/{len(production_rows)} PASS")
    print(f"INDIVIDUAL STL PRINT BED: {bed_count}/{len(production_rows)} PASS")
    print(f"INDIVIDUAL STL NON-ZERO VOLUME: {volume_count}/{len(production_rows)} PASS")
    print(f"PRINT/EXPORT CHECKS: {len(print_checks) - len(failed_print)}/{len(print_checks)} PASS")
    print(
        f"CLEARANCE CHECKS: "
        f"{len(clearance_results) - len(failed_clearance)}/{len(clearance_results)} PASS"
    )
    if failed_print or failed_clearance:
        print("SELECTIVE BUILD RESULT: FAIL")
        for check in failed_print + failed_clearance:
            print(f"  FAIL - {check.name}: {check.detail}")
        print(f"Elapsed: {elapsed:.1f} s")
        return 1

    print("SELECTIVE BUILD RESULT: SUCCESS")
    print(f"Elapsed: {elapsed:.1f} s")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    # The snapshot is deliberately taken before directory creation or export.
    before = _snapshot_artifacts()
    result = 2
    try:
        result = _run_selective_build()
    except Exception:
        print("SELECTIVE BUILD RESULT: ERROR")
        traceback.print_exc()
        result = 2
    finally:
        try:
            after = _snapshot_artifacts()
            violations = _scope_violations(before, after)
        except Exception:
            print("ARTIFACT SCOPE GUARD: ERROR")
            traceback.print_exc()
            return 3
        if violations:
            print("ARTIFACT SCOPE GUARD: FAIL")
            for violation in violations:
                print(f"  FAIL - {violation}")
            return 3
        print("ARTIFACT SCOPE GUARD: PASS")
        print("Protected fit tests, unrelated individual exports, 3MFs, and keeper report are unchanged.")
    return result


if __name__ == "__main__":
    sys.exit(main())
