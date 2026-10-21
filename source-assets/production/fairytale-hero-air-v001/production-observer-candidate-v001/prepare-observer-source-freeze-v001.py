from pathlib import Path
import datetime as dt
import difflib,hashlib,json

ROOT=Path('F:/Ourgame')
OUT=Path(__file__).resolve().parent


def pin(p):
    p=Path(p);b=p.read_bytes()
    return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(rel,value):
    p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:
        f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return p


native=OUT.parent/'native-ready-candidate-v001'
full=OUT.parent/'production-candidate-v001/full-production-v001'
assert pin(OUT/'new-source/DungeonHeroAirProductionProbeV001.cpp')['sha256']=='dce5897a70c8f612cd5b7bc3a5c5dee718d13e40683a0a0fb7291bdeee2903d4'
assert pin(OUT/'new-source/DungeonHeroAirProductionProbeV001.h')['sha256']=='c9a5e0e261c1688e87d1e80605fcff408fcd9dff019184ff06f010c60a9102c9'
assert pin(OUT/'new-source/DungeonHUD.cpp')['sha256']=='02b33839be77835a21566e5062f7db7c7faf5fd81c3e843a67c94154428e4204'
native_freeze=native/'Air48-native-ready-freeze-v001.json'
full_freeze=full/'HeroAir-full-production-candidate-freeze-v001.json'
assert pin(native_freeze)['sha256']=='e3786b74ac2292479780368531a99ebc097ec8df3c70629d8168a39ff75dfea7'
assert pin(full_freeze)['sha256']=='7197705254448e380d643edbef4b31fe3adf4f95a7b3c9d389ad574adea532e6'
for _ in range(2):
    for item in read(native_freeze)['members']:assert pin(item['path'])==item
    # Full-production freeze uses members; verify all its immutable files.
    f=read(full_freeze)
    for item in f.get('members',f.get('files',[])):
        fp=Path(item['path']);fp=fp if fp.is_absolute() else full/fp
        actual=pin(fp)
        assert actual['bytes']==item['bytes'] and actual['sha256']==item['sha256']
    for item in read(OUT/'immutable-baseline-input-pins-v001.json'):
        p=ROOT/item['path'];q=pin(p)
        assert q['bytes']==item['bytes'] and q['sha256']==item['sha256']
        assert (OUT/'before-source'/p.name).read_bytes()==p.read_bytes()
inputs={
    'native_ready_freeze':pin(native_freeze),
    'source_manifest48':pin(native/'import-Air48-v001.json'),
    'typed_profile':pin(native/'Air-runtime-profile-data-v001.json'),
    'canonical_source49':pin(native/'Air49-source-closure-canonical-v001.json'),
    'artist_points':pin(native/'Air6-actual-author-points-and-armor-results-v001.json'),
    'full_production_freeze':pin(full_freeze),
    'future_HUD_before':pin(full/'existing-source/DungeonHUD.cpp'),
    'actual_typed_interface':pin(ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordAirV001.h'),
    'actual_draw_readback_interface':pin(ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordAirDrawStateV001.h'),
    'actual_audio_helper_header':pin(ROOT/'UnrealGame/Source/CodexDungeon/DungeonNativeMainSubmixCaptureV001.h'),
    'actual_audio_helper_cpp':pin(ROOT/'UnrealGame/Source/CodexDungeon/DungeonNativeMainSubmixCaptureV001.cpp'),
    'actual_original_screenshot_writer':pin(ROOT/'UnrealGame/Source/CodexDungeon/DungeonProofScreenshots.cpp'),
    'E599_real_ZIP_index':pin(Path('E:/OurGame/Knight/过程图稿与视频/2026-10-19-本项目E599-钟盔Air253九层棕皮甲军剑试装-v001/E-retention-index-v001.json')),
    'E600_real_ZIP_index':pin(Path('E:/OurGame/Knight/过程图稿与视频/2026-10-19-本项目E600-钟盔Air253四十八源原生准备-v001/E-retention-index-v001.json')),
}
api={name:pin(Path(path)) for name,path in {
    'ReadSurfaceData':'G:/UE_5.5/Engine/Source/Runtime/RHI/Public/RHICommandList.h',
    'ReadFlags':'G:/UE_5.5/Engine/Source/Runtime/RHI/Public/RHITypes.h',
    'Raw8BitConversion':'G:/UE_5.5/Engine/Source/Runtime/RHI/Public/RHISurfaceDataConversion.h',
    'TextureRHI':'G:/UE_5.5/Engine/Source/Runtime/RHI/Public/RHIResources.h',
    'TextureSourceMacro':'G:/UE_5.5/Engine/Source/Runtime/Engine/Classes/Engine/Texture.h',
    'CRC32IntLength':'G:/UE_5.5/Engine/Source/Runtime/Core/Public/Misc/Crc.h',
    'RenderCorePublicRHI':'G:/UE_5.5/Engine/Source/Runtime/RenderCore/RenderCore.Build.cs',
}.items()}
fixed=write('observer-fixed-inputs-v001.json',{
    'schema':'HeroAir-production-observer-fixed-inputs-v001','inputs':inputs,'primary_local_UE55_API':api,
    'source_closure_digest':'5df0479bd1689b8adeb525255e748db13288839bbc1b8523f7ec012f404bdaec',
    'required_flags':['DungeonHeroAirProductionProofV001','DungeonFairytaleSwordAirPreview','DungeonFairytaleSwordEquipmentBoundPreview','DungeonContentProof','DungeonFastLosslessCapture','DungeonAsyncLosslessCapture'],
    'side_argument':'DungeonHeroAirProductionFacing=-1 or +1',
    'optional_explicit_knight_clearance_flag':'DungeonHeroAirProductionClearKnightDiagnostic',
    'mandatory_fresh_processes':2,'opposite_faces':[-1,1],
    'scenario':'NormalEnter_StarterNone6_E_LGT9_LandingRejump',
    'runtime_report_schema':'hero-nonattack-air-production-native-observer-v001',
    'primary_flow':['normalEnter','normalA_or_D','normalSpace_starterNoArmor6_allposes','normalE_LGT_commit','normalSpace_LGT9_allposes','normalSpace_inside_original_landing_age[.06,.12)','LGT9_second_jump_allposes','two_ordinaryReady_callbacks'],
    'GPU_source_bytes_before_audio_movie_input':True,'RHI_flags':'RCM_UNorm/Mip0/LinearToGamma=false',
    'source_GPU_byte_format':'original49_BGRA8_raw; editor_source49_TSF_BGRA8_raw; no image mutations',
    'native_root_virtual_y530_legal':True,'profile_source48_plus_existing_sword49':True,
    'None_is_formal20_pair':False,'extra_J_Shift_save_restore':'OPEN_not_run',
    'actual_import_receipt':None,'actual_compiled_manifest':None,'actual203Green':None,'native_run':None,'FinalAccepted':False})
before=(OUT/'before-source/DungeonHUD.cpp').read_text(encoding='utf-8-sig')
after=(OUT/'new-source/DungeonHUD.cpp').read_text(encoding='utf-8-sig')
diff=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='futureFullProduction/DungeonHUD.cpp',tofile='NEWProductionObserver/DungeonHUD.cpp'))
write('HUD-only-include-and-mutually-exclusive-spawn-v001.diff',diff)
assert diff.count('+')<30 and 'DungeonHeroAirProductionProofV001' in diff
static_review=write('independent-CPlusPlus-local-UE55-static-review-v001.json',{
    'schema':'HeroAir-production-observer-independent-static-review-v001',
    'reviewer':'/root/guard_move_production_v141','exact_final_cpp':pin(OUT/'new-source/DungeonHeroAirProductionProbeV001.cpp'),
    'exact_header':pin(OUT/'new-source/DungeonHeroAirProductionProbeV001.h'),
    'actual_primary_local_API_evidence':api,
    'findings_resolved':['CRC length made explicit checked int32 1MiB; no claim actual warning was enabled','WITH_EDITOR && WITH_EDITORONLY_DATA required for Source GetMipData APIs','lostWorld/GameMode/Controller/HUD nulls fail before dereference','Observe local bool bAir avoids namespace alias ambiguity; five name references only'],
    'remaining_deterministic_blockers_found':0,
    'validated_scopes':['UHT header naming/forward unique ptr deleter','RHI source strong ref + local pixel lifetime through Flush','8bit UNORM/_SRGB actual BGRA copy or channel reorder, not shader gamma/double-sRGB','TextureSource read-only RAII mip copy','actual screenshot Captured then Processed ordering','last actual callback Stop then Poll terminal then PNG Flush','old baseline bytes remain unchanged'],
    'CPlusPlus_compiled':False,'UE_started':False,'actual_GPU_readback_run':False,'native_passed':False,'visual_reviewed':False,'audio_listened':False,
    'status':'No deterministic static blocker found at pinned code. Root actual UE compilation/runtime remains required.'})
write('SOURCE-HANDOFF.md','''NEW production observer source-only freeze，尚非完整工具/原生PASS。

Root可将new-source/DungeonHeroAirProductionProbeV001.h/.cpp作为新增两文件，并将new-source/DungeonHUD.cpp作为其future full-production HUD上的窄include/互斥spawn变更准入；未来HUD基准6f86936...，不要覆盖Root当前未准入的旧HUD。旧baseline h/cpp只在before-source保全，实际6366d0.../37812b...未改，旧baseline flag分支保留。

新增flag -DungeonHeroAirProductionProofV001，配合-DungeonFairytaleSwordAirPreview -DungeonFairytaleSwordEquipmentBoundPreview -DungeonContentProof -DungeonFastLosslessCapture -DungeonAsyncLosslessCapture -DungeonHeroAirProductionFacing=-1或1及NEW绝对DungeonContentProofDir。若Root明确选择前置Knight公共clearance，另加-DungeonHeroAirProductionClearKnightDiagnostic；只允许该Knight ApplyCombatHit，不Player/Guard/HP赋值/位置/AI/时间改写。

主flow正常Enter、A/D定向、SWD/NoArmor六相跳，正常E换LGT，LGT六相跳，第一LGT真实Land5 callback后原[.06,.12) landing内正常Space再跳，完整第三跳六相与两次普通Ready callback。所有mask63；没有伪造gameplay jumpId，只记录观察器transition ordinal。None6不算正式20搭配，landing J/Shift/真实save_restore OPEN。

49实际RHI原BGRA8与49 editor Source mip0原BGRA8在预热、audioOrigin/movie/输入前读取并Flush，原bytes/CRC独立保存。DTO不是GPU字节替代；host checker还必须对源RGBA/原PNG CRC/FIFO/实际float几何单镜像/固定source-pixel误差门/真实clock/音频PCM非静音与时长独立核。原helper Arming→Recording origin→最后真实callback Stop→Poll terminal→Flush沿用。两freshface PID需要分别预注册与完整archive，不跨side复用。

本Source-only静态API审查无剩余确定性阻断，但没有编译/UE/纹理导入/GPU/原生/试听证明。Root实际48 import+productionSource294+full203GREEN及后续观察器Source准入/编译仍是运行前必要项；独立tooling正在等Root import同步边界修复后续写，不可用部分tooling冒验证通过。整体候选最终freeze待独立checker/负例完整完成。
''')
source_files=[pin(p) for p in sorted((OUT/'new-source').glob('*')) if p.is_file()]
members=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file() and 'tooling' not in p.relative_to(OUT).parts and p.name!='host-checker-protocol-v001.json']
for _ in range(2):
    for r in members:assert pin(r['path'])==r
    for r in read(OUT/'immutable-baseline-input-pins-v001.json'):
        p=ROOT/r['path'];assert pin(p)['sha256']==r['sha256']
freeze_path=write('HeroAir-production-observer-source-freeze-v001.json',{
    'schema':'HeroAir-production-observer-source-freeze-v001','created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
    'members':members,'member_count':len(members),'source_files':source_files,'source_file_count':3,
    'fixed_inputs_pin':pin(fixed),'independent_static_review':pin(static_review),
    'verification_passes':2,'mismatches':0,'old_baseline_actual_bytes_unchanged':True,
    'excludes_incomplete_child_tooling_and_protocol':True,'actual_imports':0,'UE_started':False,'native_passed':False,'FinalAccepted':False})
print(json.dumps({'source_freeze':pin(freeze_path),'source_files':source_files,'old_baseline_unchanged':True,'overall_checker_pending':True,'UE_calls':0},indent=2))
