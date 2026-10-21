"""Record native/partition facts without promoting raw candidates to completion."""
from pathlib import Path
import datetime, hashlib, json, shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary1-v001';D=R/'docs/production/first-batch-v2'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=B/'body-partition-v001/partition-freeze-v001.json'; f=load(freeze)
assert desc(freeze)['sha256']=='ac1abca8cbb132e825a536bbc01719a8192854c912fb12e96cb2989c1398a7ee'
for x in f['files']:assert desc(Path(x['path']))==x
reviewed=[desc(B/f'body-partition-v001/layers/{owner}/frame-{i}.png') for owner in ['HelmetForeground','NearArmWithoutHand','NearHand','BodyRest'] for i in range(6)]
assert len(reviewed)==24
new(B/'root-body-partition-review-v001.json',{'freeze':desc(freeze),'actually_viewed':reviewed,'retention_before_views':'E175; 80files/2414249B/two size-SHA passes0diff',
 'facts':['All six original helmet/eyes/topknob remain in HelmetForeground; no collar cloth seen in that layer','NearArmWithoutHand contains gray sleeve only; NearHand includes whole brown cuff/glove as requested','BodyRest retains collar/torso/legs/far hand, with original visible near-arm/hand/head pixels assigned to other exclusive owners','185 exact reconstruction checks are numeric preservation only, not independent anatomy or motion acceptance'],
 'reasoning':'Four-source ownership is suitable for an initial explicit layer-stack fit trial. Original pixels are not used to reconstruct hidden anatomy.',
 'risks':['Shared ink bands at helmet/collar +-2px and sleeve/cuff/hand/body +-3px remain uncertainty','Phase1 back brim/fist; phase2 crossing gray arm and far wrist; phase3 cuff/belt need composite/runtime inspection','Not a claim of zero clipping, physical shoulder joints, footlock, all motion or real equipment IDs'],
 'semantic_candidate_for_fit_trial':True,'independent_review_pending':True,'runtime_accepted':False,'formal_complete_units':0})
l=load(R/'source-assets/production/first-unit-animation-v003/generation-ledger.json')
assert l['requested_count']==167 and l['remaining_batch_requests']==1
receipts=[load(B/f'generation-control-v001/generation-receipt{i}-v001.json') for i in range(164,168)]
for receipt in receipts:assert desc(Path(receipt['canonical_raw']['path']))==receipt['canonical_raw']
new(B/'root-native164-167-review-v001.json',{'native_receipts':[desc(B/f'generation-control-v001/generation-receipt{i}-v001.json') for i in range(164,168)],
 'actual_raws_viewed_after_retention':True,'source163_raw_also_viewed':True,
 'verdicts':[{'request':164,'component':'Chest','verdict':'Six connected broad plates, round central boss apparent in all; extraction completed by worker but derived frames not yet root-viewed; no fit acceptance'},
             {'request':165,'component':'NearShoulder','verdict':'Six connected shells with central washer and changed raised/crossed/down projections; extraction completed but derived frames not yet root-viewed; no fit acceptance'},
             {'request':166,'component':'FarShoulder','identity_passed':False,'verdict':'Adds large central front disk absent from original163; worker actual extract QA also RED; preserved failed candidate, do not import'},
             {'request':167,'component':'FarShoulder','verdict':'Correction preserves plain front face and actual top strap rivet across six poses; native candidate only, standard extraction pending'}],
 'view_precision':'2172x724 native raws displayed2048x683; no component coordinates measured from resized views','external_api_calls':0,'formal_complete_units':0})
back=D/'evidence/primary1-armor-v001/status-before-native167-v001';assert not back.exists();back.mkdir(parents=True)
for name in ['README.md','AGENTS.md','项目需求台账.md','docs/production/first-batch-v2/progress.json']:
 p=R/name;shutil.copy2(p,back/p.name);assert desc(p)['sha256']==desc(back/p.name)['sha256']
for name in ['README.md','AGENTS.md']:
 p=R/name;old=p.read_text(encoding='utf-8-sig')
 text='2026-10-16进行中：保持EV048怪诞钟盔、小比例72px和UI隐藏。首斩胸甲164、近肩165、远肩166/纠错167四次原生生成已保留；166新增正面圆盘且提取QA失败，保留失败版本。164/165已标准提取，167待提取，均未导入/未接受穿戴动作。原159身体24互斥像素层已冻结，185数值检查过，root看完24层，待组合与独立语义复核。当前实际Production仍941，最近可运行盔甲仅v101待机四帧；攻击仍卸甲。\n\n新存档Codec四组Stage0与诚实未实现stub已新增；122244首次编译因test-local变量遮蔽exit6，尚未实际语义RED。当前工作源码未编译验证，旧111349build0/111515完整126与v101实景是历史已核检查点。正式完整0/15，目标active。\n\n此前已核检查点（历史）：\n\n'
 p.write_text(text+old,encoding='utf-8')
p=D/'progress.json';d=load(p)
d.update(current_task='EV048 Primary1 armor native164/165/166failed/167corrected retained; exclusive24body layers exact/visually candidate; no new import. Codec Stage0 initial UBT122244 compilefailed6 due local shadow; no semanticRED yet. Fullgoalactive0/15.',
 ue_current_working_source_compiled=False,ue_current_working_source_verified=False,
 current_source_uncompiled_changes='New RunSnapshotCodec Stage0 h/cpp and four test registrations/oracle; initial compilation exit6, fix pending. Existing v101 DLL still last successful build.',
 latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261016-122244.log',latest_build_attempt_exit_code=6,
 next_native_request=168,next_snapshot='v102',next_retention_batch='E178',next_human_event='EV-049',
 production_texture_count_actual=917,production_texture_count_scope='Actual941Productionpackages=917T_+22SW_+2M_; no new Primary1 armor import',
 current_turn_progress_classification='Actual4native calls plus24exclusive source layers and failed-candidate diagnosis; no new human event, art/runtime/fullstates remain unfinished')
d['generation_accounting_current']={'requested_count':167,'window_number':7,'window_requested_count':23,'window_limit':24,'remaining_in_window':1,'lifetime_requested_count':191,'external_api_calls':0,'fee_unknown':True}
d['fairytale_sword_primary1_armor_preparation_v001']['status']='Original33-file draft remains frozen historical. Root reviewed v002 input explicitly defines hidden trial targets; native164-167 actually requested/generated/retained, not fit acceptance.'
d['fairytale_sword_primary1_armor_current_v001']={'requests':[164,165,166,167],'failed_request':166,'native_retention':['E169','E170','E171','E172','E173','E174','E176','E177'],'body_partition_retention':'E175','root_body_layers_viewed':24,'body_partition_source_exact':True,'new_Texture2Ds_imported':0,'equipment_or_motion_accepted':False,'formal_complete_units':0}
d['current_retention_batches']=[f'E{i}' for i in range(138,178)]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n| 2026-10-16；EV048继续执行，无新要求事件 | 强化盔甲与轮廓辨识 | 首斩胸片164/近肩165/远肩166及纠错167已生成F/E留档；166新增错误正面圆盘和提取QA失败保持记录。原159四类互斥身体像素24层185数值检查过，root24层审图，仅候选。 | 未新导入，Production941；首斩穿甲实景仍待，正式0/15。存档Codec新增Stage0首次编译局部变量遮蔽exit6，不冒测试RED/GREEN。 |\n')
print(json.dumps({'native_requested':167,'remaining_window':1,'body_layers_actually_viewed':24,'production_packages':941,'current_source_compiled':False,'formal_complete_units':0}))
