"""Read-only exact source/ordering checks. --against-current is admission-time only."""
from pathlib import Path
import hashlib,json,ast,sys
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((HERE/'exact-seams.json').read_text());ops=0
for r in m['files']:
 before=(HERE/r['before']).read_bytes();after=(HERE/r['projected']).read_bytes()
 assert (len(before),sha(before))==(r['before_bytes'],r['before_sha256'])
 assert (len(after),sha(after))==(r['after_bytes'],r['after_sha256'])
 if '--against-current' in sys.argv:assert (ROOT/'UnrealGame/Source/CodexDungeon'/r['name']).read_bytes()==before,('Actual source changed',r['name'])
 nl='\r\n' if r['line_ending']=='CRLF' else '\n';s=before.decode()
 for op in r['operations']:
  a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert s.count(a)==1;s=s.replace(a,b,1);ops+=1
 assert s.encode()==after
 for op in reversed(r['operations']):
  a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert s.count(b)==1;s=s.replace(b,a,1)
 assert s.encode()==before,'All original bytes must roundtrip'
w=(HERE/'projected/DungeonWorldProjectiles.cpp').read_text(encoding='utf-8')
start=w.index('void ADungeonGameMode::ConsumeBoundWeaponEvents(');end=w.index('else if (E.Kind==EEvent::ProjectileEmitted',start);step=w[start:end]
assert step.index('E.EventId<=Fighter->LastSkillEventId')<step.index('AudioBefore=')<step.index('SweepWeaponStep')<step.index('SetActorLocation')<step.index('AudioAfter=')<step.index('DungeonHeroForwardStepAudioV001::Eligible')<step.index('AppendActionAudio')<step.index('Witness.Present=true')
assert step.count('BatchSkillStepDelta+=Delta;')==1 and step.count('SetActorLocation(')==1 and step.count('AppendActionAudio(')==1
assert 'Witness.CommittedDelta=AudioAfter-AudioBefore' in step
assert 'AudioSkill.Time==SimulationTime' in step and 'WeaponWorld.RoomInstanceId==AudioView.RoomInstanceId' in step
assert 'Fighter==PlayerFighter' in step and 'AudioView.OwnerId,AudioScope' in step
for forbidden in ('PlaySound2D','ObserveHeroGroundDistanceV001','GroundDistance','TryStart','SetGamePaused'):
 assert forbidden+'(' not in step
h=(HERE/'projected/DungeonActionAudioFeedback.h').read_text(encoding='utf-8');assert 'FVector2D Before{0.,0.}, After{0.,0.}, CommittedDelta{0.,0.};' in h
hud=(HERE/'projected/DungeonHUD.cpp').read_text(encoding='utf-8');assert hud.count('ActionAudioSounds.Add(TEXT("HERO_STEP_LIGHT_01"),Sound)')==1
assert 'const float Volume=(Melee||HeroForwardStep)?.25f:' in hud
for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
print(json.dumps(dict(files=len(m['files']),exact_operations=ops,all_original_bytes_roundtrip=True,postcommit_order_and_single_journal_append=True,no_new_motion_or_cadence_calls=True,actual_before_checked='--against-current' in sys.argv,UE_run=False)))
