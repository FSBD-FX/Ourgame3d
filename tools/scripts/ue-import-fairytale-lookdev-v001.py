"""Root-owned actual8 Texture2D import, or ordinary Python --validate-only.

Candidate visual trial only. Never changes a pixel, old package or UE gameplay.
"""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("fairytale_lookdev_v001_checks", Path(__file__).with_name("ue_fairytale_lookdev_v001_checks.py"))
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
require = checks.require


def import_in_unreal(job):
    import unreal
    require(Path(unreal.Paths.project_dir()).resolve().parent == checks.ROOT, "Wrong UE project")
    rows = job["rows"]
    receipt = {"schema": "fairytale-lookdev-native-import-receipt-v1", "version": 1,
        "utc": datetime.now(timezone.utc).isoformat(), "manifest": str(checks.MANIFEST),
        "manifest_sha256": checks.MANIFEST_SHA256, "namespace": checks.NAMESPACE,
        "importer_sha256": checks.sha256(Path(__file__)), "checks_sha256": checks.sha256(Path(checks.__file__)),
        "expected_count": 8, "actual_count": 0, "saved_count": 0, "success": False,
        "assets": rows, "actors": job["manifest"]["actors"], "style": job["manifest"]["style"],
        "source_validation": job["summary"], "unreal_import_run": True,
        "runtime_verified": False, "motion_accepted": False, "full_character_accepted": False,
        "four_armor_accepted": False, "complete20equipment_combinations": False,
        "formal_complete_units": 0, "pixels_modified": False, "old_packages_modified": False,
        "scope": "Eight candidate native idle textures for independent EV047 visual trial; no final style, motion, full character/equipment/content acceptance"}
    folder = checks.ROOT / "UnrealGame/Saved/Bootstrap"
    receipt_path = folder / ("fairytale-lookdev-v001-import-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".json")
    try:
        checks.require_unused_destination(checks.DISK)
        registered = list(unreal.EditorAssetLibrary.list_assets(checks.NAMESPACE, recursive=True, include_folder=False)) if unreal.EditorAssetLibrary.does_directory_exist(checks.NAMESPACE) else []
        checks.require_exact_set(registered, [])
        tasks = []
        for row in rows:
            require(not unreal.EditorAssetLibrary.does_asset_exist(row["package_path"]), "Existing object; no replacement")
            task = unreal.AssetImportTask()
            for key, value in (("filename", row["source"]), ("destination_path", row["package_path"].rsplit("/", 1)[0]), ("destination_name", row["name"]), ("automated", True), ("save", False), ("replace_existing", False)):
                task.set_editor_property(key, value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        settings = {"compression_settings": unreal.TextureCompressionSettings.TC_EDITOR_ICON,
            "mip_gen_settings": unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
            "lod_group": unreal.TextureGroup.TEXTUREGROUP_UI, "never_stream": True, "srgb": True}
        for row, task in zip(rows, tasks):
            paths = list(task.get_editor_property("imported_object_paths"))
            require(paths == [row["object_path"]], "Unexpected actual import object path")
            require(Path(task.get_editor_property("filename")).resolve() == Path(row["source"]).resolve(), "Import filename changed")
            texture = unreal.load_asset(row["package_path"])
            require(isinstance(texture, unreal.Texture2D), "Expected actual Texture2D")
            for key, value in settings.items():
                texture.set_editor_property(key, value)
                require(texture.get_editor_property(key) == value, "Texture readback differs: " + key)
            size = [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()]
            require(size == [512, 512], "UE changed native canvas")
            row.update(actual_object_type=texture.get_class().get_name(), imported_object_paths=paths,
                actual_size_px=size, ue_config={k: v if isinstance(v, bool) else str(texture.get_editor_property(k)) for k, v in settings.items()}, saved=False)
            receipt["actual_count"] += 1
        for path, digest in job["hashes"].items():
            checks.checked_hash(path, digest)
        for row in rows:
            texture = unreal.load_asset(row["package_path"])
            require(unreal.EditorAssetLibrary.save_loaded_asset(texture, False), "New texture save failed")
            disk = checks.ROOT / "UnrealGame/Content" / row["package_path"].removeprefix("/Game/")
            disk = disk.with_suffix(".uasset")
            require(disk.is_file() and disk.stat().st_size > 0, "No actual saved package")
            require([texture.blueprint_get_size_x(), texture.blueprint_get_size_y()] == [512, 512], "Saved texture canvas changed")
            for key, value in settings.items():
                require(texture.get_editor_property(key) == value, "Saved texture setting changed")
            row.update(saved=True, saved_uasset=str(disk), saved_bytes=disk.stat().st_size, saved_sha256=checks.sha256(disk))
            receipt["saved_count"] += 1
        registered = list(unreal.EditorAssetLibrary.list_assets(checks.NAMESPACE, recursive=True, include_folder=False))
        checks.require_exact_set(registered, [r["object_path"] for r in rows])
        disk_actual = [str(p.resolve()) for p in checks.DISK.rglob("*") if p.is_file()]
        checks.require_exact_set(disk_actual, [str(Path(r["saved_uasset"]).resolve()) for r in rows])
        receipt.update(registered_object_paths=registered, registry_exact_set_passed=True, disk_exact_set_passed=True,
            success=receipt["actual_count"] == receipt["saved_count"] == 8)
    except Exception as error:
        receipt["error"] = str(error)
        raise
    finally:
        folder.mkdir(parents=True, exist_ok=True)
        with receipt_path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
        unreal.log("Fairytale candidate8 import receipt: " + str(receipt_path))


if __name__ == "__main__":
    if "--validate-hero-only" in sys.argv:
        print(json.dumps(checks.hero_preflight(), ensure_ascii=False))
    else:
        job = checks.preflight()
        if "--validate-only" in sys.argv:
            print(json.dumps(job["summary"], ensure_ascii=False))
        else:
            import_in_unreal(job)
