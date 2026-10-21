#include "DungeonStoneGuardDriver.h"
#include "DungeonFighter.h"
FDungeonStoneGuardDriver::FDungeonStoneGuardDriver(ADungeonFighter* InOwner,uint64 Id,double Time)
    : Owner(InOwner),Kernel(Id,Time,InOwner?DungeonStoneGuard::FPoint{InOwner->GetGroundPosition().X,InOwner->GetGroundPosition().Y,0.}:DungeonStoneGuard::FPoint{}) {}
FDungeonGuardBatch FDungeonStoneGuardDriver::StepTo(double,const FDungeonKnightFrame&,const std::vector<DungeonStoneGuard::FIncomingHit>&){return {};}
FDungeonGuardBatch FDungeonStoneGuardDriver::ApplyResolvedHit(double,double,const FDungeonKnightFrame&){return {};}
DungeonStoneGuard::FSweepResult FDungeonStoneGuardDriver::QuerySweep(const DungeonStoneGuard::FSweepRequest&,const FDungeonKnightFrame&)const{return {false,0,DungeonStoneGuard::EStop::None};}
bool FDungeonStoneGuardDriver::BeginCombat(){return false;}
bool FDungeonStoneGuardDriver::NotifyOtherAcceptedEnemiesCleared(){return false;}
bool FDungeonStoneGuardDriver::ClaimDeathReward(){return false;}
