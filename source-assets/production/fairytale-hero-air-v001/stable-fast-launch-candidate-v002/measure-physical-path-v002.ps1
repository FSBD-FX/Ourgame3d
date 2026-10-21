$ErrorActionPreference='Stop'
$stage='F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906'
$original=Join-Path $stage '_proof/tools/launch-stable-preview-v001.ps1'
if((Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'f94a28e6064973781292897089fce7d92b1ab1021f82e400ef0331e3133026f1'){throw 'Original source changed'}
$tokens=$null;$errors=$null;$ast=[System.Management.Automation.Language.Parser]::ParseFile($original,[ref]$tokens,[ref]$errors)
$old=$ast.Find({param($node)$node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Assert-PhysicalPath'},$true).Extent.Text
Invoke-Expression ($old.Replace('function Assert-PhysicalPath','function Assert-PhysicalPathOriginal'))
function Assert-PhysicalPathDotNet([string]$Path,[switch]$File){
 $current=[IO.Path]::GetFullPath($Path)
 while($current){
  $attributes=$null
  try{$attributes=[IO.File]::GetAttributes($current)}catch [IO.FileNotFoundException]{}catch [IO.DirectoryNotFoundException]{}
  if($null -ne $attributes){
   if($attributes -band [IO.FileAttributes]::ReparsePoint){throw "Linked path rejected: $current"}
   if(-not ($attributes -band [IO.FileAttributes]::Directory)){
    $item=Get-Item -LiteralPath $current -Force
    if($item.LinkType){throw "Linked path rejected: $current"}
   }
  }
  $parent=[IO.Path]::GetDirectoryName($current);if($parent -eq $current){break};$current=$parent
 }
 if($File -and -not [IO.File]::Exists($Path)){throw "Physical file missing: $Path"}
}
$manifest=Get-Content -LiteralPath (Join-Path $stage '_proof/runtime-snapshot-manifest-v001.json') -Raw|ConvertFrom-Json
$deep=@($manifest.runtime_files|Where-Object {$_.path -like 'Content/Production/*'}|Sort-Object {$_.path.Length} -Descending)[0].path
$paths=@((Join-Path $stage 'Config/DefaultEngine.ini'),(Join-Path $stage $deep),(Join-Path $stage '_proof/tools/launch-stable-preview-v001.ps1'))
# Warm up each function once; measure only six further calls per method.
foreach($path in $paths){Assert-PhysicalPathOriginal $path -File;Assert-PhysicalPathDotNet $path -File}
$rows=@()
foreach($method in @('Original','DotNet','DotNet','Original')){
 $watch=[Diagnostics.Stopwatch]::StartNew()
 for($repeat=0;$repeat -lt 2;$repeat++){foreach($path in $paths){if($method -eq 'Original'){Assert-PhysicalPathOriginal $path -File}else{Assert-PhysicalPathDotNet $path -File}}}
 $watch.Stop();$rows+=@{method=$method;calls=6;elapsed_ms=$watch.Elapsed.TotalMilliseconds}
}
$result=[ordered]@{schema='stable-physical-path-small-readonly-microbenchmark-v002';utc=(Get-Date).ToUniversalTime().ToString('o');original_core_sha256='f94a28e6064973781292897089fce7d92b1ab1021f82e400ef0331e3133026f1';representative_paths=$paths;measurements=$rows;scope='path queries only, same existing files, no hash timing or full-launch estimate';full_launcher_run=$false;UE_started=$false;actual_stage_modified=$false;RootApproved=$false}
$result|ConvertTo-Json -Depth 5
$target=Join-Path $PSScriptRoot 'path-microbenchmark-result-v001.json'
if(Test-Path -LiteralPath $target){throw 'Prior benchmark retained'}
$result|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $target -Encoding utf8
