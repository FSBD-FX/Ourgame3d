"""Private stdlib preflight for eight candidate EV047 idle textures only.

No UE import, pixel edits, resampling, generation, network or gameplay access.
The existing CRC/RGBA decoder is loaded from one exact SHA-pinned repository file.
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = (ROOT / "source-assets/production").resolve()
MANIFEST = PRODUCTION / "fairytale-lookdev-v001/manifests/import-lookdev-v001.json"
MANIFEST_SHA256 = "f3cea39ccea3432568ef1e5f37d919f16b3fb083c4a47be22c8783287481b445"
STONE_ROOTS = [[260, 464], [257, 464], [264, 464], [265, 464]]
NAMESPACE = "/Game/Production/ArtTrials/EV047/v001"
DISK = ROOT / "UnrealGame/Content/Production/ArtTrials/EV047/v001"
ACTORS = {
    "hero": ("HeroCommonIdle", "HeroIdle", 1, PRODUCTION / "fairytale-hero-v001/sprite-run-idle-v002"),
    "stone": ("StoneIdle", "StoneIdle", -1, PRODUCTION / "fairytale-stone-knight-v001/sprite-run-idle-v002"),
}
HERO_SHA256 = (
    "f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718",
    "7bedc3d428f8b1e008d0627d671660b0fd3a68c61c6593872e800d0f19e395a3",
    "5d3d6c88289f2aa6347c98869082e551ed2918a86725376af75fbd698f412bbb",
    "c27bfb46301397c627f7346a8890a84358ad1e0465f9fa3cc238e8600cedfe4c",
)
NATIVE = Path(__file__).with_name("ue-import-armor-primary2-four-v001.py")
NATIVE_SHA256 = "5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_hash(path, digest):
    require(isinstance(digest, str) and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), "Malformed/unfrozen SHA256")
    data = Path(path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, "Changed frozen source: " + str(path))
    return data


def require_unused_destination(destination):
    require(not destination.exists() or not any(p.is_file() for p in destination.rglob("*")), "Namespace has disk files; refusing overwrite")


def require_exact_set(actual, expected):
    require(len(actual) == len(expected) == len(set(actual)) == len(set(expected)) and set(actual) == set(expected), "Missing/extra/duplicate object or package")


def validate_contract(document, stone_roots):
    d = document
    require(d.get("schema") == "frozen-fairytale-lookdev-eight-textures-v1" and d.get("version") == 1 and d.get("frozen") is True, "Not the frozen lookdev v001 contract")
    require(d.get("namespace") == NAMESPACE and d.get("asset_count") == 8, "Wrong unused namespace/count")
    for flag in ("runtime_verified", "motion_accepted", "full_character_accepted", "four_armor_accepted", "complete20equipment_combinations"):
        require(d.get(flag) is False, "Source import cannot certify " + flag)
    require(type(d.get("formal_complete_units")) is int and d["formal_complete_units"] == 0, "Full units remain 0/15")
    require(set(d.get("actors", {})) == set(ACTORS), "Exactly hero+stone required")
    require(stone_roots is not None and len(stone_roots) == 4, "Root has not confirmed the four Stone roots")
    roots = {"hero": [[256, 464] for _ in range(4)], "stone": stone_roots}
    require(len(d.get("assets", [])) == 8 and [(r["actor"], r["frame"]) for r in d["assets"]] == [(a, i) for a in ACTORS for i in range(4)], "Wrong/reordered eight frame rows")
    for actor, (folder, prefix, facing, run) in ACTORS.items():
        meta = d["actors"][actor]
        require(meta["frame_count"] == 4 and meta["canvas_px"] == [512, 512] and meta["loop"] is True, "Changed native four-frame loop/canvas")
        require(meta["durations_ms"] == [167] * 4 and all(type(t) is int for t in meta["durations_ms"]), "Durations must be manifest167ms, never GIF160ms")
        require(type(meta["native_facing"]) is int and meta["native_facing"] == facing, "Changed native facing")
        require(meta["root_confirmed"] is True and meta["roots_px"] == roots[actor], "Unconfirmed/changed actor roots")
        for row in (r for r in d["assets"] if r["actor"] == actor):
            i = row["frame"]
            name = f"T_Fairytale_{prefix}_{i:03d}_v001"
            package = NAMESPACE + "/" + folder + "/" + name
            source = Path(row["source"]).resolve()
            require(source.is_relative_to(PRODUCTION) and source == (run / "curated" / f"frame-{i}.png").resolve(), "Only exact curated v002 source frames are importable")
            require((row["name"], row["package_path"], row["object_path"]) == (name, package, package + "." + name), "Changed/duplicate asset destination")
            require(row["root_px"] == roots[actor][i] and row["native_facing"] == facing and row["duration_ms"] == 167, "Frame root/facing/time differs from actor contract")
    require_exact_set([r["object_path"] for r in d["assets"]], [NAMESPACE + "/" + folder + "/" + f"T_Fairytale_{prefix}_{i:03d}_v001.T_Fairytale_{prefix}_{i:03d}_v001" for folder, prefix, _, _ in ACTORS.values() for i in range(4)])


def native_decoder():
    checked_hash(NATIVE, NATIVE_SHA256)
    spec = importlib.util.spec_from_file_location("fairytale_native_png_v001", NATIVE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inspect_source(path, digest):
    data = checked_hash(path, digest)
    pixels = native_decoder().inspect_rgba_png(data)
    require(pixels["nonempty"] and pixels["corners_transparent"] and pixels["alpha_extrema"] == [0, 255], "Invalid native RGBA alpha")
    left, top, right, bottom = pixels["bbox_px"]
    require(0 < left < right < 512 and 0 < top < bottom < 512, "Actual nontransparent pixels touch canvas edges")
    return pixels


def hero_preflight():
    run = ACTORS["hero"][3]
    rows = []
    for i, digest in enumerate(HERO_SHA256):
        path = run / "curated" / f"frame-{i}.png"
        rows.append({"frame": i, "source": str(path), "source_sha256": digest, "pixels": inspect_source(path, digest), "root_px": [256, 464], "duration_ms": 167, "native_facing": 1})
    return {"source_validation_success": True, "scope": "Hero-only preparation; not full8 import preflight", "assets": rows, "actual_count": 4, "unreal_import_run": False, "runtime_verified": False}


def preflight():
    require(MANIFEST_SHA256 is not None and STONE_ROOTS is not None, "Full import is disabled until actual Stone roots and frozen manifest are confirmed")
    document = json.loads(checked_hash(MANIFEST, MANIFEST_SHA256).decode("utf-8-sig"))
    validate_contract(document, STONE_ROOTS)
    hashes = {MANIFEST: MANIFEST_SHA256, NATIVE: NATIVE_SHA256}
    rows = copy.deepcopy(document["assets"])
    for actor, (_, _, _, run) in ACTORS.items():
        references = document["actors"][actor]["references"]
        paths = {"run_manifest": "manifest.json", "frames_manifest": "frames/frames-manifest.json", "sprite_request": "sprite-request.json", "raw_idle": "raw/idle.png"}
        parsed = {}
        for key, relative in paths.items():
            record = references[key]; path = Path(record["path"]).resolve()
            require(path == (run / relative).resolve() and path.is_relative_to(PRODUCTION), "Unexpected exact source provenance path")
            data = checked_hash(path, record["sha256"]); hashes[path] = record["sha256"]
            if path.suffix == ".json":
                parsed[key] = json.loads(data.decode("utf-8-sig"))
        run_manifest, frames = parsed["run_manifest"], parsed["frames_manifest"]
        if actor == "stone":
            anchor = document["actors"][actor]["sole_anchor_measurement"]
            anchor_path = Path(anchor["path"]).resolve()
            require(anchor_path == (PRODUCTION / "fairytale-stone-knight-v001/sole-anchor-measurement-v001.json").resolve(), "Wrong exact sole measurement")
            measured = json.loads(checked_hash(anchor_path, anchor["sha256"]).decode("utf-8-sig")); hashes[anchor_path] = anchor["sha256"]
            require([p["frame"] for p in measured] == list(range(4)), "Missing/reordered measured sole frame")
            for record, root in zip(measured, STONE_ROOTS):
                runs = record["bottom4_column_runs"]
                require(len(runs) == 2 and record["native_facing"] == -1, "Expected two separate actual feet")
                # Measurement intervals are left-inclusive/right-exclusive.
                midpoint = sum(left + right - 1 for left, right in runs) / 4
                require([round(midpoint), record["bbox_alpha128"][3]] == root, "Root is not the confirmed two-foot contact midpoint")
        timing = run_manifest["animation"]["rows"]["idle"]
        require(timing["frames"] == 4 and timing["durations_ms"] == [167] * 4 and timing["loop"] is True and run_manifest["degraded_static_fallback"] is False, "Source timing/fallback changed")
        require(frames["ok"] is True and frames["errors"] == frames["warnings"] == [] and len(frames["rows"]) == 1, "Extraction has errors/warnings")
        row = frames["rows"][0]
        require(row["state"] == "idle" and row["method"] == "components" and row["frames"] == 4 and row["ok"] is True, "Not actual four-frame component extraction")
        require([p["index"] for p in row["frame_records"]] == list(range(4)) and all(p["edge_pixels"] == p["chroma_adjacent_pixels"] == 0 for p in row["frame_records"]), "Unsafe extraction edges/chroma")
        for asset in (a for a in rows if a["actor"] == actor):
            path = Path(asset["source"]).resolve(); pixels = inspect_source(path, asset["source_sha256"])
            require(pixels == asset["pixels"] and path.stat().st_size == asset["source_bytes"], "Actual source pixel/byte metadata changed")
            require(asset["body_height_px"] == pixels["bbox_px"][3] - pixels["bbox_px"][1] == document["actors"][actor]["body_heights_px"][asset["frame"]], "Body alpha height differs")
            require(row["frame_records"][asset["frame"]]["bbox"] == pixels["bbox_px"], "Curated frame differs from extraction bbox")
            hashes[path] = asset["source_sha256"]
            original_frame = run / "frames/idle" / f"frame-{asset['frame']}.png"
            checked_hash(original_frame, asset["source_sha256"]); hashes[original_frame] = asset["source_sha256"]
    require(len({r["source_sha256"] for r in rows}) == 8, "Expected eight distinct actual frame files")
    for actor, visible, canvas in (("hero", 72.0, 88.61538461538461), ("stone", 93.6, 123.9927554980595)):
        meta = document["actors"][actor]
        require(meta["preview_visible_body_height_world"] == visible and meta["preview_canvas_size_world"] == canvas and meta["per_frame_rescale"] is False, "Changed fixed preview scale or introduced per-frame fitting")
    require_unused_destination(DISK)
    return {"manifest": document, "rows": rows, "hashes": hashes, "summary": {"source_validation_success": True, "native_RGBA512_count": 8, "verified_reference_count": len(hashes), "manifest_sha256": MANIFEST_SHA256, "namespace": NAMESPACE, "unreal_import_run": False, "runtime_verified": False, "motion_accepted": False, "formal_complete_units": 0}}
