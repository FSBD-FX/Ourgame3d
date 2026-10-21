$ErrorActionPreference='Stop'
$bridgeRoot='F:/Ourgame'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Exclusive import requires no UE/UBT process'}
$bridgeCandidate=Join-Path $bridgeRoot 'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/UE-import-binding-candidate-v001'
$bridgeFreeze=Join-Path $bridgeCandidate 'candidate-freeze-v001.json'
if((Get-FileHash -LiteralPath $bridgeFreeze -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'eaa11e20169bb6b53687671800100aa1eea1e703a29ec48ecb36ab55cbb0c6b9'){throw 'Frozen candidate differs'}
$bridgeReview=Join-Path $bridgeRoot '.superpowers/sdd/2026-10-19-hero-locomotion-audio-v145/art258-import-binding-review-v001.md'
if((Get-FileHash -LiteralPath $bridgeReview -Algorithm SHA256).Hash.ToLowerInvariant() -ne '3315578d568df3d031e60484deaf96dcc1ac5c82bbe1f8d881ab63cd057fd7d4'){throw 'Fresh approved review differs'}
$bridgeEvidence=Join-Path $bridgeRoot 'docs/production/first-batch-v2/evidence/HeroPrimary1Bridge258-v146-v001/Root-native-import-v001'
if(Test-Path -LiteralPath $bridgeEvidence){throw 'Never retry/overwrite initial native import; inspect retained outcome'}
New-Item -ItemType Directory -Path $bridgeEvidence | Out-Null
function Write-BridgeNewJson([string]$Path,[object]$Value){
 $bridgeStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$bridgeBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 20));$bridgeStream.Write($bridgeBytes,0,$bridgeBytes.Length);$bridgeStream.Flush($true)}finally{$bridgeStream.Dispose()}
}
$bridgeWrapper=Join-Path $bridgeEvidence 'run-frozen-import-v001.py'
$bridgePythonCode=@'
import sys,runpy,hashlib,json
from pathlib import Path
sys.dont_write_bytecode=True
base=Path('F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/UE-import-binding-candidate-v001')
freeze=base/'candidate-freeze-v001.json'
assert hashlib.sha256(freeze.read_bytes()).hexdigest()=='eaa11e20169bb6b53687671800100aa1eea1e703a29ec48ecb36ab55cbb0c6b9'
importer=base/'import/ue-import-primary1-bridge258-v001.py'
sys.argv=[str(importer),'--native-import','--host-proof',str(base/'reports/host-preflight-v002.json'),'--output','F:/Ourgame/docs/production/first-batch-v2/evidence/HeroPrimary1Bridge258-v146-v001/Root-native-import-v001/import-receipt.json']
runpy.run_path(str(importer),run_name='__main__')
'@
[IO.File]::WriteAllText($bridgeWrapper,$bridgePythonCode,[Text.UTF8Encoding]::new($false))
$bridgeArgs=@('F:/Ourgame/UnrealGame/CodexDungeon.uproject','-unattended','-nosplash','-nop4','-NoLiveCoding','-AllowCommandletAudio','-run=pythonscript',('-script='+$bridgeWrapper),('-abslog='+(Join-Path $bridgeEvidence 'native-UE-import-v001.log')))
$bridgeArgumentLine=($bridgeArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
$bridgeProcess=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' -ArgumentList $bridgeArgumentLine -WorkingDirectory 'F:/Ourgame/UnrealGame' -WindowStyle Hidden -PassThru
Write-BridgeNewJson (Join-Path $bridgeEvidence 'launch-receipt-v001.json') @{schema='Root-primary1-bridge258-import-launch-v001';process_id=$bridgeProcess.Id;started_utc=(Get-Date).ToUniversalTime().ToString('O');arguments=$bridgeArgs;paid_API_calls=0;FinalAccepted=$false}
Write-Output ('Fourteen new request258 textures native import PID '+$bridgeProcess.Id)
$bridgeProcess.WaitForExit()
Write-BridgeNewJson (Join-Path $bridgeEvidence 'exit-receipt-v001.json') @{schema='Root-primary1-bridge258-import-exit-v001';process_id=$bridgeProcess.Id;exit_code=$bridgeProcess.ExitCode;finished_utc=(Get-Date).ToUniversalTime().ToString('O');os_exit_confirmed=$true;FinalAccepted=$false}
if($bridgeProcess.ExitCode -ne 0){Write-Output 'Preserved actual nonzero outcome. Do not rerun/delete/overwrite any imported assets.'}
exit $bridgeProcess.ExitCode
