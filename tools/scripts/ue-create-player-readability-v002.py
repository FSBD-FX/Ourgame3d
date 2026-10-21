"""Shader-only actual occlusion presentation; no sprite or combat mutation."""
from pathlib import Path
import json
import unreal as u

root=Path(u.Paths.project_dir()).resolve().parent
asset_path='/Game/Production/FirstBatch/v002/Presentation/M_PlayerOcclusionReadability_v002'
receipt=root/'UnrealGame/Saved/Bootstrap/player-readability-v002.json'
assert not u.EditorAssetLibrary.does_asset_exist(asset_path), 'Never overwrite a saved shader graph'
material=u.AssetToolsHelpers.get_asset_tools().create_asset(asset_path.rsplit('/',1)[1],asset_path.rsplit('/',1)[0],u.Material,u.MaterialFactoryNew())
assert material
material.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
material.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
material.set_editor_property('two_sided',True)
material.set_editor_property('disable_depth_test',True)
lib=u.MaterialEditingLibrary
nodes=[]
def node(cls,**props):
    n=lib.create_material_expression(material,cls,len(nodes)%8*220,len(nodes)//8*160)
    for key,value in props.items():n.set_editor_property(key,value)
    nodes.append(n);return n
def connect(source,pin,target,input_pin):
    assert lib.connect_material_expressions(source,pin,target,input_pin),(source.get_name(),pin,target.get_name(),input_pin,list(lib.get_material_expression_input_names(target)))
def binary(cls,a,ap,b,bp):
    n=node(cls);connect(a,ap,n,'A');connect(b,bp,n,'B');return n
def xy(n):
    out=node(u.MaterialExpressionComponentMask,r=True,g=True,b=False,a=False);connect(n,'',out,'');return out
def component(n,is_u):
    out=node(u.MaterialExpressionComponentMask,r=is_u,g=not is_u,b=False,a=False);connect(n,'',out,'');return out
def scalar(name,value):return node(u.MaterialExpressionScalarParameter,parameter_name=name,default_value=value)
def vector(name,x,y):return xy(node(u.MaterialExpressionVectorParameter,parameter_name=name,default_value=u.LinearColor(x,y,0,0)))
hero=u.load_asset('/Game/Production/FirstBatch/v006/CandidateSprites/Hero/T_hero_idle_000_v006')
stone=u.load_asset('/Game/Production/FirstBatch/v002/CandidateSprites/Stone/T_stone_idle_000_v002')
assert hero and stone
uv=node(u.MaterialExpressionTextureCoordinate)
width=scalar('OutlineWidth',1.4/160.)
mirrors={}
def sample(name,texture,coords):
    if name not in mirrors:mirrors[name]=scalar(name+'Mirror',0.)
    flip_scale=node(u.MaterialExpressionConstant2Vector,r=-1.,g=1.)
    flip_offset=node(u.MaterialExpressionConstant2Vector,r=1.,g=0.)
    flipped=binary(u.MaterialExpressionMultiply,coords,'',flip_scale,'')
    flipped=binary(u.MaterialExpressionAdd,flipped,'',flip_offset,'')
    mirrored=node(u.MaterialExpressionLinearInterpolate)
    connect(coords,'',mirrored,'A');connect(flipped,'',mirrored,'B');connect(mirrors[name],'',mirrored,'Alpha')
    n=node(u.MaterialExpressionTextureSampleParameter2D,parameter_name=name,texture=texture)
    connect(mirrored,'',n,'UVs');return n
center=sample('ActorSprite',hero,uv)
neighbors=[]
for x,y in ((1.,0.),(-1.,0.),(0.,1.),(0.,-1.)):
    delta=binary(u.MaterialExpressionMultiply,node(u.MaterialExpressionConstant2Vector,r=x,g=y),'',width,'')
    neighbors.append(sample('ActorSprite',hero,binary(u.MaterialExpressionAdd,uv,'',delta,'')))
expanded=binary(u.MaterialExpressionMax,neighbors[0],'A',neighbors[1],'A')
expanded=binary(u.MaterialExpressionMax,expanded,'',neighbors[2],'A')
expanded=binary(u.MaterialExpressionMax,expanded,'',neighbors[3],'A')
outer=binary(u.MaterialExpressionSubtract,expanded,'',center,'A')
edge=node(u.MaterialExpressionSaturate);connect(outer,'',edge,'')
ucoord=component(uv,True);vcoord=component(uv,False)
px=binary(u.MaterialExpressionMultiply,vector('OccluderUVAxisX',1,0),'',ucoord,'')
py=binary(u.MaterialExpressionMultiply,vector('OccluderUVAxisY',0,1),'',vcoord,'')
occluder_uv=binary(u.MaterialExpressionAdd,binary(u.MaterialExpressionAdd,px,'',py,''),'',vector('OccluderUVOffset',0,0),'')
zero=node(u.MaterialExpressionConstant,r=0.);one=node(u.MaterialExpressionConstant,r=1.)
def bound(value,upper):
    n=node(u.MaterialExpressionIf,equals_threshold=0.)
    connect(value,'',n,'A');connect(one if upper else zero,'',n,'B')
    connect(zero if upper else one,'',n,'A > B')
    connect(one,'',n,'A == B');connect(one if upper else zero,'',n,'A < B');return n
inside=one
for coord in (component(occluder_uv,True),component(occluder_uv,False)):
    for upper in (False,True):inside=binary(u.MaterialExpressionMultiply,inside,'',bound(coord,upper),'')
occluder=sample('OccluderSprite',stone,occluder_uv)
mask=binary(u.MaterialExpressionMultiply,occluder,'A',inside,'')
mask=binary(u.MaterialExpressionMultiply,mask,'',scalar('OccluderOpacity',1.),'')
edge_alpha=binary(u.MaterialExpressionMultiply,edge,'',scalar('OutlineOpacity',.8),'')
fill_alpha=binary(u.MaterialExpressionMultiply,center,'A',scalar('OccludedFillOpacity',.28),'')
alpha=binary(u.MaterialExpressionMultiply,binary(u.MaterialExpressionAdd,edge_alpha,'',fill_alpha,''),'',mask,'')
alpha=binary(u.MaterialExpressionMultiply,alpha,'',scalar('ActorOpacity',1.),'')
color=node(u.MaterialExpressionVectorParameter,parameter_name='OutlineColor',default_value=u.LinearColor(.55,.91,1.,1.))
tint=node(u.MaterialExpressionVectorParameter,parameter_name='ActorTint',default_value=u.LinearColor(1.,1.,1.,1.))
body_color=binary(u.MaterialExpressionMultiply,center,'RGB',tint,'')
mixed=node(u.MaterialExpressionLinearInterpolate);connect(body_color,'',mixed,'A');connect(color,'',mixed,'B');connect(edge,'',mixed,'Alpha')
assert lib.connect_material_property(mixed,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
assert lib.connect_material_property(alpha,'',u.MaterialProperty.MP_OPACITY)
lib.recompile_material(material)
assert u.EditorAssetLibrary.save_loaded_asset(material,only_if_is_dirty=False)
receipt.write_text(json.dumps(dict(asset=asset_path,graph_nodes=len(nodes),source_png_changes=0,scope='Actual already-drawn player body/weapon pixels only where later drawn enemy alpha overlaps; explicit UV bounds; affine rotated weapon mapping. No sorting/AI/collision/hit/time change.',runtime_visual_verified=False),ensure_ascii=False,indent=2),encoding='utf-8')
u.log('Saved readability candidate; actual runtime visual review pending.')
