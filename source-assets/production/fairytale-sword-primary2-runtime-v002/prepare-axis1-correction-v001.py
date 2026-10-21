"""Append the approved axis1 correction; preserve every initially frozen candidate file.
Only candidate data under this family is written. No image output/transform or Unreal.
"""
from pathlib import Path
from datetime import datetime
import copy, hashlib, importlib.util, json, math, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FINAL=HERE/'axis1-correction-v001'

def fact(p):
 p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def require(v,why):
 if not v:raise RuntimeError(why)
def verify(rows):
 for x in rows:require(fact(x['path'])==x,'Frozen file changed '+x['path'])

old_freeze=HERE/'ready-for-root-import-freeze-v002.json'
require(fact(old_freeze)['sha256']=='2ee7363d17bc07f7419e495dbc52fe6bd0705c72dd7d9dbeacaa9f72e3889a75','Original freeze changed')
old_rows=read(old_freeze)['files'];verify(old_rows)
require(not FINAL.exists(),'Do not overwrite final correction')
old_manifest=HERE/'manifests/import-sword-primary2-v002.json';old_marker=HERE/'data/primary2-marker-candidate-v002.json';old_inl=HERE/'data/DungeonFairytaleSwordPrimary2V003.inl'
m=read(old_marker);manifest=read(old_manifest)
old_axis=copy.deepcopy(m['markers'][1]['axis_design_only']);new_axis=[.85,.526]
require(old_axis==[.35,.937],'Original axis1 design differs')
def estimate(axis):
 angle=math.atan2(axis[1],axis[0]);point=[167+383*.50*math.cos(angle),333+383*.50*math.sin(angle)]
 return {'axis_design':axis,'angle_degrees':math.degrees(angle),'estimated_tip_source_px':point,'tip_minus_display_root_y_source_px':point[1]-464,'tip_minus_display_root_y_planned_screen_px':(point[1]-464)*72/416}
history={'schema':'native171-independent-sword-axis-design-history-v1','created_local':datetime.now().astimezone().isoformat(),'source_body_unchanged':True,'original_candidate_freeze':fact(old_freeze),'original_candidate_manifest':fact(old_manifest),'original_marker':fact(old_marker),'native_or_frozen_input_contracts_modified':False,'design_revisions':[{'revision':1,'status':'Initial Root explicit design, locally frozen before correction arrived; preserved, not imported/current','axes':[[.94,-.341],[.35,.937],[.8,.6],[.9,-.436],[.95,-.312],[.94,-.341]],'reason':'Original low-palm171 rising-fit design','phase1_estimate':estimate(old_axis)},{'revision':2,'status':'Root approved final candidate design, still untested','axes':[[.94,-.341],[.85,.526],[.8,.6],[.9,-.436],[.95,-.312],[.94,-.341]],'reason':'Palm1 actual visible candidate167,333; original near-vertical downward design estimated tip below display sole. Root replaced axis1 with shallower forward/down31.8deg; all other axes unchanged.','phase1_estimate':estimate(new_axis)}],'estimate_basis':{'actual_visible_palm_candidate':[167,333],'palm_uncertainty_px':3,'sword_source_grip':[99,256],'front_blade_length_source_px_approx':383,'independent_sword_scale':.50,'display_root':[256,464],'source_to_screen_planned':72/416,'method':'Use atan2 design orientation and prior approximate front blade length, not a new source-tip measurement or observed render. Axis values are preserved, not normalized in data.','existing_native_body_or_input_contracts_changed':False},'remaining_design_risks':['New p1 tip estimate around330,434 avoids former floor crossing in this approximation but may overlap legs/boots; actual runtime must judge.','Axis3(.9,-.436) is a shallower forward/up design intended to avoid helmet lower rim; no measured tip/head clearance asserted.','Actual hand grasp, thumb, full blade silhouette, motion and P1 boundary fit remain unaccepted.'],'unreal_called':False,'source_pixels_modified':False,'motion_accepted':False}
history_path=HERE/'axis-design-history-v001.json';write(history_path,history)
FINAL.mkdir()
m['markers'][1]['axis_design_only']=new_axis;m['markers'][1]['axis_angle_degrees_design']=math.degrees(math.atan2(new_axis[1],new_axis[0]))
m['axis_design_revision']=2;m['references']['axis_design_history']=fact(history_path)
m['supersedes_unpublished_design_marker']=fact(old_marker)
risks=['Phase1 revised shallower forward/down axis(.85,.526) reduces prior estimated floor crossing; it can still overlap leg/boot silhouettes. Tip estimates are design-only, no runtime clearance passed.','Phase3(.9,-.436) shallower forward/up axis is intended to avoid helmet lower rim, not proof of no helmet/hand overlap.','Phases0/5 differ from P1 source; continuous boundary fit unaccepted.','Near-hand polygon +/-4px is not exact AA ownership; current originalUV fist replay remains a bounded fit trial.']
m['design_risks']=risks
marker_path=FINAL/'data/primary2-marker-candidate-v002.json';write(marker_path,m)
text=old_inl.read_text(encoding='utf-8')
require(text.count('FVector2D(0.35, 0.937)')==1,'Unexpected old inline axis1 occurrences')
text=text.replace('FVector2D(0.35, 0.937)','FVector2D(0.85, 0.526)')
text=text.replace('// MarkerJSON SHA256: '+fact(old_marker)['sha256'],'// MarkerJSON SHA256: '+fact(marker_path)['sha256'])
text=text.replace('namespace DungeonFairytaleSwordPrimary2V003\n','// Axis design revision2: phase1(.85,.526), all other axes unchanged. No runtime clearance acceptance.\n// AxisHistory SHA256: '+fact(history_path)['sha256']+'\nnamespace DungeonFairytaleSwordPrimary2V003\n',1)
inl=FINAL/'data/DungeonFairytaleSwordPrimary2V003.inl';inl.parent.mkdir(parents=True,exist_ok=True)
with inl.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
manifest['marker_json']=fact(marker_path);manifest['marker_inl_candidate']=fact(inl);manifest['axis_design_revision']=2
manifest['references']['axis_design_history']=fact(history_path);manifest['supersedes_unpublished_design_manifest']=fact(old_manifest);manifest['design_risks']=risks
manifest_path=FINAL/'manifests/import-sword-primary2-v002.json';write(manifest_path,manifest)
# Every actual source, copied PNG and package is read again; no new image is written.
pre=read(HERE/'source-preflight-v002.json');decoder_path=Path(pre['native_decoder']['path']);require(fact(decoder_path)==pre['native_decoder'],'Native decoder changed')
spec=importlib.util.spec_from_file_location('native171_final_readonly_decoder',decoder_path);decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
checks=[]
for row in manifest['assets']:
 p=Path(row['source']);q=Path(row['canonical_curated']['path']);require(p.read_bytes()==q.read_bytes(),'PNG source/copy changed')
 require(fact(p)['sha256']==row['source_sha256'] and p.stat().st_size==row['source_bytes'],'Asset pin changed')
 pixels=decoder.inspect_rgba_png(p.read_bytes());require(pixels['canvas_px']==[512,512] and pixels['mode']=='RGBA' and pixels['alpha_extrema']==[0,255] and pixels['corners_transparent'],'NativePNG checks failed')
 require(pixels['bbox_px'][3]-pixels['bbox_px'][1]<=416,'Fixed height exceeded')
 checks.append({'frame':row['frame'],'canonical':fact(q),'copy':fact(p),'byte_equal':True,'native_decoder':pixels})
require(len({x['copy']['sha256'] for x in checks})==6,'Unique6 changed')
for i in range(6):
 original=read(old_marker)['markers'][i];revised=m['markers'][i]
 if i!=1:require(original==revised,'Other phase marker changed')
 else:
  for k in original:
   if k not in ['axis_design_only','axis_angle_degrees_design']:require(original[k]==revised[k],'Phase1 non-axis field changed '+k)
root=Path('F:/Ourgame');disk=root/'UnrealGame/Content/Production/ArtTrials/EV048/v009/HeroSwordPrimary2';require(not disk.exists() or not any(disk.rglob('*')),'Unused namespace changed')
old_inventory=read(HERE/'manifests/old-production989-before-import.json');actual=[]
for p in sorted((root/'UnrealGame/Content/Production').rglob('*')):
 if p.is_file():
  row=fact(p);row['path']=p.relative_to(root).as_posix();actual.append(row)
require(actual==old_inventory['files'],'Original989 disk packages changed')
verify(old_rows)
write(FINAL/'source-preflight-v002.json',{'schema':'native171-final-axis2-readonly-preflight-v2','created_local':datetime.now().astimezone().isoformat(),'manifest':fact(manifest_path),'native_decoder':fact(decoder_path),'actual_source_and_copy_checks':checks,'six_unique':True,'maximum_visible_height':max(x['native_decoder']['bbox_px'][3]-x['native_decoder']['bbox_px'][1] for x in checks),'initial_frozen_13_files_unchanged':True,'only_marker1_axis_changed':True,'other_five_markers_exact':True,'all_grips_polygons_source_references_exact':True,'actual_original989packages_unchanged':True,'candidate_disk_namespace_unused':True,'actual_UE_registry_unused':None,'Root_registry_preflight_required':True,'candidate_inl_compiled':False,'unreal_called':False,'imported':False,'new_media_created':False})
readme='''# 最终导入候选：native171 / axis revision2

当前入口是本目录`manifests/import-sword-primary2-v002.json`，inline为本目录`data/DungeonFairytaleSwordPrimary2V003.inl`。同family顶层初始轴包已冻结并原样保留，历史不是当前导入入口。六图复用顶层curated的exact171 PNG；没有新增、变换或改图。两包的assets、握点、polygon、名字及目标namespace完全相同。

Root唯一更正轴1为(.85,.526)，其余(.94,-.341)/(.8,.6)/(.9,-.436)/(.95,-.312)/(.94,-.341)不变。原(.35,.937)与更正依据见上层`axis-design-history-v001.json`。旧约383前刃×.50的设计估算把新tip置约330,434，避开旧约234,512的脚线下位置，但可能压腿/靴。相3浅向前上旨在避盔下沿，也必须实际运行核手、腿、盔；均未tip-clear或motion接受。没有修改native输入或旧ArcB。

256,464 / 最高72 / Canvas72*512/416 / SwordScale.50 / 剑源Grip99,256不变。171实际棕掌候选±3、近手polygon±4，非真实柄轴/拇指或AA owner；currentBody→Sword→同originalUV近拳回绘仍只是bounded trial。本段无甲，0/5与P1边界未连续验收；standard600ms!=kernel540ms保留。UE registry、实际import/save、预加载与真实动作观察须Root完成；本步没有UE/import/Source安装/新展示图或视频。
'''
with (FINAL/'README.md').open('x',encoding='utf-8',newline='\n') as f:f.write(readme)
entry=HERE/'final-candidate-ref-v001.json';write(entry,{'schema':'native171-primary2-final-candidate-entry-v1','current_axis_design_revision':2,'manifest':fact(manifest_path),'marker_json':fact(marker_path),'marker_inl':fact(inl),'axis_history':fact(history_path),'old_initial_manifest_status':'superseded design candidate preserved unchanged; do not import it','imported':False,'runtime_verified':False})
files=[fact(Path(row['path'])) for row in old_rows]+[fact(old_freeze),fact(history_path),fact(Path(__file__)),fact(entry)]+[fact(p) for p in sorted(FINAL.rglob('*')) if p.is_file()]
require(len({row['path'] for row in files})==len(files),'Duplicate freeze path')
freeze=FINAL/'ready-for-root-import-freeze-v002.json';write(freeze,{'schema':'fairytale-primary2-native171-final-axis2-candidate-freeze-v2','created_local':datetime.now().astimezone().isoformat(),'file_count':len(files),'total_bytes':sum(row['bytes'] for row in files),'files':files,'current_manifest':fact(manifest_path),'status':'ready-for-Root-import candidate, registry pending; not imported','old_axis_candidate_preserved':True,'new_media_created':False,'unreal_called':False,'armor_present':False,'full_motion_accepted':False,'formal_complete_units':0})
verify(files)
print(json.dumps({'final_freeze':fact(freeze),'final_manifest':fact(manifest_path),'final_marker_json':fact(marker_path),'final_inline':fact(inl),'axis_history':fact(history_path),'entry':fact(entry),'file_count_including_freeze':len(files)+1,'total_bytes_including_freeze':sum(x['bytes'] for x in files)+freeze.stat().st_size,'old13_preserved':True,'source6_exact':True,'packages989_unchanged':True,'imported':False},ensure_ascii=False,indent=2))