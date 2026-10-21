#pragma once
// Standalone value-seam harness types only. No native actor/resource/artist claim.
#include <cmath>
#include <cstdint>
#include <string>
#include <vector>
#define TEXT(S) S
struct FString{std::string Value;FString& operator=(const char* V){Value=V;return *this;}void Reset(){Value.clear();}};
struct FGuid{uint32_t A=0,B=0,C=0,D=0;bool IsValid()const{return A||B||C||D;}};
struct FVector2D{double X=0.,Y=0.;};
struct FMath{template<class T>static bool IsFinite(T V){return std::isfinite(V);}};
template<class T>using TArray=std::vector<T>;
class ADungeonGameMode;class ADungeonFighter;
struct FDungeonHeroAirSample
{
 bool Valid=false;FGuid RunGuid;uint64_t OwnerId=0,RoomInstanceId=0,PresentationEpoch=0;double NativeTime=0.;FVector2D GroundPosition;
 float Facing=0.f,JumpHeight=0.f,VerticalVelocity=0.f,LandingVisualAge=.12f;
};
namespace DungeonFairytaleSwordEquipmentBinding{struct FBinding{};}
namespace DungeonFairytaleSwordAirV001
{
enum class EPose:uint8_t{None,RiseEarly,RiseLate,Apex,Fall,LandingImpact,LandingSettle};
struct FSelection{bool Valid=false;EPose Pose=EPose::None;int32_t Frame=-1;};
struct FProfile{bool SourceClosureVerified=false;};struct FDrawContext{};struct FDrawPlan{};struct FResidentTexture{};
}
