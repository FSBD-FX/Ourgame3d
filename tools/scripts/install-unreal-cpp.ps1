$ErrorActionPreference = 'Stop'
$installer = 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\setup.exe'
$installPath = 'C:\Program Files\Microsoft Visual Studio\2022\Community'
$compiler = Join-Path $installPath 'VC\Tools\MSVC\14.38.33130\bin\Hostx64\x64\cl.exe'
if (Test-Path -LiteralPath $compiler) { Write-Output "MSVC already available: $compiler"; return }
if (-not (Test-Path -LiteralPath $installer)) { throw "Visual Studio Installer is missing: $installer" }
$arguments = @('modify','--installPath',"`"$installPath`"",'--channelId','VisualStudio.17.Release','--add','Microsoft.VisualStudio.Component.VC.CoreIde','--add','Microsoft.VisualStudio.Component.VC.14.38.17.8.x86.x64','--passive','--norestart')
$process = Start-Process -FilePath $installer -ArgumentList $arguments -Verb RunAs -WindowStyle Hidden -PassThru
Write-Output "Visual Studio component installation launched (PID $($process.Id)); verify cl.exe and a real Unreal build after it finishes."
