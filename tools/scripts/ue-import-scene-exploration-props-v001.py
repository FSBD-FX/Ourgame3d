"""Import exactly two frozen SceneExploration prop candidates into an unused package.

Ordinary Python --validate-only checks frozen files/native PNG pixels without UE.
UE Editor Python imports only the two 512 RGBA textures, preserving their canvas.
No existing package is edited; a failed partial import is retained for inspection
and a repeated attempt refuses that populated destination. Inferred footprints,
the wall's plane mismatch and the separate foundation route remain unverified at
runtime. This tool neither changes gameplay geometry nor approves scene art.
"""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import math
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
ASSET_ROOT = (ROOT / "source-assets/production/scene-exploration-props-v001").resolve()
MANIFEST = ASSET_ROOT / "manifests/import-scene-exploration-props-v001.json"
MANIFEST_SHA256 = "a6eb21c81c1c2a29ac703454ee03318604e4cf5c96bde8070540e3f8c2a5c969"
PACKAGE = "/Game/Production/SceneExploration/v001"
NAMES = {"moss_low_wall": "T_scene_moss_low_wall_v001", "old_city_stele": "T_scene_old_city_stele_v001"}
spec = importlib.util.spec_from_file_location("scene_native_png_checks", Path(__file__).with_name("ue-import-armor-primary2-four-v001.py"))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
require = helper.require


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def point(value):
    return isinstance(value, list) and len(value) == 2 and all(finite_number(x) and 0 <= x <= 512 for x in value)


def require_unused_disk_destination(destination):
    require(not destination.exists() or not any(p.is_file() for p in destination.rglob("*")), "Destination has files; refusing overwrite")


def native_root_rgba(data, root):
    """Sample the actual visible root after the shared decoder has checked PNG CRC/header.

    The shared inspector reports alpha extent/bbox but not individual RGBA pixels.
    Decode the same native rows with stdlib; never crop, resample or rewrite them.
    """
    require(all(isinstance(x, int) and not isinstance(x, bool) and 0 <= x < 512 for x in root), "Root must address an actual source pixel")
    offset, chunks = 8, []
    while offset + 12 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        if kind == b"IDAT":
            chunks.append(data[offset + 8:offset + 8 + length])
        offset += length + 12
        if kind == b"IEND":
            break
    raw, stride = zlib.decompress(b"".join(chunks)), 512 * 4
    previous = bytearray(stride)
    for y in range(root[1] + 1):
        start = y * (stride + 1)
        filtering = raw[start]
        row = bytearray(raw[start + 1:start + 1 + stride])
        if filtering:
            for i in range(stride):
                a, b, c = row[i - 4] if i >= 4 else 0, previous[i], previous[i - 4] if i >= 4 else 0
                if filtering == 1:
                    predictor = a
                elif filtering == 2:
                    predictor = b
                elif filtering == 3:
                    predictor = (a + b) // 2
                else:
                    p = a + b - c
                    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                    predictor = a if pa <= pb and pa <= pc else b if pb <= pc else c
                row[i] = (row[i] + predictor) & 255
        previous = row
    return list(previous[root[0] * 4:root[0] * 4 + 4])


def verify_references(node, hashes, originals):
    # The frozen manifest explicitly names two C: native-tool originals. They
    # are read-only provenance and must hash-identically to their production
    # raw copies. They can never be an imported texture source.
    if isinstance(node, dict):
        for key, value in node.items():
            digest_key = "sha256" if key == "path" else key[:-5] + "_sha256" if key.endswith("_path") else key + "_sha256"
            if isinstance(value, str) and digest_key in node:
                path = Path(value).resolve()
                digest = node[digest_key]
                if key == "tool_original_path":
                    require(path in originals and originals[path] == digest and path.is_file(), "Unfrozen tool-original provenance")
                else:
                    path = helper.source_path(value)
                require(path not in hashes or hashes[path] == digest, "Contradictory frozen path hashes")
                if path not in hashes:
                    helper.checked_hash(path, digest)
                    hashes[path] = digest
            verify_references(value, hashes, originals)
    elif isinstance(node, list):
        for value in node:
            verify_references(value, hashes, originals)


def preflight():
    manifest = json.loads(helper.checked_hash(MANIFEST, MANIFEST_SHA256).decode("utf-8-sig"))
    require(manifest["schema"] == "frozen-scene-exploration-props-v1" and manifest["version"] == 1
            and manifest["frozen"] is True and manifest["runtime_verified"] is False, "Wrong frozen scene contract")
    require(set(manifest["props"]) == set(NAMES) and manifest["actual_unique_PNGs"] == 2
            and manifest["suggested_asset_names"] == NAMES and manifest["engine_destination_suggestion"] == PACKAGE, "Changed two-prop destination")
    hashes, originals, rows = {}, {}, []
    for item in manifest["props"].values():
        provenance = item["source_provenance"]
        require(provenance["tool_original_sha256"] == provenance["raw_sha256"], "Tool original and raw copy differ")
        originals[Path(provenance["tool_original_path"]).resolve()] = provenance["tool_original_sha256"]
    require(len(originals) == 2, "Expected two distinct native originals")
    verify_references(manifest, hashes, originals)
    for prop_id, name in NAMES.items():
        item = manifest["props"][prop_id]
        source = helper.source_path(item["path"])
        require(source.is_relative_to(ASSET_ROOT), "Import texture escapes this frozen prop topic")
        data = helper.checked_hash(source, item["sha256"])
        pixels = helper.inspect_rgba_png(data)
        for field in ("canvas_px", "mode", "alpha_extrema", "corner_alpha"):
            require(pixels[field] == item[field], "Actual native pixels differ: " + prop_id + "/" + field)
        require(pixels["bbox_px"] == item["actual_source_bbox_px"] and pixels["nonempty"]
                and pixels["corners_transparent"] and pixels["alpha_extrema"] == [0, 255], "Invalid native alpha/bbox")
        root, footprint, scale = item["root_px"], item["ground_footprint_px"], item["uniform_scale"]
        require(point(root) and item["actual_visible_front_contact_root_px"] == root, "Changed fixed-canvas root")
        sample = native_root_rgba(data, root)
        require(sample == item["root_sample_rgba"] and sample[3] >= 128, "Root is not the measured visible contact pixel")
        require(finite_number(scale) and scale > 0, "Expected one positive uniform scale")
        require(len(footprint) == 4 and all(point(p) for p in footprint) and len({tuple(p) for p in footprint}) == 4,
                "Footprint must be four distinct finite canvas points")
        crosses = []
        for i in range(4):
            a, b, c = footprint[i], footprint[(i + 1) % 4], footprint[(i + 2) % 4]
            crosses.append((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]))
        require(all(x > 0 for x in crosses) or all(x < 0 for x in crosses), "Degenerate or crossed inferred footprint")
        expected_canvas = [512 * scale, 512 * scale]
        expected_bbox = [(pixels["bbox_px"][2] - pixels["bbox_px"][0]) * scale,
                         (pixels["bbox_px"][3] - pixels["bbox_px"][1]) * scale]
        for actual, expected in ((item["display_canvas_logical_px"], expected_canvas),
                                 (item["display_actual_bbox_logical_px"], expected_bbox)):
            require(len(actual) == 2 and all(math.isclose(a, b, rel_tol=0, abs_tol=1e-9) for a, b in zip(actual, expected)),
                    "Display metadata must use the same single uniform scale")
        require(item["footprint_measurement"] == "inferred" and item["hidden_footprint_verified"] is False
                and item["runtime_verified"] is False and item["frozen"] is True, "Do not promote inferred geometry to verified")
        rows.append({"prop_id": prop_id, "texture_name": name, "source": str(source), "source_sha256": item["sha256"],
                     "source_bytes": len(data), "package_path": PACKAGE + "/" + name,
                     "object_path": PACKAGE + "/" + name + "." + name, "pixels": pixels,
                     "root_px": root, "actual_root_rgba": sample, "uniform_scale": scale,
                     "ground_footprint_px": footprint, "footprint_measurement": item["footprint_measurement"],
                     "world_ground_anchor_cm": item["world_ground_anchor_cm"], "status": item["status"],
                     "limitations": item["limitations"], "runtime_verified": False, "saved": False})
    require(len({r["source"] for r in rows}) == len({r["source_sha256"] for r in rows}) == 2, "Repeated prop pixels/source")
    wall = manifest["props"]["moss_low_wall"]
    require(wall["full_AABB_footprint_alignment_ready"] is False
            and wall["existing_world_aabb_cm"] == {"xmin": -1100, "xmax": -700, "ymin": 60, "ymax": 160}
            and wall["world_ground_anchor_cm"] == [-900, 60], "Changed existing wall/foundation boundary")
    require(manifest["props"]["old_city_stele"]["world_ground_anchor_cm"] == [-920, 300], "Changed investigation anchor")
    return manifest, rows, hashes


def import_in_unreal(manifest, rows, hashes):
    import unreal
    receipt = {"schema": "scene-exploration-props-import-receipt-v1", "utc": datetime.now(timezone.utc).isoformat(),
               "manifest": str(MANIFEST), "manifest_sha256": MANIFEST_SHA256, "destination": PACKAGE,
               "expected_count": 2, "actual_count": 0, "saved_count": 0, "success": False, "assets": rows,
               "verified_reference_count": len(hashes), "runtime_verified": False, "formal_scene_accepted": False,
               "collision_or_interaction_modified": False, "wall_full_AABB_alignment_verified": False,
               "scope": "Two native Texture2D prop candidates/settings only; inferred footprint and wall foundation composition need actual runtime review"}
    receipt_path = ROOT / "UnrealGame/Saved/Bootstrap" / ("scene-exploration-props-v001-import-"
                   + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".json")
    try:
        require(Path(unreal.Paths.project_dir()).resolve().parent == ROOT, "Wrong UE project")
        destination = ROOT / "UnrealGame/Content/Production/SceneExploration/v001"
        require_unused_disk_destination(destination)
        if unreal.EditorAssetLibrary.does_directory_exist(PACKAGE):
            require(not unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False), "Package is populated; refusing overwrite")
        tasks = []
        for row in rows:
            require(not unreal.EditorAssetLibrary.does_asset_exist(row["package_path"]), "Existing prop asset; refusing overwrite")
            task = unreal.AssetImportTask()
            for key, value in (("filename", row["source"]), ("destination_path", PACKAGE), ("destination_name", row["texture_name"]),
                               ("automated", True), ("save", False), ("replace_existing", False)):
                task.set_editor_property(key, value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        settings = {"compression_settings": unreal.TextureCompressionSettings.TC_EDITOR_ICON,
                    "mip_gen_settings": unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
                    "lod_group": unreal.TextureGroup.TEXTUREGROUP_UI, "never_stream": True, "srgb": True}
        for row, task in zip(rows, tasks):
            imported = list(task.get_editor_property("imported_object_paths"))
            require(imported == [row["object_path"]], "Wrong imported object paths")
            texture = unreal.load_asset(row["package_path"])
            require(isinstance(texture, unreal.Texture2D), "Expected native Texture2D")
            receipt["actual_count"] += 1
            for key, value in settings.items():
                texture.set_editor_property(key, value)
                require(texture.get_editor_property(key) == value, "Wrong actual texture setting: " + key)
            size = [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()]
            require(size == [512, 512], "UE changed fixed native canvas")
            row["imported_object_paths"] = imported
            row["ue_config"] = {key: value if isinstance(value, bool) else str(texture.get_editor_property(key)) for key, value in settings.items()}
            row["ue_config"]["size_px"] = size
        helper.checked_hash(MANIFEST, MANIFEST_SHA256)
        for path, digest in hashes.items():
            helper.checked_hash(path, digest)
        for row in rows:
            require(unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset(row["package_path"]), False), "Could not save new prop")
            row["saved"] = True
            receipt["saved_count"] += 1
        require(set(unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False)) == {r["object_path"] for r in rows}, "Unexpected package contents")
        receipt["success"] = receipt["actual_count"] == receipt["saved_count"] == 2
    except Exception as error:
        receipt["error"] = str(error)
        raise
    finally:
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        with receipt_path.open("x", encoding="utf-8") as output:
            json.dump(receipt, output, ensure_ascii=False, indent=2)
        unreal.log("Scene exploration prop import receipt: " + str(receipt_path))


if __name__ == "__main__":
    frozen, textures, references = preflight()
    if "--validate-only" in sys.argv:
        print(json.dumps({"source_validation_success": True, "native_textures": len(textures),
                          "verified_references": len(references), "manifest_sha256": MANIFEST_SHA256,
                          "destination": PACKAGE, "assets": textures, "unreal_import_run": False,
                          "runtime_verified": False, "wall_full_AABB_alignment_verified": False}, ensure_ascii=False))
    else:
        import_in_unreal(frozen, textures, references)
