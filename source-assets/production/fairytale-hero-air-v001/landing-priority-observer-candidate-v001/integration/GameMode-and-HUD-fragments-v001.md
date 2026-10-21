# Root integration fragments, source-only

Predecessor: actual CM52f906 Source296/Production1419/strict203. These are exact insertion/replacement suggestions, not permission to overwrite shared files. Root combines mutual exclusions with other NEW observers.

`DungeonGameMode.cpp` include list:
```cpp
#include "DungeonHeroLandingPriorityProbeV001.h"
```

Immediately after `Super::StartPlay();` in `ADungeonGameMode::StartPlay` (before pristine/lookdev/FirstBatch returns):
```cpp
if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroLandingPriorityProofV001")))
    GetWorld()->SpawnActor<ADungeonHeroLandingPriorityProbeV001>();
```

`DungeonHUD.cpp` existing BeginPlay ContentProof block must still call `InstallFastLosslessProofScreenshots();`. Insert the following immediately after that call and before AirProduction/AirBaseline/other proof dispatch. This excludes old ContentProbe and all existing HUD proof dispatch without removing capture installation:
```cpp
if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroLandingPriorityProofV001")))return;
```

The observer rejects all existing proof/visible-interface/range flags; Root must add this new flag to any other concurrently introduced observer exclusion list. No Fighter/gameplay/tests/profile changes are required. Source count increases only by the admitted header/cpp, subject to Root's actual combined inventory.

Keep the normal map URL `/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom`. The observer explicitly registers one display LGT source through the public API, then waits for actual selection before normal E; it never assigns equipped inventory or actor state. Keep the optional Knight diagnostic named explicitly in CLI/evidence.
