"""Versioned Root launcher adapter for an explicit final checker directory."""
from pathlib import Path
R=Path('F:/Ourgame/tools/scripts')
old=R/'prepare-hero-landing-priority-prereg-v001.py';new=R/'prepare-hero-landing-priority-prereg-v002.py';s=old.read_text(encoding='utf-8')
a="ap.add_argument('--checker-freeze',required=True);a=ap.parse_args();assert"
b="ap.add_argument('--checker-freeze',required=True);ap.add_argument('--checker-directory',required=True);a=ap.parse_args();T=Path(a.checker_directory).resolve();assert T.parent==C,'Checker directory must be one retained candidate child';assert"
assert s.count(a)==1;s=s.replace(a,b)
with new.open('x',encoding='utf-8') as f:f.write(s)
old=R/'run-hero-landing-priority-v001.ps1';new=R/'run-hero-landing-priority-v002.ps1';s=old.read_text(encoding='utf-8')
a="[Parameter(Mandatory=$true)][string]$CheckerFreeze)";b="[Parameter(Mandatory=$true)][string]$CheckerFreeze,[Parameter(Mandatory=$true)][string]$CheckerDirectory)";assert s.count(a)==1;s=s.replace(a,b)
a="$landingChecker=Join-Path $landingRoot 'source-assets/production/fairytale-hero-air-v001/landing-priority-observer-candidate-v001/tooling/verify-landing-priority-native-v001.py'";b="$landingChecker=Join-Path ([IO.Path]::GetFullPath($CheckerDirectory)) 'verify-landing-priority-native-v001.py'";assert s.count(a)==1;s=s.replace(a,b)
s=s.replace('prepare-hero-landing-priority-prereg-v001.py','prepare-hero-landing-priority-prereg-v002.py')
a='--checker-freeze $CheckerFreeze';assert s.count(a)==1;s=s.replace(a,a+' --checker-directory $CheckerDirectory')
with new.open('x',encoding='utf-8') as f:f.write(s)
print('NEW v002 Root tooling ready; old v001 unchanged; no prereg or UE yet')
