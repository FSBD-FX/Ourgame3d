#pragma once
#include <cstdint>
#include <vector>
namespace DungeonHeroLocomotionAudioV001 {
enum class ECue : std::uint8_t { StepLight01,StepLight02,TakeoffLight01,LandLight01,LandFirm01,DodgeShort01 };
struct FScope { std::uint64_t Owner=0,Room=0,Restart=0,Epoch=0; };
struct FEvent { std::uint64_t Sequence=0; FScope Scope; ECue Cue=ECue::StepLight01; double AtTime=0; std::uint64_t DodgeEventId=0,DodgeActionId=0,StepOrdinal=0; double FallSpeed=0,FallDistance=0; };
class FState {
public:
 bool Attach(FScope,double,std::uint64_t,double,double){return true;}
 void GroundDistance(FScope,double,double,double,bool,bool,bool,bool){}
 void AcceptedTakeoff(FScope,double,bool){}
 void AirMotion(FScope,double,double,double,double,double,bool){}
 void DodgeEvent(FScope,std::uint64_t,std::uint64_t,std::uint64_t,double,bool,bool){}
 std::vector<FEvent> Consume(double,bool){return {};}
};
}
