from pathlib import Path
from PIL import Image
import numpy as np
import hashlib,json,shutil
R=Path('F:/Ourgame');P=R/'source-assets/production';B=P/'fairytale-sword-primary3-v001';O=P/'fairytale-sword-primary3-runtime-v001';T=O/'textures';assert not T.exists()
def desc(p):
    d=p.read_bytes();return {'path':p.as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
def write(p,d):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mf=B/'primary3-measurement-v001/primary3-measurement-candidate-v001.json';assert desc(mf)['sha256']=='474be5e1b1046ee59a28e0be3141f9785c56c8e94975665f0297264b44b045f9';m=json.loads(mf.read_text(encoding='utf-8'))
af=B/'armor-input-v001/component-measurement-v001/physical-feature-measurement-v001.json';assert desc(af)['sha256']=='5c8ca223a52ff578579f8bdbe2ce057953ba674196e9852ce8e5f8a7ae910546';am=json.loads(af.read_text(encoding='utf-8'))
partition=P/'fairytale-sword-primary3-body-partition-v001';pf=partition/'partition-freeze-v001.json';assert desc(pf)['sha256']=='b7393d7d1a8640e356be7f7e944ccae9e8f3dbe6ba06a06f16b20fd8858eba3e'
for pin in json.loads(pf.read_text(encoding='utf-8'))['files']:assert desc(Path(pin['path']))==pin
write(O/'root-partition-trial-review-v001.json',{'partition_freeze':desc(pf),'retention':'2026-10-16-OurgameUE-primary3-body-partition-v238','all24_layers_actually_viewed':True,'allowed':'Only bounded integer armor trial. Complete cuffs/helm/near sleeves present, farhand and major collar/belt/boots kept.','remaining':'Some helmet outer-AA slivers remain BodyRest; NearArm3/4 retains tiny waist ink/brown fragments; NearHand4 has a small pants-side gray edge. Numerical soleownership is exact, semantic edges/real sword grip/motion not accepted. Watch fist-helmet1, near/far hands2, low wrist3/4.','semantic_accepted':False,'formal_complete_units':0})
hidden={'Chest':{2:([263,270],8)},'NearShoulder':{},'FarShoulder':{2:([310,276],10),3:([320,282],10),4:([322,293],10)}}
write(O/'data/hidden-attachment-trial-design-v001.json',{'kind':'Root independent HIDDEN TRIAL DESIGN, not visible cloth, measured bones or physical generated A','hidden_trials':hidden,'immutable_measurement_modified':False,'formal_complete_units':0})
axes=[[.94,-.341],[-.7071,-.7071],[.866,.5],[.85,.526],[.98,-.2],[.94,-.341]]
markers=[]
for row,axis in zip(m['rows'],axes):
    assert desc(Path(row['source']['path']))==row['source']
    markers.append({'frame':row['frame'],'source':row['source'],'display_root':[256,464],'grip_candidate_px':row['near_palm_candidate']['point'],'grip_uncertainty_source_px':row['near_palm_candidate']['uncertainty_source_px'],'actual_handle_center':None,'actual_blade_axis':None,'directed_blade_axis_DESIGN':axis,'fist_polygon_candidate':row['near_glove_visible_polygon_candidate']['points'],'not_complete_AA_ownership':True})
marker=O/'data/primary3-marker-candidate-v001.json';write(marker,{'source_native':175,'measurement':desc(mf),'markers':markers,'durations_ms':[110,110,60,60,160,160],'axis_authority':'Root explicit trial design, not source measured axis/bone. One overhead-outside backswing to forward/down finisher, then guard return. Native clearance required.','independent_sword_grip':[99,256],'sword_scale':.5,'body_max_height':72,'full_motion_accepted':False,'formal_complete_units':0})
old=(R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPrimary2ArmorV001.inl').read_text(encoding='utf-8')
inline=old.replace('DungeonFairytaleSwordPrimary2ArmorV001','DungeonFairytaleSwordPrimary3V001').replace('DungeonFairytaleSwordPrimary2ArmorPreview','DungeonFairytaleSwordPrimary3ArmorPreview').replace('T_Fairytale_SwordPrimary2','T_Fairytale_SwordPrimary3').replace('/EV048/v010/HeroSwordPrimary2Armor/','/EV048/v011/HeroSwordPrimary3/')
inline=inline.replace('// UNAPPLIED trial: native171 exact body owners + integer-registered172/173/174.\n// Seven same512 quads plus independent Sword; source72px/root256,464 unchanged.\n// Marker/grip/axes MUST remain current DungeonFairytaleSwordPrimary2V003.\n// Actual grasp/axis/AA semantic ownership/clearance/motion are not accepted.', '// Native175 exact body owners + integer registered176/177/178 armor. Trial only.\n// Actual175 palms are candidates; directed blade axes are Root DESIGN, not measured.\n// KernelStage2 110/110/60/60/160/160ms; source72px/root256,464/Sword.50.\n// Grasp, clearance, semantic AA ownership and full motion remain unaccepted.')
inline=inline.replace('#include "Engine/Texture2D.h"','#include "Engine/Texture2D.h"\n#include "DungeonFairytaleSwordBodyV001.inl"')
inline=inline.replace('inline bool Enabled()','inline bool ArmorEnabled()')
pos=inline.index('inline UTexture2D* GetTexture')
extra='inline bool Enabled()\n{ return ArmorEnabled() || FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary3Preview")); }\nusing FMarker = DungeonFairytaleSwordBodyV001::FMarker;\ninline int32 Count(const FString& Clip) { return Clip==TEXT("sword_primary_3")?6:0; }\ninline const FMarker* Find(const FString& Clip,int32 Index)\n{\n    if(Clip!=TEXT("sword_primary_3") || Index<0 || Index>=6)return nullptr;\n    static const FMarker Markers[]={\n'
for r in markers:
    poly=', '.join(f'FVector2D({x}.,{y}.)' for x,y in r['fist_polygon_candidate']);x,y=r['grip_candidate_px'];ax,ay=r['directed_blade_axis_DESIGN']
    extra+=f'        FMarker{{FVector2D(256.,464.),FVector2D({x}.,{y}.),FVector2D({ax},{ay}),TArray<FVector2D>{{{poly}}}}},\n'
extra+='    };\n    return &Markers[Index];\n}\n'
inline=inline[:pos]+extra+inline[pos:];inline=inline.replace('for(const TCHAR* Name:{TEXT("BodyRest")','for(const TCHAR* Name:{TEXT("Body"),TEXT("BodyRest")')
inl=O/'data/DungeonFairytaleSwordPrimary3V001.inl';write(inl,inline)
stack=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand'];textures=[];registration=[];assemblies=[]
for i,body in enumerate(m['rows']):
    for c in ['Body','BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']:
        p=Path(body['source']['path']) if c=='Body' else partition/f'layers/{c}/frame-{i}.png';q=T/c/f'frame-{i}.png';q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();textures.append({'component':c,'frame':i,'source':desc(q),'exact_original_source':desc(p)})
    for c,targetc in [('Chest','Chest'),('NearShoulder','ShoulderNear'),('FarShoulder','ShoulderFar')]:
        feature=next(x for x in am['rows'] if x['component']==c and x['frame']==i);p=Path(feature['source']['path']);assert desc(p)==feature['source'];src=np.asarray(Image.open(p)).copy();sourceA=feature['physical_feature_A_candidate'];visible=body['body_design_A_candidates'][c]['point'];trial=None
        if visible is None:target,uncertainty=hidden[c][i];trial={'point':target,'uncertainty':uncertainty,'kind':'HIDDEN TRIAL DESIGN, not measured or visible cloth'}
        else:target=visible
        dx,dy=target[0]-sourceA[0],target[1]-sourceA[1];dst=np.zeros_like(src);sx0=max(0,-dx);sx1=min(512,512-dx);sy0=max(0,-dy);sy1=min(512,512-dy);dst[sy0+dy:sy1+dy,sx0+dx:sx1+dx]=src[sy0:sy1,sx0:sx1]
        back=np.zeros_like(src);back[sy0:sy1,sx0:sx1]=dst[sy0+dy:sy1+dy,sx0+dx:sx1+dx];assert np.array_equal(back,src),'Integer placement must not clip any RGBA including alpha0 nonzeroRGB'
        q=T/targetc/f'frame-{i}.png';q.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(dst).save(q);assert np.array_equal(np.asarray(Image.open(q)),dst)
        textures.append({'component':targetc,'frame':i,'source':desc(q)})
        registration.append({'component':c,'frame':i,'original_component':desc(p),'physical_feature_candidate_A':sourceA,'physical_feature_uncertainty':feature['uncertainty_source512_px'],'visible_cloth_DESIGN':visible,'hidden_TRIAL':trial,'target_design':target,'integer_offset':[dx,dy],'RGBA_reverse_exact':True,'accepted_fit':False})
    combined=Image.new('RGBA',(512,512),(0,0,0,0))
    for c in stack:combined=Image.alpha_composite(combined,Image.open(T/c/f'frame-{i}.png'))
    q=O/f'assemblies/frame-{i}-armor-no-sword.png';q.parent.mkdir(parents=True,exist_ok=True);combined.save(q);assemblies.append({'frame':i,'source':desc(q),'sword_present':False,'grip_or_helmet_fit_accepted':False})
candidate=O/'candidate-import-v001.json';write(candidate,{'schema':'fairytale-primary3-armor48-integer-candidate-v1','textures':textures,'texture_count':48,'frame_count':6,'durations_ms':[110,110,60,60,160,160],'source_canvas':[512,512],'native_facing':1,'display_canvas':72*512/416,'hero_visible_height_limit':72,'display_root':[256,464],'static_stack_without_sword':stack,'runtime_sword_between':['HelmetForeground','NearHand'],'marker':desc(marker),'marker_inl':desc(inl),'registration':registration,'assemblies':assemblies,'new_outputs_explicitly_viewed':False,'import_permitted':False,'visual_fit_or_motion_accepted':False,'formal_complete_units':0})
files=[p for folder in [O/'data',T,O/'assemblies'] for p in folder.rglob('*') if p.is_file()]+[candidate,O/'root-partition-trial-review-v001.json',Path(__file__).resolve()];freeze=O/'delivery-freeze-v001.json';write(freeze,{'files':[desc(p) for p in sorted(files)],'candidate':desc(candidate),'source_body_measurement':desc(mf),'component_measurement':desc(af),'body_partition_freeze':desc(pf),'new_outputs_viewed':False,'formal_complete_units':0})
print(json.dumps({'candidate':desc(candidate),'freeze':desc(freeze),'marker_inl':desc(inl),'textures':len(textures),'registration':len(registration)},ensure_ascii=False))
