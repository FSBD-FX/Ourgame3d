param([switch]$Prepare)
$ErrorActionPreference = 'Stop'
$candidateDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sgPython = 'C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe'
$meta = Get-Content -LiteralPath (Join-Path $candidateDir 'input-authority-and-pins-v001.json') -Raw | ConvertFrom-Json
foreach ($item in @($meta.tools) + @($meta.old_freezes) + @($meta.sole_identity) + @($meta.motion_only)) {
    $actualFile = Get-Item -LiteralPath $item.path
    $actualHash = (Get-FileHash -LiteralPath $item.path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualFile.Length -ne $item.bytes -or $actualHash -ne $item.sha256) { throw "Pinned input drift: $($item.path)" }
}
if (-not $Prepare) { Write-Output 'Pinned inputs verified; no guide/native/UE operation. Use -Prepare only to create a NEW standard technical layout.'; exit 0 }
$outDir = Join-Path $candidateDir 'prepared-run-v001'
if (Test-Path -LiteralPath $outDir) { throw 'Preserve old preparation; output already exists.' }
$argsVector = @('-B','-X','utf8','C:/Users/22499/.codex/skills/sprite-gen/scripts/prepare_sprite_run.py',
 '--out-dir',$outDir,'--character-id','fairytale-clock-hero-hurt-neargrip-v002',
 '--description','Exact accepted body-only SwordReady v002 frame0 identity; original native219 supplies only four Hurt poses; targeted nearhand closure, common bare cloth body.',
 '--request',(Join-Path $candidateDir 'request-input-v001.json'),'--chroma-key','#00FF00')
& $sgPython @argsVector
if ($LASTEXITCODE -ne 0) { throw "Standard prepare failed: $LASTEXITCODE" }
Write-Output 'Standard prepare only. New guide is UNVIEWED and must be Root E-retained before View/native attachment. No generation called.'
