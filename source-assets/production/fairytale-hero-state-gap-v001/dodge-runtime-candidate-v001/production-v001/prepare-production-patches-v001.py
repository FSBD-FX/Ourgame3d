from pathlib import Path
import difflib
import hashlib
import json

ROOT = Path('F:/Ourgame')
HERE = Path(__file__).resolve().parent
SRC = ROOT / 'UnrealGame/Source/CodexDungeon'

query = '''bool ADungeonFighter::QueryDodgePresentation(FDungeonDodgePresentationSample& Out) const
{
    // Published actual owner/action facts stay readable while Continue is closed.
    // This query never advances a clock, admits input, or grants gear authority.
    if (bEnemy || StoneKnight || StoneBat || StoneGuard || bDead || !FMath::IsFinite(Health) || Health<=0.f
        || !FMath::IsFinite(HurtTime) || HurtTime>0.f || JumpHeight!=0.f || JumpVelocity!=0.f
        || AnimationName!=TEXT("dodge")) return false;
    const auto& S=Dodge.State();
    if (S.Phase!=DungeonDodge::EPhase::Dodging || S.Records.empty() || !S.OwnerId
        || S.OwnerId!=GetRuntimeEntityId()) return false;
    const auto& R=S.Records.back();
    for (double T:{S.Time,R.Start,R.End,R.ReadyAt,R.Travelled,R.Direction.X,R.Direction.Y})
        if (!FMath::IsFinite(T)) return false;
    if (!R.ActionId || !R.StartEventId || R.Finish!=DungeonDodge::EFinish::None
        || R.Start<0. || R.End!=R.Start+DungeonDodge::Duration || R.ReadyAt!=R.Start+DungeonDodge::Cooldown
        || S.Time<R.Start || S.Time>=R.End || R.Travelled<0. || R.Travelled>DungeonDodge::Distance
        || uint32(R.Block)>uint32(DungeonDodge::EBlock::Body)
        || !FMath::IsNearlyEqual(R.Direction.X*R.Direction.X+R.Direction.Y*R.Direction.Y,1.,1.e-12)) return false;
    FDungeonDodgePresentationSample Candidate;
    Candidate.Active=true;Candidate.OwnerId=S.OwnerId;Candidate.ActionId=R.ActionId;Candidate.StartEventId=R.StartEventId;
    Candidate.SampleTime=S.Time;Candidate.Start=R.Start;Candidate.End=R.End;Candidate.ReadyAt=R.ReadyAt;
    Candidate.Elapsed=S.Time-R.Start;Candidate.Remaining=R.End-S.Time;Candidate.Travelled=R.Travelled;
    Candidate.Direction={R.Direction.X,R.Direction.Y};Candidate.Block=R.Block;Candidate.Finish=R.Finish;
    Candidate.Invulnerable=IsDodgeInvulnerableAt(S.Time);
    Out=MoveTemp(Candidate);return true;
}'''

def replace_once(data, old, new):
    if data.count(old) != 1:
        raise RuntimeError(f'Expected one exact insertion anchor; found {data.count(old)}: {old[:100]!r}')
    return data.replace(old, new, 1)

changes = {}
name = 'DungeonFighter.cpp'
before = (SRC / name).read_text(encoding='utf-8-sig')
old = '''bool ADungeonFighter::QueryDodgePresentation(FDungeonDodgePresentationSample&) const
{
    // Stage0 semantic unsupported; no state/clock writes and no partial output.
    return false;
}'''
changes[name] = replace_once(before, old, query)

name = 'DungeonHUD.h'
before = (SRC / name).read_text(encoding='utf-8-sig')
changes[name] = replace_once(before,
    '    FDungeonFairytaleSwordDodgeDraw FairytaleSwordDodgeDraw; // Stage0 DTO only; no draw/preload routing.',
    '''    bool bUseFairytaleSwordDodgePreview=false;
    FDungeonFairytaleSwordDodgeDraw FairytaleSwordDodgeDraw;
    bool DrawFairytaleSwordDodgeBody(ADungeonFighter* Fighter);''')

name = 'DungeonHUD.cpp'
before = (SRC / name).read_text(encoding='utf-8-sig')
after = replace_once(before, '#include "DungeonFairytaleSwordDeathTextures.inl"',
    '#include "DungeonFairytaleSwordDeathTextures.inl"\n#include "DungeonFairytaleSwordDodgeTextures.inl"')
after = replace_once(after,
    '    bUseFairytaleSwordWalkPreview=bUseFairytaleSwordEquipmentBoundPreview',
    '''    bUseFairytaleSwordDodgePreview=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordDodgeV001::CommandLineFlag);
    bUseFairytaleSwordWalkPreview=bUseFairytaleSwordEquipmentBoundPreview''')
after = replace_once(after, '#if WITH_EDITOR\n        FTextureCompilingManager::Get().FinishCompilation(ReadyArmorTextures);',
    '''        if(bUseFairytaleSwordDodgePreview)
        {
            // All32 nonempty owners and existing sword33 finish at startup.
            const auto& DodgeProfile=DungeonFairytaleSwordDodgeV001::Profile();
            for(const auto& Phase:DodgeProfile.Frames)
                for(const auto& Layer:Phase.Layers)
                    if(auto Texture=DungeonFairytaleSwordDodgeV001::PreloadTexture(Layer.TexturePath,Frames))ReadyArmorTextures.Add(Texture);
            if(auto Texture=DungeonFairytaleSwordDodgeV001::PreloadTexture(DodgeProfile.SwordTexturePath,Frames))ReadyArmorTextures.Add(Texture);
        }
#if WITH_EDITOR
        FTextureCompilingManager::Get().FinishCompilation(ReadyArmorTextures);''')
changes[name] = after

name = 'DungeonFairytaleSwordPresentation.cpp'
before = (SRC / name).read_text(encoding='utf-8-sig')
after = replace_once(before, '    if(!F || F->bEnemy)return false;\n    const uint64 PreviousDeathDrawId=',
    '''    if(!F || F->bEnemy)return false;
    // Clear Dodge observation before higher-priority Death/Hurt can return.
    const uint64 PreviousDodgeDrawId=FairytaleSwordDodgeDraw.DrawId;
    FairytaleSwordDodgeDraw=FDungeonFairytaleSwordDodgeDraw();
    FairytaleSwordDodgeDraw.DrawId=PreviousDodgeDrawId;
    FairytaleSwordDodgeDraw.OptIn=bUseFairytaleSwordDodgePreview;
    const uint64 PreviousDeathDrawId=''')
after = replace_once(after, '        return DrawFairytaleSwordHurtBody(F);\n    using namespace DungeonFairytaleSwordBodyV001;',
    '''        return DrawFairytaleSwordHurtBody(F);
    // Death > Hurt > actual air > Dodge. Backward roll keeps actual Facing.
    if(bUseFairytaleSwordDodgePreview && !F->bDead && F->JumpHeight==0.f && F->GetVerticalVelocity()==0.f
        && F->AnimationName==TEXT("dodge") && F->GetDodgeState().Phase==DungeonDodge::EPhase::Dodging
        && DrawFairytaleSwordDodgeBody(F))return true;
    using namespace DungeonFairytaleSwordBodyV001;''')
changes[name] = after

for name, after in changes.items():
    p = HERE / 'changed-source' / name
    p.parent.mkdir(parents=True, exist_ok=True)
    # Review copy only. All actual admissions use the narrow patch below.
    p.write_bytes(after.replace('\n', '\r\n').encode('utf-8'))

names = [*changes, 'DungeonFairytaleSwordDodgePlan.cpp']
pins = []
for name in names:
    actual = SRC / name
    baseline = actual.read_bytes()
    dest = HERE / 'before' / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(baseline)
    before = baseline.decode('utf-8-sig').replace('\r\n', '\n')
    after = (HERE / 'changed-source' / name).read_text(encoding='utf-8-sig')
    target = f'UnrealGame/Source/CodexDungeon/{name}'
    patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=target, tofile=target, n=3))
    if not patch:
        raise RuntimeError(f'Empty production change: {name}')
    pp = HERE / 'patches' / f'{name}.patch'
    pp.parent.mkdir(parents=True, exist_ok=True)
    pp.write_bytes(patch.encode('utf-8'))
    pins.append({'path':target, 'bytes':len(baseline), 'sha256':hashlib.sha256(baseline).hexdigest(),
                 'patch':pp.relative_to(HERE).as_posix()})
(HERE / 'actual-before-pins-v001.json').write_text(json.dumps({'schema':'Dodge32-production-actual-Stage0-before-pins-v001','files':pins},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate_only':True,'before_files':len(pins),'patches':len(pins),'new_source_files':2}))
