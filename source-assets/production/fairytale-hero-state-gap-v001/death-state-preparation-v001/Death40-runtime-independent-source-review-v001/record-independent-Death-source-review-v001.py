"""Read-only source closure + analytical mirror check; no UE/build/native claims."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,math,difflib,sys
R=Path('F:/Ourgame');OUT=Path(__file__).resolve().parent;S=R/'UnrealGame/Source/CodexDungeon'
assert Path(sys.executable).resolve()==(R/'tools/runtime/asset-gen/Scripts/python.exe').resolve()
BASE=OUT.parent;PROD=BASE/'Death40-runtime-production-v001';FREEZE=PROD/'Death40-production-freeze-v001.json'
AUTHOR=BASE/'Death40-native-ready-author-candidate-v002/Death40-source-manifest-author-candidate-v002.json'
AP=BASE/'Death40-native-ready-author-candidate-v002/Death-runtime-profile-author-candidate-v002.json'
def pin(p):
 b=Path(p).read_bytes();return {'path':Path(p).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,v):
 p=OUT/name
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
fr=read(FREEZE);assert pin(FREEZE)['sha256']=='132a326e6b29cf39622de30de040cc3a1a6fadb84a2bb4be12accab0e2121a90'
newpins=[];existing=[]
for x in fr['new_source_files']:
 v=pin(x['path']);assert v==x,'Production9 changed after STOP: '+x['path'];newpins.append(v)
for x in fr['existing_modified_files']:
 v=pin(x['path']);allowed=Path(x['path']).name in ['DungeonHUD.h','DungeonHUD.cpp']
 if not allowed:assert v==x,'Production existing non-startup implementation changed'
 existing.append({'production_pin':x,'actual_current_pin':v,'matches_production_freeze':v==x,'Root_Probe_startup_merge_allowed':allowed})
m=read(AUTHOR);ap=read(AP);cpp=(S/'DungeonFairytaleSwordDeathProfile.cpp').read_text(encoding='utf-8-sig');by={(a['frame'],a['component']):a for a in m['assets']}
needsha=re.search(r'P.SourceClosureSHA256=TEXT\("([0-9a-f]{64})"\)',cpp)[1];assert needsha=='5f6506b609440d8cfda40b493b7ce9b23131b0f83aa09add333f8d8e74ef788c'
parts=re.split(r'auto& F=P.Frames\[(\d)\];',cpp)[1:];assert len(parts)==10;rows=[]
def vector(block,label):return [float(x) for x in re.search(r'F\.'+label+r'=\{([^}]+)\};',block)[1].split(',')]
for z in range(0,len(parts),2):
 i=int(parts[z]);block=parts[z+1];a=ap['frames'][i];root=vector(block,'Root');anchor=vector(block,'SwordAnchor');axis=vector(block,'AxisArtist')
 age=float(re.search(r'F.KeyAge=([0-9.]+);',block)[1]);released=re.search(r'F.VisualSwordReleased=(true|false);',block)[1]=='true'
 order=re.search(r'F.SlotOrder=\{([^}]+)\};',block)[1].replace('EComponent::','').split(',');expected_order=[q['component'] for q in a['slots_bottom_to_top']]
 assert root==a['root_source_author'] and anchor==a['weapon_anchor_source_author'] and axis==a['weapon_axis_artist'] and age==a['nominal_key_age_s'] and released==a['visual_weapon_released'] and order==expected_order
 layers=re.findall(r'F.Layers\[(\d)\]=\{EComponent::([A-Za-z]+),TEXT\("([^"]+)"\),TEXT\("([0-9a-f]{64})"\),TEXT\("([0-9a-f]{64})"\),(\d+)u,false\};',block);assert len(layers)==8
 for j,n,path,sha,rgba,used in layers:
  f=by[i,n];assert path==f['object_path'] and sha==f['source_sha256'] and rgba==f['source_RGBA_sha256'] and int(used)==f['source_alpha_nonzero_pixels'] and not f['known_optional_empty']
 # Independent vertex math: compare complete actor-reflected artist matrix to UV-reflected
 # DrawTexture's local coordinates/angle/pivot. This does not execute UE or certify pixels.
 theta=math.atan2(axis[1],axis[0]);k=72/416*1.25;ground=(640.,490.);height=17.*.70*1.25;maxerr=0.
 for side in [-1,1]:
  ac=(ground[0]+side*(anchor[0]-root[0])*k,ground[1]+(anchor[1]-root[1])*k-height);pivot=((512.-99.) if side<0 else 99.,256.);angle=theta*side;c=math.cos(angle);s=math.sin(angle)
  for q in [(0.,0.),(512.,0.),(512.,512.),(0.,512.),(99.,256.),(482.,256.)]:
   dx,dy=q[0]-99.,q[1]-256.;rx=math.cos(theta)*dx-math.sin(theta)*dy;ry=math.sin(theta)*dx+math.cos(theta)*dy
   expected=(ac[0]+side*.5*k*rx,ac[1]+.5*k*ry);local=((512.-q[0]) if side<0 else q[0],q[1]);x,y=(local[0]-pivot[0])*.5*k,(local[1]-pivot[1])*.5*k;actual=(ac[0]+c*x-s*y,ac[1]+s*x+c*y)
   maxerr=max(maxerr,math.hypot(actual[0]-expected[0],actual[1]-expected[1]))
  for q in [(0.,0.),(512.,512.),(242.,464.)]:
   top=(ground[0]-((512.-root[0]) if side<0 else root[0])*k,ground[1]-root[1]*k-height);local=((512.-q[0]) if side<0 else q[0],q[1]);actual=(top[0]+local[0]*k,top[1]+local[1]*k);expected=(ground[0]+side*(q[0]-root[0])*k,ground[1]+(q[1]-root[1])*k-height);maxerr=max(maxerr,math.hypot(actual[0]-expected[0],actual[1]-expected[1]))
 assert maxerr<1.e-10
 rows.append({'frame':i,'Root':root,'SwordAnchor':anchor,'AxisArtist':axis,'nominal_key_age':age,'visual_sword_released':released,'slot_order':order,'source8_all_path_SHA_RGBA_alpha_exact_to_author':True,'author_order_exact':True,'independent_right_left_analytical_max_error':maxerr})
closure=write('actual-Death-profile40-author-closure-and-mirror-analysis-v001.json',{'schema':'Death40-actual-source-constant-independent-review-v001','actual_profile_cpp':pin(S/'DungeonFairytaleSwordDeathProfile.cpp'),'author40_manifest':pin(AUTHOR),'author5_profile':pin(AP),'source_count':40,'all40_exact':True,'frames':rows,'analytical_geometry_only_not_UE_execution':True})
diffs=[]
for name in ['DungeonFighter.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonHUD.cpp']:
 before=PROD/'before-stage0'/name;after=PROD/'changed-source'/name
 text=''.join(difflib.unified_diff(before.read_text(encoding='utf-8-sig').splitlines(True),after.read_text(encoding='utf-8-sig').splitlines(True),fromfile='frozen-stage0/'+name,tofile='production/'+name))
 p=write(name+'.readonly-production.diff',text);diffs.append(pin(p))
baseline=read(R/'source-assets/production/backups/v137-range187G/compiled-source-manifest.json');old={x['path']:x for x in baseline['files']}
unchanged=[]
for name in ['DungeonGameMode.cpp','DungeonFairytaleSwordEquipmentBinding.cpp']:
 p=S/name;v=pin(p);x=old[p.relative_to(R).as_posix()];assert v['bytes']==x['bytes'] and v['sha256']==x['sha256'];unchanged.append(v)
evidence=[
 {'topic':'Death priority and supported failure closure','file':'DungeonFairytaleSwordPresentation.cpp','lines':[99,112],'fact':'Death reset/dispatch ahead of livingHurt; supportedLGT failure is consumed closed, unsupported continues same currentclockhelmet presenter, no legacyhuman route.'},
 {'topic':'Original terminal clock and pause','file':'DungeonFighter.cpp','lines':[1325,1334],'fact':'Read-only atomic Query from actual HP0/dead/death and finiteoriginalAnimationTime. No DiedAt, simulation clock, newtimer, mutation or reset.'},
 {'topic':'Existing terminal advance','file':'DungeonGameMode.cpp','lines':[1861,1894],'fact':'Existing Continue gate returns before terminal advance. GameOver ticks only existing AdvanceTerminalPresentation then returns before simulation; GameMode bytes unchanged fromv137.'},
 {'topic':'Dead committed equipment','file':'DungeonFairytaleSwordEquipmentBinding.cpp','lines':[63,157],'fact':'Unchanged authoritative Game.Player/World/itemversion/revision/instances/committed slots resolver. Inactive deadmelee can retain identity; no blanketalive/Continue rejection or newequipmentauthority.'},
 {'topic':'Terminal phase and last hold','file':'DungeonFairytaleSwordDeathPlan.cpp','lines':[59,84],'fact':'Source40 validated before selecting finiteoriginalage/.2. Age>=.8 clamps4 beforeinteger conversion; scale416→72/Sword.50 constant, whitebase, onetimewholeactor reflection + matchingUV/pivot/angle.'},
 {'topic':'Startup41 GPU initialization','file':'DungeonHUD.cpp','lines':[151,163],'fact':'Configured startup preloads40+Sword41 and passes all to editorFinishCompilation beforeexistingFlush267. Final startup2Probe merge belongsRoot and not countedimplementationdrift.'},
 {'topic':'Atomic cache and exact submissions','file':'DungeonFairytaleSwordDeathPresentation.cpp','lines':[48,104],'fact':'Cache-only all41 exactTexture2D/path/512/resource/notpending beforeanyquad; Canvas required. SamePlan floatargs/9orderedSlots/ActualRenderedStack afteractualDrawTexture, missingresources emitno partialdraw.'},
 {'topic':'White material','file':'DungeonFairytaleSwordDeathPlan.cpp','lines':[74,84],'fact':'WhiteTint independentof persistentHitFlash. ActualrendererusesP.Tint; releasedSword changesrenderorder/anchor only.'},
 {'topic':'Inventory/worldDrop immutability','file':'DungeonFighter.cpp','lines':[1325,1334],'fact':'ProductionFighterdiff only replaces read-onlyQuery stub. New runtimeplan/presentation contain no HP/Inventory/drop/clockmutation; originalGameMode andBinding bytesunchanged. VisualSwordReleased hasno gameequipment/drop sideeffect.'},
 {'topic':'Tests and limits','file':'Tests/DungeonFairytaleSwordDeathV001Tests.cpp','lines':[135,240],'fact':'Three originalRED tests byteSHA unchanged; actualfatal interruptedairprimary, fivephases/lastheld, committedbothfacing/sourceinvalid rejection, CodecPauseContinue/frozenowners. Tests exercise productionquery/plan, notactualCanvas/GPU; Rootnativeprobe remainsrequired.'}
]
rp=write('Death40-runtime-independent-source-review-v001.json',{'schema':'Death40-runtime-independent-source-review-v001','reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'production_freeze':pin(FREEZE),'actual_new9_pins_match_stopped_production_freeze':newpins,'existing5_comparison_with_explicit_startup_exception':existing,'unchanged_GameMode_and_Binding_from_v137':unchanged,'profile40_and_author_geometry_closure':pin(closure),'narrow_production_diffs':diffs,'blocking_findings':[],'nonblocking_findings':[],'verdict':'No blocking source defect identified in this scoped read-only review. This is not build/GREEN/actualGPU/nativevisual/final acceptance.','review_evidence':evidence,'limits':['Root Probe2 and startup branch are separatelyadopted; no wholeSource stability/count audit attempted.','Actual41 residency/submission/whitepixel/once-mirror native proof and sourcepose release quality stillrequire running review.','Author roots/anchors/axes remain author proposals; no physical grip/bone/floor certification.'],'Source_Content_tools_ledger_modified':False,'UE_or_UBT_started':False,'new_media_generated_or_Viewed':False,'actual_190GREEN_claimed':False,'actual_native_acceptance_claimed':False,'FinalAccepted':False})
write('REVIEW.md','只读审查未发现阻断实现问题。死亡在Hurt/Ready前；实际terminal AnimationTime通过原GameOver展示路径推进，Continue关闭时不消耗；死后committed SWD/LGT绑定有效且不增权限；40+剑41启动编译/Flush并在提交前cache-only整组核；九槽来自同一plan，持剑/释放顺序和一次镜像与E505作者合同闭合；白材质不依赖冻结HitFlash；没有新库存、真实掉落、HP或游戏时钟修改。\n\n独立逐项核40个路径/SHA/RGBA/非空计数以及五相Root/Anchor/Axis/顺序，全部等于author冻结；右/左完整矩阵与UV/pivot/旋转解析式一致。原三个RED测试字节未改。Root正在加Probe和HUD启动窄分支，因此本审查不核全Source稳定性或宣称计数漂移。\n\n结论仅源码范围；未运行UBT/UE、未宣称190GREEN/GPU驻留/原生画面通过。仍需Root实际双向Death五相、白色终帧、渲染资源与落剑作者位置审录。\n')
fp=write('independent-source-review-freeze-v001.json',{'schema':'Death40-independent-source-review-freeze-v001','script':pin(Path(__file__)),'files':[pin(p) for p in sorted(OUT.glob('*')) if p.is_file() and p.name!=Path(__file__).name],'read_only_Source_review':True,'no_GPU_native_or_final_acceptance':True})
print(json.dumps({'review':pin(rp),'freeze':pin(fp),'source40_closure':pin(closure),'blocking_findings':0,'nonblocking_findings':0,'UE_started':False,'actualSource_total_count_not_audited':True},ensure_ascii=False,indent=2))
