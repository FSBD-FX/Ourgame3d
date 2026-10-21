"""Root prepares a NEW staged native launcher; never runs UE or changes frozen launchers."""
from pathlib import Path
import hashlib, json
R=Path('F:/Ourgame')
source=R/'tools/scripts/run-hero-Air6-production-v003.ps1'
target=R/'tools/scripts/run-hero-Air6-staged-v001.ps1'
text=source.read_text(encoding='utf-8-sig')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='40436a9322289c5a498e5a69ed2be8a4d498065163f883ec7f68b4b63c66472c'
text=text.replace("[string]$Version='v003'","[string]$Version='v004'")
text=text.replace("$airRoot='F:\\Ourgame'", "$airRoot='F:\\Ourgame'\n$airStage='F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906'\n$airStageManifest=Get-Content -LiteralPath (Join-Path $airStage '_proof/runtime-snapshot-manifest-v001.json') -Raw | ConvertFrom-Json\nfunction Assert-AirStageRuntime {\n foreach($row in $airStageManifest.runtime_files){$p=Join-Path $airStage $row.path;$f=Get-Item -LiteralPath $p -Force;if($f.LinkType -or ($f.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $f.Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Actual staged runtime changed: '+$p}}\n}\nAssert-AirStageRuntime")
assert text.count("'F:/Ourgame/UnrealGame/CodexDungeon.uproject'")==1
text=text.replace("'F:/Ourgame/UnrealGame/CodexDungeon.uproject'","(Join-Path $airStage 'CodexDungeon.uproject')")
old="'-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleSwordWalkPreview'"
new="'-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordWalkPreview'"
assert old in text;text=text.replace(old,new)
text=text.replace('-WindowStyle Hidden -PassThru','-WorkingDirectory $airStage -WindowStyle Hidden -PassThru')
anchor='$airProcess.WaitForExit()'
assert text.count(anchor)==1
proof='''$airModule=$null
$airModuleDeadline=[DateTime]::UtcNow.AddSeconds(20)
while(-not $airProcess.HasExited -and [DateTime]::UtcNow -lt $airModuleDeadline){
 try{$airProcess.Refresh();$airModule=@($airProcess.Modules | Where-Object {$_.ModuleName -eq 'UnrealEditor-CodexDungeon.dll'} | Select-Object -First 1);if($airModule.Count){break}}catch{}
 Start-Sleep -Milliseconds 100
}
if($airModule -and $airModule.Count){
 $airLoadedPath=[IO.Path]::GetFullPath($airModule[0].FileName)
 Write-AirNewJson (Join-Path $airMedia 'actual-loaded-staged-module-v001.json') @{schema='Root-actual-native-staged-module-observation-v001';process_id=$airProcess.Id;actual_loaded_DLL=$airLoadedPath.Replace('\\','/');module_pin=(Get-AirPin $airLoadedPath);expected_staged_DLL=(Join-Path $airStage 'Binaries/Win64/UnrealEditor-CodexDungeon.dll').Replace('\\','/');staged_project_path=$airTokens[0];observed_utc=(Get-Date).ToUniversalTime().ToString('O');observation_method='System.Diagnostics.Process.Modules actual live process';FinalAccepted=$false}
}
$airProcess.WaitForExit()
Assert-AirStageRuntime
'''
text=text.replace(anchor,proof)
assert not target.exists()
with target.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
print(json.dumps(dict(path=target.as_posix(),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),UE_started=False),ensure_ascii=False))
