"""Create an exclusive candidate-only freeze; never pin mutable actual project files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
sha=lambda b:hashlib.sha256(b).hexdigest()
def pin(p,role=None):
 b=p.read_bytes();r=dict(path=p.as_posix(),bytes=len(b),sha256=sha(b))
 if role:r['role']=role
 return r
deps=[
 ('prior_observer_freeze',ROOT/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/native-observation-review-fix-v002/candidate-freeze-v002.json'),
 ('prior_checker_freeze',ROOT/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/native-checker-candidate-v001/review-fix-v002/Primary1Bridge258-native-checker-review-fix-freeze-v002.json'),
 ('compiled_manifest_before',ROOT/'source-assets/production/backups/v146-Primary1Bridge258-303-1439-203GREEN-v001/compiled-source-manifest.json'),
 ('readonly_failure_diagnosis',ROOT/'docs/production/first-batch-v2/evidence/HeroPrimary1Bridge258-v146-v001/Root-old-primary-residency-native-failure-diagnosis-v001.md'),
]
engine=Path('G:/UE_5.5/Engine/Source/Runtime')
for rel in ('Engine/Public/TextureCompiler.h','Engine/Private/TextureCompiler.cpp','Engine/Classes/Engine/Texture.h','Engine/Private/Texture.cpp','Engine/Private/Texture2D.cpp','Engine/Public/TextureResource.h','RenderCore/Public/RenderResource.h','RenderCore/Private/RenderingThread.cpp'):
 deps.append(('installed_UE55_API_source',engine/rel))
out=HERE/'candidate-freeze-v003.json'
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p!=out and '__pycache__' not in p.parts]
data=dict(schema='request258-native-observation-residency-fix-freeze-v003',created_utc=datetime.now(timezone.utc).isoformat(),status='CANDIDATE_ONLY_NOT_ADMITTED_NOT_UE_COMPILED_NOT_RUN',projected_source=pin(HERE/'projected/DungeonHeroLandingPriorityProbeV001.cpp'),before_source=pin(HERE/'before/DungeonHeroLandingPriorityProbeV001.cpp'),members=members,dependencies=[pin(p,role) for role,p in deps],static_tests=5,static_red_expected_failures=4,static_green_failures=0,retained_checker_tests=34,retained_checker_failures=0,retained_preload_host_checks=11,retained_preload_failures=0,exact_insert_operations=7,original_strict_capture_byte_unchanged=True,actual_project_writes=0,UE_builds=0,UE_runs=0,native_fix_proven=False)
with out.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
for row in data['members']+data['dependencies']:
 b=Path(row['path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256']
print(json.dumps(dict(freeze=pin(out),members=len(members),dependencies=len(deps),all_pins_verified=True)))
