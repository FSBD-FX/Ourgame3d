"""Read-only static candidate checks; no UE or native execution claims."""
from pathlib import Path
import hashlib
import json
import re

C = Path(__file__).resolve().parent.parent
ROOT = Path('F:/Ourgame')

def pin(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def matches(expected):
    actual = pin(Path(expected['path']))
    return actual['bytes'] == expected['bytes'] and actual['sha256'] == expected['sha256']

def verify():
    cpp = (C/'new-source/DungeonHeroAirDiskRestoreProbeV001.cpp').read_text(encoding='utf-8')
    h = (C/'new-source/DungeonHeroAirDiskRestoreProbeV001.h').read_text(encoding='utf-8')
    proto = json.loads((C/'protocol-v001.json').read_text(encoding='utf-8'))
    before = json.loads((C/'before-source-pins-v001.json').read_text(encoding='utf-8'))
    integration = json.loads((C/'integration/Root-integration-index-v001.json').read_text(encoding='utf-8'))
    checks = []
    def check(name, ok, detail=''):
        checks.append({'name': name, 'passed': bool(ok), 'detail': detail})
    check('exact before compiled manifest', matches(before['compiled_manifest_pin']))
    source = before['source_files']
    check('all298 actual Source bytes unchanged', len(source) == 298 and all(pin(ROOT/x['path'])['bytes'] == x['bytes'] and pin(ROOT/x['path'])['sha256'] == x['sha256'] for x in source))
    check('actual Source exact membership', {str(x.relative_to(ROOT)).replace('\\','/') for x in (ROOT/'UnrealGame/Source').rglob('*') if x.is_file()} == {x['path'] for x in source})
    for overlay in integration['existing_source_overlay']:
        data = Path(overlay['destination']).read_bytes()
        check('overlay before '+Path(overlay['destination']).name, matches(overlay['before']))
        for edit in overlay['edits']:
            needle, replacement = edit['needle'].encode(), edit['replacement'].encode()
            check('unique overlay needle '+edit['needle'].splitlines()[0], data.count(needle) == edit['expected_occurrences'] == 1)
            data = data.replace(needle, replacement)
        check('exact derived overlay '+Path(overlay['destination']).name, len(data) == overlay['after_bytes'] and hashlib.sha256(data).hexdigest() == overlay['after_sha256'])
    check('exact2 new source files', sorted(p.name for p in (C/'new-source').iterdir()) == sorted(proto['source_files']))
    check('UHT generated header is last header include', re.findall(r'^#include\s+"([^"]+)"', h, re.M)[-1] == 'DungeonHeroAirDiskRestoreProbeV001.generated.h')
    check('strong texture/audio UObject references', 'UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001>' in h and 'UPROPERTY(Transient) TMap<FString,TObjectPtr<UTexture2D>>' in h)
    loops = re.findall(r'for\(const TCHAR\* Flag:\{(.*?)\}\)', cpp)
    check('complete minimum CLI / forbidden flags match protocol', len(loops) == 2 and re.findall(r'TEXT\("([^"]+)"\)',loops[0]) == proto['common_cli'] and re.findall(r'TEXT\("([^"]+)"\)',loops[1]) == proto['forbidden_flags'])
    check('every FString Printf has literal TCHAR array', all(re.match(r'\s*TEXT\("',cpp[m.end():]) for m in re.finditer(r'FString::Printf\(',cpp)))
    check('no manual player/gameplay value assignments', not re.search(r'(?:P|Player|G|Game)->(?:JumpHeight|JumpVelocity|Health|Facing|SimulationTime|bAIEnabled)\s*=(?!=)',cpp))
    check('legal Installer restoration is reported separately', 'player_Guard_HP_position_AI_time_writes' not in cpp and 'observer_forced_gameplay_writes' in cpp and 'snapshot_restoration_via_actual_installer' in cpp and 'FDungeonRunInstaller::Install(*G,Prepared,Why)' in cpp)
    check('source capture is actual completed Frame2 same game thread', 'SaveApex(Index,A,P)' in cpp and 'Draw.Plan.Frame==2' in cpp and 'IsInGameThread()&&Game.IsValid()&&Game->CaptureRunSnapshot' in cpp)
    check('gen1 parent0 exact commit/readback and Close', 'Request.GenerationId=1;Request.ParentGeneration=0' in cpp and 'Store.CloseWriter()' in cpp and 'Bytes==SavedCodec' in cpp)
    check('target noPawn origin / hidden prepare / possess', 'PristineIndex!=INDEX_NONE' in cpp and 'LoadAndPreparePristine' in cpp and 'all_staged_hidden_tick_collision_off' in cpp and 'C->GetPawn()==P' in cpp)
    check('whole paused Codec includes queued Enter residual Await', 'Phase==12&&G->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue' in cpp and 'LastPausedWall=Start+Offset' in cpp and 'LastPausedWall-InstalledWall>=.20' in cpp and 'PauseCount>=3&&NeutralCount>=1' in cpp)
    target_tick = cpp[cpp.index('if(Restore)\n  {',cpp.index('void Tick(')):cpp.index('const auto P=G->PlayerFighter.Get();FDungeonFirstBatchGuardRoomView')]
    check('target Enter only / no Space reset', 'Pulse(EKeys::Enter)' in target_tick and 'EKeys::SpaceBar' not in target_tick and 'Pose>=2' in cpp and 'JumpInputs==0' in cpp)
    check('texture115 exact and source guarded / byte size before file', proto['startup_resources']['total_unique'] == 115 and 'ExpectedReadbacks==115' in cpp and '#if WITH_EDITOR && WITH_EDITORONLY_DATA' in cpp and cpp.index('GPU.Num()==512*512') < cpp.index('Directory/GPUFile') and cpp.index('Mip.Num()==512*512*4') < cpp.index('Directory/SourceFile'))
    check('raw GPU has no gamma conversion / render ref lifetime flush', '[RHI,&GPU]' in cpp and 'Flags.SetLinearToGamma(false)' in cpp and cpp.index('FlushRenderingCommands();const double ReadStop') < cpp.index('Directory/GPUFile'))
    check('audio Arming waits Recording before movie/input', cpp.index('Status().Phase==EDungeonNativeMixCapturePhaseV001::Recording',cpp.index('void Tick(')) < cpp.index('Capturing=true;GIsDumpingMovie=-1') and 'Start=Status.StartMonotonic' in cpp)
    check('exclusive evidence writes and capture exit cleanup', 'CREATE_NEW' in cpp and 'OnScreenshotRequestProcessed().RemoveAll(this)' in cpp and 'GIsDumpingMovie=0' in cpp and 'MainMixCapture->Abort' in cpp)
    check('target audio may be authentic silent / no fake play', 'require_non_silent' not in cpp and not re.search(r'PlaySound|PlaySynth|CreateSound2D|SpawnSound',cpp) and proto['audio_addendum_pin']['sha256'] == 'c406da45c144572dc598a546f75f07d487885280df19510eed7237de3584d4d9')
    return {'schema':'hero-air-disk-restore-static-source-validation-v001','checks':checks,'passed':all(x['passed'] for x in checks),'checked_count':len(checks),'UE_compiled':False,'native_executed':False,'RootApproved':False,'FinalAccepted':False,'source_cpp_pin':pin(C/'new-source/DungeonHeroAirDiskRestoreProbeV001.cpp'),'protocol_pin':pin(C/'protocol-v001.json')}

if __name__ == '__main__':
    result = verify()
    output = C/'validation/source-contract-result-v002.json'
    with output.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({'passed':result['passed'],'checked_count':result['checked_count'],'failed':[x['name'] for x in result['checks'] if not x['passed']],'result':pin(output)},ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 3)
