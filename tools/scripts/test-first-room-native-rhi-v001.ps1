param([string]$EngineRoot='G:\UE_5.5')
$ErrorActionPreference='Stop'
$airWorkspace='F:\Ourgame'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Sequential native RHI test requires no UE/UBT process'}
$airRun=Get-Date -Format 'yyyyMMdd-HHmmss'
$airLog=Join-Path $airWorkspace ("UnrealGame\Saved\Bootstrap\first-room-native-rhi-tests-$airRun.log")
$airReport=Join-Path $airWorkspace ("UnrealGame\Saved\Automation\FirstRoomNativeRHI-$airRun")
$airArguments=@(('"{0}"' -f (Join-Path $airWorkspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-d3d11','-nop4','-nosplash','-NoLiveCoding','-ExecCmds="Automation RunTests CodexDungeon"','-TestExit="Automation Test Queue Empty"',('-ReportExportPath="{0}"' -f $airReport),('-abslog="{0}"' -f $airLog))
$airProcess=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe') -ArgumentList $airArguments -WindowStyle Hidden -PassThru
Write-Output ('UE native D3D11 full203 PID '+$airProcess.Id)
$airProcess.WaitForExit()
$airIndex=Join-Path $airReport 'index.json'
if($airProcess.ExitCode -ne 0 -or -not(Test-Path -LiteralPath $airIndex)){throw ('Native RHI automation failed/missing report: '+$airLog)}
$airResult=Get-Content -LiteralPath $airIndex -Raw | ConvertFrom-Json
if($airResult.succeeded -ne 203 -or $airResult.failed -ne 0 -or $airResult.notRun -ne 0 -or $airResult.succeededWithWarnings -ne 0 -or $airResult.inProcess -ne 0){throw ('Native RHI203 not all GREEN: '+$airIndex)}
if(-not(Select-String -LiteralPath $airLog -Pattern 'LogD3D11RHI' -Quiet)){throw 'Actual D3D11 initialization not recorded'}
Write-Output ('Native D3D11 full203 passed: '+$airIndex)
