#pragma once
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <utility>
#include <vector>

namespace DungeonExploration {
struct FPoint { double X=0, Y=0; };
struct FBounds { double MinX=0, MaxX=0, MinY=0, MaxY=0; };
struct FState {
 std::uint32_t Schema=1;
 FBounds Bounds;
 int RoomId=0;
 std::vector<double> Memory;
};
class FExploration {
 static constexpr double Grid=64;
 static constexpr std::size_t MaxVertices=1048576;
 FBounds Bounds;
 int CurrentRoom=0;
 std::vector<double> XVertices,YVertices,Memory;
 std::size_t Explored=0;
 static bool FinitePoint(FPoint P) { return std::isfinite(P.X)&&std::isfinite(P.Y); }
 bool Contains(FPoint P) const { return !Memory.empty()&&FinitePoint(P)&&P.X>=Bounds.MinX&&P.X<=Bounds.MaxX&&P.Y>=Bounds.MinY&&P.Y<=Bounds.MaxY; }
 static std::vector<double> Axis(double Min,double Max,std::size_t Cells) {
  std::vector<double> Result;Result.reserve(Cells+1);
  for(std::size_t I=0;I<Cells;++I)Result.push_back(Min+static_cast<double>(I)*Grid);
  Result.push_back(Max);return Result;
 }
 static std::size_t Cell(const std::vector<double>& Vertices,double At) {
  if(At==Vertices.back())return Vertices.size()-2;
  return static_cast<std::size_t>(std::upper_bound(Vertices.begin(),Vertices.end(),At)-Vertices.begin()-1);
 }
public:
 explicit FExploration(FBounds InBounds,int InRoomId) : Bounds(InBounds),CurrentRoom(InRoomId) {
  if(!std::isfinite(Bounds.MinX)||!std::isfinite(Bounds.MaxX)||!std::isfinite(Bounds.MinY)||!std::isfinite(Bounds.MaxY)||Bounds.MaxX<=Bounds.MinX||Bounds.MaxY<=Bounds.MinY)return;
  const double Width=Bounds.MaxX-Bounds.MinX,Height=Bounds.MaxY-Bounds.MinY;
  if(!std::isfinite(Width)||!std::isfinite(Height))return;
  const double NX=std::ceil(Width/Grid),NY=std::ceil(Height/Grid);
  // Reject unreasonable allocation before any floating-to-integer conversion.
  if(NX<1||NY<1||NX>=static_cast<double>(MaxVertices)||NY>=static_cast<double>(MaxVertices))return;
  const auto XCells=static_cast<std::size_t>(NX),YCells=static_cast<std::size_t>(NY);
  if((XCells+1)>MaxVertices/(YCells+1))return;
  XVertices=Axis(Bounds.MinX,Bounds.MaxX,XCells);YVertices=Axis(Bounds.MinY,Bounds.MaxY,YCells);
  Memory.resize(XVertices.size()*YVertices.size(),0);
 }
 void Reset(int InRoomId) { CurrentRoom=InRoomId;std::fill(Memory.begin(),Memory.end(),0);Explored=0; }
 void Reveal(FPoint Observer) {
  if(!Contains(Observer))return;
  for(std::size_t Y=0;Y<YVertices.size();++Y)for(std::size_t X=0;X<XVertices.size();++X){
   const double Value=VisibilityAt({XVertices[X],YVertices[Y]},Observer);
   auto& Stored=Memory[Y*XVertices.size()+X];
   if(Value>Stored){if(Stored==0)++Explored;Stored=Value;}
  }
 }
 double MemoryAt(FPoint P) const {
  if(!Contains(P))return 0;
  const auto X=Cell(XVertices,P.X),Y=Cell(YVertices,P.Y),Stride=XVertices.size();
  const double TX=(P.X-XVertices[X])/(XVertices[X+1]-XVertices[X]);
  const double TY=(P.Y-YVertices[Y])/(YVertices[Y+1]-YVertices[Y]);
  const double Lower=Memory[Y*Stride+X]*(1-TX)+Memory[Y*Stride+X+1]*TX;
  const double Upper=Memory[(Y+1)*Stride+X]*(1-TX)+Memory[(Y+1)*Stride+X+1]*TX;
  return std::clamp(Lower*(1-TY)+Upper*TY,0.,1.);
 }
 static double VisibilityAt(FPoint P,FPoint Observer) {
  if(!FinitePoint(P)||!FinitePoint(Observer))return 0;
  const double R=std::hypot((P.X-Observer.X)/620.,(P.Y-Observer.Y)/280.);
  if(!std::isfinite(R)||R>=1)return 0;
  if(R<=.68)return 1;
  const double T=(R-.68)/.32;
  return 1-T*T*(3-2*T);
 }
 std::size_t ExploredVertexCount() const { return Explored; }
 int RoomId() const { return CurrentRoom; }
 FState Capture() const { return {1,Bounds,CurrentRoom,Memory}; }
 bool Restore(const FState& Saved) {
  if(Saved.Schema!=1||Saved.RoomId<=0)return false;
  FExploration Candidate(Saved.Bounds,Saved.RoomId);
  if(Candidate.Memory.empty()||Saved.Memory.size()!=Candidate.Memory.size())return false;
  // Large finite origins can collapse a grid step after floating point rounding.
  const auto Increasing=[](const std::vector<double>& Vertices){
   for(std::size_t I=1;I<Vertices.size();++I)if(!(Vertices[I]>Vertices[I-1]))return false;
   return true;
  };
  if(!Increasing(Candidate.XVertices)||!Increasing(Candidate.YVertices))return false;
  for(double Value:Saved.Memory)if(!std::isfinite(Value)||Value<0||Value>1)return false;
  Candidate.Memory=Saved.Memory;
  Candidate.Explored=static_cast<std::size_t>(std::count_if(Saved.Memory.begin(),Saved.Memory.end(),[](double Value){return Value>0;}));
  *this=std::move(Candidate);return true;
 }
};
}
