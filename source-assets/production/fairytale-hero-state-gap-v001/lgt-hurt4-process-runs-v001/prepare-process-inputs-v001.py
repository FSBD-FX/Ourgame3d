from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path('F:/Ourgame');BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001';HERE=Path(__file__).resolve().parent
INPUT=BASE/'lgt-hurt4-standard-input-v001/prepared-input-v001'
OUT=HERE/'process-inputs-v001';assert not OUT.exists();OUT.mkdir()
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
SOURCE_WRAPPER=ROOT/'source-assets/production/fairytale-lgt-readability-v003/primary1-leather-extraction-v001/shared-HD-fit-explicit-component-min-v001.py'
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
freeze=json.loads((INPUT/'standard-input-freeze-v001.json').read_text(encoding='utf-8'))
for f in freeze['files']:assert pin(Path(f['path']))==f
handoff=json.loads((INPUT/'Root-LGT-Hurt4-three-official-component-row-input-handoff-v001.json').read_text(encoding='utf-8'))
wrapper=OUT/'shared-HD-fit-explicit-component-min-UNCHANGED.py';shutil.copyfile(SOURCE_WRAPPER,wrapper);assert wrapper.read_bytes()==SOURCE_WRAPPER.read_bytes()
tools=[SG/'sprite_gen/frames/extract.py',SG/'scripts/compose_sprite_atlas.py',SG/'scripts/export_curated_pngs.py',SG/'scripts/preview_animation.py',SG/'scripts/inspect_sprite_run.py',SG/'sprite_gen/qa/inspect.py']
assert pin(tools[0])['sha256']=='f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539'
rows=[]
for row,token,native,rawfolder in zip(handoff['rows'],['chest','nearshoulder','farshoulder'],[228,229,230],['chest','near','far']):
 prepared=Path(row['run_dir']);run=OUT/'runs'/f'run-Hurt4-{token}-native{native}-shared-HD-v001'
 assert not run.exists();shutil.copytree(prepared,run)
 assert not any(p.is_file() for p in (run/'raw').rglob('*'))
 copies=[]
 for p in sorted(prepared.rglob('*')):
  if p.is_file():q=run/p.relative_to(prepared);assert p.read_bytes()==q.read_bytes();copies.append({'source':pin(p),'copy':pin(q)})
 state=row['state'];req=json.loads((run/'sprite-request.json').read_text(encoding='utf-8'));assert list(req['states'])==[state]
 assert req['states'][state]['frames']==4 and req['states'][state]['durations_ms']==[100]*4 and req['fit']['shared_row_scale'] and req['fit']['pixel_unfake'] is False
 assert [req['cell']['width']-2*req['cell']['safe_margin_x'],req['cell']['height']-2*req['cell']['safe_margin_y']]==row['fit_window_px']
 rawcanonical=BASE/f'lgt-hurt4-standard-input-v001/process-batches/2026-10-18-LGT-Hurt4-{rawfolder}-native{native}-v001/raw/{state}.png'
 commands=[{'stage':'extract-shared-whole-components','argv':[str(PY),'-B','-X','utf8',str(wrapper),'--run-dir',str(run),'--min-used-pixels',str(row['extraction_min_used_pixels_PROPOSAL'])]},
 {'stage':'compose-official','argv':[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run)]},
 {'stage':'curated-official','argv':[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state',state]},
 {'stage':'preview-official-QA','argv':[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)]},
 {'stage':'inspect-official','argv':[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run)]}]
 rows.append({'component':row['component'],'token':token,'native_request_planned':native,'state':state,'source_frozen_prepared_run':prepared.as_posix(),'independent_process_run':run.as_posix(),'raw_canonical_expected_from_Root':rawcanonical.as_posix(),'process_raw_copy_after_E_gate_only':(run/f'raw/{state}.png').as_posix(),'request':pin(run/'sprite-request.json'),'copied_inputs_all_byte_exact':copies,'commands_PLAN_NOT_EXECUTED':commands,'explicit_min_used_pixels':row['extraction_min_used_pixels_PROPOSAL'],'min_floor_role':'Carried E424 frozen physicalcomponent input proposal512/512/256, no effectrelabelling ornewlowering; actualQAfailurespreserved.','fit_window_px':row['fit_window_px'],'one_scale_per_row_not_perframe':True,'raw_received_or_read':False,'actual_shared_scale':None,'future_source_frames':None,'future_A':[None]*4,'future_B':[None]*4,'future_integer_delta':[None]*4,'future_coverage':[None]*4})
plan=write('three-independent-process-run-and-gated-command-plan-v001.json',{'schema':'Hurt227-LGT-three-independent-standard-process-inputs-v001','frozen_input_handoff':pin(INPUT/'Root-LGT-Hurt4-three-official-component-row-input-handoff-v001.json'),'frozen_input_manifest':pin(INPUT/'standard-input-freeze-v001.json'),'frozen_input_files_verified':len(freeze['files']),'source_inputs_E424':'RootexplicitallinputstwoSHAretainedandreviewed; onlybytecopiesofexistinginputimages,nounviewednewguidescreatedhere.','rows':rows,'shared_fit_wrapper':pin(wrapper),'wrapper_source':pin(SOURCE_WRAPPER),'wrapper_byte_unchanged':True,'official_tool_pins':[pin(p) for p in tools],'installed_SG_or_Roottools_modified':False,'raw_admission_gate':'EachrowneedsseparateexplicitRootrawF/Eretentionnotification+actualmatchingF/Epins beforecopy/read/extract. PlannedID/path isnotactualrawpin.','no_current_outputs':'Noextract/inspect/compose/curatedcommandsrunyet; raw/sourceframes/scale/A/B/coverageunknown. NoAI/native/UE/Source/Contentcalls.','next':'Runnewcandidateextractoronlyafterexplicitperrowadmission; allnewtransparentoutputsFcanonicalthenRootEbeforeView.'})
write('HANDOFF.md','''# LGT Hurt4：三个独立标准process run\n\n冻结prepared输入全部逐字节复核后，复制到本candidate下三个独立run，原prepared run未写raw。Root native raw canonical仍在各自process-batches，由Root逐行F/E保全通知后才复制进独立run。当前未读任何未来raw，未执行提取/compose/curated/inspect；数值scale/source/A/B/coverage全null。\n\n标准请求、guide、prompt、fit/chroma和100ms时序逐字节沿用E424输入。共享HD桥直接复制现有component-min版本，字节不变；只承接已明列512/512/物理小far256门，不改installedSG/Roottools或制造effect身份。组件无法分离/源裁缺/QA失败一律保留失败，不slot剪/绘补/按帧归一。\n\n每row实际rawE gate后使用计划五命令，并将新透明输出canonicalF另批待RootE再View。Hurt专属近臂/盔/近手遮挡须从227像素排他分割；无Ready mask复用，无LGT/native接受。\n''')
write('process-inputs-freeze-v001.json',{'schema':'LGT-Hurt4-independent-process-INPUTS-ONLY-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'future_raw_frames_outputs_not_frozen_yet':True,'script':pin(Path(__file__)),'raw_read':False,'pipeline_executed':False})
print(json.dumps({'plan':pin(plan),'prepared_runs':[r['independent_process_run'] for r in rows],'frozen_input_files_verified':len(freeze['files']),'request_guide_prompt_copies_exact':True,'raw_read':False,'pipeline_executed':False},ensure_ascii=False,indent=2))
