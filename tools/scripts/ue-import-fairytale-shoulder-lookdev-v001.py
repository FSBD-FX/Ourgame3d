"""Root-owned actual eight Texture2D import; never changes source pixels."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("shoulder_lookdev_checks", Path(__file__).with_name("ue_fairytale_shoulder_lookdev_checks.py"))
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
document = checks.preflight()
if "--validate-only" in sys.argv:
    print(json.dumps({"source_preflight": True, "sources":8,"old_packages_unchanged":873,"manifest_sha":checks.MANIFEST_SHA}))
    raise SystemExit(0)

import unreal
checks.require(Path(unreal.Paths.project_dir()).resolve().parent == checks.ROOT, "Wrong UE project")
receipt = {"schema":"fairytale-shoulder-lookdev-eight-native-import-v1","utc":datetime.now(timezone.utc).isoformat(),
    "manifest":str(checks.MANIFEST),"manifest_sha256":checks.MANIFEST_SHA,"namespace":checks.NAMESPACE,
    "importer_sha256":checks.sha(__file__),"checks_sha256":checks.sha(checks.__file__),
    "actual_count":0,"saved_count":0,"expected_count":8,"assets":[],"success":False,
    "runtime_verified":False,"motion_accepted":False,"formal_complete_units":0,
    "scope":"147 eight-source isolated shoulder observation only; no complete armor/action acceptance"}
folder = checks.ROOT / "UnrealGame/Saved/Bootstrap"
receipt_path = folder / ("fairytale-shoulder-lookdev-v001-import-"+datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")+".json")
try:
    tasks=[]
    for row in document["assets"]:
        checks.require(not unreal.EditorAssetLibrary.does_asset_exist(row["package_path"]), "Existing object; no replacement")
        task=unreal.AssetImportTask()
        for key,value in (("filename",row["source"]),("destination_path",checks.NAMESPACE),("destination_name",row["name"]),("automated",True),("save",False),("replace_existing",False)):
            task.set_editor_property(key,value)
        tasks.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    settings={"compression_settings":unreal.TextureCompressionSettings.TC_EDITOR_ICON,"mip_gen_settings":unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
        "lod_group":unreal.TextureGroup.TEXTUREGROUP_UI,"never_stream":True,"srgb":True}
    for row,task in zip(document["assets"],tasks):
        paths=list(task.get_editor_property("imported_object_paths"))
        checks.require(paths==[row["object_path"]], "Unexpected import object paths")
        texture=unreal.load_asset(row["package_path"])
        checks.require(isinstance(texture,unreal.Texture2D), "Not actual Texture2D")
        checks.require([texture.blueprint_get_size_x(),texture.blueprint_get_size_y()]==[512,512], "Native canvas changed")
        for key,value in settings.items():
            texture.set_editor_property(key,value)
            checks.require(texture.get_editor_property(key)==value, "Native texture setting changed")
        receipt["actual_count"]+=1
    checks.preflight()
    for row in document["assets"]:
        texture=unreal.load_asset(row["package_path"])
        checks.require(unreal.EditorAssetLibrary.save_loaded_asset(texture,False), "New texture save failed")
        disk=checks.DISK/(row["name"]+".uasset")
        checks.require(disk.is_file() and disk.stat().st_size>0, "Saved package missing")
        receipt["assets"].append({**row,"actual_object_type":texture.get_class().get_name(),"saved_uasset":str(disk),"saved_bytes":disk.stat().st_size,"saved_sha256":checks.sha(disk)})
        receipt["saved_count"]+=1
    registered=list(unreal.EditorAssetLibrary.list_assets(checks.NAMESPACE,recursive=True,include_folder=False))
    expected=[row["object_path"] for row in document["assets"]]
    checks.require(len(registered)==8 and set(registered)==set(expected), "Actual registry set differs")
    checks.require({p.name for p in checks.DISK.iterdir() if p.is_file()}=={row["name"]+".uasset" for row in document["assets"]}, "Actual disk set differs")
    receipt.update(success=True,old_packages_unchanged=checks.old_packages_unchanged(),registry_exact_set_passed=True,disk_exact_set_passed=True)
except Exception as error:
    receipt["error"]=str(error)
    raise
finally:
    folder.mkdir(parents=True,exist_ok=True)
    with receipt_path.open("x",encoding="utf-8") as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2)
    unreal.log("Fairytale shoulder eight import receipt: "+str(receipt_path))
