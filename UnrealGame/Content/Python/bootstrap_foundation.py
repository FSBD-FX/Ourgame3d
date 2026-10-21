"""Build a preparation map and an empty Blueprint through the real UE Editor API.

No player combat, enemy behavior, or game progression is implemented here.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import unreal


def main():
    project = Path(unreal.Paths.project_dir()).resolve()
    report_path = project / "Saved" / "Bootstrap" / "foundation-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    map_path = "/Game/Maps/Foundation"
    blueprint_path = "/Game/Blueprints/Infrastructure/BP_WorkspaceMarker"
    for folder in ["Maps", "Blueprints/Infrastructure", "Art/Models", "Art/Textures", "Art/Materials", "Art/Animations", "Audio", "Tests/Fixtures"]:
        unreal.EditorAssetLibrary.make_directory("/Game/" + folder)

    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(map_path):
        unreal.EditorLoadingAndSavingUtils.load_map(map_path)
    else:
        unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
        cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
        material = unreal.load_asset("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")

        floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -25))
        floor.set_actor_label("Calibration Floor")
        floor.set_actor_scale3d(unreal.Vector(15, 15, 0.5))
        component = floor.get_component_by_class(unreal.StaticMeshComponent)
        component.set_static_mesh(cube)
        component.set_material(0, material)

        marker = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 50))
        marker.set_actor_label("Scale Marker (1 metre)")
        marker.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(cube)
        marker.get_component_by_class(unreal.StaticMeshComponent).set_material(0, material)

        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 500), unreal.Rotator(pitch=-45, yaw=25, roll=0))
        light.set_actor_label("Foundation Directional Light")
        light_component = light.get_component_by_class(unreal.DirectionalLightComponent)
        light_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        light_component.set_editor_property("intensity", 3.0)
        sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 300))
        sky.set_actor_label("Foundation Sky Light")
        sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
        sky_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        sky_component.set_editor_property("real_time_capture", True)
        actors.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0)).set_actor_label("Foundation Sky Atmosphere")

        camera = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(-800, 800, 650), unreal.Rotator(pitch=-30, yaw=-45, roll=0))
        camera.set_actor_label("Foundation Camera")
        camera_component = camera.get_component_by_class(unreal.CameraComponent)
        camera_component.set_editor_property("field_of_view", 55.0)
        camera.set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.PLAYER0)
        actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-400, 0, 150)).set_actor_label("Foundation Player Start")

        if not unreal.EditorAssetLibrary.does_asset_exist(blueprint_path):
            factory = unreal.BlueprintFactory()
            factory.set_editor_property("parent_class", unreal.Actor)
            unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_WorkspaceMarker", "/Game/Blueprints/Infrastructure", unreal.Blueprint, factory)
        unreal.EditorAssetLibrary.save_directory("/Game/Blueprints", only_if_is_dirty=False, recursive=True)
        if not unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), map_path):
            raise RuntimeError("Foundation map could not be saved.")

    all_actors = actors.get_all_level_actors()
    rotation_repairs = []
    for actor in all_actors:
        target_rotation = None
        if actor.get_actor_label() == "Foundation Camera":
            target_rotation = unreal.Rotator(pitch=-30, yaw=-45, roll=0)
        elif actor.get_actor_label() == "Foundation Directional Light":
            target_rotation = unreal.Rotator(pitch=-45, yaw=25, roll=0)
        if target_rotation is not None:
            previous = actor.get_actor_rotation()
            if any(abs(getattr(previous, field) - getattr(target_rotation, field)) > 0.01 for field in ("pitch", "yaw", "roll")):
                actor.set_actor_rotation(target_rotation, False)
                rotation_repairs.append(actor.get_actor_label())
    if rotation_repairs and not unreal.EditorLoadingAndSavingUtils.save_current_level():
        raise RuntimeError("Foundation rotation repair could not be saved")
    report = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": unreal.SystemLibrary.get_engine_version(),
        "project": str(project),
        "map": map_path,
        "map_exists": unreal.EditorAssetLibrary.does_asset_exist(map_path),
        "blueprint_exists": unreal.EditorAssetLibrary.does_asset_exist(blueprint_path),
        "rotation_repairs": rotation_repairs,
        "actors": [{"label": actor.get_actor_label(), "class": actor.get_class().get_name()} for actor in all_actors],
        "scope": "Preparation map and empty Blueprint only. Does not prove gameplay or Play In Editor."
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[CodexBootstrap] Foundation map and infrastructure Blueprint verified: " + str(report_path))


if __name__ == "__main__":
    main()
