"""Deferred standard SG whole-component extraction of Root-retained native218-220.

Default mode validates text/tools only and never reads raw image bytes. Extraction
requires an explicit Root-notification record with exact equal F/E raw pins.
Output is NEW owned F run media, never displayed; Root E-retains before View.
"""
from __future__ import annotations
import argparse
import ast
import copy
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SKILL = Path("C:/Users/22499/.codex/skills/sprite-gen")
PROJECT = Path("F:/Ourgame")
STANDARD = HERE.parent / "standard-input-candidate-v001"
BATCH = STANDARD / "process-batches/2026-10-18-right-body-states-v001"
E_ROOT = Path("E:/OurGame/Knight/过程图稿与视频")


def pin(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write_new(path, value):
    if path.exists():
        raise ValueError("Never overwrite prior candidate evidence: " + path.as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    path.write_text(data, encoding="utf-8")


def validate_plan():
    if Path(sys.executable).resolve() != (SKILL / ".venv/Scripts/python.exe").resolve():
        raise ValueError("Use the pinned sprite-gen venv; never global Python")
    plan = json.loads((HERE / "extraction-plan-v002.json").read_text(encoding="utf-8"))
    for record in plan["pinned_tools_and_inputs"]:
        if pin(Path(record["path"])) != record:
            raise ValueError("Pinned text/tool input changed: " + record["path"])
    original = json.loads((STANDARD / "standard-input-freeze-v001.json").read_text(encoding="utf-8"))
    for record in original["files"]:
        if pin(Path(record["path"])) != record:
            raise ValueError("Original standard18 changed: " + record["path"])
    request = json.loads((STANDARD / "sprite-request.json").read_text(encoding="utf-8"))
    if (BATCH / "sprite-request.json").read_bytes() != (STANDARD / "sprite-request.json").read_bytes():
        raise ValueError("Root batch numeric SSoT differs from original frozen input")
    assert [(state, entry["frames"], entry["fps"]) for state, entry in request["states"].items()] == [("dodge", 4, 10), ("hurt", 4, 10), ("death", 5, 5)]
    assert all(not entry["loop"] and "durations_ms" not in entry for entry in request["states"].values())
    assert request["fit"]["shared_row_scale"] is True and request["fit"]["pixel_unfake"] is False
    for script in HERE.glob("*.py"):
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    return plan, request


def admit_raw(admission_path, state, number):
    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    if admission.get("root_notification_received") is not True or not admission.get("root_notification_text"):
        raise ValueError("Root must notify that this actual raw is F/E-retained before any raw read/extraction")
    rows = [row for row in admission["rows"] if row["state"] == state and row["native_request_number"] == number]
    if len(rows) != 1:
        raise ValueError("Exact state/native-number raw admission required")
    row = rows[0]
    source = Path(row["F_raw"]["path"]).resolve()
    retained = Path(row["E_original"]["path"]).resolve()
    if source != (BATCH / "raw" / (state + ".png")).resolve():
        raise ValueError("Unexpected Root raw path")
    if not retained.is_relative_to(E_ROOT.resolve()):
        raise ValueError("Exact retained E original required")
    if pin(source) != row["F_raw"] or pin(retained) != row["E_original"]:
        raise ValueError("Actual F/E raw pin changed")
    if (row["F_raw"]["bytes"], row["F_raw"]["sha256"]) != (row["E_original"]["bytes"], row["E_original"]["sha256"]):
        raise ValueError("F/E original raw must be byte-identical")
    return row, source


def extract_one(plan, request, state, admission_path):
    row_plan = next(row for row in plan["rows"] if row["state"] == state)
    admission, raw = admit_raw(admission_path, state, row_plan["native_request_number"])
    run = HERE / row_plan["new_run_relative"]
    if run.exists():
        raise ValueError("Preserve prior extraction; select a NEW candidate/run version")
    run.mkdir(parents=True)
    receipt = {"schema": "hero218-220-standard-extraction-receipt-v001", "state": state,
               "native_request_number": row_plan["native_request_number"], "raw_admission": admission,
               "started_local": datetime.datetime.now().astimezone().isoformat(),
               "commands": [], "status": "STARTED_NO_VIEW", "art_accepted": False,
               "source_pixels_locally_redrawn": False, "View_called": False, "UE_called": False,
               "physical_floor_root_grip_axis": None, "E_retention_pending_for_all_new_media": True}
    try:
        one = copy.deepcopy(request)
        one["states"] = {state: copy.deepcopy(request["states"][state])}
        # Pin the SDK defaults before extraction so its documented chroma write is byte-stable.
        one["chroma"] = copy.deepcopy(plan["explicit_sdk_chroma_defaults"])
        write_new(run / "sprite-request.json", one)
        request_bytes = (run / "sprite-request.json").read_bytes()
        raw_copy = run / "raw" / (state + ".png")
        raw_copy.parent.mkdir(parents=True)
        shutil.copyfile(raw, raw_copy)
        assert raw_copy.read_bytes() == raw.read_bytes()
        for relative in ("prompts/" + state + ".txt", "references/layout-guides/" + state + ".png"):
            target = run / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BATCH / relative, target)
        write_new(run / "original-multirow-input-pin-v001.json", pin(BATCH / "sprite-request.json"))
        write_new(run / "runtime-timing-annotations-v001.json", json.loads((STANDARD / "runtime-timing-annotations-v001.json").read_text(encoding="utf-8")))
        from PIL import Image
        with Image.open(raw_copy) as opened:
            receipt["actual_raw"] = {"file": pin(raw_copy), "mode": opened.mode, "size": list(opened.size),
                                     "actual_native_dimensions_not_assumed_from_layout": True}
        commands = [
            ("extract-shared-row", PROJECT / "tools/scripts/extract-sprite-shared-row-scale.py", []),
            ("compose-atlas", SKILL / "scripts/compose_sprite_atlas.py", []),
            ("export-curated", SKILL / "scripts/export_curated_pngs.py", ["--state", state]),
            ("preview-standard-QA", SKILL / "scripts/preview_animation.py", []),
            ("inspect-standard", SKILL / "scripts/inspect_sprite_run.py", []),
        ]
        for name, tool, extra in commands:
            argv = [sys.executable, "-B", "-X", "utf8", str(tool), "--run-dir", str(run)] + extra
            result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
            log = run / "pipeline-logs" / (name + "-v001.log")
            write_new(log, result.stdout + result.stderr)
            receipt["commands"].append({"argv": argv, "tool": pin(tool), "exit_code": result.returncode, "log": pin(log)})
            if request_bytes != (run / "sprite-request.json").read_bytes():
                raise ValueError("Standard pipeline changed numeric/fit request")
            if result.returncode and name != "inspect-standard":
                raise ValueError(name + " failed; preserve all outputs, never relax QA or patch image pixels")
        manifest_path = run / "frames/frames-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["errors"] == manifest["warnings"] == [] and len(manifest["rows"]) == 1
        row = manifest["rows"][0]
        shared = row["shared_row_fit"]
        assert row["state"] == state and row["frames"] == row_plan["frames"] and row["method"] == "components"
        assert shared["per_frame_scale_normalization"] is False
        frames = []
        for index in range(row_plan["frames"]):
            frame = run / "curated" / ("frame-" + str(index) + ".png")
            with Image.open(frame) as opened:
                assert opened.mode == "RGBA" and opened.size == (512, 512)
                rgba = opened.tobytes();alpha = opened.getchannel("A");histogram = alpha.histogram()
                bbox = alpha.getbbox();assert bbox is not None
                core_bbox = alpha.point(lambda value: 255 if value >= 128 else 0).getbbox()
                frames.append({"frame": index, "file": pin(frame), "actual_RGBA_sha256": hashlib.sha256(rgba).hexdigest(),
                               "actual_alpha_bbox": list(bbox), "actual_alpha128_bbox": list(core_bbox) if core_bbox else None,
                               "nonzero_alpha_pixels": sum(histogram[1:]), "alpha128_pixels": sum(histogram[128:]),
                               "alpha255_pixels": histogram[255], "partial_alpha_pixels": sum(histogram[1:255]),
                               "coverage_of_512_cell": sum(histogram[1:]) / (512. * 512.),
                               "physical_floor_support_contacts": None, "actual_root_px": None, "actual_crown_px": None,
                               "actual_near_grip_px": None, "actual_handle_axis_xy": None, "actual_hand_replay_mask": None,
                               "semantic_body_density_or_anatomy_accepted": False})
        unique = len({frame["actual_RGBA_sha256"] for frame in frames})
        if unique != row_plan["frames"]:
            raise ValueError("Exact duplicate RGBA bodies found; no cloning Ready or pretending repeated poses are distinct")
        inspect = json.loads((run / "sprite-inspect.report.json").read_text(encoding="utf-8"))
        composed = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        animation = composed["animation"]["rows"][state]
        assert animation["frames"] == row_plan["frames"] and animation["fps"] == row_plan["fps"] and animation["loop"] is False
        assert len(composed["frame_layout"]["rows"][state]) == row_plan["frames"]
        gif = run / "qa" / (state + ".gif")
        with Image.open(gif) as opened:
            gif_info = {"actual_frame_count": opened.n_frames, "encoded_loop_count": opened.info.get("loop"),
                        "scope": "Standard QA convenience GIF; not runtime nonloop/terminal corpse hold proof"}
        receipt.update({"status": "STANDARD_EXTRACTED_WITH_INSPECT_FINDINGS_PENDING_REVIEW" if inspect["errors"] or inspect["warnings"] else "STANDARD_EXTRACTED_PENDING_ROOT_E_RETENTION_AND_VISUAL_REVIEW",
                        "frames": frames, "unique_RGBA_frames": unique, "shared_row_fit": shared,
                        "frames_manifest": pin(manifest_path), "composed_manifest": pin(run / "manifest.json"),
                        "inspect_report": pin(run / "sprite-inspect.report.json"),
                        "inspect_errors": inspect["errors"], "inspect_warnings": inspect["warnings"],
                        "QA_gif": gif_info,
                        "cross_row_scale_against_identity": "UNMEASURED: common row ratio alone does not prove equal anatomy/helmet scale across rows",
                        "all_actual_foot_floor_grip_axis_markers": None})
    except BaseException as error:
        receipt["status"] = "STOPPED_PRESERVE_FAILED_CANDIDATE_NO_VISUAL_ACCEPTANCE"
        receipt["failure"] = repr(error)
        raise
    finally:
        receipt_path = run / "extraction-receipt-v001.json"
        write_new(receipt_path, receipt)
        files = [pin(path) for path in sorted(run.rglob("*")) if path.is_file()]
        write_new(run / "extracted-files-freeze-v001.json", {
            "schema": "hero218-220-extracted-files-freeze-v001", "state": state,
            "status": receipt["status"], "file_count": len(files), "files": files,
            "new_media_View": False, "E_retention_pending": True, "art_accepted": False})
        print(json.dumps({"state": state, "receipt": pin(receipt_path), "freeze": pin(run / "extracted-files-freeze-v001.json"),
                          "status": receipt["status"], "E_retention_pending": True}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--state", choices=("dodge", "hurt", "death"))
    parser.add_argument("--admission", type=Path)
    args = parser.parse_args()
    plan, request = validate_plan()
    if not args.extract:
        print(json.dumps({"text_and_tool_preparation_valid": True, "raw_bytes_read": False,
                          "status": "WAIT_ROOT_NOTIFICATION_RAW_F_E_RETAINED", "images_created": 0,
                          "next": "After Root notification record real F/E pins, then --extract --state STATE --admission PATH"}))
        return
    if not args.state or args.admission is None:
        raise ValueError("Explicit state and actual Root raw-admission record required")
    extract_one(plan, request, args.state, args.admission.resolve())


if __name__ == "__main__":
    main()
