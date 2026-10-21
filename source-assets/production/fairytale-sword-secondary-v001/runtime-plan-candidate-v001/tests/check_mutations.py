from pathlib import Path
import subprocess,json,hashlib

HERE=Path(__file__).resolve().parents[1]
NAME='DungeonFairytaleSwordSecondaryPlanV001.h'
REAL=HERE/'projected/UnrealGame/Source/CodexDungeon'/NAME
original=REAL.read_text(encoding='utf-8')
mutations=[
 ('wrong-recovery-boundary','Recovery*(12./38.)','Recovery*(11./38.)'),
 ('skip-future-resource-check','for(bool Ready:Resident)if(!Ready)return false;','for(bool Ready:Resident)(void)Ready;'),
 ('ignore-explicit-optin','if(!C.OptIn||!C.EquipmentBound','if(false||!C.EquipmentBound'),
]
results=[]
for name,before,after in mutations:
 assert original.count(before)==1,(name,'nonunique mutation')
 target=HERE/'verification/mutations'/name;target.mkdir(parents=True,exist_ok=True)
 mutated=original.replace(before,after,1);(target/NAME).write_text(mutated,encoding='utf-8')
 script=target/'run.cmd'
 script.write_text('@echo off\ncall "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\Tools\\VsDevCmd.bat" -arch=x64 -host_arch=x64 >nul\n'
  'if errorlevel 1 exit /b %errorlevel%\n'
  f'cl /nologo /std:c++17 /EHsc /W4 /WX /I"{target.as_posix()}" /I"{(HERE/"projected/UnrealGame/Source/CodexDungeon").as_posix()}" /I"F:/Ourgame/UnrealGame/Source/CodexDungeon" tests/secondary_plan_tests.cpp /Fe:"{(target/"test.exe").as_posix()}" /Fo:"{(target/"test.obj").as_posix()}"\n'
  'if errorlevel 1 exit /b %errorlevel%\n'
  f'"{(target/"test.exe").as_posix()}"\nexit /b %errorlevel%\n',encoding='ascii')
 result=subprocess.run(['cmd.exe','/d','/c',str(script)],cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 output=result.stdout.decode('utf-8',errors='replace');(target/'result.txt').write_text(output,encoding='utf-8')
 assert result.returncode==1 and 'checks=135 failures=' in output and 'FAIL ' in output,(name,result.returncode,output)
 results.append(dict(mutation=name,exit_code=result.returncode,mutation_detected=True,source_sha256=hashlib.sha256((target/NAME).read_bytes()).hexdigest(),failures=[line for line in output.splitlines() if line.startswith('FAIL ')]))
assert REAL.read_text(encoding='utf-8')==original,'candidate mutated'
(HERE/'verification/mutation-results-v001.json').write_text(json.dumps(dict(schema='secondary8-host-mutation-evidence-v001',candidate_unchanged=True,ue_build_run=False,native_run=False,mutations=results),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=True,mutations_detected=len(results),candidate_unchanged=True)))
