"""Import frozen XBW primary body tracks; actor events retain combat authority."""
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
MANIFEST = ROOT / "source-assets/production/first-batch-weapon-actions-v001/manifests/import-XBW-primary-v001.json"
SHA = "79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f"
PACKAGE = "/Game/Production/FirstBatch/v017/XBWPrimary"
TRACKS = ("body_far", "body_support", "body_near")


def verify_references(node, hashes):
    # Frozen provenance includes this exact design timing source outside production.
    # All image/component references still use the shared production-root guard.
    if isinstance(node, dict):
        for key, value in node.items():
            hash_key = "sha256" if key == "path" else key[:-5] + "_sha256" if key.endswith("_path") else key + "_sha256"
            if isinstance(value, str) and hash_key in node:
                path = Path(value).resolve()
                timing_path = (ROOT / "docs/design/equipment-v1/weapons.json").resolve()
                if path != timing_path:
                    path = helper.source_path(value)
                expected = node[hash_key]
                require(path not in hashes or hashes[path] == expected, "Contradictory frozen references")
                if path not in hashes:
                    helper.checked_hash(path, expected)
                    hashes[path] = expected
            verify_references(value, hashes)
    elif isinstance(node, list):
        for value in node:
            verify_references(value, hashes)


def preflight():
    manifest = json.loads(helper.checked_hash(MANIFEST, SHA).decode("utf-8-sig"))
    require(manifest["frozen"] and manifest["weapon_id"] == "WPN-XBW-001"
            and manifest["clip_id"] == "xbw_primary" and not manifest["loop"], "Wrong frozen clip")
    require(manifest["frame_count"] == 6 and manifest["body_texture_count_new"] == 18
            and manifest["duration_s"] == .68, "Changed primary contract")
    require(manifest["draw_order"] == ["body_far", "independent_XBW_weapon", "body_support", "body_near"], "Changed layer order")
    require(manifest["nominal_emission_events"] == [{"time_s": .16, "frame_index": 2,
            "kind": "single_primary_bolt", "emit_body_px": [423.5311940307165, 224.3741693502523],
            "authority": "actual_actor_kernel_event_only"}], "Changed emission authority")
    intervals = [(0., .08), (.08, .16), (.16, .18), (.18, .20), (.20, .44), (.44, .68)]
    grips = [[224, 316], [250, 260], [255, 267], [250, 267], [240, 300], [224, 316]]
    angles = [-5.065580597958718, -6.776388900189802, -9.601046219591353,
              -11.266152277695031, -6.765269983288224, -5.065580597958718]
    hashes, rows = {}, []
    verify_references(manifest, hashes)
    require([frame["index"] for frame in manifest["frames"]] == list(range(6)), "Changed frame order")
    for frame, timing, grip, expected_angle in zip(manifest["frames"], intervals, grips, angles):
        require(frame["ground_root_px"] == [256, 472] and frame["primary_grip_px"] == grip
                and frame["weapon_scale"] == .48 and frame["weapon_angle_image_clockwise_deg"] == expected_angle,
                "Changed fixed canvas or rigid pose")
        require((frame["time_start_s"], frame["time_end_s"]) == timing, "Changed phase interval")
        events = frame["damage_or_projectile_emission_events"]
        require(events == ([{"nominal_source_time_s": .16, "event": "single_primary_bolt",
                 "authority": "actor_kernel_only_not_image_or_HUD"}] if frame["index"] == 2 else []),
                "Visual frame must not add combat events")
        angle, scale = math.radians(frame["weapon_angle_image_clockwise_deg"]), frame["weapon_scale"]
        matrix = frame["component_to_body_affine_2x3"]
        for landmark, expected in (("support", frame["transformed_support_px"]), ("emit", frame["transformed_emit_body_px"])):
            point = frame["component_" + landmark + "_px"] if landmark == "emit" else frame["component_support_grip_px"]
            dx, dy = [point[i] - frame["component_primary_grip_px"][i] for i in range(2)]
            actual = [grip[0] + scale * (dx * math.cos(angle) - dy * math.sin(angle)),
                      grip[1] + scale * (dx * math.sin(angle) + dy * math.cos(angle))]
            affine = [matrix[0] * point[0] + matrix[1] * point[1] + matrix[2],
                      matrix[3] * point[0] + matrix[4] * point[1] + matrix[5]]
            require(max(abs(actual[i] - expected[i]) for i in range(2)) < 1e-6
                    and max(abs(actual[i] - affine[i]) for i in range(2)) < 1e-6,
                    "Grips and emit must share the same actual weapon matrix")
        for track in TRACKS:
            item = frame[track]
            source = helper.source_path(item["path"])
            pixels = helper.inspect_rgba_png(helper.checked_hash(source, item["sha256"]))
            for key in ("canvas_px", "mode", "alpha_extrema", "bbox_px"):
                require(pixels[key] == item[key], "Actual native pixels differ: " + track)
            require(pixels["nonempty"] and pixels["corners_transparent"] and pixels["alpha_extrema"] == [0, 255], "Invalid native alpha")
            name = f"T_XBWPrimary_{track}_{frame['index']:03d}_v001"
            rows.append({"frame": frame["index"], "track": track, "source": str(source), "source_sha256": item["sha256"],
                         "name": name, "package_path": PACKAGE + "/" + name, "object_path": PACKAGE + "/" + name + "." + name,
                         "time_start_s": timing[0], "time_end_s": timing[1], "primary_grip_px": grip,
                         "weapon_scale": scale, "weapon_angle_image_clockwise_deg": expected_angle,
                         "transformed_emit_body_px": frame["transformed_emit_body_px"]})
    require(len(rows) == 18 and len({r["source"] for r in rows}) == 18, "Repeated/missing track paths")
    return rows, hashes


def import_in_unreal(rows, hashes):
    import unreal
    require(Path(unreal.Paths.project_dir()).resolve().parent == ROOT, "Wrong UE project")
    destination = ROOT / "UnrealGame/Content/Production/FirstBatch/v017/XBWPrimary"
    require(not destination.exists() or not any(p.is_file() for p in destination.rglob("*")), "Do not overwrite prior imports")
    if unreal.EditorAssetLibrary.does_directory_exist(PACKAGE):
        require(not unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False), "Package populated")
    receipt = {"schema": "xbw-primary-import-v1", "manifest_sha256": SHA, "destination": PACKAGE,
               "expected_count": 18, "actual_count": 0, "saved_count": 0, "success": False,
               "assets": rows, "verified_reference_count": len(hashes), "runtime_verified": False,
               "attack_or_four_armor_accepted": False, "scope": "Native common-underclothes XBW primary body/rigid prop candidate; no string mechanics, actor muzzle or four-armor acceptance"}
    receipt_path = ROOT / "UnrealGame/Saved/Bootstrap" / ("xbw-primary-v001-import-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".json")
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
        unreal.log("XBW primary receipt: " + str(receipt_path))


if __name__ == "__main__":
    rows, hashes = preflight()
    if "--validate-only" in sys.argv:
        print(json.dumps({"source_validation_success": True, "native_tracks": len(rows), "verified_references": len(hashes),
                          "manifest_sha256": SHA, "destination": PACKAGE, "unreal_import_run": False}))
    else:
        import_in_unreal(rows, hashes)
