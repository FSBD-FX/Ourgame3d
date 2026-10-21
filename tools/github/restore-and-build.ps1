[CmdletBinding()]
param(
    [string]$EngineRoot = 'G:\UE_5.5',
    [switch]$VerifyOnly,
    [switch]$NoLaunch,
    [ValidateRange(1,16)][int]$MaxParallelActions = 2
)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$manifestPath = Join-Path $projectRoot 'source-assets/production/backups/v148-SWDSecondary8-308-1495-203GREEN-v001/compiled-source-manifest.json'
if ((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne '8936717c38f67a3bb08791537f38a60d953fd5df8132c642112a507f4eeb8772') { throw 'Historical checkpoint manifest changed.' }
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
function Test-SourceSnapshot {
    foreach ($set in @(@{Prefix='UnrealGame/Source/';Count=308},@{Prefix='UnrealGame/Content/Production/';Count=1495})) {
        $expected = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        foreach ($member in $manifest.files) {
            if (-not $member.path.StartsWith($set.Prefix,[StringComparison]::Ordinal)) { continue }
            [void]$expected.Add([string]$member.path)
            $file = Get-Item -LiteralPath (Join-Path $projectRoot $member.path)
            if ($file.Length -ne $member.bytes -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -ne $member.sha256) { throw "Source snapshot mismatch: $($member.path)" }
        }
        $actual = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        foreach ($file in Get-ChildItem -LiteralPath (Join-Path $projectRoot $set.Prefix) -Recurse -File -Force) {
            [void]$actual.Add($file.FullName.Substring($projectRoot.Length+1).Replace('\','/'))
        }
        if ($expected.Count -ne $set.Count -or -not $expected.SetEquals($actual)) { throw "Source directory membership mismatch: $($set.Prefix)" }
    }
    $projectMember = @($manifest.files | Where-Object path -eq 'UnrealGame/CodexDungeon.uproject')
    if ($projectMember.Count -ne 1 -or (Get-FileHash -LiteralPath (Join-Path $projectRoot $projectMember[0].path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $projectMember[0].sha256) { throw 'Project descriptor mismatch.' }
}
Test-SourceSnapshot
if ($VerifyOnly) {
    [ordered]@{source_files=308;production_files=1495;source_hashes_verified=$true;historical_DLL_or_runtime_acceptance_claimed=$false;UE_started=$false} | ConvertTo-Json
    return
}
& python (Join-Path $PSScriptRoot 'restore-unreal-mcp.py')
if ($LASTEXITCODE -ne 0) { throw 'External plugin restoration failed.' }
$buildTool = Join-Path $EngineRoot 'Engine/Build/BatchFiles/Build.bat'
if (-not (Test-Path -LiteralPath $buildTool)) { throw 'Set -EngineRoot to your Unreal Engine 5.5 installation.' }
& (Join-Path $projectRoot 'tools/scripts/unreal-build.ps1') -EngineRoot $EngineRoot -Target Editor -MaxParallelActions $MaxParallelActions
if ($LASTEXITCODE -ne 0) { throw 'Editor build failed; see UnrealGame/Saved/Bootstrap.' }
Test-SourceSnapshot
if ($NoLaunch) { return }
$editor = Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe'
$project = Join-Path $projectRoot 'UnrealGame/CodexDungeon.uproject'
$options = @(Get-Content -LiteralPath (Join-Path $projectRoot 'docs/github/preview-arguments.json') -Raw | ConvertFrom-Json)
$arguments = @($project) + $options
$line = ($arguments | ForEach-Object { '"{0}"' -f $_ }) -join ' '
Start-Process -FilePath $editor -ArgumentList $line -WorkingDirectory (Split-Path $project) -WindowStyle Normal
