#include "production-source/DungeonGroundWalkPhase.h"
#include <limits>
#include <cstdio>

#define CHECK(X) do{++Checks;if(!(X)){std::printf("FAIL line %d\n",__LINE__);return 1;}}while(0)
int main()
{
    int Checks=0;using namespace DungeonGroundWalk;
    FPolicy P;P.CycleDistance=120.;P.CycleSeconds=.6;P.Durations={.1,.1,.1,.1,.1,.1};
    CHECK(Valid(P));
    FPolicy Bad=P;Bad.CycleDistance=0.;CHECK(!Valid(Bad));
    Bad=P;Bad.CycleSeconds=std::numeric_limits<double>::infinity();CHECK(!Valid(Bad));
    Bad=P;Bad.Durations[2]=-1.;CHECK(!Valid(Bad));
    Bad=P;Bad.Durations[2]=std::numeric_limits<double>::quiet_NaN();CHECK(!Valid(Bad));
    Bad=P;Bad.Durations[5]=.2;CHECK(!Valid(Bad));
    double Out=77.;CHECK(!Advance(-1.,1.,P,Out)&&Out==77.);
    CHECK(!Advance(1.,-1.,P,Out)&&Out==77.);
    CHECK(!Advance(1.,std::numeric_limits<double>::quiet_NaN(),P,Out)&&Out==77.);
    CHECK(!Advance(std::numeric_limits<double>::infinity(),1.,P,Out)&&Out==77.);
    CHECK(!Advance(1.,1.,Bad,Out)&&Out==77.);
    CHECK(Advance(.23,0.,P,Out)&&Out==.23);
    const double Huge=std::numeric_limits<double>::max();CHECK(Advance(Huge,0.,P,Out)&&Out==Huge);
    CHECK(Advance(Huge,Huge,P,Out)&&std::isfinite(Out)&&Out>=0.&&Out<P.CycleSeconds);
    double Whole=-1.,Split=-2.,First=-3.;
    CHECK(Advance(.05,91.125,P,Whole));
    CHECK(Advance(.05,91.125*.4,P,First)&&Advance(First,91.125*.6,P,Split)&&std::abs(Whole-Split)<1.e-12);
    CHECK(Advance(.05,P.CycleDistance,P,Out)&&std::abs(Out-.05)<1.e-12);
    int FrameIndex=99;CHECK(!Frame(-1.,P,FrameIndex)&&FrameIndex==99);
    CHECK(!Frame(std::numeric_limits<double>::quiet_NaN(),P,FrameIndex)&&FrameIndex==99);
    CHECK(Frame(Huge,P,FrameIndex)&&FrameIndex>=0&&FrameIndex<6);
    double Edge=0.;
    for(int I=0;I<6;++I)
    {
        CHECK(Frame(Edge+P.Durations[I]*.25,P,FrameIndex)&&FrameIndex==I);
        CHECK(Frame(Edge+P.Durations[I]*.75,P,FrameIndex)&&FrameIndex==I);
        Edge+=P.Durations[I];
    }
    CHECK(Frame(P.CycleSeconds,P,FrameIndex)&&FrameIndex==0);
    FPolicy Tiny=P;Tiny.CycleDistance=1.e-300;CHECK(Advance(Huge,Huge,Tiny,Out)&&std::isfinite(Out));
    std::printf("phase checks %d PASS; numeric fixture only; no UE/native/art claim\n",Checks);
    return 0;
}
