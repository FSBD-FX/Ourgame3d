"""Import only the frozen XBW two-hand ready-idle body; no attack approval."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("native_component_checks", Path(__file__).with_name("ue-import-armor-primary2-four-v001.py"))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
require = helper.require
MANIFEST = ROOT / "source-assets/production/first-batch-weapon-actions-v001/manifests/import-XBW-ready-idle-v001.json"
SHA = "21c8ff90c59c411bfdbcabcfee0292881d77e4e652cc2fde46cab35e99373813"
PACKAGE = "/Game/Production/FirstBatch/v016/XBWReadyIdle"
TRACKS = ("body_far", "body_support", "body_near")


def preflight():
    manifest = json.loads(helper.checked_hash(MANIFEST, SHA).decode("utf-8-sig"))
    require(manifest["frozen"] and manifest["weapon_id"] == "WPN-XBW-001"
            and manifest["clip_id"] == "xbw_ready_idle" and manifest["loop"], "Wrong frozen clip")
    require(manifest["frame_count"] == 6 and manifest["body_texture_count_new"] == 18
            and manifest["duration_s"] == .9 and manifest["damage_or_projectile_emission_events"] == [], "Changed idle contract")
    hashes, rows = {}, []
    helper.verify_paired_references(manifest, hashes)
    require([frame["index"] for frame in manifest["frames"]] == list(range(6)), "Changed frame order")
    for frame in manifest["frames"]:
        require(frame["ground_root_px"] == [256, 472] and frame["damage_or_projectile_emission_events"] == [], "Changed root or idle events")
        angle, scale = math.radians(frame["weapon_angle_image_clockwise_deg"]), frame["weapon_scale"]
        for landmark, expected in (("support", frame["transformed_support_px"]), ("emit", frame["transformed_emit_body_px"])):
            point = frame["component_" + landmark + "_px"] if landmark == "emit" else frame["component_support_grip_px"]
            dx, dy = [point[i] - frame["component_primary_grip_px"][i] for i in range(2)]
            actual = [frame["primary_grip_px"][0] + scale * (dx * math.cos(angle) - dy * math.sin(angle)),
                      frame["primary_grip_px"][1] + scale * (dx * math.sin(angle) + dy * math.cos(angle))]
            require(max(abs(actual[i] - expected[i]) for i in range(2)) < 1e-6, "Landmarks do not share actual weapon matrix")
        for track in TRACKS:
            item = frame[track]
            source = helper.source_path(item["path"])
            pixels = helper.inspect_rgba_png(helper.checked_hash(source, item["sha256"]))
            for key in ("canvas_px", "mode", "alpha_extrema", "bbox_px"):
                require(pixels[key] == item[key], "Actual native pixels differ: " + track)
            require(pixels["nonempty"] and pixels["corners_transparent"] and pixels["alpha_extrema"] == [0, 255], "Invalid native alpha")
            name = f"T_XBWReadyIdle_{track}_{frame['index']:03d}_v001"
            rows.append({"frame": frame["index"], "track": track, "source": str(source), "source_sha256": item["sha256"],
                         "name": name, "package_path": PACKAGE + "/" + name, "object_path": PACKAGE + "/" + name + "." + name})
    require(len(rows) == 18 and len({r["source"] for r in rows}) == 18, "Repeated/missing track paths")
    return rows, hashes


def import_in_unreal(rows, hashes):
    import unreal
    require(Path(unreal.Paths.project_dir()).resolve().parent == ROOT, "Wrong UE project")
    destination = ROOT / "UnrealGame/Content/Production/FirstBatch/v016/XBWReadyIdle"
    require(not destination.exists() or not any(p.is_file() for p in destination.rglob("*")), "Do not overwrite prior imports")
    if unreal.EditorAssetLibrary.does_directory_exist(PACKAGE):
        require(not unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False), "Package populated")
    receipt = {"schema": "xbw-ready-idle-import-v1", "manifest_sha256": SHA, "destination": PACKAGE,
               "expected_count": 18, "actual_count": 0, "saved_count": 0, "success": False,
               "assets": rows, "verified_reference_count": len(hashes), "runtime_verified": False,
               "attack_or_four_armor_accepted": False, "scope": "Native common-underclothes two-hand XBW ready-idle only; no authority muzzle or attack approval"}
    receipt_path = ROOT / "UnrealGame/Saved/Bootstrap" / ("xbw-ready-idle-v001-import-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".json")
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
        require(set(unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False)) == {r["object_path"] for r in rows}, "Wrong package contents")
        receipt["success"] = receipt["actual_count"] == receipt["saved_count"] == 18
    except Exception as error:
        receipt["error"] = str(error)
        raise
    finally:
        with receipt_path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
        unreal.log("XBW ready-idle receipt: " + str(receipt_path))


if __name__ == "__main__":
    rows, hashes = preflight()
    if "--validate-only" in sys.argv:
        print(json.dumps({"source_validation_success": True, "native_tracks": len(rows), "verified_references": len(hashes),
                          "manifest_sha256": SHA, "destination": PACKAGE, "unreal_import_run": False}))
    else:
        import_in_unreal(rows, hashes)
