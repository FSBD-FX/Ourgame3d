#include "DungeonStoneGuard.h"
namespace DungeonStoneGuard
{
FGuardKernel::FGuardKernel(std::uint64_t Id,double Time,FPoint P,int Face,FPolicy InPolicy)
{S.EntityId=Id;S.InitialTime=S.Time=Time;S.InitialPosition=S.Position=P;S.Facing=Face;Policy=InPolicy;Initialized=Id!=0;}
FDefinition FGuardKernel::Definition(){return {};}
FAttackDefinition FGuardKernel::AttackDefinition(EAttack K)
{
 if(K==EAttack::AxeSweep)return {"ENM-STN-003-A1",1,.5,.2,1.4,3.1,24,30,180,65,65};
 if(K==EAttack::Stomp)return {"ENM-STN-003-A2",.9,.45,.15,1.5,3,18,25,160,90,65};
 return {};
}
EAttack FGuardKernel::ChooseAttack(const FWorldInput&)const{return EAttack::None;}
FResult FGuardKernel::StepTo(double,const FWorldInput&,const std::vector<FIncomingHit>&){return {};}
FResult FGuardKernel::TryStartAttack(EAttack,const FWorldInput&){return {};}
FResult FGuardKernel::ApplyResolvedHit(std::uint64_t,double,double,const FWorldInput&){return {};}
FResult FGuardKernel::TryHit(const FTarget&){return {};}
bool FGuardKernel::BeginCombat(){return false;}
bool FGuardKernel::NotifyOtherAcceptedEnemiesCleared(){return false;}
FResult FGuardKernel::ClaimDeathReward(){return {};}
bool FGuardKernel::GroundBodyEnabled()const{return false;}
bool FGuardKernel::CounterWindowOpen()const{return false;}
bool FGuardKernel::ResetForNewEntity(std::uint64_t,double,FPoint,int){return false;}
}
