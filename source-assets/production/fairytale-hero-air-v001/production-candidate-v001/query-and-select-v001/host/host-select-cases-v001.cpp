#include "../existing-source/DungeonFairytaleSwordAirV001.cpp"
#include <iostream>
#include <limits>

namespace A=DungeonFairytaleSwordAirV001;
int main()
{
 int Cases=0,Failed=0;
 FDungeonHeroAirSample Base;Base.Valid=true;Base.RunGuid.A=1;Base.OwnerId=1;Base.RoomInstanceId=1;Base.PresentationEpoch=0;Base.NativeTime=17.;Base.Facing=1.f;Base.GroundPosition={12.,-14.};
 struct Case{float H,V,Age;int Expected;};const float Inf=std::numeric_limits<float>::infinity();
 const Case Values[]={
  {0.f,630.f,.01f,0},{0.f,630.f,.12f,0},{.0000001f,630.f,0.f,0},
  {80.f,std::nextafter(315.f,Inf),.12f,0},{80.f,315.f,.12f,1},{80.f,std::nextafter(315.f,-Inf),.12f,1},
  {108.f,std::nextafter(90.f,Inf),.12f,1},{108.f,90.f,.12f,2},{110.25f,0.f,.12f,2},
  {108.f,-90.f,.12f,2},{108.f,std::nextafter(-90.f,Inf),.12f,2},{108.f,std::nextafter(-90.f,-Inf),.12f,3},
  {.00000001f,-630.f,.12f,3},{1.f,-450.f,.01f,3},
  {0.f,0.f,0.f,4},{0.f,0.f,std::nextafter(.06f,0.f),4},{0.f,0.f,.06f,5},{0.f,0.f,std::nextafter(.06f,Inf),5},
  {0.f,0.f,std::nextafter(.12f,0.f),5},{0.f,0.f,.12f,-1},{0.f,0.f,std::nextafter(.12f,Inf),-1},
  {0.f,-1.f,.01f,-1},{-1.f,630.f,.01f,-1},{0.f,0.f,-.01f,-1},{Inf,450.f,.12f,-1},{110.f,Inf,.12f,-1},
  {110.f,std::numeric_limits<float>::quiet_NaN(),.12f,-1}};
 const auto Check=[&](const FDungeonHeroAirSample& Q,int Expected)
 {
  ++Cases;A::FSelection Out;Out.Valid=true;Out.Frame=91;Out.Pose=A::EPose::Fall;FString Why;const bool Ok=A::Select(Q,Out,Why);
  const bool Pass=Expected>=0?Ok&&Out.Valid&&Out.Frame==Expected&&int(Out.Pose)==Expected+1&&Why.Value.empty():!Ok&&Out.Valid&&Out.Frame==91&&Out.Pose==A::EPose::Fall&&!Why.Value.empty();
  if(!Pass){++Failed;std::cerr<<"case "<<Cases<<" failed expected "<<Expected<<"\n";}
 };
 for(const auto& V:Values){auto Q=Base;Q.JumpHeight=V.H;Q.VerticalVelocity=V.V;Q.LandingVisualAge=V.Age;Check(Q,V.Expected);}
 Base.JumpHeight=54.f;Base.VerticalVelocity=450.f;
 for(int Domain=0;Domain<10;++Domain)
 {
  auto Q=Base;switch(Domain){case 0:Q.Valid=false;break;case 1:Q.RunGuid={};break;case 2:Q.OwnerId=0;break;case 3:Q.RoomInstanceId=0;break;
   case 4:Q.NativeTime=-1.;break;case 5:Q.NativeTime=std::numeric_limits<double>::infinity();break;case 6:Q.GroundPosition.X=std::numeric_limits<double>::quiet_NaN();break;
   case 7:Q.Facing=0.f;break;case 8:Q.Facing=2.f;break;case 9:Q.LandingVisualAge=std::numeric_limits<float>::quiet_NaN();break;}
  Check(Q,-1);
 }
 for(float Face:{-1.f,1.f}){auto Q=Base;Q.Facing=Face;Check(Q,0);}
 std::cout<<"{\"actual_select_cpp_cases\":"<<Cases<<",\"failed\":"<<Failed<<",\"scope\":\"standalone actual Select CPP with harness types; no UE/native-owner/resource/art claim\"}\n";
 return Failed?1:0;
}
