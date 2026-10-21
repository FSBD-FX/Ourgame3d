"""Read the original character FBX rest/animated transforms, without save/render."""
from pathlib import Path
import json
import math
import bpy

ROOT = Path(__file__).resolve().parent


def matrix_record(matrix):
    location, rotation, scale = matrix.decompose()
    return {'translation': list(location), 'quaternion_wxyz': list(rotation), 'scale': list(scale)}


def snapshot(armature):
    bpy.context.view_layer.update()
    dependency = bpy.context.evaluated_depsgraph_get()
    vertices = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            evaluated = obj.evaluated_get(dependency)
            mesh = evaluated.to_mesh()
            try:
                vertices.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
            finally:
                evaluated.to_mesh_clear()
    minimum = [min(vertex[axis] for vertex in vertices) for axis in range(3)]
    maximum = [max(vertex[axis] for vertex in vertices) for axis in range(3)]
    return {
        'evaluated_world_bounds_min': minimum,
        'evaluated_world_bounds_max': maximum,
        'evaluated_world_dimensions_xyz': [maximum[axis] - minimum[axis] for axis in range(3)],
        'armature_world_transform': matrix_record(armature.matrix_world),
        'bones': {bone.name: {'pose_armature_space': matrix_record(bone.matrix), 'pose_world_space': matrix_record(armature.matrix_world @ bone.matrix)} for bone in armature.pose.bones},
    }


results = []
for role in ('human', 'orc'):
    source = ROOT / ('kenney-mini-dungeon/extracted/Models/FBX format/character-' + role + '.fbx')
    item = {'source': str(source), 'source_written': False, 'render_performed': False, 'samples': []}
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(source))
        armature = next(obj for obj in bpy.data.objects if obj.type == 'ARMATURE')
        item['object_transforms'] = {obj.name: {'parent': obj.parent.name if obj.parent else None, 'local': matrix_record(obj.matrix_local), 'world': matrix_record(obj.matrix_world)} for obj in bpy.data.objects}
        item['scene_fps'] = bpy.context.scene.render.fps
        armature.data.pose_position = 'REST'
        item['reference_rest'] = snapshot(armature)
        armature.data.pose_position = 'POSE'
        armature.animation_data_create()
        for take in ('idle', 'attack-melee-right', 'attack-melee-left'):
            action = next(action for action in bpy.data.actions if ('|' + take + '|') in action.name)
            armature.animation_data.action = action
            if action.slots:
                armature.animation_data.action_slot = action.slots[0]
            start, end = action.frame_range
            for frame in (start, (start + end) / 2):
                bpy.context.scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
                item['samples'].append({'take': take, 'action': action.name, 'frame': frame, 'action_frame_range': [start, end], **snapshot(armature)})
        item['status'] = 'source_rest_and_animated_geometry_read_no_save_no_render'
    except Exception as exc:
        item['status'] = 'failed'
        item['error'] = str(exc)
    results.append(item)
report = {'blender_version': bpy.app.version_string, 'scene_coordinate_system': 'Blender evaluated world space; not UE actor/component space', 'inspections': results}
(ROOT / 'blender-source-axis-inspection.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('SOURCE_AXIS_INSPECTION', [(item['source'], item['status']) for item in results])
