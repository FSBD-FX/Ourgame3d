"""Create an isolated, saved asset intake map, keeping Foundation unchanged."""
from datetime import datetime, timezone
from pathlib import Path
import json
import os

import unreal


MAP = "/Game/Tests/Preparation/AssetIntake"
MINI = "/Game/ThirdParty/Kenney/MiniDungeon"
DUNGEON = "/Game/ThirdParty/Kenney/ModularDungeon"
EDITOR = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()


def material(name, texture_path):
    path = "/Game/Tests/Preparation/Materials/" + name
    existing = unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    if existing:
        return existing
    result = ASSETS.create_asset(name, "/Game/Tests/Preparation/Materials", unreal.Material, unreal.MaterialFactoryNew())
    result.set_editor_property("two_sided", True)
    sample = unreal.MaterialEditingLibrary.create_material_expression(result, unreal.MaterialExpressionTextureSample, -400, 0)
    sample.set_editor_property("texture", unreal.load_asset(texture_path))
    unreal.MaterialEditingLibrary.connect_material_property(sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    roughness = unreal.MaterialEditingLibrary.create_material_expression(result, unreal.MaterialExpressionConstant, -400, 160)
    roughness.set_editor_property("r", 0.85)
    unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(result)
    unreal.EditorAssetLibrary.save_loaded_asset(result, only_if_is_dirty=False)
    return result


def main():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    else:
        unreal.EditorLoadingAndSavingUtils.load_map("/Game/Maps/Foundation")
        if not unreal.EditorLoadingAndSavingUtils.save_map(EDITOR.get_editor_world(), MAP):
            raise RuntimeError("Could not create isolated AssetIntake map")
        # SaveMap is Save As: explicitly load the new package before editing it.
        unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    for actor in ACTORS.get_all_level_actors():
        if actor.get_actor_label().startswith("Intake "):
            ACTORS.destroy_actor(actor)
        elif actor.get_actor_label() == "Scale Marker (1 metre)":
            actor.set_actor_location(unreal.Vector(320, -250, 50), False, False)
        elif actor.get_actor_label() == "Foundation Camera":
            location = unreal.Vector(-430, 430, 320)
            rotation = unreal.MathLibrary.find_look_at_rotation(location, unreal.Vector(0, 0, 40))
            actor.set_actor_location_and_rotation(location, rotation, False, False)
        elif actor.get_actor_label() == "Foundation Directional Light":
            actor.set_actor_rotation(unreal.Rotator(pitch=-45, yaw=25, roll=0), False)
    mini_material = material("M_MiniDungeonIntake", MINI + "/Textures/T_MiniColormap")
    dungeon_material = material("M_ModularDungeonIntake", DUNGEON + "/Textures/T_DungeonColormap")
    created = []

    def static(label, asset_path, x, y, chosen_material):
        mesh = unreal.load_asset(asset_path)
        if mesh is None:
            raise RuntimeError("Missing static mesh: " + asset_path)
        bounds = mesh.get_bounds()
        z = 2.0 - (bounds.origin.z - bounds.box_extent.z)
        actor = ACTORS.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
        actor.set_actor_label("Intake " + label)
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        component.set_static_mesh(mesh)
        for index in range(component.get_num_materials()):
            component.set_material(index, chosen_material)
        created.append({"label": actor.get_actor_label(), "mesh": mesh.get_path_name(), "material": chosen_material.get_path_name(), "scale": [1, 1, 1]})

    static("Dungeon Floor", DUNGEON + "/Floor/SM_Floor", 0, 0, dungeon_material)
    static("Sword", MINI + "/Sword/SM_Sword", -90, -120, mini_material)
    static("Coin", MINI + "/Coin/SM_Coin", -120, 0, mini_material)
    static("Chest", MINI + "/Chest/SM_Chest", -90, 110, mini_material)
    character_cases = [("Human", -75, False), ("Orc", 75, False)]
    if os.environ.get("CODEX_CHARACTER_AXIS_DIAGNOSTIC") == "1" and os.environ.get("CODEX_CHARACTER_AXIS_APPLY_CANONICAL") != "1":
        for kind in ("Human", "Orc"):
            fresh_path = "/Game/Tests/Preparation/AxisDiagnostic/" + kind + "Fresh/SK_" + kind + "Fresh"
            if unreal.EditorAssetLibrary.does_asset_exist(fresh_path):
                character_cases.append((kind, -75 if kind == "Human" else 75, True))
    for kind, y, fresh in character_cases:
        base = ("/Game/Tests/Preparation/AxisDiagnostic/" + kind + "Fresh/SK_" + kind + "Fresh") if fresh else (MINI + "/" + kind + "/SK_" + kind)
        mesh = unreal.load_asset(base)
        animation = unreal.load_asset(base + "_Anim_idle")
        if mesh is None or animation is None:
            raise RuntimeError("Missing skeletal mesh or idle animation: " + kind)
        bounds = mesh.get_bounds()
        z = 3.0 - (bounds.origin.z - bounds.box_extent.z)
        actor = ACTORS.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(130 if fresh else 20, y, z), unreal.Rotator(pitch=0, yaw=180, roll=0))
        actor.set_actor_label("Intake " + ("Fresh " if fresh else "") + kind)
        component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        component.set_skeletal_mesh_asset(mesh)
        for index in range(component.get_num_materials()):
            component.set_material(index, mini_material)
        component.override_animation_data(animation, True, True, 0.0, 1.0)
        component.set_editor_property("visibility_based_anim_tick_option", unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        created.append({"label": actor.get_actor_label(), "mesh": mesh.get_path_name(), "animation": animation.get_path_name(), "material": mini_material.get_path_name(), "scale": [1, 1, 1]})
    unreal.EditorAssetLibrary.save_loaded_asset(mini_material, only_if_is_dirty=False)
    unreal.EditorAssetLibrary.save_loaded_asset(dungeon_material, only_if_is_dirty=False)
    if not unreal.EditorLoadingAndSavingUtils.save_current_level():
        raise RuntimeError("Could not save AssetIntake map")
    report = {"utc": datetime.now(timezone.utc).isoformat(), "map": MAP, "foundation_preserved": "/Game/Maps/Foundation", "actors": created, "scope": "Source-scale static/skeletal assets and material/idle animation intake only. No gameplay."}
    path = Path(unreal.Paths.project_saved_dir()) / "Bootstrap" / "asset-validation-map-report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    unreal.log("[CodexAssetMap] Saved isolated validation map: " + str(path))


if __name__ == "__main__":
    main()
