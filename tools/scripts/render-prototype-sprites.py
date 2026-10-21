"""Render project-owned prototype sprite frames from licensed CC0 Kenney FBX.

Run with Blender's --background --python, never through the live MCP scene.
"""
from __future__ import annotations

import argparse
import json
import math
import hashlib
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "source-assets/third-party/preparation-2026-10-10-v1/kenney-mini-dungeon/extracted"
FBX = PACK / "Models/FBX format"
OUTPUT = ROOT / "source-assets/prototype/first-room-v1"


def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def import_model(filename):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(FBX / filename), use_anim=True)
    return [obj for obj in bpy.data.objects if obj not in before]


def inspect():
    reset()
    objs = import_model("character-human.fbx")
    rig = next(obj for obj in objs if obj.type == "ARMATURE")
    action = next(action for action in bpy.data.actions if "|idle|" in action.name)
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    report = {
        "world_bounds": {obj.name: [list(obj.matrix_world @ Vector(corner)) for corner in obj.bound_box]
                         for obj in objs if obj.type == "MESH"},
        "pose_bones": [{"name": bone.name, "head": list(rig.matrix_world @ bone.head),
                        "tail": list(rig.matrix_world @ bone.tail)} for bone in rig.pose.bones],
        "objects": [{"name": obj.name, "type": obj.type,
                     "location": list(obj.location), "rotation": list(obj.rotation_euler),
                     "dimensions": list(obj.dimensions),
                     "parent": obj.parent.name if obj.parent else None,
                     "bones": [{"name": bone.name, "head": list(bone.head_local),
                                "tail": list(bone.tail_local)} for bone in obj.data.bones] if obj.type == "ARMATURE" else []}
                    for obj in objs],
        "actions": [{"name": action.name, "range": list(action.frame_range),
                     "slots": [slot.identifier for slot in action.slots]} for action in bpy.data.actions],
        "materials": [{"name": material.name, "nodes": [{"name": node.name,
                     "type": node.type, "image": node.image.filepath if node.type == "TEX_IMAGE" and node.image else None}
                    for node in material.node_tree.nodes] if material.use_nodes else []} for material in bpy.data.materials],
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "source-inspection.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def setup_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.image_settings.color_depth = "8"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studiolight_rotate_z = math.radians(25)
    scene.display.shading.color_type = "TEXTURE"
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.display.shading.curvature_ridge_factor = 1.4
    scene.display.shading.curvature_valley_factor = 1.1
    scene.display.shading.show_object_outline = True
    scene.display.shading.object_outline_color = (0.12, 0.10, 0.10)
    scene.display.render_aa = "16"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    camera_data = bpy.data.cameras.new("SpriteCamera")
    camera = bpy.data.objects.new("SpriteCamera", camera_data)
    scene.collection.objects.link(camera)
    direction = Vector((-6, -3.5, 2.5))
    camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 1.4
    camera_up = camera.rotation_euler.to_matrix() @ Vector((0, 1, 0))
    target = camera_up * (camera_data.ortho_scale * (220 / 256 - 0.5))
    camera.location = target + direction
    scene.camera = camera
    scene.world.color = (0.6, 0.6, 0.6)
    return scene


def action_for(name):
    return next(action for action in bpy.data.actions if f"|{name}|" in action.name)


def render_character(kind, preview=False):
    reset()
    objects = import_model(f"character-{kind}.fbx")
    rig = next(obj for obj in objects if obj.type == "ARMATURE")
    scene = setup_scene()
    clips = {
        "idle": ("idle", 8, 8, True),
        "walk": ("walk", 8, 12, True),
        "attack": ("attack-melee-right", 6, 15, False),
        "hurt": ("idle", 2, 10, False),
        "death": ("die", 8, 12, False),
    }
    report = {}
    for clip, (source, count, fps, loop) in clips.items():
        if preview and clip != "idle":
            continue
        action = action_for(source)
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        lo, hi = action.frame_range
        paths = []
        for index in range(1 if preview else count):
            fraction = index / (count if loop else max(1, count - 1))
            source_frame = lo + (hi - lo) * fraction
            scene.frame_set(int(source_frame), subframe=source_frame % 1)
            # No source hurt animation is supplied. The neutral pose is a visibly
            # small backward lean; runtime tint/knockback supplies hit feedback.
            rig.rotation_euler.y = math.radians(-9 if index == 0 else -5) if clip == "hurt" else 0
            bpy.context.view_layer.update()
            path = OUTPUT / "sprites" / kind / clip / f"{kind}_{clip}_{index:03d}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            paths.append(path.relative_to(OUTPUT).as_posix())
        report[clip] = {"frames": paths, "fps": fps, "loop": loop,
                        "source_action": source,
                        "fallback": "neutral pose with 9/5 degree lean; no original hurt take" if clip == "hurt" else None}
    pivot = world_to_camera_view(scene, scene.camera, Vector((0, 0, 0)))
    return {"clips": report, "ground_pivot_px": [round(pivot.x * 256, 4), round((1 - pivot.y) * 256, 4)]}


def render(preview=False):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    characters = {kind: render_character(kind, preview) for kind in ("human", "orc")}
    manifest = {
        "version": 1, "purpose": "free CC0 conversion for first-room gameplay prototype, not final art",
        "generator": "Blender 5.2.2 LTS offline workbench", "paid_generation_cost": 0,
        "size_px": [256, 256], "color": "RGBA", "facing": "right", "ground_pivot_px": [128, 220],
        "characters": characters,
        "source": {"pack": "Kenney Mini Dungeon", "license": "CC0 1.0",
                   "local_root": str(PACK), "url": "https://kenney.nl/assets/mini-dungeon"},
        "status": "preview" if preview else "rendered awaiting visual review",
    }
    (OUTPUT / ("preview-manifest.json" if preview else "manifest.json")).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SPRITE_RENDER_COMPLETE " + json.dumps({"characters": list(characters), "output": str(OUTPUT), "preview": preview}))


def render_items():
    report = {}
    for kind, filename in {"sword": "weapon-sword.fbx", "coin": "coin.fbx",
                           "potion": "potion.fbx", "chest": "chest.fbx", "shield": "shield-round.fbx"}.items():
        reset()
        objects = import_model(filename)
        scene = setup_scene()
        bpy.context.view_layer.update()
        corners = [obj.matrix_world @ Vector(corner) for obj in objects if obj.type == "MESH" for corner in obj.bound_box]
        center = sum(corners, Vector()) / len(corners)
        scene.camera.location = center + Vector((-6, -3.5, 2.5))
        scene.camera.data.ortho_scale = 1.0
        projected = [world_to_camera_view(scene, scene.camera, corner) for corner in corners]
        width = max(p.x for p in projected) - min(p.x for p in projected)
        height = max(p.y for p in projected) - min(p.y for p in projected)
        scene.camera.data.ortho_scale = max(width, height) * 1.18
        path = OUTPUT / "items" / f"{kind}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        report[kind] = {"file": path.relative_to(OUTPUT).as_posix(), "source": filename,
                        "size_px": [256, 256], "pivot_px": [128, 128], "purpose": "inventory icon"}
    manifest_path = OUTPUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["items"] = report
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ITEM_RENDER_COMPLETE " + json.dumps(report))


def write_index():
    manifest_path = OUTPUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_files = [FBX / f"character-{kind}.fbx" for kind in ("human", "orc")]
    source_files += [FBX / item["source"] for item in manifest.get("items", {}).values()]
    source_files += [FBX / "Textures/colormap.png", PACK / "License.txt", Path(__file__).resolve()]
    index = {"version": 1, "created_date": "2026-10-12", "paid_generation_cost": 0,
             "source_files": [{"file": str(path.relative_to(ROOT)),
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in source_files],
             "outputs": [{"file": str(path.relative_to(OUTPUT)), "bytes": path.stat().st_size,
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                         for folder in (OUTPUT / "sprites", OUTPUT / "items") for path in sorted(folder.rglob("*.png"))]}
    (OUTPUT / "source-index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SOURCE_INDEX_COMPLETE " + str(len(index["outputs"])))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--items", action="store_true")
    parser.add_argument("--index", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    if args.inspect:
        inspect()
    elif args.items:
        render_items()
        write_index()
    elif args.index:
        write_index()
    else:
        render(args.preview)
        if not args.preview:
            write_index()
