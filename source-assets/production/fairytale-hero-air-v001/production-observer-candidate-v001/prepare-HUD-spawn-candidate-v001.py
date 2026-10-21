from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent
SOURCE=OUT.parent/'production-candidate-v001/full-production-v001/existing-source/DungeonHUD.cpp'
b=SOURCE.read_bytes()
assert hashlib.sha256(b).hexdigest()=='6f86936c6a4c7b26afb812d585334a4a4bf471f0182295f94ae6374e9fb17bd5'
with (OUT/'before-source/DungeonHUD.cpp').open('xb') as f:f.write(b)
s=b.decode('utf-8-sig')
old='#include "DungeonHeroAirProbeV001.h"'
assert s.count(old)==1
s=s.replace(old,old+'\n#include "DungeonHeroAirProductionProbeV001.h"')
old='        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirProofV001")))GetWorld()->SpawnActor<ADungeonHeroAirProbeV001>();'
assert s.count(old)==1
new='''        const bool AirProduction=FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirProductionProofV001"));
        const bool AirBaseline=FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirProofV001"));
        if(AirProduction&&AirBaseline)
        {UE_LOG(LogTemp,Error,TEXT("Production Air and unchanged baseline observers are mutually exclusive"));FPlatformMisc::RequestExitWithStatus(false,3);return;}
        if(AirProduction)GetWorld()->SpawnActor<ADungeonHeroAirProductionProbeV001>();
        else if(AirBaseline)GetWorld()->SpawnActor<ADungeonHeroAirProbeV001>();'''
s=s.replace(old,new)
with (OUT/'new-source/DungeonHUD.cpp').open('x',encoding='utf-8',newline='\n') as f:f.write(s)
data={'future_full_production_HUD':{'path':SOURCE.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},
      'changes':['include ProductionProbe','mutually-exclusive explicit new production flag before old unchanged baseline branch'],'actual_HUD_changed':False}
with (OUT/'HUD-narrow-spawn-input-and-scope-v001.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2);f.write('\n')
print(json.dumps(data,indent=2))
