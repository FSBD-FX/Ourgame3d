param([switch]$ExecuteNative)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $workspace 'source-assets\production\stone-guard-feedback-v001\tooling\ue-import-guard-audio-v001.py'
& $python -B -X utf8 $script --validate-only
if($LASTEXITCODE -ne 0){throw '11 source WAV preflight failed.'}
if(-not $ExecuteNative){return}
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Sequential import needs UE/UBT closed.'}
$beforeCode=@'
from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');O=R/'source-assets/production/stone-guard-feedback-v001/root-audio-import-v001'
assert not O.exists();O.mkdir()
rows=[]
for p in sorted((R/'UnrealGame/Content/Production').rglob('*')):
 if p.is_file():
  b=p.read_bytes();rows.append(dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
assert len(rows)==1199,len(rows)
(O/'before1199.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print('Pinned old1199 packages before native import')
'@
& $python -B -X utf8 -c $beforeCode
if($LASTEXITCODE -ne 0){throw 'Old1199 inventory failed.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'guard-audio-v001-*.json' -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('guard-audio-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$argsList=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath 'G:\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList $argsList -WindowStyle Hidden -PassThru
Write-Output "Guard audio actual import PID $($process.Id), log $log"
$process.WaitForExit()
$fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'guard-audio-v001-*.json' -File | Where-Object {$_.FullName -notin $before})
if($process.ExitCode -ne 0 -or $fresh.Count -ne 1){throw 'Native import failed or unique receipt missing.'}
$afterCode=@'
from pathlib import Path
import hashlib,json,sys
R=Path('F:/Ourgame');O=R/'source-assets/production/stone-guard-feedback-v001/root-audio-import-v001'
receipt=Path(sys.argv[1]);v=json.loads(receipt.read_text(encoding='utf-8-sig'));assert v['success'] and len(v['assets'])==11,v
rows=json.loads((O/'before1199.json').read_text(encoding='utf-8-sig'))
for repeat in range(2):
 for row in rows:
  p=R/row['path'];b=p.read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],p
 for row in v['assets']:
  p=Path(row['saved_path']);b=p.read_bytes();assert len(b)==row['saved_bytes'] and hashlib.sha256(b).hexdigest()==row['saved_sha256'],p
files=[p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()];assert len(files)==1210,len(files)
out=dict(success=True,old1199_unchanged=True,verification_passes=2,actual_count=11,actual_total=1210,receipt=str(receipt),sound_quality_accepted=False)
(O/'independent-import-verification.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
'@
& $python -B -X utf8 -c $afterCode $fresh[0].FullName
if($LASTEXITCODE -ne 0){throw 'Actual receipt/disk/old1199 verification failed.'}
