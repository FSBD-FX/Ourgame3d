param([string]$EngineRoot='G:\UE_5.5',[ValidateRange(1,999)][int]$Version=3)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker=Join-Path $PSScriptRoot 'verify-sword-primary2-fit-v003.py'
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Sequential capture requires no existing UE/UBT.'}
& $python -B -X utf8 $checker --preflight-only
if($LASTEXITCODE -ne 0){throw 'Frozen imported-source preflight failed.'}
$topic=(Get-Date -Format 'yyyy-MM-dd')+'_钟盔军剑第二段真实连击试装_v'+$Version.ToString('000')
$archive=Join-Path $workspace ('过程图稿与视频\'+$topic)
if(Test-Path -LiteralPath $archive){throw 'Choose an unused version; preserve prior evidence.'}
$original=Join-Path $archive '原件'
$presentation=Join-Path $archive '展示副本'
[IO.Directory]::CreateDirectory($original)|Out-Null
[IO.Directory]::CreateDirectory($presentation)|Out-Null
$index=[ordered]@{status='capture_started';profile='fairytale_sword_normal_input_v001';formal_complete_units=0;audio_recorded=$false;scope='158Ready/Primary1 armor plus native171 Primary2 body fit. Second armor absent. Candidate only; grip/footlock/fullmotion/complete unit unaccepted.';module_sha256=(Get-FileHash -LiteralPath (Join-Path $workspace 'UnrealGame\Binaries\Win64\UnrealEditor-CodexDungeon.dll') -Algorithm SHA256).Hash}
$sources=[ordered]@{}
foreach($source in Get-ChildItem -LiteralPath (Join-Path $workspace 'UnrealGame\Source\CodexDungeon') -Recurse -File){$sources[$source.FullName.Substring($workspace.Length+1)]=(Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash}
$index['source_sha256_at_capture']=$sources
$indexPath=Join-Path $archive 'index.json'
$index | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath $indexPath -Encoding utf8
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$argsList=@(('"{0}"' -f $project),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonSceneExplorationPreview','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2ArcPreview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordBodyProof','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir="{0}"' -f $original),'-ExecCmds="t.MaxFPS 30,r.ScreenshotDelegate 1"',('-abslog="{0}"' -f (Join-Path $archive 'runtime.log')))
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $argsList -WindowStyle Hidden -PassThru
Write-Output "Normal-input sword capture PID $($process.Id), archive $archive"
if(-not $process.WaitForExit(240000)){Stop-Process -Id $process.Id -Force;throw 'Capture timeout; interrupted originals retained.'}
$process.Refresh();$index['exit_code']=$process.ExitCode
if($process.ExitCode -ne 0){throw 'Capture process failed; original evidence retained.'}
& $python -B -X utf8 (Join-Path $PSScriptRoot 'verify-native-sword-capture-pixels.py') --archive $archive --write-receipt
if($LASTEXITCODE -ne 0){throw 'Native viewport pixel verification failed.'}
& $python -B -X utf8 $checker --archive $archive
if($LASTEXITCODE -ne 0){throw 'Normal-input phase/presentation verification failed.'}
& $python -B -X utf8 (Join-Path $PSScriptRoot 'verify-ready-primary2-body-pixel-presence-v001.py') --archive $archive
if($LASTEXITCODE -ne 0){throw 'Visible Ready helmet presence failed; native originals retained.'}
$index['status']='native_pixels_real_input_and_visible_ready_head_passed_art_review_pending'
$index | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath $indexPath -Encoding utf8
Write-Output $archive
