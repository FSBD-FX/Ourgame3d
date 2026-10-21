from pathlib import Path
import datetime,hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
P=D/'progress.json';DOC=D/'runtime-review-sword-primary3-fit-v001.md'
C=D/'evidence/primary3-native-fit-status-v001/checkpoint.json'
O=C.parent/'authority-amendment-v001';assert not O.exists();O.mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def desc(p):
    b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
for p in [P,DOC,C]:shutil.copy2(p,O/('before-'+p.name))
t=DOC.read_text(encoding='utf-8');assert t.count('实际Production纹理1085')==1
DOC.write_text(t.replace('实际Production纹理1085','实际Production包1085'),encoding='utf-8')
m=read(P);assert m['latest_visual_runtime_proof']['observations']==174
m['previous_visual_runtime_proof_before_primary3']=m['latest_visual_runtime_proof']
A=R/'过程图稿与视频/2026-10-16_钟盔军剑三段真实连击试装_v001'
m['latest_visual_runtime_proof']=dict(report=desc(DOC),archive=A.as_posix(),capture_snapshot=m['current_compiled_snapshot'],video=desc(A/'展示副本/fairytale-sword-primary3-fit-silent.mp4'),observations=198,original_PNG_including_prewarm=199,duration_s=6.601578898727894,uniform_weapon_scale=.5,body_max_px=72,root_whole_views=4,root_unscaled_crop_views=26,independent_whole_views=2,independent_unscaled_crop_views=20,independent_review_freeze=desc(D/'evidence/sword-primary3-native-review-v001/review-freeze-v001.json'),audio_recorded=False,full_motion_accepted=False,art_review_status='NEEDS_WORK',formal_complete_units=0)
m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(P,m)
c=read(C);c['after']=[desc(Path(x['path'])) for x in c['after']]
c['authority_amendment']='authority-amendment-v001/receipt.json';write(C,c)
assert all(desc(Path(x['path']))==x for x in c['after'])
write(O/'receipt.json',dict(reason='Independent read-only audit found stale v105 latest_visual_runtime_proof authority field and package-vs-texture wording.',after=[desc(p) for p in [P,DOC,C]],prior_visual_proof_preserved=True,source_changed=False,UE_or_tests_rerun=False,formal_complete_units=0,goal_status='active'))
print(json.dumps(dict(authority_snapshot='v116',observations=198,original_PNGs=199,production_count_kind='packages',all_six_checkpoint_after_files_match=True,Source_changed=False),ensure_ascii=False))
