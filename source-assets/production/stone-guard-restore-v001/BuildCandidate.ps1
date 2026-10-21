$ErrorActionPreference='Stop'
$guardRestoreCandidate=Join-Path $PSScriptRoot 'candidate-source'
$guardRestoreCpp=[System.IO.File]::ReadAllText((Join-Path $PSScriptRoot 'before-v124/DungeonStoneGuard.cpp'))
$guardRestoreCpp=$guardRestoreCpp.Replace('#include <limits>','#include <limits>'+"`n"+'#include <set>'+"`n"+'#include <utility>')
$guardRestoreHelper=[System.IO.File]::ReadAllText((Join-Path $PSScriptRoot 'validator-implementation-v001.inc'))
$guardRestoreMarker="}`n`nFGuardKernel::FGuardKernel"
if(-not $guardRestoreCpp.Contains($guardRestoreMarker)){throw 'Missing constructor insertion marker'}
$guardRestoreCpp=$guardRestoreCpp.Replace($guardRestoreMarker,$guardRestoreHelper+"`n}`n`nFGuardKernel::FGuardKernel")
$guardRestoreDefinition=@'
bool FGuardKernel::Restore(const FState& Saved)
{
    if(!Initialized||!Finite(Policy.ExtremelyCloseRadius)||Policy.ExtremelyCloseRadius<0
        ||Policy.ExtremelyCloseRadius>160||Saved.EntityId!=S.EntityId||Saved.InitialTime!=S.InitialTime
        ||!SamePoint(Saved.InitialPosition,S.InitialPosition)||!SavedStateValid(Saved))return false;
    FState Candidate=Saved;
    S=std::move(Candidate);
    return true;
}
'@
$guardRestoreTail=$guardRestoreCpp.LastIndexOf('}')
$guardRestoreCpp=$guardRestoreCpp.Substring(0,$guardRestoreTail)+$guardRestoreDefinition+"`n}"+$guardRestoreCpp.Substring($guardRestoreTail+1)
[System.IO.File]::WriteAllText((Join-Path $guardRestoreCandidate 'DungeonStoneGuard.cpp'),$guardRestoreCpp,[System.Text.UTF8Encoding]::new($false))
