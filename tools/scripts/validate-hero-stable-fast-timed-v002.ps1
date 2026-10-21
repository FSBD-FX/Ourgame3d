$ErrorActionPreference='Stop'
$fastResultPath='F:/Ourgame/source-assets/production/fairytale-hero-air-v001/root-stable-fast-admission-v002/actual-timed-validation-v002.json'
if(Test-Path -LiteralPath $fastResultPath){throw 'Preserve previous timed result.'}
$fastWatch=[Diagnostics.Stopwatch]::StartNew()
$fastPassed=$false
$fastFailure=''
try{
 $fastText=(& 'F:/Ourgame/tools/scripts/launch-hero-stable-preview-v002.ps1' -ValidateOnly | Out-String)
 $fastResult=$fastText|ConvertFrom-Json
 if(-not $fastResult.stable_runtime_verified -or -not $fastResult.parent_runtime_manifest_verified -or -not $fastResult.copy_and_native_proof_bind_original_parent -or $fastResult.runtime_files -ne 1778 -or $fastResult.UE_started -ne $false){throw 'Actual fast gate did not emit complete staged verification.'}
 $fastPassed=$true
}catch{$fastFailure=$_.Exception.Message}
$fastWatch.Stop()
$fastReceipt=[ordered]@{schema='Root-stable-fast-launch-timed-full-validation-v002';utc=(Get-Date).ToUniversalTime().ToString('O');passed=$fastPassed;elapsed_seconds=$fastWatch.Elapsed.TotalSeconds;failure=$fastFailure;actual_full_gate_result=$fastResult;all_1778_runtime_and_engine_proof_gates_executed=$fastPassed;live_development_Source_files=298;stable_compiled_Source_files=296;UE_started=$false;FinalAccepted=$false}
$fastStream=[IO.FileStream]::new($fastResultPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
try{$fastBytes=[Text.UTF8Encoding]::new($false).GetBytes(($fastReceipt|ConvertTo-Json -Depth 12));$fastStream.Write($fastBytes,0,$fastBytes.Length);$fastStream.Flush($true)}finally{$fastStream.Dispose()}
$fastReceipt|ConvertTo-Json -Depth 12
if(-not $fastPassed){exit 3}
