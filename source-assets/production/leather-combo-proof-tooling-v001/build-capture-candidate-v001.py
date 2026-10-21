from pathlib import Path
here = Path(__file__).resolve().parent
text = Path("F:/Ourgame/tools/scripts/capture-leather-primary1-trial-v001.ps1").read_text(encoding="utf-8-sig")
text = text.replace("_软皮轻甲左右第一刀试装_", "_软皮轻甲左右三段连击试装_")
text = text.replace("'-DungeonFairytaleLeatherPrimary1OnlyProof'", "'-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleLeatherComboOnlyProof'")
marker = "$archive=Join-Path $workspace"
position = text.index(marker)
text = text[:position] + '''& (Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-leather-combo-proof-v001.py') --snapshot $Snapshot --source-only
if($LASTEXITCODE -ne 0){throw 'Concrete combo Source/DLL/production/receipts/current full-suite contract preflight failed before capture.'}
''' + text[position:]
text = text.replace("$index.runtime_passed=$report.passed;$index.observations=@($report.observations).Count", "$index.runtime_passed=$report.passed;$index['native_reported_passed']=$report.passed;$index.observations=@($report.observations).Count")
marker = " # A native behavior RED is evidence"
position = text.index(marker)
text = text[:position] + ''' $index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8
 & (Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-leather-combo-proof-v001.py') --snapshot $Snapshot --source-only
 if($LASTEXITCODE -ne 0){throw 'Capture changed combo Source/compiled inputs/original RGBA contract.'}
 if($report.passed){
  & (Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-leather-combo-proof-v001.py') --snapshot $Snapshot --archive $archive
  if($LASTEXITCODE -ne 0){$index.runtime_passed=$false;throw 'Native reported passed but independent combo technical verification failed; preserve all originals.'}
 }
''' + text[position:]
(here / "capture-leather-combo-trial-v001.ps1").write_text(text, encoding="utf-8", newline="\n")
