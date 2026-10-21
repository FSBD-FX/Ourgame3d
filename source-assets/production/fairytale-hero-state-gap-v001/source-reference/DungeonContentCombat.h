#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <utility>
#include <cstdint>
#include <vector>
namespace DungeonContentCombat {
enum class EWeapon { SWD001, GSW001, SPR001, XBW001, STF001 };
enum class EArmor { None, LGT001, MED001, HVY001, ROB001 };
enum class EShape { ForwardEllipse, ForwardRectangle, Projectile, GroundRectangle };
enum class EPhase { Idle, Windup, Active, Recovery };
enum class EEventKind { Started, Locked, ActiveWindow, Completed, Interrupted };
enum class EInterruptReason { ReverseBeforeLock, PoiseBreak, Death, SwitchWeapon, ExclusiveAction };
struct FStageDefinition { double Windup=0,Active=0,Recovery=0,Cycle=0,ActiveEnd=0,Damage=0,Stagger=0,MinRange=0,Range=0,Depth=0,MoveMultiplier=1; EShape Shape=EShape::ForwardRectangle; };
struct FSkillDefinition { const char* Name=""; FStageDefinition Timeline; double Cooldown=0,AmmoCost=0,FocusCost=0; std::array<double,3> SubhitTimes{},SubhitDamage{},SubhitStagger{}; std::array<double,3> SubhitDurations{}; std::uint32_t SubhitCount=0; double ForwardStep=0,ProjectileSpeed=0,SecondTargetRatio=1,BurnDps=0,BurnDuration=0; std::uint32_t MaxTargets=1; };
struct FWeaponDefinition { const char* ContentId=""; std::array<FStageDefinition,3> Primary{}; bool HasCombo=false; double Magazine=0,Reload=0,AmmoPerPrimary=0,FocusPerPrimary=0,ProjectileSpeed=0; FSkillDefinition Skill; };
struct FArmorDefinition { const char* ContentId=""; double Armor=0,Ward=0,MoveMultiplier=1,PoiseBonus=0,FocusRegen=12,FocusDelay=1; };
// Authoring uses integer milliseconds; simulation deadlines stay unrounded absolute doubles.
inline FStageDefinition MakeStage(std::uint32_t W,std::uint32_t A,std::uint32_t R,double Damage,double Stagger,double Min,double Max,double Depth,double Move,EShape Shape){
 FStageDefinition D;D.Windup=W/1000.;D.Active=A/1000.;D.Recovery=R/1000.;D.Cycle=(W+A+R)/1000.;D.ActiveEnd=(W+A)/1000.;D.Damage=Damage;D.Stagger=Stagger;D.MinRange=Min;D.Range=Max;D.Depth=Depth;D.MoveMultiplier=Move;D.Shape=Shape;return D;
}
inline const FWeaponDefinition* GetWeaponDefinition(EWeapon Weapon){
 static const std::array<FWeaponDefinition,5> Definitions=[](){
  std::array<FWeaponDefinition,5> D{};
  D[0].ContentId="WPN-SWD-001";D[0].HasCombo=true;
  D[0].Primary={MakeStage(170,120,310,26,16,0,135,46,.5,EShape::ForwardEllipse),MakeStage(150,120,270,24,14,0,135,46,.5,EShape::ForwardEllipse),MakeStage(220,120,320,28,18,0,145,46,.5,EShape::ForwardEllipse)};
  D[0].Skill.Name="advance_slash";D[0].Skill.Timeline=MakeStage(200,100,380,32,22,0,145,40,.5,EShape::ForwardEllipse);D[0].Skill.Cooldown=4;D[0].Skill.SubhitCount=1;D[0].Skill.SubhitTimes={.20,0,0};D[0].Skill.SubhitDurations={.10,0,0};D[0].Skill.SubhitDamage={32,0,0};D[0].Skill.SubhitStagger={22,0,0};D[0].Skill.ForwardStep=30;D[0].Skill.MaxTargets=0;
  D[1].ContentId="WPN-GSW-001";D[1].HasCombo=true;
  D[1].Primary={MakeStage(450,140,600,46,42,0,165,36,.16,EShape::ForwardRectangle),MakeStage(400,140,560,42,36,0,165,36,.16,EShape::ForwardRectangle),MakeStage(530,140,610,50,48,0,175,36,.16,EShape::ForwardRectangle)};
  D[1].Skill.Name="heavy_press";D[1].Skill.Timeline=MakeStage(680,160,850,68,65,0,175,48,.16,EShape::ForwardRectangle);D[1].Skill.Cooldown=8;D[1].Skill.SubhitCount=1;D[1].Skill.SubhitTimes={.68,0,0};D[1].Skill.SubhitDurations={.16,0,0};D[1].Skill.SubhitDamage={68,0,0};D[1].Skill.SubhitStagger={65,0,0};D[1].Skill.MaxTargets=0;
  D[2].ContentId="WPN-SPR-001";D[2].HasCombo=true;
  D[2].Primary={MakeStage(110,70,240,21,10,45,230,18,.6,EShape::ForwardRectangle),MakeStage(90,70,220,19,8,45,230,18,.6,EShape::ForwardRectangle),MakeStage(150,70,240,23,12,45,230,18,.6,EShape::ForwardRectangle)};
  D[2].Skill.Name="triple_thrust";D[2].Skill.Timeline=MakeStage(180,270,360,36,18,45,240,16,.6,EShape::ForwardRectangle);D[2].Skill.Cooldown=4.5;D[2].Skill.SubhitCount=3;D[2].Skill.SubhitTimes={.18,.28,.38};D[2].Skill.SubhitDurations={.04,.04,.04};D[2].Skill.SubhitDamage={12,12,12};D[2].Skill.SubhitStagger={6,6,6};
  D[3].ContentId="WPN-XBW-001";D[3].Primary[0]=MakeStage(160,40,480,34,12,0,420,14,.45,EShape::Projectile);D[3].Magazine=1;D[3].Reload=1.1;D[3].AmmoPerPrimary=1;D[3].ProjectileSpeed=950;
  D[3].Skill.Name="piercing_bolt";D[3].Skill.Timeline=MakeStage(550,50,550,50,24,0,520,12,.45,EShape::Projectile);D[3].Skill.Cooldown=6;D[3].Skill.AmmoCost=1;D[3].Skill.ProjectileSpeed=1100;D[3].Skill.SubhitCount=1;D[3].Skill.SubhitTimes={.55,0,0};D[3].Skill.SubhitDurations={.05,0,0};D[3].Skill.SubhitDamage={50,0,0};D[3].Skill.SubhitStagger={24,0,0};D[3].Skill.MaxTargets=2;D[3].Skill.SecondTargetRatio=.6;
  D[4].ContentId="WPN-STF-001";D[4].Primary[0]=MakeStage(220,50,400,24,8,0,360,20,.5,EShape::Projectile);D[4].FocusPerPrimary=10;D[4].ProjectileSpeed=600;
  D[4].Skill.Name="coal_line";D[4].Skill.Timeline=MakeStage(450,120,450,18,6,0,240,35,.5,EShape::GroundRectangle);D[4].Skill.Cooldown=7;D[4].Skill.FocusCost=24;D[4].Skill.SubhitCount=1;D[4].Skill.SubhitTimes={.45,0,0};D[4].Skill.SubhitDurations={.12,0,0};D[4].Skill.SubhitDamage={18,0,0};D[4].Skill.SubhitStagger={6,0,0};D[4].Skill.BurnDps=2;D[4].Skill.BurnDuration=3;D[4].Skill.MaxTargets=0;
  return D;
 }();
 const auto I=static_cast<unsigned>(Weapon);return I<Definitions.size()?&Definitions[I]:nullptr;
}
inline const FArmorDefinition* GetArmorDefinition(EArmor Armor){
 static const std::array<FArmorDefinition,5> Definitions={FArmorDefinition{"",0,0,1,0,12,1},FArmorDefinition{"ARM-LGT-001",14,12,1.08,0,12,1},FArmorDefinition{"ARM-MED-001",32,18,1,10,12,1},FArmorDefinition{"ARM-HVY-001",85,12,.84,40,12,1},FArmorDefinition{"ARM-ROB-001",6,50,1,0,16,1}};
 const auto I=static_cast<unsigned>(Armor);return I<Definitions.size()?&Definitions[I]:nullptr;
}
struct FAttackContext { double Facing=1,ActionSpeedPct=0,DamagePct=0,StaggerPct=0,ReachPct=0,CritMultiplier=1.5; bool Grounded=true,Critical=false,CanStart=true; };
struct FActionState { bool Active=false,Locked=false,StartedAirborne=false,WindowIssued=false; EPhase Phase=EPhase::Idle; EWeapon Weapon=EWeapon::SWD001; std::uint64_t WeaponInstanceId=1,AttackId=0; std::uint32_t Stage=0; double Facing=1,Start=0,LockTime=0,ActiveStart=0,ActiveEnd=0,End=0,Damage=0,Stagger=0,MinRange=0,Range=0,Depth=0,MoveMultiplier=1,ActionSpeedPct=0; EShape Shape=EShape::ForwardRectangle; bool Critical=false; double CritMultiplier=1.5; };
struct FCombatEvent { std::uint64_t EventId=0,AttackId=0; std::uint32_t Stage=0,SubhitId=0; EEventKind Kind=EEventKind::Started; double AtTime=0,WindowEnd=0; FActionState Action; };
struct FWindowReceipt { std::uint64_t AttackId=0,EventId=0; std::uint32_t SubhitId=0; double Start=0,End=0; FActionState FrozenAction; };
struct FHitReceipt { std::uint64_t AttackId=0,TargetId=0; std::uint32_t SubhitId=0; };
struct FCombatState { std::uint32_t Version=3; EWeapon Weapon=EWeapon::SWD001; std::uint64_t WeaponInstanceId=1,NextAttackId=1,NextEventId=1; double Time=0,ComboExpiry=0; std::uint32_t NextComboStage=0; bool ComboReady=false,PendingPrimary=false,Grounded=true,AirPrimarySpent=false,Dead=false; FActionState Action; std::vector<FWindowReceipt> IssuedWindows; std::vector<FHitReceipt> HitReceipts; std::vector<FCombatEvent> PendingEvents; };
// Actor-local IDs must be combined with the stable owner ID by the UE adapter.
// StepTo is the only clock mutation. PressPrimary must follow StepTo at exactly the same time.
// The supplied context is constant over the stepped interval; split at external stat/ground changes.
class FCombatKernel {
 FCombatState S;
 static bool Finite(double V){return std::isfinite(V);}
 static bool ValidContext(const FAttackContext& C){return Finite(C.Facing)&&C.Facing!=0&&Finite(C.ActionSpeedPct)&&Finite(C.DamagePct)&&Finite(C.StaggerPct)&&Finite(C.ReachPct)&&Finite(C.CritMultiplier);}
 void ResetChain(){S.PendingPrimary=false;S.ComboReady=false;S.NextComboStage=0;S.ComboExpiry=0;}
 void ExpireChain(){if(S.ComboReady&&S.Time>=S.ComboExpiry)ResetChain();}
 void Emit(EEventKind Kind,double At){FCombatEvent E;E.EventId=S.NextEventId++;E.AttackId=S.Action.AttackId;E.Stage=S.Action.Stage;E.Kind=Kind;E.AtTime=At;E.WindowEnd=S.Action.ActiveEnd;E.Action=S.Action;S.PendingEvents.push_back(E);if(Kind==EEventKind::ActiveWindow)S.IssuedWindows.push_back({E.AttackId,E.EventId,0,At,E.WindowEnd,E.Action});}
 void SetPhase(){if(!S.Action.Active)S.Action.Phase=EPhase::Idle;else if(S.Time<S.Action.ActiveStart)S.Action.Phase=EPhase::Windup;else if(S.Time<S.Action.ActiveEnd)S.Action.Phase=EPhase::Active;else S.Action.Phase=EPhase::Recovery;}
 bool Start(double At,std::uint32_t Stage,const FAttackContext& C){
  const auto* W=GetWeaponDefinition(S.Weapon);if(!W||!W->HasCombo||Stage>=3||S.Dead||!C.CanStart||!ValidContext(C)||S.NextAttackId==std::numeric_limits<std::uint64_t>::max()||S.NextEventId>std::numeric_limits<std::uint64_t>::max()-8)return false;
  const auto& D=W->Primary[Stage];FActionState A;A.Active=true;A.Phase=EPhase::Windup;A.Weapon=S.Weapon;A.WeaponInstanceId=S.WeaponInstanceId;A.AttackId=S.NextAttackId++;A.Stage=Stage;A.Facing=C.Facing>0?1:-1;A.StartedAirborne=!C.Grounded;A.Start=At;A.ActionSpeedPct=std::clamp(C.ActionSpeedPct,-20.,20.);const double Speed=1+A.ActionSpeedPct/100.;A.LockTime=At+D.Windup/Speed*.4;A.ActiveStart=At+D.Windup/Speed;A.ActiveEnd=At+D.ActiveEnd/Speed;A.End=At+D.Cycle/Speed;A.Damage=D.Damage;A.Stagger=D.Stagger;A.MinRange=D.MinRange;A.Range=D.Range;A.Depth=D.Depth;A.MoveMultiplier=D.MoveMultiplier;A.Shape=D.Shape;S.Action=A;S.PendingPrimary=false;S.ComboReady=false;S.NextComboStage=Stage;S.ComboExpiry=0;if(A.StartedAirborne)S.AirPrimarySpent=true;Emit(EEventKind::Started,At);return true;
 }
 void Lock(const FAttackContext& C){
  auto& A=S.Action;const auto& D=GetWeaponDefinition(A.Weapon)->Primary[A.Stage];A.Locked=true;A.Facing=C.Facing>0?1:-1;A.Critical=C.Critical;A.CritMultiplier=std::clamp(C.CritMultiplier,1.,2.);A.Damage=D.Damage*(1+std::clamp(C.DamagePct,-30.,50.)/100.)*(A.Critical?A.CritMultiplier:1.);A.Stagger=D.Stagger*(1+std::clamp(C.StaggerPct,-25.,25.)/100.);A.Range=D.Range*(1+std::clamp(C.ReachPct,-15.,15.)/100.);Emit(EEventKind::Locked,S.Time);
 }
 static bool ValidActionData(const FActionState& A){
  const auto* W=GetWeaponDefinition(A.Weapon);if(!W||!W->HasCombo||A.WeaponInstanceId==0||A.AttackId==0||A.Stage>=3||static_cast<unsigned>(A.Phase)>static_cast<unsigned>(EPhase::Recovery))return false;
  for(double N:{A.Facing,A.Start,A.LockTime,A.ActiveStart,A.ActiveEnd,A.End,A.Damage,A.Stagger,A.MinRange,A.Range,A.Depth,A.MoveMultiplier,A.ActionSpeedPct,A.CritMultiplier})if(!Finite(N))return false;
  if((A.Facing!=1&&A.Facing!=-1)||A.Start<0||A.ActionSpeedPct < -20||A.ActionSpeedPct>20||A.CritMultiplier<1||A.CritMultiplier>2||(A.StartedAirborne&&A.Stage!=0)||(A.WindowIssued&&!A.Locked)||(A.Active==(A.Phase==EPhase::Idle)))return false;
  const auto& D=W->Primary[A.Stage];const double Speed=1+A.ActionSpeedPct/100.;
  if(A.LockTime!=A.Start+D.Windup/Speed*.4||A.ActiveStart!=A.Start+D.Windup/Speed||A.ActiveEnd!=A.Start+D.ActiveEnd/Speed||A.End!=A.Start+D.Cycle/Speed||!(A.Start<A.LockTime&&A.LockTime<A.ActiveStart&&A.ActiveStart<A.ActiveEnd&&A.ActiveEnd<A.End))return false;
  if(A.Shape!=D.Shape||A.MinRange!=D.MinRange||A.Depth!=D.Depth||A.MoveMultiplier!=D.MoveMultiplier)return false;
  if(!A.Locked)return !A.Critical&&A.CritMultiplier==1.5&&A.Damage==D.Damage&&A.Stagger==D.Stagger&&A.Range==D.Range;
  const double Crit=A.Critical?A.CritMultiplier:1.;return A.Damage>=D.Damage*(1-30./100.)*Crit&&A.Damage<=D.Damage*(1+50./100.)*Crit&&A.Stagger>=D.Stagger*(1-25./100.)&&A.Stagger<=D.Stagger*(1+25./100.)&&A.Range>=D.Range*(1-15./100.)&&A.Range<=D.Range*(1+15./100.);
 }
 static bool SameAttackFacts(const FActionState& A,const FActionState& B){
  if(A.Weapon!=B.Weapon||A.WeaponInstanceId!=B.WeaponInstanceId||A.AttackId!=B.AttackId||A.Stage!=B.Stage||A.StartedAirborne!=B.StartedAirborne||A.Start!=B.Start||A.LockTime!=B.LockTime||A.ActiveStart!=B.ActiveStart||A.ActiveEnd!=B.ActiveEnd||A.End!=B.End||A.ActionSpeedPct!=B.ActionSpeedPct||A.MinRange!=B.MinRange||A.Depth!=B.Depth||A.MoveMultiplier!=B.MoveMultiplier||A.Shape!=B.Shape)return false;
  // Started is pre-lock: direction and damage may legitimately change at the lock event.
  return !A.Locked||!B.Locked||(A.Facing==B.Facing&&A.Damage==B.Damage&&A.Stagger==B.Stagger&&A.Range==B.Range&&A.Critical==B.Critical&&A.CritMultiplier==B.CritMultiplier);
 }
 static bool ValidEventAction(const FCombatEvent& E){
  const auto& A=E.Action;if(!ValidActionData(A)||A.AttackId!=E.AttackId||A.Stage!=E.Stage||E.SubhitId!=0||!Finite(E.WindowEnd)||E.WindowEnd!=A.ActiveEnd||E.AtTime<A.Start)return false;
  if(A.Active){const auto P=E.AtTime<A.ActiveStart?EPhase::Windup:E.AtTime<A.ActiveEnd?EPhase::Active:EPhase::Recovery;if(E.AtTime>=A.End||A.Phase!=P||A.Locked!=(E.AtTime>=A.LockTime)||A.WindowIssued!=(E.AtTime>=A.ActiveStart))return false;}
  switch(E.Kind){
   case EEventKind::Started:return A.Active&&!A.Locked&&!A.WindowIssued&&E.AtTime==A.Start;
   case EEventKind::Locked:return A.Active&&A.Locked&&!A.WindowIssued&&E.AtTime==A.LockTime;
   case EEventKind::ActiveWindow:return A.Active&&A.Locked&&A.WindowIssued&&E.AtTime==A.ActiveStart;
   case EEventKind::Completed:return !A.Active&&A.Locked&&A.WindowIssued&&E.AtTime==A.End;
   case EEventKind::Interrupted:return A.Active;
  }return false;
 }
 static bool ValidWindowReceipt(const FWindowReceipt& W){
  FCombatEvent E;E.EventId=W.EventId;E.AttackId=W.AttackId;E.Stage=W.FrozenAction.Stage;E.SubhitId=W.SubhitId;E.Kind=EEventKind::ActiveWindow;E.AtTime=W.Start;E.WindowEnd=W.End;E.Action=W.FrozenAction;return ValidEventAction(E);
 }
 static bool ValidState(const FCombatState& V){
  if(V.Version!=3||!GetWeaponDefinition(V.Weapon)||V.WeaponInstanceId==0||!Finite(V.Time)||V.Time<0||!Finite(V.ComboExpiry)||V.NextComboStage>=3||V.NextAttackId==0||V.NextEventId==0||V.NextEventId>std::numeric_limits<std::uint64_t>::max()-8)return false;
  if(V.Dead&&(V.Action.Active||V.PendingPrimary||V.ComboReady))return false;
  if(V.ComboReady&&(V.Action.Active||V.ComboExpiry<=V.Time))return false;
  const auto& A=V.Action;
  if((A.AttackId!=0&&A.AttackId>=V.NextAttackId)||static_cast<unsigned>(A.Shape)>static_cast<unsigned>(EShape::GroundRectangle))return false;
  if(A.AttackId!=0&&(!ValidActionData(A)||A.Start>V.Time))return false;
  if(A.Active){
   if(!GetWeaponDefinition(A.Weapon)||!GetWeaponDefinition(A.Weapon)->HasCombo||A.Weapon!=V.Weapon||A.WeaponInstanceId!=V.WeaponInstanceId||A.AttackId==0||A.AttackId>=V.NextAttackId||A.Stage>=3)return false;
   for(double N:{A.Facing,A.Start,A.LockTime,A.ActiveStart,A.ActiveEnd,A.End,A.Damage,A.Stagger,A.MinRange,A.Range,A.Depth,A.MoveMultiplier,A.ActionSpeedPct,A.CritMultiplier})if(!Finite(N))return false;
   if((A.Facing!=1&&A.Facing!=-1)||A.Start<0||A.Start>V.Time||!(A.Start<A.LockTime&&A.LockTime<A.ActiveStart&&A.ActiveStart<A.ActiveEnd&&A.ActiveEnd<A.End)||V.Time>=A.End||A.Damage<0||A.Stagger<0||A.MinRange<0||A.Range<A.MinRange||A.Depth<=0)return false;
   if(A.Locked!=(V.Time>=A.LockTime)||A.WindowIssued!=(V.Time>=A.ActiveStart))return false;
   const auto P=V.Time<A.ActiveStart?EPhase::Windup:V.Time<A.ActiveEnd?EPhase::Active:EPhase::Recovery;if(A.Phase!=P)return false;
  }
  if(V.PendingPrimary&&(!A.Active||A.StartedAirborne||!V.Grounded||V.Time<A.End-.12||V.Time<A.ActiveEnd))return false;
  for(std::size_t I=0;I<V.IssuedWindows.size();++I){const auto& W=V.IssuedWindows[I];if(W.AttackId==0||W.AttackId>=V.NextAttackId||W.EventId<3||W.EventId>=V.NextEventId||W.SubhitId!=0||!Finite(W.Start)||!Finite(W.End)||W.Start<0||W.Start>V.Time||W.End<=W.Start||!ValidWindowReceipt(W))return false;for(std::size_t J=0;J<I;++J)if(V.IssuedWindows[J].EventId==W.EventId||(V.IssuedWindows[J].AttackId==W.AttackId&&V.IssuedWindows[J].SubhitId==W.SubhitId))return false;}
  if(A.AttackId!=0){bool Found=false;for(const auto& W:V.IssuedWindows)if(W.AttackId==A.AttackId){if(W.SubhitId!=0||W.Start!=A.ActiveStart||W.End!=A.ActiveEnd||!SameAttackFacts(A,W.FrozenAction))return false;Found=true;}if(Found!=A.WindowIssued)return false;}
  for(std::size_t I=0;I<V.HitReceipts.size();++I){const auto& H=V.HitReceipts[I];if(H.TargetId==0)return false;bool Found=false;for(const auto& W:V.IssuedWindows)Found|=W.AttackId==H.AttackId&&W.SubhitId==H.SubhitId;if(!Found)return false;for(std::size_t J=0;J<I;++J)if(V.HitReceipts[J].AttackId==H.AttackId&&V.HitReceipts[J].SubhitId==H.SubhitId&&V.HitReceipts[J].TargetId==H.TargetId)return false;}
  for(std::size_t I=0;I<V.PendingEvents.size();++I){const auto& E=V.PendingEvents[I];
   if(E.EventId==0||E.EventId>=V.NextEventId||E.AttackId==0||E.AttackId>=V.NextAttackId||!Finite(E.AtTime)||E.AtTime<0||E.AtTime>V.Time||!ValidEventAction(E))return false;
   if(E.AttackId==A.AttackId&&!SameAttackFacts(E.Action,A))return false;
   if(I&&(V.PendingEvents[I-1].EventId>=E.EventId||V.PendingEvents[I-1].AtTime>E.AtTime))return false;
   for(std::size_t J=0;J<I;++J){const auto& P=V.PendingEvents[J];if(P.AttackId==E.AttackId&&(!SameAttackFacts(P.Action,E.Action)||P.Kind==E.Kind||((P.Kind==EEventKind::Completed||P.Kind==EEventKind::Interrupted)&&(E.Kind==EEventKind::Completed||E.Kind==EEventKind::Interrupted))))return false;}
   bool Receipt=false;for(const auto& W:V.IssuedWindows){
    if(W.EventId==E.EventId&&(E.Kind!=EEventKind::ActiveWindow||W.AttackId!=E.AttackId||W.SubhitId!=E.SubhitId))return false;
    if(W.AttackId!=E.AttackId)continue;Receipt=true;
    if(W.Start!=E.Action.ActiveStart||W.End!=E.Action.ActiveEnd||W.SubhitId!=E.SubhitId||!SameAttackFacts(E.Action,W.FrozenAction))return false;
    const auto Expected=E.Kind==EEventKind::Started?W.EventId-2:E.Kind==EEventKind::Locked?W.EventId-1:E.Kind==EEventKind::ActiveWindow?W.EventId:W.EventId+1;if(E.EventId!=Expected)return false;
   }
   if((E.Kind==EEventKind::ActiveWindow||E.Kind==EEventKind::Completed)&&!Receipt)return false;
  }
  return true;
 }
public:
 explicit FCombatKernel(EWeapon W=EWeapon::SWD001,std::uint64_t I=1){S.Weapon=W;S.WeaponInstanceId=I;}
 const FCombatState& State()const{return S;}
 std::vector<FCombatEvent> StepTo(double Now,const FAttackContext& Context={}){
  if(!Finite(Now)||Now<S.Time||!ValidContext(Context))return {};
  while(S.Action.Active){
   const double Next=!S.Action.Locked?S.Action.LockTime:!S.Action.WindowIssued?S.Action.ActiveStart:S.Action.End;if(Next>Now)break;S.Time=Next;SetPhase();
   if(!S.Action.Locked){Lock(Context);}
   else if(!S.Action.WindowIssued){S.Action.WindowIssued=true;Emit(EEventKind::ActiveWindow,S.Time);}
   else {const bool Pending=S.PendingPrimary;const bool Air=S.Action.StartedAirborne;const auto Stage=S.Action.Stage;S.Action.Active=false;SetPhase();Emit(EEventKind::Completed,S.Time);S.PendingPrimary=false;if(!Air){S.ComboReady=true;S.NextComboStage=(Stage+1)%3;S.ComboExpiry=S.Time+.45;}else ResetChain();if(Pending&&!Air&&S.Grounded&&Context.Grounded&&Context.CanStart){const auto NextStage=S.NextComboStage;Start(S.Time,NextStage,Context);}}
  }
  S.Time=Now;SetPhase();ExpireChain();auto Events=std::move(S.PendingEvents);S.PendingEvents.clear();return Events;
 }
 bool PressPrimary(double Now,const FAttackContext& Context={},bool FreshPress=true){
  if(!Finite(Now)||Now!=S.Time||!ValidContext(Context)||!FreshPress||!Context.CanStart||S.Dead||Context.Grounded!=S.Grounded)return false;const auto* W=GetWeaponDefinition(S.Weapon);if(!W||!W->HasCombo||S.WeaponInstanceId==0)return false;ExpireChain();
  if(S.Action.Active){if(!S.Action.StartedAirborne&&S.Grounded&&S.Time>=S.Action.ActiveEnd&&S.Time>=S.Action.End-.12&&S.Time<S.Action.End&&!S.PendingPrimary){S.PendingPrimary=true;return true;}return false;}
  if(!S.Grounded&&S.AirPrimarySpent)return false;const auto Stage=S.Grounded&&S.ComboReady?S.NextComboStage:0;if(!S.Grounded)ResetChain();return Start(Now,Stage,Context);
 }
 bool TryReverseCancel(double Now,double DesiredFacing){if(!Finite(Now)||Now!=S.Time||!Finite(DesiredFacing)||DesiredFacing==0||!S.Action.Active||S.Action.Locked||S.Time>=S.Action.LockTime||DesiredFacing*S.Action.Facing>=0)return false;return Interrupt(EInterruptReason::ReverseBeforeLock);}
 void NotifyLand(){S.Grounded=true;}
 void NotifyTakeoff(){if(S.Grounded&&!S.Action.Active&&!S.Dead){S.Grounded=false;S.AirPrimarySpent=false;ResetChain();}}
 void ClearPendingInput(){S.PendingPrimary=false;}
 bool Interrupt(EInterruptReason Reason){
  if(Reason==EInterruptReason::ReverseBeforeLock&&(!S.Action.Active||S.Action.Locked||S.Time>=S.Action.LockTime))return false;
  if(S.Action.Active&&(Reason==EInterruptReason::SwitchWeapon||Reason==EInterruptReason::ExclusiveAction))return false;
  if(S.Action.Active){Emit(EEventKind::Interrupted,S.Time);S.Action.Active=false;SetPhase();}ResetChain();if(Reason==EInterruptReason::Death)S.Dead=true;return true;
 }
 bool ChangeWeapon(EWeapon Weapon,std::uint64_t InstanceId){if(!GetWeaponDefinition(Weapon)||InstanceId==0||S.Action.Active||S.Dead)return false;Interrupt(EInterruptReason::SwitchWeapon);S.Weapon=Weapon;S.WeaponInstanceId=InstanceId;return true;}
 bool TryMarkHit(std::uint64_t AttackId,std::uint32_t SubhitId,std::uint64_t TargetId){if(TargetId==0)return false;bool Window=false;for(const auto& W:S.IssuedWindows)Window|=W.AttackId==AttackId&&W.SubhitId==SubhitId;if(!Window)return false;for(const auto& H:S.HitReceipts)if(H.AttackId==AttackId&&H.SubhitId==SubhitId&&H.TargetId==TargetId)return false;S.HitReceipts.push_back({AttackId,TargetId,SubhitId});return true;}
 FCombatState Capture()const{return S;}
 bool Restore(const FCombatState& State){if(!ValidState(State))return false;S=State;return true;}
}; }
