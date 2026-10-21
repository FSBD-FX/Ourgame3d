"""Freeze only NEW callback-ready source candidates, excluding parallel tooling."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json

ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
CM=ROOT/'source-assets/production/backups/v142-HeroAir6-Observer296-203GREEN-v001/compiled-source-manifest.json'
CM_SHA='57da85947be6d028dbc413f3c4fc6221ff5b0f4c66eed4cedea07773995da647'
CPP_SHA='75dd41c0b615363e82a4b18d3dcfa018bc966ea371cf4510126ed0c0fe701da3'


def pin(p):
    p=Path(p).resolve();data=p.read_bytes()
    return dict(path=p.as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write_new(p,data):
    if not isinstance(data,str):data=json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    with Path(p).open('xb') as f:f.write(data.encode('utf-8'))


def main():
    cm=pin(CM)
    if cm['sha256']!=CM_SHA:raise ValueError('Current actual CM296 differs')
    cm_data=read(CM);before=read(HERE/'before-actual-Source296-three-pins-v002.json')
    for row in before:
        if pin(row['path'])!=row:raise ValueError('Actual Source changed before Root admission')
        relative=Path(row['path']).relative_to(ROOT).as_posix()
        if dict(row,path=relative) not in cm_data['files']:raise ValueError('Before Source not current CM296 member')
    sources=[pin(p) for p in sorted((HERE/'new-source').glob('*'))]
    cpp=next(x for x in sources if Path(x['path']).suffix=='.cpp' and Path(x['path']).name!='DungeonHUD.cpp')
    if len(sources)!=3 or cpp['sha256']!=CPP_SHA:raise ValueError('Reviewed Source3 pin differs')
    for name in ('DungeonHeroAirProductionProbeV001.h','DungeonHUD.cpp'):
        if (HERE/'before-source'/name).read_bytes()!=(HERE/'new-source'/name).read_bytes():raise ValueError('Nonowned h/HUD drift')
    old=(HERE/'before-source/DungeonHeroAirProductionProbeV001.cpp').read_text(encoding='utf-8')
    new=(HERE/'new-source/DungeonHeroAirProductionProbeV001.cpp').read_text(encoding='utf-8')
    for start,end in ((' bool CaptureTextureBytesBeforeAudio()',' void Observe('),(' bool Pulse(',' bool ClearKnightIfRequested('),(' bool ClearKnightIfRequested(',' bool CaptureTextureBytesBeforeAudio()')):
        if old[old.index(start):old.index(end)]!=new[new.index(start):new.index(end)]:raise ValueError('Out-of-scope native/Stop/gear function changed')
    review=HERE/'independent-callback-ready-CPlusPlus-review-v002.json'
    write_new(review,dict(schema='HeroAir-callback-ready-independent-CPlusPlus-review-v002',reviewer_agent='/root/guard_move_production_v141',
        reviewed_CPP=cpp,reviewed_header=next(x for x in sources if Path(x['path']).suffix=='.h'),
        independent_exact_old_new_diff_confirmed=True,
        conclusion='No deterministic source/API blocker in completed-callback token, identity/clock guard, one consumption and original Need preservation. Actual compilation/native remain Root work.',
        completed_callback_requires_same_draw_sim_and_identity=True,consumer_allows_next_native_tick_sim_to_advance=True,
        Ready_stack='Existing nonempty actual7 stack equal to HUD; no invented9 Ready condition',
        immediate_InputKey_before_after_HV_unmodified=True,read_only_input_context_metadata_only=True,
        unchanged_three63_masks_HP_clock_GPU_PNG_audio_timeouts=True,actual_UE_started=False,native_passed=False,FinalAccepted=False))
    actual_after=[dict(x,path='UnrealGame/Source/CodexDungeon/'+Path(x['path']).name) for x in sources]
    index=HERE/'Root-source-admit-index-v002.json'
    write_new(index,dict(schema='HeroAir-callback-ready-source-admit-index-v002',RootApproved=False,is_template=True,actual_applied=False,
        before_compiled_manifest=cm,before_actual_source_files=before,candidate_after_source_files=sources,
        actual_after_paths_and_pins=actual_after,expected_source_before=296,expected_source_after=296,
        actual_source_semantic_scope='Observer callback synchronization and truthful Key metadata only; same class/header/HUD, no new game modules or gameplay/physics changes.',
        current_Build_RHI_dependency_not_modified_by_this_candidate=True,
        new_source_freeze_required=True,new_actual_source_admission_build_and_NativeRHI203_required=True,FinalAccepted=False))
    write_new(HERE/'SOURCE-HANDOFF-v002.md',
'''本NEW源码候选只修观察器同步。原e7b9、66f1、595总freeze、left_v001失败与presentation6a42均保留，不倒改通过状态。

new-source有同名h/cpp/HUD三项供Root通用准入；只有cpp改变。先验证before CM29657da与实际旧三源，Root备份/准入后真实编译，并用当前Source296/实际DLL/NativeRHI全203严格GREEN形成新CM。观察器仍原flag/class/schema，Source计数296不变；Build.cs显式RHI由Root已有独立修复链约束，本候选不改它。

Phase5只等Observe收到已完成真实LGT Ready callback，验证同draw sim/owner/run/room/epoch/装备版本/facing、新DrawId、既有非空7栈等原Ready条件；记录LGT_completed_Ready_callback与实际observation_index。下一Tick才消费一次，允许真实sim前进、仍核当前绑定和owner身份，原commit/PinGear/CanPulse/原Need均保留。不sleep、不代替玩家InputKey、不改H/V或游戏物理。

Key追加真实pre-InputKey上下文及明确非gameplay jumpID的观察序号；原before/after即时物理字段完全不变。真实InputKey排队，所以旧66f1同步afterV630假设不能冒未来PASS，必须等NEW独立queued因果checker/协议冻结。其核心口径由Root预登记为实际输入→后继完成空中callback的一一严格因果；.005基础模型只额外诊断，不冒实际子段回放或验收门。原mask63×3/半开landing/None6LGT9/49GPU/floatquad/sourcepixel/PNG/audio/Ready2不变。

本freeze只含已审三源及源准入准备，不包含并行未冻tooling。Root独占实际准入/编译/捕获/E保全/View；本候选没有UE/native/GPU/试听/最终美术PASS。
''')
    paths=list((HERE/'before-source').glob('*'))+list((HERE/'new-source').glob('*'))+[HERE/'prepare-callback-ready-source-v002.py',Path(__file__),HERE/'callback-ready-only-v002.diff',HERE/'before-actual-Source296-three-pins-v002.json',HERE/'callback-ready-source-lineage-v002.json',review,index,HERE/'SOURCE-HANDOFF-v002.md']
    members=[pin(p) for p in sorted(paths)]
    for repeat in range(2):
        for row in members:
            if pin(row['path'])!=row:raise ValueError('Member changed')
    output=HERE/'HeroAir-production-observer-callback-ready-source-freeze-v002.json'
    write_new(output,dict(schema='HeroAir-production-observer-callback-ready-source-freeze-v002',utc=datetime.now(timezone.utc).isoformat(),
        member_count=len(members),members=members,source_files=sources,before_compiled_manifest=cm,
        derivative_of=read(HERE/'callback-ready-source-lineage-v002.json')['old_source_freeze'],
        source_admit_index=pin(index),independent_static_review=pin(review),expected_source_before=296,expected_source_after=296,
        two_SHA_verification_passes=2,mismatches=0,old_frozen_and_failed_originals_preserved=True,
        parallel_tooling_excluded=True,actual_Source_Content_E_ledger_writes=0,UE_started=False,native_passed=False,FinalAccepted=False))
    print(json.dumps(dict(freeze=pin(output),members=len(members),source_files=sources,two_SHA_mismatches=0,UE_started=False,FinalAccepted=False)))


if __name__=='__main__':main()
