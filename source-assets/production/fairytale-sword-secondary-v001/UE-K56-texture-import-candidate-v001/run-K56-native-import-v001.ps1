param(
 [Parameter(Mandatory=$true)][string]$Manifest,
 [Parameter(Mandatory=$true)][string]$ManifestSha256,
 [Parameter(Mandatory=$true)][string]$CandidateFreezeSha256,
 [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference='Stop'
$kRoot='F:/Ourgame'
$kPython='F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe'
$kCM='F:/Ourgame/source-assets/production/backups/v147-SWDStepAudio303-1439-203GREEN-v001/compiled-source-manifest.json'
$kCMSha='ae00569bad81eae953b989b964ed2592e6f1e8e0dff43b81163358c43bb3007a'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Exclusive K56 entry requires no UE/UBT process'}
foreach($kHash in @($ManifestSha256,$CandidateFreezeSha256)){if($kHash -cnotmatch '^[0-9a-f]{64}$'){throw 'Explicit exact SHA256 arguments required'}}
$kManifestFull=[IO.Path]::GetFullPath($Manifest)
if((Get-FileHash -LiteralPath $kManifestFull -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ManifestSha256){throw 'Manifest bytes differ'}
$kFreeze=Join-Path $PSScriptRoot 'candidate-freeze-v001.json'
if((Get-FileHash -LiteralPath $kFreeze -Algorithm SHA256).Hash.ToLowerInvariant() -ne $CandidateFreezeSha256){throw 'Reviewed tool freeze differs'}
if((Get-FileHash -LiteralPath $kCM -Algorithm SHA256).Hash.ToLowerInvariant() -ne $kCMSha){throw 'Pinned current CM differs'}
$kOutFull=[IO.Path]::GetFullPath($Out)
$kEvidenceRoot=[IO.Path]::GetFullPath('F:/Ourgame/docs/production/first-batch-v2/evidence').TrimEnd('\')+'\'
if(-not $kOutFull.StartsWith($kEvidenceRoot,[StringComparison]::OrdinalIgnoreCase)){throw 'Fresh Root evidence directory required'}
if(Test-Path -LiteralPath $kOutFull){throw 'Never retry/delete/overwrite prior K56 run directory; inspect retained outcome'}
if(-not (Test-Path -LiteralPath ([IO.Path]::GetDirectoryName($kOutFull)))){throw 'Root evidence parent must already exist'}
New-Item -ItemType Directory -Path $kOutFull | Out-Null
function Write-KNewJson([string]$Path,[object]$Value){
 $kStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$kBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 30));$kStream.Write($kBytes,0,$kBytes.Length);$kStream.Flush($true)}finally{$kStream.Dispose()}
}
function Get-KPin([string]$Path){$kFile=Get-Item -LiteralPath $Path;return @{path=$kFile.FullName.Replace('\','/');bytes=$kFile.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
$kImporter=Join-Path $PSScriptRoot 'ue-import-K56-v001.py'
$kProof=Join-Path $kOutFull 'host-preflight-v001.json'
$kReceipt=Join-Path $kOutFull 'actual-native-import-v001.json'
$kCommonArgs=@('--manifest',$kManifestFull,'--manifest-sha',$ManifestSha256,'--compiled-manifest',$kCM,'--compiled-manifest-sha',$kCMSha)
& $kPython -B -X utf8 $kImporter --preflight @kCommonArgs --candidate-freeze-sha $CandidateFreezeSha256 --output $kProof *> (Join-Path $kOutFull 'host-preflight-output-v001.log')
$kHostExit=$LASTEXITCODE
Write-KNewJson (Join-Path $kOutFull 'host-preflight-exit-v001.json') @{schema='Root-K56-host-preflight-exit-v001';exit_code=$kHostExit;UE_started=$false;utc=(Get-Date).ToUniversalTime().ToString('O')}
if($kHostExit -ne 0){Write-Output 'Host preflight failed before UE; retained exact output.';exit $kHostExit}
$kProofSha=(Get-FileHash -LiteralPath $kProof -Algorithm SHA256).Hash.ToLowerInvariant()
$kConfig=Join-Path $kOutFull 'native-arguments-v001.json'
$kNativeArgs=@($kImporter,'--native-import')+$kCommonArgs+@('--candidate-freeze-sha',$CandidateFreezeSha256,'--host-proof',$kProof,'--host-proof-sha',$kProofSha,'--output',$kReceipt)
Write-KNewJson $kConfig @{schema='Root-K56-native-arguments-v001';importer=(Get-KPin $kImporter);argv=$kNativeArgs}
$kWrapper=Join-Path $kOutFull 'run-frozen-K56-import-v001.py'
$kWrapperCode=@'
import hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
config=json.loads(Path(__file__).with_name('native-arguments-v001.json').read_text(encoding='utf-8-sig'))
source=Path(config['importer']['path']);data=source.read_bytes()
assert len(data)==config['importer']['bytes'] and hashlib.sha256(data).hexdigest()==config['importer']['sha256']
sys.path.insert(0,str(source.parent));sys.argv=config['argv'];runpy.run_path(str(source),run_name='__main__')
'@
$kWrapperStream=[IO.FileStream]::new($kWrapper,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
try{$kWrapperBytes=[Text.UTF8Encoding]::new($false).GetBytes($kWrapperCode);$kWrapperStream.Write($kWrapperBytes,0,$kWrapperBytes.Length)}finally{$kWrapperStream.Dispose()}
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'UE/UBT appeared after preflight; no UE launch permitted'}
$kExe='G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$kArgs=@('F:/Ourgame/UnrealGame/CodexDungeon.uproject','-unattended','-nosplash','-nop4','-NoLiveCoding','-AllowCommandletAudio','-run=pythonscript',('-script='+$kWrapper),('-abslog='+(Join-Path $kOutFull 'native-UE-K56-import-v001.log')))
foreach($kArg in $kArgs){if($kArg.Contains('"') -or $kArg.Contains("`r") -or $kArg.Contains("`n")){throw 'Unsupported quote/newline in exact argv'}}
$kArgumentLine=($kArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
$kProcess=Start-Process -FilePath $kExe -ArgumentList $kArgumentLine -WorkingDirectory 'F:/Ourgame/UnrealGame' -WindowStyle Hidden -PassThru
Write-KNewJson (Join-Path $kOutFull 'launch-receipt-v001.json') @{schema='Root-K56-native-import-launch-v001';process_id=$kProcess.Id;executable=$kExe;started_utc=(Get-Date).ToUniversalTime().ToString('O');arguments=$kArgs;manifest=(Get-KPin $kManifestFull);host_proof=(Get-KPin $kProof);native_wrapper=(Get-KPin $kWrapper);native_arguments=(Get-KPin $kConfig);FinalAccepted=$false}
Write-Output ('Exclusive new56 Texture2D import PID '+$kProcess.Id)
$kProcess.WaitForExit()
$kOSExit=$kProcess.ExitCode
Write-KNewJson (Join-Path $kOutFull 'exit-receipt-v001.json') @{schema='Root-K56-native-import-exit-v001';process_id=$kProcess.Id;exit_code=$kOSExit;finished_utc=(Get-Date).ToUniversalTime().ToString('O');os_exit_confirmed=$true;FinalAccepted=$false}
if($kOSExit -ne 0){Write-Output 'Retained native nonzero outcome. No retry/cleanup/overwrite.';exit $kOSExit}
$kVerifier=Join-Path $PSScriptRoot 'verify-K56-import-v001.py'
& $kPython -B -X utf8 $kVerifier @kCommonArgs --receipt $kReceipt --host-proof $kProof --launch-receipt (Join-Path $kOutFull 'launch-receipt-v001.json') --exit-receipt (Join-Path $kOutFull 'exit-receipt-v001.json') --output (Join-Path $kOutFull 'readonly-import-verification-v001.json') *> (Join-Path $kOutFull 'readonly-verifier-output-v001.log')
$kVerifyExit=$LASTEXITCODE
Write-KNewJson (Join-Path $kOutFull 'wrapper-result-v001.json') @{schema='Root-K56-wrapper-result-v001';actual_native_os_exit=$kOSExit;readonly_verifier_exit=$kVerifyExit;success=($kVerifyExit -eq 0);FinalAccepted=$false}
exit $kVerifyExit
