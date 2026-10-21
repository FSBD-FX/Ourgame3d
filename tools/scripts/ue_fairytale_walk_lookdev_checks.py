"""Frozen six-PNG preflight for the v008 source walk trial. Stdlib only."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "source-assets/production/fairytale-hero-v001/sprite-run-walk-v008"
MANIFEST = ROOT / "source-assets/production/fairytale-walk-lookdev-v001/manifests/import-walk-lookdev-v001.json"
MANIFEST_SHA = "16c5cfef46662730a48ac1a5c68a6e250710f5330fe11c57b548d7e2779787fd"
NAMESPACE = "/Game/Production/ArtTrials/EV047/v002/HeroCommonWalk"
DISK = ROOT / "UnrealGame/Content/Production/ArtTrials/EV047/v002/HeroCommonWalk"
DECODER = Path(__file__).with_name("ue-import-armor-primary2-four-v001.py")
DECODER_SHA = "5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a"
IMPORT_RECEIPT = ROOT / "UnrealGame/Saved/Bootstrap/fairytale-walk-lookdev-v001-import-20261015-193357-409584.json"
IMPORT_RECEIPT_SHA = "8644226159e33d7f77eafffb7bce65de206549c3ea63a4a9624f1b24cfa60f5f"


def require(condition, why):
    if not condition:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def old_packages_unchanged():
    before = json.loads((MANIFEST.parent / "old-production863-before-import.json").read_text(encoding="utf-8"))["files"]
    require(len(before) == 863, "Frozen old production package inventory changed")
    for row in before:
        p = ROOT / row["path"]
        require(p.stat().st_size == row["bytes"] and sha(p) == row["sha256"], "Old production package changed: " + str(p))
    return len(before)


def imported_packages_unchanged(document):
    require(sha(IMPORT_RECEIPT) == IMPORT_RECEIPT_SHA, "Actual native import receipt changed")
    receipt = json.loads(IMPORT_RECEIPT.read_text(encoding="utf-8"))
    require(receipt["success"] and receipt["actual_count"] == receipt["saved_count"] == 6
            and receipt["manifest_sha256"] == MANIFEST_SHA, "Actual six import did not succeed")
    require(len(receipt["assets"]) == 6, "Actual import package inventory changed")
    for source, saved in zip(document["assets"], receipt["assets"]):
        require(source["object_path"] == saved["object_path"] and source["source_sha256"] == saved["source_sha256"], "Saved package/source binding changed")
        path = Path(saved["saved_uasset"])
        require(path.resolve() == (DISK / (source["name"] + ".uasset")).resolve()
                and path.stat().st_size == saved["saved_bytes"] and sha(path) == saved["saved_sha256"], "Native saved package changed")
    return 6


def preflight(require_unused=True):
    require(sha(MANIFEST) == MANIFEST_SHA and sha(DECODER) == DECODER_SHA, "Frozen manifest/PNG decoder changed")
    d = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(d["schema"] == "frozen-fairytale-walk-lookdev-six-v1" and d["frozen"] is True, "Wrong source contract")
    require(d["namespace"] == NAMESPACE and d["asset_count"] == 6 and d["canvas_px"] == [512,512], "Wrong namespace/count/canvas")
    require(d["durations_ms"] == [83]*6 and d["loop"] is True and d["native_facing"] == 1, "Original phase/timing contract changed")
    require(d["preview_canvas_size"] == 72*512/416 and d["display_pivot_px"] == [256,464] and not d["per_frame_resize"], "Presentation registration/scale changed")
    require(not d["runtime_verified"] and not d["full_motion_accepted"] and d["formal_complete_units"] == 0, "Import cannot grant content acceptance")
    exact_refs = {"request":"sprite-request.json","frames":"frames/frames-manifest.json","atlas":"manifest.json","raw":"raw/walk.png","registration":"source-cell-registration-receipt.json"}
    require(set(d["references"]) == set(exact_refs), "Unexpected/missing source references")
    for name, relative in exact_refs.items():
        ref = d["references"][name]
        require(Path(ref["path"]).resolve() == (RUN/relative).resolve() and sha(ref["path"]) == ref["sha256"], "Changed source provenance: " + name)
    frames = json.loads((RUN/exact_refs["frames"]).read_text(encoding="utf-8"))
    atlas = json.loads((RUN/"manifest.json").read_text(encoding="utf-8"))
    require(frames["ok"] and frames["errors"] == frames["warnings"] == [] and len(frames["rows"]) == 1, "Source extraction did not pass")
    row = frames["rows"][0]
    require(row["method"] == "components" and row["frames"] == 6 and row["state"] == "walk", "Not six extracted walk components")
    require(row["shared_row_fit"]["scale"] == 416/1043 and row["shared_row_fit"]["horizontal_registration"] == "native_source_cell", "Native registration changed")
    require(atlas["animation"]["rows"]["walk"]["durations_ms"] == [83]*6 and len(atlas["frame_layout"]["rows"]["walk"]) == 6, "Runtime source layout/timing changed")
    spec = importlib.util.spec_from_file_location("walk_native_png_decoder", DECODER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require([r["frame"] for r in d["assets"]] == list(range(6)), "Missing/reordered walk source frames")
    for i, asset in enumerate(d["assets"]):
        source = Path(asset["source"])
        name = f"T_Fairytale_HeroWalk_{i:03d}_v002"
        require(source.resolve() == (RUN/f"curated/frame-{i}.png").resolve(), "Only exact curated v008 source accepted")
        require(source.stat().st_size == asset["source_bytes"] and sha(source) == asset["source_sha256"], "PNG source changed")
        require((asset["name"],asset["package_path"],asset["object_path"]) == (name,NAMESPACE+"/"+name,NAMESPACE+"/"+name+"."+name), "Destination changed")
        pixels = module.inspect_rgba_png(source.read_bytes())
        require(pixels["nonempty"] and pixels["corners_transparent"] and pixels["alpha_extrema"] == [0,255], "Invalid transparent PNG")
        require(pixels["bbox_px"] == asset["source_bbox"] == row["frame_records"][i]["bbox"], "Actual source bbox changed")
        require(row["frame_records"][i]["edge_pixels"] == row["frame_records"][i]["chroma_adjacent_pixels"] == 0, "Unsafe source edge/key")
        require(asset["display_pivot_px"] == [256,464] and asset["duration_ms"] == 83 and asset["native_facing"] == 1, "Source frame metadata changed")
    require(len({r["source_sha256"] for r in d["assets"]}) == 6, "Duplicate pose substitution")
    if require_unused:
        require(not DISK.exists() or not any(p.is_file() for p in DISK.rglob("*")), "Existing namespace; never overwrite")
    else:
        imported_packages_unchanged(d)
    old_packages_unchanged()
    return d
