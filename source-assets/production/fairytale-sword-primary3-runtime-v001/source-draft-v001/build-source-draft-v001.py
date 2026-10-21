"""Create three UNAPPLIED P3 source candidates from exact v115 sources only."""
from pathlib import Path
import difflib
import hashlib
import json

ROOT = Path('F:/Ourgame')
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'source-assets/production/backups/2026-10-16_Primary2Armor42-fit-full138GREEN-v115'
INLINE = ROOT / 'source-assets/production/fairytale-sword-primary3-runtime-v001/data/DungeonFairytaleSwordPrimary3V001.inl'
INLINE_SHA = '6749343b607b21ae5d7d1b8d1bf959b67324d13b85c7f6b37f70097088116054'
NAMES = ('DungeonHUD.cpp', 'DungeonFairytaleSwordPresentation.cpp', 'DungeonFairytaleSwordProbe.cpp')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def descriptor(path):
    data = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)).replace('\\', '/'), 'bytes': len(data), 'sha256': sha(data)}

def change(text, before, after, count=1):
    assert text.count(before) == count, (before, text.count(before), count)
    return text.replace(before, after)

def new_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(data)

assert sha(INLINE.read_bytes()) == INLINE_SHA, 'Root inline dependency changed'
manifest = json.loads((BASE / 'compiled-source-manifest.json').read_text(encoding='utf-8-sig'))
rows = {row['path']: row for row in manifest['files']}
original, before_data, newlines = {}, {}, {}
for name in NAMES:
    rel = 'UnrealGame/Source/CodexDungeon/' + name
    data = (ROOT / rel).read_bytes()
    assert len(data) == rows[rel]['bytes'] and sha(data) == rows[rel]['sha256'], rel
    assert data == (BASE / rel).read_bytes(), rel
    assert b'\r' not in data.replace(b'\r\n', b''), 'Unexpected isolated CR'
    newlines[name] = '\r\n' if b'\r\n' in data else '\n'
    assert newlines[name] == '\n' or b'\n' not in data.replace(b'\r\n', b''), 'Unexpected mixed newlines'
    before_data[name] = data
    original[name] = data.decode('utf-8').replace('\r\n', '\n')

candidate = dict(original)
hud = candidate[NAMES[0]]
hud = change(hud, '#include "DungeonFairytaleSwordPrimary2ArmorV001.inl"\n',
    '#include "DungeonFairytaleSwordPrimary2ArmorV001.inl"\n#include "DungeonFairytaleSwordPrimary3V001.inl"\n')
hud = change(hud, '        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled();\n',
    '        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled()\n        ||DungeonFairytaleSwordPrimary3V001::Enabled();\n')
hud = change(hud, '        if(DungeonFairytaleSwordPrimary2ArmorV001::Enabled())\n',
    '        if(DungeonFairytaleSwordPrimary2ArmorV001::Enabled() || DungeonFairytaleSwordPrimary3V001::Enabled())\n')
warm = '''        if(DungeonFairytaleSwordPrimary3V001::Enabled())
            for(const FString Component:{TEXT("Body"),TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
                TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
                for(int32 I=0;I<6;++I)
                    if(auto Texture=DungeonFairytaleSwordPrimary3V001::GetTexture(Component,I,Frames))ReadyArmorTextures.Add(Texture);
'''
hud = change(hud, '        // The complete selected draw also needs the independent sword and the\n',
    warm + '        // The complete selected draw also needs the independent sword and the\n')
candidate[NAMES[0]] = hud

presentation = candidate[NAMES[1]]
presentation = change(presentation, '#include "DungeonFairytaleSwordPrimary2ArmorV001.inl"\n',
    '#include "DungeonFairytaleSwordPrimary2ArmorV001.inl"\n#include "DungeonFairytaleSwordPrimary3V001.inl"\n')
presentation = change(presentation, '''    using namespace DungeonFairytaleSwordBodyV001;
    const bool Second=bUseFairytaleSwordPrimary2Preview && Clip==TEXT("sword_primary_2");''',
    '''    using namespace DungeonFairytaleSwordBodyV001;
    if(DungeonFairytaleSwordPrimary3V001::Enabled() && Clip==TEXT("sword_primary_3"))
    {
        if(Index<0 || Index>=DungeonFairytaleSwordPrimary3V001::Count(Clip))return nullptr;
        return DungeonFairytaleSwordPrimary3V001::GetTexture(TEXT("Body"),Index,Frames);
    }
    const bool Second=bUseFairytaleSwordPrimary2Preview && Clip==TEXT("sword_primary_2");''')
presentation = change(presentation, '        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled());\n',
    '        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled() || DungeonFairytaleSwordPrimary3V001::Enabled());\n', 2)
presentation = change(presentation, '    const bool StableIdle=Sword && !F->bDead && !Action.Active && Melee.Grounded\n',
    '''    const bool Primary3=DungeonFairytaleSwordPrimary3V001::Enabled() && Sword && !F->bDead && Action.Active && Melee.Grounded
        && Action.Weapon==DungeonContentCombat::EWeapon::SWD001
        && Action.Stage==2 && !Action.StartedAirborne;
    const bool StableIdle=Sword && !F->bDead && !Action.Active && Melee.Grounded
''')
presentation = change(presentation, '    Record.Supported=Primary1 || Primary2 || StableIdle;\n',
    '    Record.Supported=Primary1 || Primary2 || Primary3 || StableIdle;\n')
presentation = change(presentation, '    Record.Clip=Primary2?TEXT("sword_primary_2"):Primary1?TEXT("sword_primary_1"):TEXT("sword_ready_idle");\n',
    '    Record.Clip=Primary3?TEXT("sword_primary_3"):Primary2?TEXT("sword_primary_2"):Primary1?TEXT("sword_primary_1"):TEXT("sword_ready_idle");\n')
presentation = change(presentation, '    Record.Frame=(Primary1||Primary2)?F->GetPrimaryPoseFrame():StableIdle\n',
    '    Record.Frame=(Primary1||Primary2||Primary3)?F->GetPrimaryPoseFrame():StableIdle\n')
presentation = change(presentation, '    const FMarker* Marker=Primary2BodyTrial?DungeonFairytaleSwordPrimary2V003::Find(Record.Clip,Record.Frame)\n',
    '    const FMarker* Marker=Primary3?DungeonFairytaleSwordPrimary3V001::Find(Record.Clip,Record.Frame)\n        :Primary2BodyTrial?DungeonFairytaleSwordPrimary2V003::Find(Record.Clip,Record.Frame)\n')
presentation = change(presentation, '''    const bool Primary2ArmorPhase=Primary2 && DungeonFairytaleSwordPrimary2ArmorV001::Enabled();
    const bool ArmorPhase=(Record.ArmorPreview && StableIdle) || PrimaryArmorPhase || Primary2ArmorPhase;''',
    '''    const bool Primary2ArmorPhase=Primary2 && (DungeonFairytaleSwordPrimary2ArmorV001::Enabled()
        ||DungeonFairytaleSwordPrimary3V001::Enabled());
    const bool Primary3ArmorPhase=Primary3 && DungeonFairytaleSwordPrimary3V001::ArmorEnabled();
    const bool ArmorPhase=(Record.ArmorPreview && StableIdle) || PrimaryArmorPhase || Primary2ArmorPhase || Primary3ArmorPhase;''')
presentation = change(presentation, '    // Ready, Primary1 and opt-in Primary2 each use their own source phase partition.\n',
    '    // Ready and each supported primary stage use their own source phase partition.\n')
presentation = change(presentation, '    const int32 LayerCount=(PrimaryArmorPhase||Primary2ArmorPhase)?7:6;\n',
    '    const int32 LayerCount=(PrimaryArmorPhase||Primary2ArmorPhase||Primary3ArmorPhase)?7:6;\n')
presentation = change(presentation, '            ReadyLayers[I]=Primary2ArmorPhase\n',
    '            ReadyLayers[I]=Primary3ArmorPhase\n                ?DungeonFairytaleSwordPrimary3V001::GetTexture(PrimaryComponents[I],Record.Frame,Frames)\n                :Primary2ArmorPhase\n')
candidate[NAMES[1]] = presentation

probe = candidate[NAMES[2]]
probe = change(probe, '#include "DungeonProofScreenshots.h"\n',
    '#include "DungeonProofScreenshots.h"\n#include "DungeonFairytaleSwordPrimary3V001.inl"\n')
probe = change(probe, '    const double T=Wall-CaptureStart;\n',
    '    const double T=Wall-CaptureStart;\n    const bool Third=DungeonFairytaleSwordPrimary3V001::Enabled();\n')
probe = change(probe, '''    Key(EKeys::Enter,T<.12);
    if(Second)
''', '''    Key(EKeys::Enter,T<.12);
    if(Third)
    {
        Key(EKeys::J,(T>=1.10&&T<1.18)||(T>=1.60&&T<1.68)||(T>=2.16&&T<2.24)
            ||(T>=4.30&&T<4.38)||(T>=4.80&&T<4.88)||(T>=5.36&&T<5.44));
        Key(EKeys::A,T>=3.40&&T<3.48);
        if(T>=6.60)Finish();
    }
    else if(Second)
''')
probe = change(probe, '''    R->SetBoolField(TEXT("primary2_fit_trial"),Second);
    R->SetStringField(TEXT("scope"),Primary2ArmorTrial
''', '''    const bool Third=DungeonFairytaleSwordPrimary3V001::Enabled();
    const bool ThirdArmor=DungeonFairytaleSwordPrimary3V001::ArmorEnabled();
    R->SetBoolField(TEXT("primary3_fit_trial"),Third);
    R->SetBoolField(TEXT("primary3_armor_trial"),ThirdArmor);
    R->SetBoolField(TEXT("primary2_fit_trial"),Second || Third);
    if(Third)
        R->SetStringField(TEXT("scope"),ThirdArmor
            ?TEXT("Native175 body with opt-in48 Primary3 source/body/armor textures, including integer-registered native176/177/178 armor; real six J requests traverse grounded kernelStages0/1/2, with Stage2 660ms. Existing Ready/Primary1 and native171 V003 Primary2 armor trials retained. No hit target, equipment identity, thumb/grasp, footlock, fullmotion or audio acceptance")
            :TEXT("Native175 six-body independent-sword fit under real six J requests traversing grounded kernelStages0/1/2, with Stage2 660ms. Existing Ready/Primary1 and native171 V003 Primary2 armor trials retained; Primary3 armor absent. No hit target, equipment identity, thumb/grasp, footlock, fullmotion or audio acceptance"));
    else
    R->SetStringField(TEXT("scope"),Primary2ArmorTrial
''')
candidate[NAMES[2]] = probe

checks = []
def verify(name, condition):
    assert condition, name
    checks.append({'check': name, 'passed': True})

verify('HUD original full suffix from weapon flags onward unchanged',
    hud.split('    bUseWeaponBodyPreview =',1)[1] == original[NAMES[0]].split('    bUseWeaponBodyPreview =',1)[1])
verify('RunContinueProof include and spawn preserved', '#include "DungeonRunContinueProbe.h"' in hud and
    'GetWorld()->SpawnActor<ADungeonRunContinueProbe>();' in hud)
verify('Presentation whole-resource gate + transform + draw suffix unchanged',
    presentation.split('    // Validate the whole supported draw',1)[1] == original[NAMES[1]].split('    // Validate the whole supported draw',1)[1])
old_input = original[NAMES[2]].split('    if(Second)\n',1)[1].split('\nvoid ADungeonFairytaleSwordProbe::Finish',1)[0]
new_input = probe.split('    else if(Second)\n',1)[1].split('\nvoid ADungeonFairytaleSwordProbe::Finish',1)[0]
verify('Original second/first input blocks byte-identical', old_input == new_input)
old_scope = original[NAMES[2]].split('    R->SetStringField(TEXT("scope"),Primary2ArmorTrial\n',1)[1].split('    R->SetArrayField(TEXT("observations")',1)[0]
new_scope = probe.split('    R->SetStringField(TEXT("scope"),Primary2ArmorTrial\n',1)[1].split('    R->SetArrayField(TEXT("observations")',1)[0]
verify('Original first/second scope strings unchanged', old_scope == new_scope)
verify('Original capture/flush/report suffix unchanged',
    probe.split('    R->SetArrayField(TEXT("observations")',1)[1] == original[NAMES[2]].split('    R->SetArrayField(TEXT("observations")',1)[1])
verify('P3 actual Stage2 + grounded/nonair/kernel frame',
    'Action.Stage==2 && !Action.StartedAirborne' in presentation and 'Action.Active && Melee.Grounded' in presentation and
    'Record.Frame=(Primary1||Primary2||Primary3)?F->GetPrimaryPoseFrame()' in presentation)
verify('Selected P2 uses V003 under either P3 flag', presentation.count('|| DungeonFairytaleSwordPrimary3V001::Enabled());') == 2)
verify('All48 P3 textures use existing GC-owned Frames and targeted compilation',
    'TEXT("Body"),TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest")' in hud and
    'DungeonFairytaleSwordPrimary3V001::GetTexture(Component,I,Frames)' in hud and 'FinishCompilation(ReadyArmorTextures)' in hud)
verify('Independent weapon scale remains .50 and same UV layer draw unchanged',
    'constexpr double WeaponScale=.50;' in presentation and 'DrawBodyLayer(ReadyLayers[LayerCount-1]);' in presentation)
verify('Root inline is consumed, never generated or edited', sha(INLINE.read_bytes()) == INLINE_SHA)

patches = []
for name in NAMES:
    rel = 'UnrealGame/Source/CodexDungeon/' + name
    new_file(HERE / 'source-before' / name, before_data[name])
    new_file(HERE / 'candidate-source' / name, candidate[name].replace('\n',newlines[name]).encode('utf-8'))
    patches.extend(difflib.unified_diff(original[name].splitlines(True), candidate[name].splitlines(True),
        fromfile='a/'+rel, tofile='b/'+rel))
new_file(HERE / 'primary3-source-draft-v001.patch', ''.join(patches).encode('utf-8'))
for name in NAMES:
    verify('Actual Source remains untouched: '+name,
        (ROOT / 'UnrealGame/Source/CodexDungeon' / name).read_bytes() == before_data[name])
audit = {'schema':'primary3-unapplied-source-draft-audit-v001','applied':False,'compiled':False,
    'baseline_manifest':descriptor(BASE/'compiled-source-manifest.json'),'root_inline_dependency':descriptor(INLINE),
    'expected_namespace':'/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3',
    'new_flags':['DungeonFairytaleSwordPrimary3Preview','DungeonFairytaleSwordPrimary3ArmorPreview'],
    'root_inline_Enabled_includes_both_flags':True,'P3_armor_only_on_ArmorEnabled':True,
    'P2_V003_and_P2_armor_inherited_under_either_P3_flag':True,
    'requested_J_wall_offsets_s':[1.10,1.60,2.16,4.30,4.80,5.36],
    'requested_A_wall_offset_s':3.40,'requested_stop_wall_offset_s':6.60,
    'staging_not_applied':True,'checks':checks,
    'source_newlines_preserved':{name:('CRLF' if newlines[name]=='\r\n' else 'LF') for name in NAMES},
    'local_preflight_correction':'Initial uniform-CRLF assertion stopped before outputs; actual v115 HUD is CRLF and Presentation/Probe are LF. Preserve each file native newlines.',
    'limitations':['Candidate files only; no UBT/UE/import/visual execution.',
        'Requires Root-admitted pinned P3 inline and all intended texture imports.',
        'Manual rebase required if actual HUD/Presentation/Probe change after baseline.',
        'Candidate markers/axes, semantic partitioning, grip, clearance, continuous motion, hit/audio and full equipment are not accepted.']}
new_file(HERE/'static-audit-v001.json',(json.dumps(audit,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
review = '''# Primary3 source draft v001 — UNAPPLIED

Three candidate copies and a minimal patch are based byte-for-byte on v115 HUD, Presentation and Probe. Actual Unreal Source is unchanged. Root's pinned Primary3V001 inline is a dependency, not authored here.

Either new Primary3 flag enables native171 P2V003 plus its existing 42-texture armor chain and the established Ready/Primary1 chain. Stage2 is supported only for living grounded SWD001 actions that did not start airborne, using the real GetPrimaryPoseFrame. Primary3Preview draws the full175 body plus independent sword and bounded source-hand UV replay; Primary3ArmorPreview selects its own seven source layers. The existing exact-UV draw suffix yields BodyRest→Far→Chest→NearArmWithoutHand→Near→Helmet→Sword→NearHand. No Ready armor is borrowed for Stage2.

HUD retains all48 P3 texture references in its existing UPROPERTY Frames cache and includes them in the existing targeted compilation wait before the existing render flush. The unchanged complete resource gate rejects missing/pending selected body, armor or sword resources before drawing any selected quad. Body size, mirror, .50 sword scale, input consumption and combat clocks are unchanged.

Probe adds a separate Third branch with six real J requests at1.10/1.60/2.16 and4.30/4.80/5.36, one A request at3.40, and stop6.60. The complete old Second/first input branches and old scope strings remain byte-identical. Native CRC/FIFO/flush behavior is unchanged. New scope distinguishes175 body-only from176/177/178 armor and explicitly withholds hit, equipment, grasp, footlock, fullmotion and audio acceptance.

Static assertions verify original suffixes and actual source hashes. These checks are not compilation or runtime proof. Root must admit/rebase the patch, import resources, compile and observe real gameplay before any visual conclusion. No marker coordinates or axes are invented here.
'''
new_file(HERE/'self-review-v001.md',review.encode('utf-8'))
files = [descriptor(path) for path in sorted(HERE.rglob('*')) if path.is_file()]
freeze = {'schema':'primary3-unapplied-three-source-freeze-v001','applied':False,'compiled':False,
    'file_count_excluding_this_manifest':len(files),'total_bytes_excluding_this_manifest':sum(f['bytes'] for f in files),
    'actual_source_unchanged':True,'files':files}
new_file(HERE/'source-freeze-v001.json',(json.dumps(freeze,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
print(json.dumps({'freeze':descriptor(HERE/'source-freeze-v001.json'),
    'candidate_sources':[descriptor(HERE/'candidate-source'/name) for name in NAMES],
    'patch':descriptor(HERE/'primary3-source-draft-v001.patch'),'static_checks':len(checks)},indent=2))
