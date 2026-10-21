$ErrorActionPreference='Stop'
$candidate=Join-Path $PSScriptRoot 'launch-stable-preview-v002.ps1'
$before=Join-Path $PSScriptRoot 'before-launch-stable-preview-v001.ps1'
function Get-FunctionText($Path,$Name){
 $tokens=$null;$errors=$null;$ast=[System.Management.Automation.Language.Parser]::ParseFile($Path,[ref]$tokens,[ref]$errors)
 if(@($errors).Count){throw 'Source syntax error'}
 $ast.Find({param($n)$n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $Name},$true).Extent.Text
}
Invoke-Expression ((Get-FunctionText $before 'Assert-PhysicalPath').Replace('function Assert-PhysicalPath','function Assert-Original'))
Invoke-Expression ((Get-FunctionText $candidate 'Assert-PhysicalPath').Replace('function Assert-PhysicalPath','function Assert-Fast'))
Invoke-Expression (Get-FunctionText $candidate 'Same-StagePin')
$fixtures=Join-Path $PSScriptRoot '_host-fixtures/boundaries-v001'
if(Test-Path -LiteralPath $fixtures){throw 'Prior fixtures retained'}
New-Item -ItemType Directory -Path (Join-Path $fixtures 'ordinary')|Out-Null
$plain=Join-Path $fixtures 'ordinary/plain.bin';[IO.File]::WriteAllBytes($plain,[byte[]](1,2,3))
$hidden=Join-Path $fixtures 'ordinary/hidden.bin';[IO.File]::WriteAllBytes($hidden,[byte[]](4,5));[IO.File]::SetAttributes($hidden,[IO.FileAttributes]::Hidden)
$hard=Join-Path $fixtures 'hard-source.bin';[IO.File]::WriteAllBytes($hard,[byte[]](6,7));$hardAlias=Join-Path $fixtures 'hard-alias.bin'
New-Item -ItemType HardLink -Path $hardAlias -Target $hard|Out-Null
$junction=Join-Path $fixtures 'junction'
New-Item -ItemType Junction -Path $junction -Target (Join-Path $fixtures 'ordinary')|Out-Null
$script:results=[Collections.Generic.List[object]]::new()
function Check-Paths($Name,$Path,$ExpectedReject,[switch]$File){
 $states=@()
 foreach($method in @('Original','Fast')){
  $rejected=$false
  try{if($method -eq 'Original'){Assert-Original $Path -File:$File}else{Assert-Fast $Path -File:$File}}catch{$rejected=$true}
  $states+=@{method=$method;rejected=$rejected}
  if($rejected -ne $ExpectedReject){throw "Unexpected physical boundary: $Name $method"}
 }
 $script:results.Add(@{name=$Name;expected_rejected=$ExpectedReject;states=$states})
}
Check-Paths 'ordinary file' $plain $false -File
Check-Paths 'hidden ordinary file' $hidden $false -File
Check-Paths 'ordinary directory' (Split-Path $plain) $false
Check-Paths 'hardlink leaf' $hardAlias $true -File
Check-Paths 'junction parent' (Join-Path $junction 'plain.bin') $true -File
Check-Paths 'missing file in existing parent' (Join-Path $fixtures 'ordinary/missing.bin') $true -File
Check-Paths 'missing parent with required file' (Join-Path $fixtures 'missing/leaf.bin') $true -File
Check-Paths 'missing optional path preserves legacy behavior' (Join-Path $fixtures 'missing/leaf.bin') $false

# Data-only component tests: execute the actual lineage block, not the launcher or approval path.
$text=Get-Content -LiteralPath $candidate -Raw
$start=$text.IndexOf('$parentPin=$manifest.parent_runtime_manifest_pin')
$end=$text.IndexOf('$receipt=Read-StageJson $approval.stage_copy_receipt_pin',$start)
$lineage=[ScriptBlock]::Create($text.Substring($start,$end-$start))
$parentPath='F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906/_proof/runtime-snapshot-manifest-v001.json'
$parentText=Get-Content -LiteralPath $parentPath -Raw
function Read-StageJson($Pin){$script:TestParent}
function Check-Lineage($Name,[ScriptBlock]$Mutation,$ExpectedReject){
 $manifest=$parentText|ConvertFrom-Json
 $script:TestParent=$parentText|ConvertFrom-Json
 $manifest|Add-Member -NotePropertyName parent_runtime_manifest_pin -NotePropertyValue @{path='_proof/runtime-snapshot-manifest-v001.json';bytes=0;sha256='HOST_COMPONENT_ONLY_NO_APPROVAL'}
 $StageRoot=[IO.Path]::GetFullPath($manifest.stage_root)
 & $Mutation $manifest $script:TestParent
 $rejected=$false
 try{& $lineage}catch{$rejected=$true}
 if($rejected -ne $ExpectedReject){throw "Unexpected lineage boundary: $Name"}
 $script:results.Add(@{name=$Name;component_only=$true;expected_rejected=$ExpectedReject;rejected=$rejected})
}
Check-Lineage 'identical 1778 runtime/engine/CM metadata component' {param($m,$p)} $false
Check-Lineage 'runtime SHA changed' {param($m,$p)$m.runtime_files[0].sha256='0'*64} $true
Check-Lineage 'runtime order changed' {param($m,$p)$a=$m.runtime_files[0];$m.runtime_files[0]=$m.runtime_files[1];$m.runtime_files[1]=$a} $true
Check-Lineage 'runtime member omitted' {param($m,$p)$m.runtime_files=@($m.runtime_files|Select-Object -Skip 1)} $true
Check-Lineage 'engine SHA changed' {param($m,$p)$m.engine_files[0].sha256='0'*64} $true
Check-Lineage 'parent CM changed' {param($m,$p)$p.source_CM_sha256='0'*64} $true
Check-Lineage 'parent count changed' {param($m,$p)$p.runtime_count=1777} $true
Check-Lineage 'old immutable metadata omitted' {param($m,$p)$m.metadata_files=@($m.metadata_files|Select-Object -Skip 1)} $true
$result=[ordered]@{schema='stable-fast-v002-small-component-tests';passed=$true;checks=$script:results.Count;cases=$script:results;authority='HOST_COMPONENT_ONLY_NO_ROOT_APPROVAL_OR_NATIVE_CLAIM';full_launcher_run=$false;all1778_hashes_run=$false;UE_started=$false;actual_stage_modified=$false;RootApproved=$false;FinalAccepted=$false}
$target=Join-Path $PSScriptRoot 'small-boundary-tests-result-v001.json'
if(Test-Path -LiteralPath $target){throw 'Prior result retained'}
$result|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $target -Encoding utf8
$result|ConvertTo-Json -Depth 8
