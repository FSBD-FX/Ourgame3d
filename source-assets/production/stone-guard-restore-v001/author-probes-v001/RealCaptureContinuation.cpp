#include "StoneGuardRestoreCases.h"
#include <iostream>
using namespace DungeonStoneGuard;
using namespace StoneGuardRestoreCases;
int main()
{
 std::uint64_t Seed=0xa79d23f1;int Checked=0,Rejected=0;
 const auto Random=[&](){Seed^=Seed<<13;Seed^=Seed>>7;Seed^=Seed<<17;return Seed;};
 for(std::uint64_t Trial=1;Trial<=72;++Trial)
 {
  const double Birth=Trial%3==0?7.:0.;const FPoint Origin{double(int(Trial%7)*13-30),double(int(Trial%5)*11-30),double(Trial%3)};
  FGuardKernel K(8000+Trial,Birth,Origin,Trial%2?1:-1,FPolicy{double(Trial%161)});
  for(int Op=0;Op<160;++Op)
  {
   const auto Before=K.Capture();auto W=World(Origin.X+double(int(Random()%801)-400),Origin.Y+double(int(Random()%241)-120),Origin.Z);
   W.CanBeginWake=Random()%5!=0;W.HasTarget=Random()%6!=0;
   const auto Choice=Random()%8;
   if(Choice==0)K.BeginCombat();
   else if(Choice==1)K.NotifyOtherAcceptedEnemiesCleared();
   else if(Choice==2)K.TryStartAttack(K.ChooseAttack(W),W);
   else if(Choice==3)
   {
    auto P=Before.Action.LockedCenter;P.X+=Before.Action.Facing*50.;K.TryHit({100000+Random()%5,P});
   }
   else if(Choice==4&&Before.Phase!=EPhase::Dead)
   {
    const double Stagger=double(Random()%91);const double Loss=Random()%20==0?185.:double(Random()%5)*.25;
    K.ApplyResolvedHit(Before.LastDamageReceiptId+1+Random()%5,Loss,Stagger,W);
   }
   else if(Choice==5&&Before.Phase!=EPhase::Dead)
   {
    const double At=Before.Time+double(Random()%9)*.125;
    K.StepTo(At,W,{{Before.LastDamageReceiptId+3,At,double(Random()%3)*.25,double(Random()%60)},
       {Before.LastDamageReceiptId+9,At,0,double(Random()%30)}});
   }
   else if(Choice==6)K.ClaimDeathReward();
   else K.StepTo(Before.Time+double(Random()%17)*.125,W);
   const auto Saved=K.Capture();FGuardKernel R(Saved.EntityId,Birth,Origin,Saved.Facing,K.CapturePolicy());++Checked;
   if(!R.Restore(Saved)||Signature(R.Capture())!=Signature(Saved))
   {
    ++Rejected;std::cout<<"FAIL real capture trial="<<Trial<<" op="<<Op<<" choice="<<Choice<<'\n'<<Signature(Saved)<<'\n';
    if(Rejected>=5){std::cout<<"SUMMARY checked="<<Checked<<" rejected="<<Rejected<<'\n';return 1;}
   }
  }
 }
 // Huge same-cursor staggers are legal in separate, protected transactions.
 FGuardKernel Huge(9000);auto Far=World(900);
 const double Max=std::numeric_limits<double>::max();
 if(!Huge.ApplyResolvedHit(1,0,Max,Far).Accepted||!Huge.ApplyResolvedHit(2,0,Max,Far).Accepted
   ||!FGuardKernel(9000).Restore(Huge.Capture()))++Rejected;
 ++Checked;
 std::cout<<"SUMMARY checked="<<Checked<<" rejected="<<Rejected<<'\n';return Rejected?1:0;
}
