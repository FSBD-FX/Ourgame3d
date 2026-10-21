// Syntax-only compile of the exact candidate helper, not UE types or behavior.
#include <cmath>
#include <limits>
namespace Guard {struct FPoint {double X=0.,Y=0.,Z=0.;};}
struct FVec {double X=0.,Y=0.;FVec operator-(FVec P)const{return {X-P.X,Y-P.Y};}};
struct FDungeonKnightBody {};
struct FDungeonKnightFrame {};
FVec PositionAt(const FDungeonKnightBody&,const FDungeonKnightFrame&,double);
FVec XY(Guard::FPoint);
bool EllipseContact(FVec,FVec,double,double,double&,double&);
#include "exact-helper-v007.inl"
