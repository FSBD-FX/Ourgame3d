"""Create a shader-only occluded-player outline; source sprites stay immutable."""
from pathlib import Path
import json
import unreal as u

root=Path(u.Paths.project_dir()).resolve().parent
asset_path='/Game/Production/FirstBatch/v001/Presentation/M_PlayerOcclusionOutline_v001'
receipt=root/'UnrealGame/Saved/Bootstrap/player-outline-v001.json'
assert not u.EditorAssetLibrary.does_asset_exist(asset_path), 'Use a new version; never overwrite a saved shader graph'
material=u.AssetToolsHelpers.get_asset_tools().create_asset(asset_path.rsplit('/',1)[1],asset_path.rsplit('/',1)[0],u.Material,u.MaterialFactoryNew())
assert material
material.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
material.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
material.set_editor_property('two_sided',True)
material.set_editor_property('disable_depth_test',True)
lib=u.MaterialEditingLibrary
nodes=[]
def node(cls,**props):
    n=lib.create_material_expression(material,cls,len(nodes)%7*220,len(nodes)//7*160)
    for key,value in props.items():n.set_editor_property(key,value)
    nodes.append(n);return n
def connect(source,pin,target,input_pin):
    assert lib.connect_material_expressions(source,pin,target,input_pin), (source.get_name(),pin,target.get_name(),input_pin,lib.get_material_expression_input_names(target))
def binary(cls,a,ap,b,bp):
    n=node(cls);connect(a,ap,n,'A');connect(b,bp,n,'B');return n
hero=u.load_asset('/Game/Production/FirstBatch/v002/CandidateSprites/Hero/T_hero_idle_000_v002')
stone=u.load_asset('/Game/Production/FirstBatch/v002/CandidateSprites/Stone/T_stone_idle_000_v002')
assert hero and stone
uv=node(u.MaterialExpressionTextureCoordinate)
width=node(u.MaterialExpressionScalarParameter,parameter_name='OutlineWidth',default_value=2./256.)
def sample(name,texture,coords):
    mirror=node(u.MaterialExpressionScalarParameter,parameter_name=name+'Mirror',default_value=0.)
    flip_scale=node(u.MaterialExpressionConstant2Vector,r=-1.,g=1.)
    flip_offset=node(u.MaterialExpressionConstant2Vector,r=1.,g=0.)
    flipped=binary(u.MaterialExpressionMultiply,coords,'',flip_scale,'')
    flipped=binary(u.MaterialExpressionAdd,flipped,'',flip_offset,'')
    mirrored=node(u.MaterialExpressionLinearInterpolate)
    connect(coords,'',mirrored,'A');connect(flipped,'',mirrored,'B');connect(mirror,'',mirrored,'Alpha')
    n=node(u.MaterialExpressionTextureSampleParameter2D,parameter_name=name,texture=texture)
    connect(mirrored,'',n,'UVs');return n
center=sample('ActorSprite',hero,uv)
neighbors=[]
for x,y in ((1.,0.),(-1.,0.),(0.,1.),(0.,-1.)):
    offset=node(u.MaterialExpressionConstant2Vector,r=x,g=y)
    delta=binary(u.MaterialExpressionMultiply,offset,'',width,'')
    displaced=binary(u.MaterialExpressionAdd,uv,'',delta,'')
    neighbors.append(sample('ActorSprite',hero,displaced))
expanded=binary(u.MaterialExpressionMax,neighbors[0],'A',neighbors[1],'A')
expanded=binary(u.MaterialExpressionMax,expanded,'',neighbors[2],'A')
expanded=binary(u.MaterialExpressionMax,expanded,'',neighbors[3],'A')
outer=binary(u.MaterialExpressionSubtract,expanded,'',center,'A')
saturated=node(u.MaterialExpressionSaturate);connect(outer,'',saturated,'')
ratio=node(u.MaterialExpressionScalarParameter,parameter_name='OccluderUVScale',default_value=1.)
offset=node(u.MaterialExpressionVectorParameter,parameter_name='OccluderUVOffset',default_value=u.LinearColor(0,0,0,0))
offset_xy=node(u.MaterialExpressionComponentMask,r=True,g=True,b=False,a=False);connect(offset,'',offset_xy,'')
occluder_uv=binary(u.MaterialExpressionMultiply,uv,'',ratio,'')
occluder_uv=binary(u.MaterialExpressionAdd,occluder_uv,'',offset_xy,'')
occluder=sample('OccluderSprite',stone,occluder_uv)
mask=binary(u.MaterialExpressionMultiply,saturated,'',occluder,'A')
opacity=node(u.MaterialExpressionScalarParameter,parameter_name='OutlineOpacity',default_value=.9)
final_alpha=binary(u.MaterialExpressionMultiply,mask,'',opacity,'')
color=node(u.MaterialExpressionVectorParameter,parameter_name='OutlineColor',default_value=u.LinearColor(1.,.76,.32,1.))
assert lib.connect_material_property(color,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
assert lib.connect_material_property(final_alpha,'',u.MaterialProperty.MP_OPACITY)
lib.recompile_material(material)
assert u.EditorAssetLibrary.save_loaded_asset(material,only_if_is_dirty=False)
receipt.write_text(json.dumps(dict(asset=asset_path,graph_nodes=len(nodes),source_png_changes=0,scope='Only an already-rendered player edge where a later depth-sorted real actor alpha overlaps. No actor resort, collision, damage, hidden entity revelation or source image edits.',runtime_visual_verified=False),ensure_ascii=False,indent=2),encoding='utf-8')
u.log('Saved player outline material; actual Canvas render remains to be reviewed.')
