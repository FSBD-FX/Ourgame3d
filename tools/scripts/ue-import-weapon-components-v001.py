"""Import four distinct native neutral weapon props, never substitute sword art.

--validate-only checks frozen inputs without UE. This importer does not approve
paired hands, motion, scale or actor muzzle placement. Existing SWD is reused.
"""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
helper_path = Path(__file__).with_name("ue-import-armor-primary2-four-v001.py")
spec = importlib.util.spec_from_file_location("native_component_validation", helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
require = helper.require
MANIFEST = ROOT / "source-assets/production/first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json"
MANIFEST_SHA256 = "275794953add2f130f0b7912fa9e01a16c21e4e017957af4c4d9c7793c240d68"
PACKAGE = "/Game/Production/FirstBatch/v015/WeaponComponents"
NEW_IDS = ("WPN-XBW-001", "WPN-STF-001", "WPN-SPR-001", "WPN-GSW-001")


def preflight():
    manifest = json.loads(helper.checked_hash(MANIFEST, MANIFEST_SHA256).decode("utf-8-sig"))
    require(manifest.get("frozen") is True and manifest.get("new_runtime_texture_count") == 4
            and manifest.get("reused_runtime_texture_count") == 1, "Changed component catalogue")
    require(set(manifest["weapons"]) == set(NEW_IDS) | {"WPN-SWD-001"}, "Unexpected weapon IDs")
    hashes, rows = {}, []
    helper.verify_paired_references(manifest, hashes)
    for weapon_id in NEW_IDS:
        item = manifest["weapons"][weapon_id]
        path = helper.source_path(item["path"])
        pixels = helper.inspect_rgba_png(helper.checked_hash(path, item["sha256"]))
        for key in ("canvas_px", "mode", "alpha_extrema", "bbox_px"):
            require(pixels[key] == item[key], f"Changed actual pixels {key}: {weapon_id}")
        require(pixels["nonempty"] and pixels["corners_transparent"]
                and pixels["alpha_extrema"] == [0, 255], "Invalid native prop alpha")
        require(item["canonical_forward_axis"] == [1, 0] and item["bbox_fit"] is False
                and item["translation_px"] == [0, 0] and item["crop"] is None, "Changed source geometry")
        require(len(item["primary_grip_px"]) == 2 and len(item["support_grip_px"]) == 2,
                "Missing measured physical grip/support")
        require(item["emit_px"] is not None if weapon_id in NEW_IDS[:2] else item["tip_px"] is not None,
                "Missing emitter/tip landmark")
        name = "T_" + weapon_id.replace("-", "_") + "_neutral_v001"
        rows.append({"weapon_id": weapon_id, "source": str(path), "source_sha256": item["sha256"],
                     "name": name, "object_path": PACKAGE + "/" + name + "." + name,
                     "package_path": PACKAGE + "/" + name, "pixels": pixels,
                     "primary_grip_px": item["primary_grip_px"], "support_grip_px": item["support_grip_px"],
                     "emit_px": item["emit_px"], "tip_px": item["tip_px"]})
    require(len({r["source_sha256"] for r in rows}) == 4, "Families must have distinct pixels")
    return manifest, rows, hashes


def import_in_unreal(manifest, rows, hashes):
    import unreal
    require(Path(unreal.Paths.project_dir()).resolve().parent == ROOT, "Wrong UE project")
    on_disk = ROOT / "UnrealGame/Content/Production/FirstBatch/v015/WeaponComponents"
    require(not on_disk.exists() or not any(p.is_file() for p in on_disk.rglob("*")), "Do not overwrite old props")
    if unreal.EditorAssetLibrary.does_directory_exist(PACKAGE):
        require(not unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False), "Package already populated")
    receipt = {"schema": "neutral-weapon-prop-import-v1", "manifest_sha256": MANIFEST_SHA256,
               "destination": PACKAGE, "expected_count": 4, "actual_count": 0, "saved_count": 0,
               "success": False, "assets": rows, "verified_reference_count": len(hashes),
               "runtime_verified": False, "weapon_actions_accepted": False,
               "scope": "Four distinct native neutral Texture2D props/settings only; no paired body/hand/muzzle/motion acceptance"}
    receipt_path = ROOT / "UnrealGame/Saved/Bootstrap" / ("weapon-components-v001-import-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".json")
    try:
        tasks = []
        for row in rows:
            require(not unreal.EditorAssetLibrary.does_asset_exist(row["package_path"]), "Existing component asset")
            task = unreal.AssetImportTask()
            for key, value in (("filename", row["source"]), ("destination_path", PACKAGE),
                               ("destination_name", row["name"]), ("automated", True), ("save", False), ("replace_existing", False)):
                task.set_editor_property(key, value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        for row, task in zip(rows, tasks):
            require(list(task.get_editor_property("imported_object_paths")) == [row["object_path"]], "Unexpected import output")
            texture = unreal.load_asset(row["package_path"])
            require(isinstance(texture, unreal.Texture2D), "Expected Texture2D")
            for key, value in (("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON),
                               ("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),
                               ("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI), ("never_stream", True), ("srgb", True)):
                texture.set_editor_property(key, value)
                require(texture.get_editor_property(key) == value, "Wrong actual texture setting")
            require([texture.blueprint_get_size_x(), texture.blueprint_get_size_y()] == [512, 512], "Native canvas changed")
            receipt["actual_count"] += 1
        helper.checked_hash(MANIFEST, MANIFEST_SHA256)
        for path, digest in hashes.items():
            helper.checked_hash(path, digest)
        for row in rows:
            require(unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset(row["package_path"]), False), "Could not save new prop")
            row["saved"] = True
            receipt["saved_count"] += 1
        require(set(unreal.EditorAssetLibrary.list_assets(PACKAGE, recursive=True, include_folder=False)) == {r["object_path"] for r in rows}, "Package path mismatch")
        receipt["success"] = receipt["actual_count"] == receipt["saved_count"] == 4
    except Exception as error:
        receipt["error"] = str(error)
        raise
    finally:
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        with receipt_path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
        unreal.log("Weapon component receipt: " + str(receipt_path))


if __name__ == "__main__":
    frozen, components, references = preflight()
    if "--validate-only" in sys.argv:
        print(json.dumps({"source_validation_success": True, "new_native_components": len(components),
                          "verified_references": len(references), "destination": PACKAGE,
                          "manifest_sha256": MANIFEST_SHA256, "unreal_import_run": False}))
    else:
        import_in_unreal(frozen, components, references)
