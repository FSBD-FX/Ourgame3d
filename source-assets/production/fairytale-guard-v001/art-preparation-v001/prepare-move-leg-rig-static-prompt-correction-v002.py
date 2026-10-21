from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path('F:/Ourgame');HERE=ROOT/'source-assets/production/fairytale-guard-v001/art-preparation-v001'
OLD=HERE/'move-leg-rig-seven-components-generation-ready-v001'
OUT=HERE/'move-leg-rig-static-prompts-corrected-v002'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫Move七组件静态语义修正完整输入_v002'
assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
before_handoff=OLD/'Root-three-batch-generation-ready-handoff-v001.json'
prior=json.loads(before_handoff.read_text(encoding='utf-8'));groups=[]
replacements=[
 ('If this is a pre-idle/simple run, the attached base image may be used as the canonical character design. In direction-anchor mode, do not use base images for final action rows; accepted idle/direction anchors own row identity. ', 'This is a post-lock static component source run. The attached acceptedArmedReady209 is the ONLY identity; no oldbase is attached. '),
 ('If a state anchor is attached for a non-locomotion state, treat it as approved state vocabulary only. ', ''),
 ('If an additional generated row strip is attached, use it only as a motion reference, never as a replacement identity source. ', 'No motion row is attached or needed for static component source art. '),
 ('Do not redesign or reinterpret identity details while animating.', 'Do not redesign or reinterpret the visible identity while producing the specified static parts.'),
 ('- When generating a paired left/right row, use the paired row reference only for timing, scale, and animation intensity. Rotate the body, feet, shoulders, face angle, and gaze to the target facing, but keep identity details attached according to the accepted target-direction anchor.\n', '- Generate only the screen-right component perspective specified by acceptedReady209; no paired left-facing row or animation is requested.\n'),
 ('- For cyclic locomotion, do not let a single running/walking pose anchor determine every frame\'s leg phase. Use multi-pose motion references and the layout phase guide for foot contacts.\n', '- This strip contains static source component roles; no locomotion contacts or phase changes are requested here.\n'),
 ('- Prefer a subtler animation over any change that mutates the character identity.', '- Preserve identity and fixed static part construction; do not add animation to this kit.'),
 ('- Prefer pose, expression, and silhouette changes over decorative effects.', '- Produce only the specified static part silhouettes; no expression/pose variation or decorative effects.'),
 ('- Effects are allowed only when state-relevant, opaque, hard-edged, sprite-like, fully inside the same frame slot, and physically touching or overlapping the character silhouette.', '- No effects are requested for these static rig-source components.'),
 ('- Reject any pose that is cropped, overlaps another pose, crosses into a neighboring frame slot, or creates a separate disconnected component that is not attached to the character.', '- Reject cropped components, components crossing a neighboring slot, or unwanted loose fragments. The specified separate thigh/shin/shoe cells are intentionally independent static components and must NOT be attached to a character or to each other.'),
]
for g in prior['groups']:
 original=Path(g['prompt']['path']);text=original.read_text(encoding='utf-8');audit=[]
 for before,after in replacements:
  assert text.count(before)==1,(g['group'],before,text.count(before))
  text=text.replace(before,after);audit.append({'before':before,'after':after,'count':1})
 assert 'component that is not attached to the character' not in text and 'Effects are allowed' not in text and 'Prefer a subtler animation' not in text
 prompt=write(f"{g['group']}/native-fullprompt-static-components-v002.txt",text)
 a=write(f"{g['group']}/prompt-correction-audit-v002.json",{'before_prompt':pin(original),'after_prompt':pin(prompt),'text_only_replacements':audit,'standard_prepare_request_guides_extractor_SG_code_changed':False})
 oldh=Path(g['handoff']['path']);h=json.loads(oldh.read_text(encoding='utf-8'))
 h.update({'schema':'Guard-Move-isolated-static-component-input-PROMPT-CORRECTED-v002','prompt':pin(prompt),'v001_handoff_preserved':pin(oldh),'additional_v002_prompt_audit':pin(a),'new_guides_E_retained':False,'new_guides_viewed':False,'v001_generated_prompt_superseded_for_native_call':True,'standard_run_request_output_paths':'Unchanged originalpreparedv001 run; ONLY helper-native prompt is superseded. No rawnewsource generated yet. Originalfreeze/prompt remain preserved.','retention_gate':'Rootmustretainentirev002canonicalcontainingoriginal3standardruns+newcorrectedprompts beforeusingcalltimealready_retainedtrue refs.'})
 hand=write(f"{g['group']}/Root-native-generation-ready-v002.json",h)
 groups.append({'group':g['group'],'handoff':pin(hand),'prompt':pin(prompt),'refs_json':g['refs_json'],'output':g['output'],'roles':g['roles'],'standard_prepare_exit_code':g['prepare_exit_code']})
hand=write('Root-three-batch-generation-ready-handoff-v002.json',{'schema':'Guard-Move-LegRig-three-standard-static-component-batches-CORRECTED-v002','groups':groups,'component_and_pilot_contract':prior['component_and_pilot_contract'],'previous_v001_handoff':pin(before_handoff),'canonical_F_media':MEDIA.as_posix(),'identity':prior['identity'],'native_calls':0,'new_guides_viewed':False,'new_guides_E_retained':False,'TrialAllowed':False,'correction':'Preservedv001; SGgeneratedfullbody connected-character and animation/effects genericrules wereincompatiblewith3independentstaticparts. v002 removesallthosepromptconflicts only. Actualstandardprepare0/0/0, request/counts/guides/extractionpaths remainoriginal. No newfinalpixels orcode.','first_milestone':'7parts/18nullmarkers, actualsource/E/View then2oppositecontact true2Dfixedlength/IKpilot,128actualacceptedDistance. Frozenfull57 andoldwholebodycontracts/tests unchanged; noNativeSourceId orfootlockacceptance.'})
write('HANDOFF.md','''# 七组件三组输入：仅native静态语义修正v002\n\n使用本版总handoff及各组v002完整prompt。v001完整保留；标准prepare三个run、request、guides和output路径未变。复核发现通用“不连接角色的独立组件应拒绝”与Near/Far三件kit冲突，本版明确允许指定的独立thigh/shin/shoe源部件，并去掉通用动画/特效语句。Ready209仍为唯一身份。\n\ncanonicalF v002同时包含完整v001标准输入包和本版文本修正包，Root E两SHA保全后才View或调用AFTER-ROOT-E helper refs。尚未生成任何组件或rig；18标记/长度/尺度/接缝全null。第一里程碑、128真实移动、固定骨长与TrialAllowed=false等不变。\n''')
write('prompt-correction-freeze-v002.json',{'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'standard_v001_originals_preserved':True,'newguidesviewed':False,'nativecalls':0})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OLD,MEDIA/'原件/v001标准pipeline输入完整保留');shutil.copytree(OUT,MEDIA/'原件/v002静态语义修正');(MEDIA/'展示副本').mkdir()
for g in groups:
 run=Path(json.loads(Path(g['handoff']['path']).read_text(encoding='utf-8'))['run_dir'])
 for p in sorted((run/'references/layout-guides/right').glob('*.png')):shutil.copyfile(p,MEDIA/'展示副本'/f"{g['group']}-{p.name}")
index={'date':'2026-10-18','topic':'裂岩守卫Move七组件静态语义修正完整输入','version':'v002','status':'3standardinputspreserved+staticpromptcorrectiononly;newguidesunviewed/RootEandnativecallgated/Trialfalse','source':OUT.as_posix(),'handoff':pin(hand),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'handoff':pin(hand),'groups':groups,'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file())},ensure_ascii=False,indent=2))
