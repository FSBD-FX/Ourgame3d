"""Headless read-only structure check; never save or render source assets."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
files=[
 ROOT/'kenney-mini-dungeon/extracted/Models/FBX format/character-human.fbx',
 ROOT/'kenney-mini-dungeon/extracted/Models/FBX format/character-orc.fbx',
 ROOT/'kenney-mini-dungeon/extracted/Models/FBX format/weapon-sword.fbx',
 ROOT/'kenney-modular-dungeon-kit/extracted/Models/FBX format/room-small.fbx',
 ROOT/'quaternius-universal-animation-library-2-standard/extracted/Universal Animation Library 2[Standard]/Female Mannequin/Mannequin_F.blend',
]
results=[]
for path in files:
    item={'path':str(path),'source_written':False,'render_performed':False}
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if path.suffix=='.blend':
            bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        else:
            bpy.ops.import_scene.fbx(filepath=str(path))
        objects=[]
        for obj in bpy.data.objects:
            record={'name':obj.name,'type':obj.type,'location':list(obj.location),'rotation_euler':list(obj.rotation_euler),'scale':list(obj.scale),'dimensions':list(obj.dimensions),'parent':obj.parent.name if obj.parent else None}
            if obj.type=='MESH':
                record['vertices']=len(obj.data.vertices)
                record['polygons']=len(obj.data.polygons)
                record['vertex_groups']=[g.name for g in obj.vertex_groups]
                record['materials']=[m.name if m else None for m in obj.data.materials]
                record['modifiers']=[{'type':m.type,'name':m.name} for m in obj.modifiers]
            if obj.type=='ARMATURE':
                record['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'use_deform':b.use_deform} for b in obj.data.bones]
            objects.append(record)
        item['objects']=objects
        item['actions']=[{'name':a.name,'frame_range':list(a.frame_range)} for a in bpy.data.actions]
        item['scene_fps']=bpy.context.scene.render.fps
        item['unit_settings']={'system':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length}
        item['status']='loaded_by_Blender_no_render_no_save'
    except Exception as e:
        item['status']='load_failed'
        item['error']=str(e)
    results.append(item)
(ROOT/'blender-structure-inspection.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'inspections':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('ASSET_INSPECTION_COMPLETE',[(r['path'],r['status']) for r in results])
