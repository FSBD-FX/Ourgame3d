#if defined(DUNGEON_EXPLORATION_STANDALONE)
#include "../DungeonExploration.h"
#include <cmath>
#include <iostream>
#include <limits>
using namespace DungeonExploration;
namespace {
int Checks=0, Failures=0;
void Check(bool Pass,const char* Name) { ++Checks;if(!Pass){++Failures;std::cout<<"FAIL "<<Name<<'\n';} }
bool Near(double A,double B) { return std::abs(A-B)<1e-10; }
void Visibility() {
 Check(Near(FExploration::VisibilityAt({0,0},{0,0}),1),"observer center fully visible");
 Check(Near(FExploration::VisibilityAt({421.6,0},{0,0}),1),"inner ellipse remains fully visible");
 Check(Near(FExploration::VisibilityAt({520.8,0},{0,0}),.5)&&Near(FExploration::VisibilityAt({0,235.2},{0,0}),.5),"horizontal and vertical midpoint fade is half");
 Check(Near(FExploration::VisibilityAt({620,0},{0,0}),0)&&Near(FExploration::VisibilityAt({0,280},{0,0}),0),"outer ellipse excludes visibility");
 Check(Near(FExploration::VisibilityAt({372,224},{0,0}),0),"ellipse diagonal outer boundary excludes visibility");
 Check(Near(FExploration::VisibilityAt({10-520.8,-40},{10,-40}),.5),"translated left direction shares same fade");
}
void Exploration() {
 FExploration E({-256,2304,-640,640},3);
 Check(E.RoomId()==3&&E.ExploredVertexCount()==0&&E.MemoryAt({0,0})==0&&E.MemoryAt({1792,0})==0,"new room starts wholly unexplored");
 E.Reveal({0,0});const auto FirstCount=E.ExploredVertexCount();const auto FirstEdge=E.MemoryAt({512,0});
 Check(FirstCount>0&&Near(E.MemoryAt({0,0}),1)&&E.MemoryAt({1024,0})==0,"start reveals local area while distant region stays unknown");
 E.Reveal({0,0});Check(E.ExploredVertexCount()==FirstCount&&E.MemoryAt({512,0})==FirstEdge,"identical reveal is idempotent");
 E.Reveal({1024,0});
 Check(E.ExploredVertexCount()>FirstCount&&Near(E.MemoryAt({1024,0}),1)&&Near(E.MemoryAt({0,0}),1)&&E.MemoryAt({1792,0})==0,"moving reveals new area while retaining old area");
 Check(E.MemoryAt({512,0})>=FirstEdge,"soft explored memory never decreases");
 E.Reveal({0,0});Check(Near(E.MemoryAt({1024,0}),1),"returning does not clear distant explored memory");
 E.Reset(4);Check(E.RoomId()==4&&E.ExploredVertexCount()==0&&E.MemoryAt({0,0})==0&&E.MemoryAt({1024,0})==0,"room reset clears prior memory and changes identity");
 E.Reveal({0,0});E.Reset(4);Check(E.ExploredVertexCount()==0&&E.MemoryAt({0,0})==0,"explicit same-room reset also clears memory");
}
void InterpolationAndBoundaries() {
 FExploration E({0,128,0,320},9);E.Reveal({0,20.8});
 // At corners (0,256)/(64,256)/(0,320)/(64,320): .5/.47039586917282794/0/0.
 // Their equally weighted midpoint is .24259896729320699, derived independently.
 Check(Near(E.MemoryAt({32,288}),.24259896729320699),"memory uses four-corner bilinear interpolation instead of nearest cell");
 Check(Near(E.MemoryAt({0,256}),.5)&&E.MemoryAt({0,320})==0,"exact grid vertices retain their own memory");
 FExploration Short({0,70,0,300},10);Short.Reveal({70,300});
 Check(Near(Short.MemoryAt({70,300}),1)&&Short.MemoryAt({70.001,300})==0,"short final grid cell includes max room boundary only");
}
void InvalidInputs() {
 const double NaN=std::numeric_limits<double>::quiet_NaN(),Inf=std::numeric_limits<double>::infinity();
 FExploration E({0,256,0,256},1);E.Reveal({128,128});const auto Count=E.ExploredVertexCount();const auto Before=E.MemoryAt({128,128});
 for(const auto P:{FPoint{NaN,0},FPoint{0,Inf},FPoint{-1,128},FPoint{257,128}})E.Reveal(P);
 Check(E.ExploredVertexCount()==Count&&E.MemoryAt({128,128})==Before,"out of room and nonfinite observers cannot contaminate memory");
 Check(E.MemoryAt({NaN,0})==0&&E.MemoryAt({0,Inf})==0&&E.MemoryAt({-1,128})==0,"invalid or out of room memory queries return zero");
 Check(FExploration::VisibilityAt({NaN,0},{0,0})==0&&FExploration::VisibilityAt({0,0},{Inf,0})==0,"nonfinite visibility input is stable zero");
 FExploration Bad({0,0,0,256},11);Bad.Reveal({0,0});Bad.Reset(12);
 Check(Bad.RoomId()==12&&Bad.ExploredVertexCount()==0&&Bad.MemoryAt({0,0})==0,"degenerate bounds remain safely empty");
}
}
int main() { Visibility();Exploration();InterpolationAndBoundaries();InvalidInputs();std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<'\n';return Failures?1:0; }
#endif
