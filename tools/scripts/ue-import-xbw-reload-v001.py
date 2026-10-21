"""Import the frozen four-keypose XBW reload without changing any source pixel.

--validate-only uses ordinary Python. The actual UE import is root-owned.
"""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("xbw_primary_validation", Path(__file__).with_name("ue-import-xbw-primary-v001.py"))
primary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(primary)
helper, require = primary.helper, primary.require
MANIFEST = ROOT / "source-assets/production/first-batch-weapon-actions-v001/manifests/import-XBW-reload-four-keyposes-v001.json"
SHA = "9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8"
PACKAGE = "/Game/Production/FirstBatch/v018/XBWReload"
TRACKS = ("body_far", "body_support", "body_near", "weapon")


def preflight():
    manifest = json.loads(helper.checked_hash(MANIFEST, SHA).decode("utf-8-sig"))
    require(manifest["frozen"] and manifest["schema"] == "frozen-weapon-specific-reload-keyposes-v1"
            and manifest["weapon_id"] == "WPN-XBW-001" and manifest["clip_id"] == "xbw_reload_four_keyposes",
            "Wrong frozen reload")
    require(manifest["frame_count"] == 4 and manifest["body_texture_count_new"] == 12
            and manifest["weapon_texture_count_new"] == 4 and manifest["duration_s"] == 1.1
            and not manifest["loop"], "Changed keypose count/duration")
    require(manifest["draw_order"] == ["body_far", "independent_weapon_state", "body_support", "body_near"],
            "Changed draw order")
    require([f["index"] for f in manifest["frames"]] == list(range(4)), "Missing/reordered frame")
    hashes, rows = {}, []
    primary.verify_references(manifest, hashes)
    # Tool output paths are exact frozen provenance, never a general C: allowance.
    for source in manifest["source_provenance"]:
        canonical = helper.source_path(source["raw_path"])
        original = Path(source["tool_original_path"]).resolve()
        require(original.is_file(), "Missing original image-tool output")
        helper.checked_hash(original, source["raw_sha256"])
        require(original.read_bytes() == canonical.read_bytes(), "Tool original differs from preserved raw")
        hashes[original] = source["raw_sha256"]
    intervals = [(0., .2), (.2, .6), (.6, .85), (.85, 1.1)]
    angles = [-9.048593278634216, -5.633198636185468, -19.52939909323423, 1.967075854989118]
    body_support = [[321, 321], [321, 323], [321, 325], [321, 325]]
    component_support = [[344, 320], [344, 320], [344, 286], [344, 286]]
    for frame, timing, angle, support, component in zip(manifest["frames"], intervals, angles, body_support, component_support):
        require(frame["canvas_px"] == [512, 512] and frame["root_px"] == [256, 472]
                and frame["ground_root_px"] == [256, 472], "Fixed canvas/root changed")
        require((frame["time_start_s"], frame["time_end_s"]) == timing
                and frame["time_start_normalized"] == timing[0] / 1.1
                and frame["time_end_normalized"] == timing[1] / 1.1, "Changed normalized clock")
        require(frame["weapon_scale"] == .48 and frame["weapon_angle_image_clockwise_deg"] == angle
                and frame["body_support_contact_px"] == support and frame["component_support_grip_px"] == component,
                "Changed rigid support transform")
        require(not frame["ammo_commit_event_from_image"] and not frame["projectile_or_damage_events"],
                "Images must not commit ammo or emit attacks")
        matrix = frame["component_to_body_affine_2x3"]
        radians = math.radians(angle)
        require(len(matrix) == 2 and all(len(row) == 3 for row in matrix), "Invalid affine matrix")
        expected_linear = [[.48 * math.cos(radians), -.48 * math.sin(radians)],
                           [.48 * math.sin(radians), .48 * math.cos(radians)]]
        require(max(abs(matrix[y][x] - expected_linear[y][x]) for y in range(2) for x in range(2)) < 1.e-9,
                "Source weapon was stretched instead of rigid uniform transform")
        for point, expected in ((component, support), (frame["component_emit_px"], frame["transformed_emit_body_px"])):
            actual = [sum(matrix[y][x] * point[x] for x in range(2)) + matrix[y][2] for y in range(2)]
            require(max(abs(actual[i] - expected[i]) for i in range(2)) < 1.e-6, "Support/emit matrix differs")
        for track in TRACKS:
            item = frame[track]
            source = helper.source_path(item["path"])
            pixels = helper.inspect_rgba_png(helper.checked_hash(source, item["sha256"]))
            for key in ("canvas_px", "mode", "alpha_extrema", "bbox_px"):
                require(pixels[key] == item[key], "Actual pixel contract differs: " + track)
            require(pixels["nonempty"] and pixels["corners_transparent"] and pixels["alpha_extrema"] == [0, 255],
                    "Invalid native transparent layer")
            name = f"T_XBWReload_{track}_{frame['index']:03d}_v001"
            rows.append({"frame": frame["index"], "track": track, "source": str(source), "source_sha256": item["sha256"],
                         "name": name, "package_path": PACKAGE + "/" + name, "object_path": PACKAGE + "/" + name + "." + name,
                         "time_start_normalized": timing[0] / 1.1, "time_end_normalized": timing[1] / 1.1,
                         "support_body_px": support, "support_component_px": component,
                         "angle": angle, "uniform_scale": .48, "root_px": [256, 472]})
    require(len(rows) == 16 and len({r["source"] for r in rows}) == 16, "Repeated/missing native layer")
    return rows, hashes


def import_in_unreal(rows, hashes):
    import unreal
    require(Path(unreal.Paths.project_dir()).resolve().parent == ROOT, "Wrong UE project")
    destination = ROOT / "UnrealGame/Content/Production/FirstBatch/v018/XBWReload"
    require(not destination.exists() or not any(p.is_file() for p in destination.rglob("*")), "Do not overwrite prior imports")
    if unreal.EditorAssetLibrary.does_directory_exist(PACKAGE):
        require(not unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False), "Package populated")
    receipt = {"schema": "xbw-reload-import-v1", "manifest_sha256": SHA, "destination": PACKAGE,
               "expected_count": 16, "actual_count": 0, "saved_count": 0, "success": False,
               "assets": rows, "verified_reference_count": len(hashes), "runtime_verified": False,
               "full_reload_accepted": False, "scope": "Four native reload keyposes/body and rigid weapon states only; no ammo authority, interpolation, lifecycle or four-armor acceptance"}
    receipt_path = ROOT / "UnrealGame/Saved/Bootstrap" / ("xbw-reload-v001-import-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".json")
    try:
        tasks = []
        for row in rows:
            require(not unreal.EditorAssetLibrary.does_asset_exist(row["package_path"]), "Existing asset")
            task = unreal.AssetImportTask()
            for key, value in (("filename", row["source"]), ("destination_path", PACKAGE), ("destination_name", row["name"]),
                               ("automated", True), ("save", False), ("replace_existing", False)):
                task.set_editor_property(key, value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        for row, task in zip(rows, tasks):
            require(list(task.get_editor_property("imported_object_paths")) == [row["object_path"]], "Wrong import output")
            texture = unreal.load_asset(row["package_path"])
            require(isinstance(texture, unreal.Texture2D), "Expected Texture2D")
            for key, value in (("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON),
                               ("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),
                               ("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI), ("never_stream", True), ("srgb", True)):
                texture.set_editor_property(key, value)
                require(texture.get_editor_property(key) == value, "Wrong actual texture settings")
            require([texture.blueprint_get_size_x(), texture.blueprint_get_size_y()] == [512, 512], "Canvas changed")
            receipt["actual_count"] += 1
        helper.checked_hash(MANIFEST, SHA)
        for path, digest in hashes.items():
            helper.checked_hash(path, digest)
        for row in rows:
            require(unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset(row["package_path"]), False), "Could not save new asset")
            receipt["saved_count"] += 1
        require(set(unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False)) == {r["object_path"] for r in rows},
                "Wrong package contents")
        receipt["success"] = receipt["actual_count"] == receipt["saved_count"] == 16
    except Exception as error:
        receipt["error"] = str(error)
        raise
    finally:
        with receipt_path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
        unreal.log("XBW reload receipt: " + str(receipt_path))


if __name__ == "__main__":
    rows, hashes = preflight()
    if "--validate-only" in sys.argv:
        print(json.dumps({"source_validation_success": True, "native_tracks": len(rows), "verified_references": len(hashes),
                          "manifest_sha256": SHA, "destination": PACKAGE, "unreal_import_run": False}))
    else:
        import_in_unreal(rows, hashes)
