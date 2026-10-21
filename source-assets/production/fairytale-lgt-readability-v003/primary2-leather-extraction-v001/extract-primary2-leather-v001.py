"""Extract native193/194/195 component candidates; no image viewing or fitting."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import shutil
import subprocess
import sys

import PIL
import numpy as np
from PIL import Image


OUT = Path(__file__).resolve().parent
PROJECT = Path("F:/Ourgame")
FAMILY = PROJECT / "source-assets/production/fairytale-lgt-readability-v003"
INPUT = FAMILY / "primary2-leather-input-v001"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
TIMES = [75, 75, 60, 60, 135, 135]
EXTRACT_SHA = "f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539"
WRAPPER_SHA = "2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3"
COMPONENTS = [
    ("Chest", "chest", 193, [90, 90], 512, "1bcc602bae05b9d313d508fb01cfbdf995a18d581debda09548e824a5ae2d380"),
    ("NearShoulder", "nearshoulder", 194, [60, 44], 512, "df59d491a1f939fa9138094917ba58aa86617b7f9069e20a6ff77f270948ce60"),
    ("FarShoulder", "farshoulder", 195, [32, 30], 256, "5b4300b99e42c715060c0fa523774586d612bc877791e36f215cecc175dba5ca"),
]
WATCHED = {}


def pin(path, watch=True):
    data = path.read_bytes()
    value = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = value
    return value


def write(relative, data):
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError("Ownership boundary")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def copy_exact(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise RuntimeError("Existing output cannot be overwritten")
    source_pin = pin(source)
    shutil.copy2(source, target)
    copied = pin(target)
    if source_pin["sha256"] != copied["sha256"] or source_pin["bytes"] != copied["bytes"]:
        raise RuntimeError("Input byte copy changed")
    return {"source": source_pin, "copy": copied}


def command(label, argv):
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    log = write(f"logs/{label}.log", result.stdout + result.stderr)
    record = {"argv": argv, "actual_exit_code": result.returncode, "log": pin(log)}
    path = write(f"logs/{label}-command.json", record)
    return {**record, "command_record": pin(path)}


def pixel_metrics(path):
    with Image.open(path) as image:
        if image.mode != "RGBA" or image.size != (512, 512):
            raise RuntimeError("Expected candidate source 512 RGBA")
        array = np.asarray(image).copy()
        alpha = array[:, :, 3]
        core = alpha >= 128
        edge = np.zeros(alpha.shape, dtype=bool)
        edge[:4, :] = edge[-4:, :] = True
        edge[:, :4] = edge[:, -4:] = True
        box = image.getchannel("A").getbbox()
        core_box = image.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
        return {"source": pin(path), "mode": image.mode, "canvas_px": list(image.size),
                "RGBA_pixels_sha256": hashlib.sha256(array.tobytes()).hexdigest(),
                "alpha_nonzero_bbox_ltrb_exclusive": list(box) if box else None,
                "core128_bbox_ltrb_exclusive": list(core_box) if core_box else None,
                "nonzero_alpha_pixels": int(np.count_nonzero(alpha)),
                "core128_RGBA_pixels": int(np.count_nonzero(core)),
                "core128_RGBA_row_major_sha256": hashlib.sha256(array[core].tobytes()).hexdigest(),
                "partial_alpha_pixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
                "distinct_core_RGB_colors": int(len(np.unique(array[:, :, :3][core], axis=0))),
                "pure_green_core128_pixels": int(np.count_nonzero(core & np.all(array[:, :, :3] == [0, 255, 0], axis=2))),
                "pure_green_nonzero_alpha_pixels": int(np.count_nonzero((alpha > 0) & np.all(array[:, :, :3] == [0, 255, 0], axis=2))),
                "edge_nonzero_alpha_pixels_margin4": int(np.count_nonzero((alpha > 0) & edge)),
                "bodyfreecount": None, "bodyfreecount_measured": False,
                "bodyfree_semantic_note": "RGBA/chroma/edge counts cannot count anatomical bodies, hands or helmets. No semantic mask or detector was supplied; do not turn six connected components into a claim of body-free art.",
                "new_component_A": None, "matching_body_B": None, "integer_delta_xy": None}


def curate_shared_run(run, state):
    sys.path.insert(0,str(SG))
    from sprite_gen.curate.curation import load_curation, stamp_curation, state_plan, frame_variant, pixel_snap_scale
    if load_curation(run) is not None:raise RuntimeError("Unexpected old sidecar")
    # HD canonical frame-N.png is selected; false sidecar variant would wrongly
    # select nonexistent .plain twins. Request fit.pixel_unfake stays false.
    payload=stamp_curation(run,{"version":1,"kind":"sprite-gen-curation","states":{state:{"selected":list(range(6)),"transforms":{}}}})
    sidecar=write(run.relative_to(OUT)/"curation.json",payload)
    loaded=load_curation(run);order,transforms=state_plan(loaded,state,6)
    request=json.loads((run/"sprite-request.json").read_text("utf-8-sig"))
    if order!=list(range(6)) or transforms or frame_variant(loaded,state)!="pixel" or pixel_snap_scale(request) is not None or request["fit"]["pixel_unfake"] is not False:
        raise RuntimeError("Explicit canonical HD identity selection failed")
    result=command(f"export-curated-{state}-v001",[str(PYTHON),"-B","-X","utf8",str(SG/"scripts/export_curated_pngs.py"),"--run-dir",str(run),"--state",state,"--selected-only"])
    if result["actual_exit_code"]:raise RuntimeError("Actual standard curated export failed; preserved log")
    metrics=[];provenance=[]
    for frame in range(6):
        before=run/f"frames/{state}/frame-{frame}.png";after=run/f"curated/frame-{frame}.png"
        with Image.open(before) as a,Image.open(after) as b:
            if not np.array_equal(np.asarray(a.convert("RGBA")),np.asarray(b.convert("RGBA"))):raise RuntimeError("Identity export changed RGBA")
        metric=pixel_metrics(after);metric["pre_curation_source"]=pin(before);metric["curated_export_RGBA_equal"]=True
        metric["curation_sidecar"]=pin(sidecar);metrics.append(metric)
        provenance.append({"frame":frame,"pre_curation_source":pin(before),"curated_export":pin(after),"curation":pin(sidecar),"RGBA_equal":True,"selected_index":frame,"pixel_snap_scale":None,"canonical_variant_filename_label":"pixel","fit_pixel_unfake":False,"A_B_delta_measured":False})
    return {"command":result,"sidecar":pin(sidecar),"provenance":provenance,"metrics":metrics,"selection_role":"Root authorized all six for extraction/feature trial; not fit, full animation or final install acceptance"}


def main():
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError("Use sprite-gen venv")
    if OUT != FAMILY / "primary2-leather-extraction-v001" or list(OUT.glob("run-*")):
        raise RuntimeError("Unexpected or existing output")
    installed = SG / "sprite_gen/frames/extract.py"
    old_wrapper = PROJECT / "tools/scripts/extract-sprite-shared-row-scale.py"
    if pin(installed)["sha256"] != EXTRACT_SHA or pin(old_wrapper)["sha256"] != WRAPPER_SHA:
        raise RuntimeError("Pinned extractor/fit extension changed")
    copy_exact(old_wrapper, OUT / "tool-provenance/shared-row-fit-original-v001.py")
    wrapper_text = old_wrapper.read_text(encoding="utf-8")
    parser_line = "    args = parser.parse_args()"
    if wrapper_text.count(parser_line) != 1:
        raise RuntimeError("Wrapper CLI changed")
    wrapper_text = wrapper_text.replace(parser_line, "    parser.add_argument(\"--min-used-pixels\", type=int, required=True)\n" + parser_line + "\n    require(args.min_used_pixels in (256,512), \"Only authorized explicit component floors256/512\")", 1)
    original_cli = "        sys.argv = [str(EXTRACT), \"--run-dir\", str(run)]"
    if wrapper_text.count(original_cli) != 1:
        raise RuntimeError("Native fit hook bridge changed")
    wrapper_text = wrapper_text.replace(original_cli, "        sys.argv = [str(EXTRACT), \"--run-dir\", str(run), \"--min-used-pixels\", str(args.min_used_pixels)]", 1)
    wrapper = write("shared-HD-fit-explicit-component-min-v001.py", wrapper_text)
    tools = [SG / "scripts/export_curated_pngs.py", SG / "sprite_gen/compose/export_pngs.py", SG / "sprite_gen/curate/curation.py", SG / "scripts/extract_sprite_row_frames.py", installed, SG / "scripts/inspect_sprite_run.py", SG / "sprite_gen/qa/inspect.py", old_wrapper]
    write("toolchain-v001.json", {"python_executable": sys.executable, "python_version": platform.python_version(),
          "pillow_version": PIL.__version__, "numpy_version": np.__version__, "installed_tools": [pin(path) for path in tools],
          "candidate_fit_bridge": pin(wrapper), "installed_or_project_tools_modified": False,
          "fit_bridge_change": "Only explicit min-used-pixels CLI forwarding. Original shared-HD fitting/chroma/components/edge/count logic unchanged. Subject stays character; no effect relabel.",
          "standard_extract_does_not_consume_shared_row_scale": True})
    approved_path=INPUT/"primary2-leather-native-input-approved-v001.json"
    approved=json.loads(approved_path.read_text("utf-8-sig"));approved_pin=pin(approved_path)
    if approved_pin["sha256"]!="91d23ff48ae37aa797155fc43e1890d676ce9a68f797e088e8b024ecb20c5729":raise RuntimeError("Approved handoff changed")
    copy_exact(approved_path,OUT/"inputs/approved-handoff-exact.json")
    mapping_path=Path(approved["actual_runtime_source_version_mapping"]["path"])
    if pin(mapping_path)!=approved["actual_runtime_source_version_mapping"]:raise RuntimeError("Actual Body171 source mapping changed")
    mapping=json.loads(mapping_path.read_text("utf-8-sig"))
    if mapping["body_native_request"]!=171 or mapping["body_run_version"]!="run-primary2-v004":raise RuntimeError("Wrong actual body generation")
    for body in mapping["body_frames"]:
        for entry in [body["actual_canonical_body"]]+[e["current_imported_source"] for e in body["existing_runtime_four_layers_to_keep"]]:
            if pin(Path(entry["path"]))!=entry:raise RuntimeError("Body171 exact source differs")
    copy_exact(mapping_path,OUT/"inputs/actual-body171-source-version-mapping.json")
    runs = []
    source_index = []
    for name, token, native, window, minimum, raw_sha in COMPONENTS:
        source_run = INPUT / f"run-{token}-primary2-v001"
        state = f"leather_{token}_sword_primary2"
        raw = source_run / f"raw/{state}.png"
        request = source_run / "sprite-request.json"
        receipt_path = FAMILY / f"generation-control-v001/generation-receipt{native}-v001.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if pin(raw)["sha256"] != raw_sha or pin(raw) != receipt["canonical_raw"]:
            raise RuntimeError("Actual native raw pin differs")
        pin(receipt_path)
        approved_row=next(r for r in approved["rows"] if r["component"]==name)
        if receipt["source_handoff"]!=approved_pin or pin(request)!=approved_row["request"]:raise RuntimeError("Native raw not bound to exact approved request")
        with Image.open(raw) as im:
            if list(im.size)!=receipt["raw_size"] or im.mode!=receipt["raw_mode"]:raise RuntimeError("Actual native raw canvas differs")
        # Keep 195's real2171x724 canvas unchanged; no pad/resize shortcut.
        q = json.loads(request.read_text(encoding="utf-8"))
        if q["states"][state]["frames"] != 6 or q["states"][state]["durations_ms"] != TIMES:
            raise RuntimeError("Six-phase timing changed")
        if q["fit"]["pixel_unfake"] is not False or q["fit"]["shared_row_scale"] is not True:
            raise RuntimeError("Explicit nonquantized shared-HD fit required")
        if [q["cell"]["width"] - 2 * q["cell"]["safe_margin_x"], q["cell"]["height"] - 2 * q["cell"]["safe_margin_y"]] != window:
            raise RuntimeError("Shared fit window changed")
        originals = []
        for relative in [f"raw/{state}.png", "sprite-request.json", "base-source.png", f"prompts/{state}.txt"]:
            originals.append(copy_exact(source_run / relative, OUT / f"original-input/{token}" / relative))
        write(f"original-input/{token}/native-source-receipt-pin.json", {"native_request": native, "receipt": pin(receipt_path), "source_copies": originals})
        for mode in ["standard-baseline", "shared-HD"]:
            run = OUT / f"run-{token}-{mode}-v001"
            for relative in [f"raw/{state}.png", "sprite-request.json", "base-source.png", f"prompts/{state}.txt"]:
                copy_exact(source_run / relative, run / relative)
            before = pin(run / "sprite-request.json")
            # Baseline deliberately retains the standard whole-character512
            # floor, so any mismatch with a tiny attachment is preserved.
            argv = [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/extract_sprite_row_frames.py" if mode == "standard-baseline" else wrapper), "--run-dir", str(run)]
            if mode == "shared-HD":
                argv.extend(["--min-used-pixels", str(minimum)])
            extraction = command(f"extract-{token}-{mode}-v001", argv)
            after = pin(run / "sprite-request.json")
            inspection = command(f"inspect-{token}-{mode}-v001", [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/inspect_sprite_run.py"),
                                 "--run-dir", str(run), "--states", state, "--report", str(run / "inspect-report.json")])
            fm_path, inspect_path = run / "frames/frames-manifest.json", run / "inspect-report.json"
            fm = json.loads(fm_path.read_text(encoding="utf-8")) if fm_path.exists() else None
            inspect = json.loads(inspect_path.read_text(encoding="utf-8")) if inspect_path.exists() else None
            files = sorted((run / f"frames/{state}").glob("frame-*.png"))
            metrics = [pixel_metrics(path) for path in files]
            entry = {"component": name, "native_request": native, "mode": mode, "run_dir": run.as_posix(), "state": state,
                     "extraction": extraction, "inspection": inspection, "frames": len(files), "metrics": metrics,
                     "frames_manifest": pin(fm_path) if fm_path.exists() else None,
                     "manifest_ok": fm.get("ok") if fm else None, "manifest_errors": fm.get("errors") if fm else None,
                     "manifest_warnings": fm.get("warnings") if fm else None,
                     "shared_row_fit": fm["rows"][0].get("shared_row_fit") if fm and fm.get("rows") else None,
                     "inspect_report": pin(inspect_path) if inspect_path.exists() else None,
                     "inspect_ok": inspect.get("ok") if inspect else None,
                     "inspect_errors": inspect.get("errors") if inspect else None, "inspect_warnings": inspect.get("warnings") if inspect else None,
                     "actual_min_used_pixels": minimum if mode == "shared-HD" else 512,
                     "request_before": before, "request_after": after, "working_request_bytes_unchanged": before["sha256"] == after["sha256"],
                     "no_pixel_unfake_or_palette_quantization": not (run / "palette.lock.json").exists(),
                     "semantic_fit_or_full_animation_accepted": False}
            runs.append(entry)
            if mode == "shared-HD":
                available = extraction["actual_exit_code"] == 0 and fm is not None and fm["ok"] is True and len(files) == 6
                export=curate_shared_run(run,state) if available else None
                entry["curated_export"]=export
                curated_metrics=export["metrics"] if export else []
                source_index.append({"component": name, "native_request": native, "state": state, "shared_fit_window": window,
                                     "explicit_min_used_pixels": minimum, "available_for_Root_feature_measurement": available,
                                     "shared_row_fit": entry["shared_row_fit"], "frames": [{"frame": i, "duration_ms": TIMES[i], **metric} for i, metric in enumerate(curated_metrics)],
                                     "missing_frames_are_not_faked": True, "new_A_B_delta_all_null": True,
                                     "actual_body171_run_primary2_v004_fit_review_required": True, "curated_export": export["sidecar"] if export else None})
    mismatches = [path.as_posix() for path, before in WATCHED.items() if pin(path, False) != before]
    if mismatches:
        raise RuntimeError(f"Read-only source changed: {mismatches}")
    index = write("primary2-eighteen-source-index-v001.json", {"schema": "primary2-leather-six-phase-three-component-source-index-v001",
          "created_local": datetime.datetime.now().astimezone().isoformat(), "components": source_index,
          "actual_available_frame_count": sum(len(row["frames"]) for row in source_index), "expected_frame_count": 18,
          "all_three_rows_available": all(row["available_for_Root_feature_measurement"] for row in source_index),
          "durations_ms": TIMES, "all_A_B_delta_null": True, "new_media_viewed": False,
          "semantic_bodyfreecount_known": False, "fit_accepted": False, "imported": False,
          "Root_raw_review_context": "Root actually retained/reviewed193/194/195 at E305/E307 before authorizing extraction. Far195 realcanvas2171x724 is preserved, no padding or resize.",
          "actual_body171_source_version_mapping": pin(mapping_path), "approved_native_handoff": approved_pin, "next_boundary": "Root E-retains new curated source frames before viewing, then measures actual A/B against actual Body171 run-primary2-v004 and verifies fit/occlusion. No assembly/import here."})
    report = write("extraction-numeric-report-v001.json", {"schema": "primary2-leather-extraction-numeric-v001", "created_local": datetime.datetime.now().astimezone().isoformat(),
          "runs": runs, "source_index": pin(index), "read_only_sources_rechecked": len(WATCHED), "source_mismatches": [],
          "generated": False, "new_media_viewed": False, "Source_UE_ledger_or_media_modified": False,
          "lower_than_256_floor_attempted": False, "semantic_count_or_A_fabricated": False,
          "limitations": ["Standard and shared extraction/inspect exit codes are actual. Preserve default floor failures and low-motion warnings, even when another declared component floor produces frames.",
                         "Shared scale is computed per six-frame row; no per-frame normalization, pixel-unfake, palette quantization or manual paint/crop repair.",
                         "Body-free semantic counts cannot be inferred from RGBA/core/green/edge metrics; bodyfreecount is null without actual semantic masks/visual review.",
                         "New components remain unregistered against actual Body171 run-primary2-v004; extraction/identity curated export is not fit or full animation acceptance."]})
    lines = [f"- {row['component']} {row['mode']}: extract exit{row['extraction']['actual_exit_code']}; inspect exit{row['inspection']['actual_exit_code']}; frames{row['frames']}; inspect warnings={row['inspect_warnings']}." for row in runs]
    write("HANDOFF.md", "# Primary2软皮六相提取诊断 v001\n\n" + "\n".join(lines) + "\n\n" +
          "供Root测feature的Source见 `primary2-eighteen-source-index-v001.json` 与各 shared-HD run 的 curated/，显式selected0..5侧车和标准export已执行，逐帧RGBA等于pre-curation frames。A/B/delta仍null；实际Body171是run-primary2-v004，未自动贴合/镜像/动作补帧/导入。Far195原2171×724不改，失败与lowmotion保留。\n\n" +
          "min512/512/256为本组件配置；低于256未尝试。默认baseline失败及inspect低motion全部保留。bodyfreecount无语义mask无法由通道推断，诚实为null；已给每帧coreRGBA/hash/纯绿/edge及真实共同scale。执行者未查看新输出、未生成/导入/改旧run或tools/Source/UE/ledger/媒体。Root先E留后看。\n")
    files = [pin(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for item in files:
        item["path"] = Path(item["path"]).relative_to(OUT).as_posix()
    freeze = write("extraction-freeze-v001.json", {"schema": "primary2-leather-extraction-freeze-v001", "files": files,
          "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(item["bytes"] for item in files),
          "actual_available_frame_count": sum(len(row["frames"]) for row in source_index), "viewed": False, "fit_accepted": False})
    print(json.dumps({"report": pin(report), "source_index": pin(index), "freeze": pin(freeze),
          "actual_available_frame_count": sum(len(row["frames"]) for row in source_index),
          "shared_rows_available": [row["available_for_Root_feature_measurement"] for row in source_index],
          "actual_run_exits": [{"component": row["component"], "mode": row["mode"], "extract": row["extraction"]["actual_exit_code"], "inspect": row["inspection"]["actual_exit_code"]} for row in runs],
          "frozen_files": len(files), "frozen_bytes": sum(item["bytes"] for item in files), "new_media_viewed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
