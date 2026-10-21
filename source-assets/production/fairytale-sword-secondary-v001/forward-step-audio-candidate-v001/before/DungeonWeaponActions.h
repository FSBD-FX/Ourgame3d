#pragma once
#include "DungeonContentCombat.h"
// One instance per character. UE integration is deliberately a separate adapter.
namespace DungeonWeaponActions {
using DungeonContentCombat::EWeapon;
using DungeonContentCombat::EShape;
using DungeonContentCombat::EPhase;
enum class EAction { None, Primary, Skill, Reload };
enum class EEvent { Started, Locked, ForwardStep, ActiveWindow, ProjectileEmitted, Completed, Interrupted, LockFailed, ReloadStarted, ReloadCompleted, ReloadCancelled };
enum class EInterrupt { ReverseBeforeLock, PoiseBreak, Death, SwitchWeapon, ExclusiveAction };
enum class EOriginPolicy { CurrentMuzzle, CurrentActorAfterPriorEvents, GroundProjection };
struct FOrigin { double X=0,Y=0,Height=0; };
struct FContext : DungeonContentCombat::FAttackContext {
 double FocusCostPct=0,SkillCooldownPct=0,ReloadSpeedPct=0,FocusRegen=12,FocusDelay=1;
 FOrigin Muzzle;
};
struct FInstance { EWeapon Weapon=EWeapon::SWD001;std::uint64_t InstanceId=1;double Ammo=0,ReservedAmmo=0,CooldownDeadline=0; };
struct FImportResult { bool Accepted=false,Replayed=false; };
enum class ERegistrationKind { Initial,Legacy,ResolvedImport };
struct FRegistration {
 ERegistrationKind Kind=ERegistrationKind::Initial;FInstance Initial;
 double AtTime=0;std::uint64_t ReceiptId=0,ActionCursor=1,EventCursor=1;
};
struct FBudget { double Focus=100,ReservedFocus=0,LastActualSpend=0;bool HasActualSpend=false,Grounded=true,AirPrimarySpent=false,Dead=false; };
struct FAction {
 EAction Type=EAction::None;EPhase Phase=EPhase::Idle;EWeapon Weapon=EWeapon::SWD001;
 std::uint64_t InstanceId=0,ActionId=0;bool Active=false,Locked=false,StartedAirborne=false,ForwardStepIssued=false;
 std::uint32_t NextSubhit=0;double Facing=1,Start=0,LockAt=0,ActiveAt=0,ActiveEnd=0,End=0,SpeedPct=0;
 double DamagePct=0,StaggerPct=0,ReachPct=0,CritMultiplier=1.5,AmmoCost=0,FocusCost=0,CooldownDuration=0,ReloadSpeedPct=0,FocusCostPct=0,SkillCooldownPct=0;
 bool Critical=false;EEvent Terminal=EEvent::Started;
};
struct FEvent {
 std::uint64_t EventId=0,ActionId=0,InstanceId=0;std::uint32_t SubhitId=0;EEvent Kind=EEvent::Started;
 double AtTime=0,WindowEnd=0,Damage=0,Stagger=0,MinRange=0,Range=0,Depth=0,ProjectileSpeed=0,SecondTargetRatio=1;
 double BurnDps=0,BurnDuration=0,ForwardStep=0,AmmoConsumed=0,FocusConsumed=0;
 std::uint32_t MaxTargets=1;EShape Shape=EShape::ForwardRectangle;EOriginPolicy OriginPolicy=EOriginPolicy::CurrentMuzzle;FOrigin Origin;FAction Action;
};
enum class EFocusChange { Emission, ExternalSpend, ExternalRestore };
struct FFocusReceipt {
 std::uint64_t MutationId=0,ReceiptId=0;EFocusChange Kind=EFocusChange::Emission;
 double AtTime=0,Requested=0,Applied=0,Before=0,After=0,ReservedBefore=0,RegeneratedBefore=0;
};
enum class EWeaponMutation { SkillLock,Emission,ReloadCompleted };
struct FWeaponRuntimeReceipt {
 std::uint64_t EventId=0;EWeaponMutation Kind=EWeaponMutation::SkillLock;double AtTime=0;
 double BeforeAmmo=0,AfterAmmo=0,BeforeCooldown=0,AfterCooldown=0;std::uint32_t SubhitId=0;FAction Action;
};
struct FState {
  std::uint32_t Version=3;double Time=0,LastReloadCancelTime=-1;std::uint64_t EquippedId=1,NextActionId=1,NextEventId=1,AutoReloadPendingId=0;
 FBudget Budget;FAction Action;std::vector<FInstance> Instances;std::vector<FEvent> PendingEvents,Issued;
 double InitialFocus=100,AccruedFocus=0;std::uint64_t NextFocusMutationId=1;
 std::vector<FFocusReceipt> FocusHistory;
 std::vector<FRegistration> Registrations;std::uint64_t NextImportReceiptId=1;
 std::vector<FWeaponRuntimeReceipt> WeaponRuntimeHistory;
};
struct FLandingResult { bool Accepted=false;std::vector<FEvent> Events; };
class FWeaponActionsKernel {
 FState S;
 // A buffered input is not an accepted action; it is deliberately not persisted.
 bool PendingPrimary=false;
 static bool Finite(double N){return std::isfinite(N);}
 static bool MagazineCount(double Value,double Capacity){return Finite(Value)&&Value>=0&&Value<=Capacity&&std::floor(Value)==Value;}
 static bool ValidContext(const FContext& C){
  for(double N:{C.Facing,C.ActionSpeedPct,C.DamagePct,C.StaggerPct,C.ReachPct,C.CritMultiplier,C.FocusCostPct,C.SkillCooldownPct,C.ReloadSpeedPct,C.FocusRegen,C.FocusDelay,C.Muzzle.X,C.Muzzle.Y,C.Muzzle.Height})if(!Finite(N))return false;
  return C.Facing!=0&&C.FocusRegen>=0&&C.FocusDelay>=0&&C.Muzzle.Height>=0;
 }
 FInstance* MutableInstance(std::uint64_t Id){for(auto& I:S.Instances)if(I.InstanceId==Id)return &I;return nullptr;}
 double FocusCheckpoint()const{return S.FocusHistory.empty()?S.InitialFocus:S.FocusHistory.back().After;}
 bool ExternalFocusReady(double Now,double Amount,std::uint64_t ReceiptId)const{
  if(!Finite(Now)||Now!=S.Time||!Finite(Amount)||Amount<=0||ReceiptId==0||S.Budget.Dead||S.NextFocusMutationId==0||S.NextFocusMutationId>=std::numeric_limits<std::uint64_t>::max()-16||!ValidState(S))return false;
  for(const auto& R:S.FocusHistory)if(R.Kind!=EFocusChange::Emission&&R.ReceiptId==ReceiptId)return false;
  return true;
 }
 void RecordFocus(EFocusChange Kind,std::uint64_t ReceiptId,double Requested,double Applied,double Before,double After,double Reserved){
  FFocusReceipt R;R.MutationId=S.NextFocusMutationId;R.ReceiptId=ReceiptId;R.Kind=Kind;R.AtTime=S.Time;
  R.Requested=Requested;R.Applied=Applied;R.Before=Before;R.After=After;R.ReservedBefore=Reserved;R.RegeneratedBefore=S.AccruedFocus;
  S.FocusHistory.push_back(R);++S.NextFocusMutationId;S.AccruedFocus=0;
 }
 static const DungeonContentCombat::FWeaponDefinition* Def(const FAction& A){return DungeonContentCombat::GetWeaponDefinition(A.Weapon);}
 static const DungeonContentCombat::FStageDefinition& Timeline(const FAction& A){const auto* D=Def(A);return A.Type==EAction::Skill?D->Skill.Timeline:D->Primary[0];}
 static std::uint32_t Subhits(const FAction& A){return A.Type==EAction::Skill?Def(A)->Skill.SubhitCount:1;}
 static double SubhitAt(const FAction& A,std::uint32_t N){return A.Start+(A.Type==EAction::Skill?Def(A)->Skill.SubhitTimes[N]:Timeline(A).Windup)/(1+A.SpeedPct/100.);}
 static double SubhitEnd(const FAction& A,std::uint32_t N){return SubhitAt(A,N)+(A.Type==EAction::Skill?Def(A)->Skill.SubhitDurations[N]:Timeline(A).Active)/(1+A.SpeedPct/100.);}
 static double BaseAmmo(const FAction& A){return A.Type==EAction::Skill?Def(A)->Skill.AmmoCost:Def(A)->AmmoPerPrimary;}
 static double BaseFocus(const FAction& A){return A.Type==EAction::Skill?Def(A)->Skill.FocusCost:Def(A)->FocusPerPrimary;}
 void SetPhase(){auto& A=S.Action;A.Phase=!A.Active?EPhase::Idle:A.Type==EAction::Reload?EPhase::Recovery:S.Time<A.ActiveAt?EPhase::Windup:S.Time<A.ActiveEnd?EPhase::Active:EPhase::Recovery;}
 void Advance(double To,const FContext& C){
  const double Eligible=S.Budget.HasActualSpend?S.Budget.LastActualSpend+C.FocusDelay:S.Time;
  if(!S.Budget.Dead&&To>std::max(S.Time,Eligible))S.Budget.Focus=std::min(100.,S.Budget.Focus+(To-std::max(S.Time,Eligible))*C.FocusRegen);
  S.AccruedFocus=S.Budget.Focus-FocusCheckpoint();
  S.Time=To;SetPhase();
 }
 static FEvent BuildEvent(const FAction& A,EEvent Kind,double At,std::uint32_t Sub,const FOrigin& Origin={}){
  FEvent E;E.Action=A;E.ActionId=A.ActionId;E.InstanceId=A.InstanceId;E.Kind=Kind;E.AtTime=At;E.SubhitId=Sub;
  if(Kind==EEvent::ForwardStep){E.ForwardStep=Def(A)->Skill.ForwardStep*A.Facing;E.OriginPolicy=EOriginPolicy::CurrentActorAfterPriorEvents;}
  if(Kind==EEvent::ActiveWindow||Kind==EEvent::ProjectileEmitted){
   const auto* W=Def(A);const auto& T=Timeline(A);const bool Skill=A.Type==EAction::Skill;const double Crit=A.Critical?A.CritMultiplier:1.;
   E.WindowEnd=SubhitEnd(A,Sub);E.Damage=(Skill?W->Skill.SubhitDamage[Sub]:T.Damage)*(1+A.DamagePct/100.)*Crit;
   E.Stagger=(Skill?W->Skill.SubhitStagger[Sub]:T.Stagger)*(1+A.StaggerPct/100.);E.MinRange=T.MinRange;E.Range=T.Range*(1+A.ReachPct/100.);E.Depth=T.Depth;E.Shape=T.Shape;
   E.ProjectileSpeed=Skill?W->Skill.ProjectileSpeed:W->ProjectileSpeed;E.MaxTargets=Skill?W->Skill.MaxTargets:1;E.SecondTargetRatio=Skill?W->Skill.SecondTargetRatio:1;
   E.BurnDps=Skill?W->Skill.BurnDps:0;E.BurnDuration=Skill?W->Skill.BurnDuration:0;E.AmmoConsumed=A.AmmoCost/Subhits(A);E.FocusConsumed=A.FocusCost/Subhits(A);
   E.Origin=Origin;E.OriginPolicy=E.Shape==EShape::Projectile?EOriginPolicy::CurrentMuzzle:E.Shape==EShape::GroundRectangle?EOriginPolicy::GroundProjection:EOriginPolicy::CurrentActorAfterPriorEvents;
   if(E.Shape==EShape::GroundRectangle)E.Origin.Height=0;
  }
  return E;
 }
 void Emit(EEvent Kind,double At,std::uint32_t Sub=0,const FOrigin& Origin={}){
  auto E=BuildEvent(S.Action,Kind,At,Sub,Origin);E.EventId=S.NextEventId++;S.PendingEvents.push_back(E);
  if(Kind==EEvent::ActiveWindow||Kind==EEvent::ProjectileEmitted)S.Issued.push_back(E);
 }
 void RecordWeaponRuntime(EWeaponMutation Kind,double BeforeAmmo,double BeforeCooldown,std::uint32_t Sub=0){
  const auto* I=Instance(S.Action.InstanceId);FWeaponRuntimeReceipt R;R.EventId=S.NextEventId;R.Kind=Kind;R.AtTime=S.Time;
  R.BeforeAmmo=BeforeAmmo;R.AfterAmmo=I->Ammo;R.BeforeCooldown=BeforeCooldown;R.AfterCooldown=I->CooldownDeadline;R.SubhitId=Sub;R.Action=S.Action;S.WeaponRuntimeHistory.push_back(R);
 }
 bool RoomForAction()const{return S.NextActionId>0&&S.NextActionId<std::numeric_limits<std::uint64_t>::max()&&S.NextEventId>0&&S.NextEventId<std::numeric_limits<std::uint64_t>::max()-16&&S.NextFocusMutationId>0&&S.NextFocusMutationId<std::numeric_limits<std::uint64_t>::max()-16;}
 bool ResourcesValid()const{
  if(!Finite(S.Budget.Focus)||!Finite(S.Budget.ReservedFocus)||S.Budget.Focus<0||S.Budget.Focus>100||S.Budget.ReservedFocus<0||S.Budget.ReservedFocus>S.Budget.Focus)return false;
  const auto* I=Instance(S.EquippedId);if(!I||I->InstanceId==0)return false;const auto* W=DungeonContentCombat::GetWeaponDefinition(I->Weapon);
  return W&&MagazineCount(I->Ammo,W->Magazine)&&MagazineCount(I->ReservedAmmo,I->Ammo);
 }
 bool Start(EAction Type,const FContext& C){
  if(Type!=EAction::Primary&&Type!=EAction::Skill)return false;
  if(S.Action.Active||S.Budget.Dead||!C.CanStart||!ResourcesValid()||!RoomForAction()||S.Time==S.LastReloadCancelTime||C.Grounded!=S.Budget.Grounded)return false;
  auto* I=MutableInstance(S.EquippedId);const auto* W=DungeonContentCombat::GetWeaponDefinition(I->Weapon);
  if(Type==EAction::Primary&&(W->HasCombo||(!S.Budget.Grounded&&S.Budget.AirPrimarySpent)))return false;
  if(Type==EAction::Skill&&(!S.Budget.Grounded||S.Time<I->CooldownDeadline))return false;
  FAction A;A.Type=Type;A.Weapon=I->Weapon;A.InstanceId=I->InstanceId;
  if(I->Ammo-I->ReservedAmmo<BaseAmmo(A)||S.Budget.Focus-S.Budget.ReservedFocus<BaseFocus(A)*(1+std::clamp(C.FocusCostPct,-20.,25.)/100.))return false;
  A.Active=true;A.Start=S.Time;A.Facing=C.Facing>0?1:-1;A.StartedAirborne=!S.Budget.Grounded;A.SpeedPct=std::clamp(C.ActionSpeedPct,-20.,20.);
  const auto& T=Timeline(A);const double Speed=1+A.SpeedPct/100.;A.LockAt=A.Start+T.Windup/Speed*.4;A.ActiveAt=A.Start+T.Windup/Speed;A.ActiveEnd=A.Start+T.ActiveEnd/Speed;A.End=A.Start+T.Cycle/Speed;
  if(!Finite(A.End)||!(A.Start<A.LockAt&&A.LockAt<A.ActiveAt&&A.ActiveAt<A.ActiveEnd&&A.ActiveEnd<A.End))return false;
  A.ActionId=S.NextActionId++;
  S.Action=A;PendingPrimary=false;if(A.StartedAirborne)S.Budget.AirPrimarySpent=true;SetPhase();Emit(EEvent::Started,S.Time);return true;
 }
 bool StartReload(const FContext& C){
  if(S.Action.Active||S.Budget.Dead||!S.Budget.Grounded||!C.Grounded||!C.CanStart||!RoomForAction()||!ResourcesValid()||S.Time==S.LastReloadCancelTime)return false;
  const auto* I=Instance(S.EquippedId);const auto* W=DungeonContentCombat::GetWeaponDefinition(I->Weapon);if(W->Magazine<=0||W->Reload<=0||I->Ammo>=W->Magazine)return false;
  FAction A;A.Type=EAction::Reload;A.Active=true;A.Weapon=I->Weapon;A.InstanceId=I->InstanceId;A.Start=S.Time;A.LockAt=A.ActiveAt=A.ActiveEnd=A.Start;A.ReloadSpeedPct=std::clamp(C.ReloadSpeedPct,-25.,25.);A.End=A.Start+W->Reload/(1+A.ReloadSpeedPct/100.);
  if(!Finite(A.End)||A.End<=A.Start)return false;
  A.ActionId=S.NextActionId++;
  S.Action=A;S.AutoReloadPendingId=0;PendingPrimary=false;SetPhase();Emit(EEvent::ReloadStarted,S.Time);return true;
 }
 void ReleaseReservation(){if(auto* I=MutableInstance(S.Action.InstanceId))I->ReservedAmmo=0;S.Budget.ReservedFocus=0;}
 void Lock(const FContext& C){
  auto& A=S.Action;auto* I=MutableInstance(A.InstanceId);const double Ammo=BaseAmmo(A),Focus=BaseFocus(A)*(1+std::clamp(C.FocusCostPct,-20.,25.)/100.);
  if(I->Ammo-I->ReservedAmmo<Ammo||S.Budget.Focus-S.Budget.ReservedFocus<Focus){A.Active=false;A.Terminal=EEvent::LockFailed;PendingPrimary=false;SetPhase();Emit(EEvent::LockFailed,S.Time);return;}
  A.Locked=true;A.Facing=C.Facing>0?1:-1;A.DamagePct=std::clamp(C.DamagePct,-30.,50.);A.StaggerPct=std::clamp(C.StaggerPct,-25.,25.);A.ReachPct=std::clamp(C.ReachPct,-15.,15.);A.Critical=C.Critical;A.CritMultiplier=std::clamp(C.CritMultiplier,1.,2.);
  A.FocusCostPct=std::clamp(C.FocusCostPct,-20.,25.);A.SkillCooldownPct=std::clamp(C.SkillCooldownPct,-20.,25.);A.AmmoCost=Ammo;A.FocusCost=Focus;
  I->ReservedAmmo=Ammo;S.Budget.ReservedFocus=Focus;if(A.Type==EAction::Skill){const double Previous=I->CooldownDeadline;A.CooldownDuration=Def(A)->Skill.Cooldown*(1+A.SkillCooldownPct/100.);I->CooldownDeadline=A.LockAt+A.CooldownDuration;RecordWeaponRuntime(EWeaponMutation::SkillLock,I->Ammo,Previous);}
  Emit(EEvent::Locked,S.Time);
 }
 void Issue(const FContext& C){
  auto& A=S.Action;const auto N=A.NextSubhit;auto* I=MutableInstance(A.InstanceId);
  if(A.Type==EAction::Skill&&Def(A)->Skill.ForwardStep!=0&&!A.ForwardStepIssued){A.ForwardStepIssued=true;Emit(EEvent::ForwardStep,S.Time);}
  const double Ammo=N+1==Subhits(A)?I->ReservedAmmo:A.AmmoCost/Subhits(A),Focus=N+1==Subhits(A)?S.Budget.ReservedFocus:A.FocusCost/Subhits(A);
  const double FocusBefore=S.Budget.Focus,ReservedBefore=S.Budget.ReservedFocus,AmmoBefore=I->Ammo;
  I->Ammo-=Ammo;I->ReservedAmmo-=Ammo;S.Budget.Focus-=Focus;S.Budget.ReservedFocus-=Focus;
  if(Focus>0){S.Budget.HasActualSpend=true;S.Budget.LastActualSpend=S.Time;}
  ++A.NextSubhit;if(Ammo>0)RecordWeaponRuntime(EWeaponMutation::Emission,AmmoBefore,I->CooldownDeadline,N);Emit(Timeline(A).Shape==EShape::Projectile?EEvent::ProjectileEmitted:EEvent::ActiveWindow,S.Time,N,C.Muzzle);
  if(Focus>0)RecordFocus(EFocusChange::Emission,S.Issued.back().EventId,Focus,Focus,FocusBefore,S.Budget.Focus,ReservedBefore);
 }
 static bool ActionDataValid(const FAction& A){
  for(double N:{A.Facing,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.End,A.SpeedPct,A.DamagePct,A.StaggerPct,A.ReachPct,A.CritMultiplier,A.AmmoCost,A.FocusCost,A.CooldownDuration,A.ReloadSpeedPct,A.FocusCostPct,A.SkillCooldownPct})if(!Finite(N))return false;
  if(A.Type==EAction::None)return A.ActionId==0&&A.InstanceId==0&&!A.Active&&!A.Locked&&A.Phase==EPhase::Idle&&A.Start==0&&A.LockAt==0&&A.ActiveAt==0&&A.ActiveEnd==0&&A.End==0&&A.NextSubhit==0&&!A.ForwardStepIssued;
  if(static_cast<unsigned>(A.Type)>static_cast<unsigned>(EAction::Reload)||!Def(A)||A.InstanceId==0||A.ActionId==0||static_cast<unsigned>(A.Phase)>static_cast<unsigned>(EPhase::Recovery))return false;
  if(A.Start<0||(A.Facing!=1&&A.Facing!=-1)||A.Active==(A.Phase==EPhase::Idle)||A.CritMultiplier<1||A.CritMultiplier>2)return false;
  if(A.Type==EAction::Reload)return Def(A)->Magazine>0&&A.ReloadSpeedPct>=-25&&A.ReloadSpeedPct<=25&&A.LockAt==A.Start&&A.ActiveAt==A.Start&&A.ActiveEnd==A.Start&&A.End==A.Start+Def(A)->Reload/(1+A.ReloadSpeedPct/100.)&&!A.Locked&&!A.StartedAirborne&&A.NextSubhit==0&&!A.ForwardStepIssued&&A.AmmoCost==0&&A.FocusCost==0&&A.CooldownDuration==0;
  if((A.Type==EAction::Primary&&Def(A)->HasCombo)||(A.Type==EAction::Skill&&A.StartedAirborne)||A.SpeedPct < -20||A.SpeedPct>20||A.NextSubhit>Subhits(A))return false;
  const auto& T=Timeline(A);const double Speed=1+A.SpeedPct/100.;
  if(A.LockAt!=A.Start+T.Windup/Speed*.4||A.ActiveAt!=A.Start+T.Windup/Speed||A.ActiveEnd!=A.Start+T.ActiveEnd/Speed||A.End!=A.Start+T.Cycle/Speed||!(A.Start<A.LockAt&&A.LockAt<A.ActiveAt&&A.ActiveAt<A.ActiveEnd&&A.ActiveEnd<A.End))return false;
  if(A.ForwardStepIssued!=(A.Type==EAction::Skill&&Def(A)->Skill.ForwardStep!=0&&A.NextSubhit>0))return false;
  if(!A.Locked)return A.NextSubhit==0&&!A.Critical&&A.CritMultiplier==1.5&&A.DamagePct==0&&A.StaggerPct==0&&A.ReachPct==0&&A.FocusCostPct==0&&A.SkillCooldownPct==0&&A.AmmoCost==0&&A.FocusCost==0&&A.CooldownDuration==0;
  return A.DamagePct>=-30&&A.DamagePct<=50&&A.StaggerPct>=-25&&A.StaggerPct<=25&&A.ReachPct>=-15&&A.ReachPct<=15&&A.FocusCostPct>=-20&&A.FocusCostPct<=25&&A.SkillCooldownPct>=-20&&A.SkillCooldownPct<=25&&A.AmmoCost==BaseAmmo(A)&&A.FocusCost==BaseFocus(A)*(1+A.FocusCostPct/100.)&&A.CooldownDuration==(A.Type==EAction::Skill?Def(A)->Skill.Cooldown*(1+A.SkillCooldownPct/100.):0);
 }
 static bool SameFacts(const FAction& A,const FAction& B){
  if(A.Type!=B.Type||A.Weapon!=B.Weapon||A.InstanceId!=B.InstanceId||A.ActionId!=B.ActionId||A.StartedAirborne!=B.StartedAirborne||A.Start!=B.Start||A.LockAt!=B.LockAt||A.ActiveAt!=B.ActiveAt||A.ActiveEnd!=B.ActiveEnd||A.End!=B.End||A.SpeedPct!=B.SpeedPct||A.ReloadSpeedPct!=B.ReloadSpeedPct)return false;
  return !A.Locked||!B.Locked||(A.Facing==B.Facing&&A.DamagePct==B.DamagePct&&A.StaggerPct==B.StaggerPct&&A.ReachPct==B.ReachPct&&A.CritMultiplier==B.CritMultiplier&&A.Critical==B.Critical&&A.FocusCostPct==B.FocusCostPct&&A.SkillCooldownPct==B.SkillCooldownPct&&A.AmmoCost==B.AmmoCost&&A.FocusCost==B.FocusCost&&A.CooldownDuration==B.CooldownDuration);
 }
 static bool PayloadValid(const FEvent& E){
  auto ValidationAction=E.Action;
  if(E.Kind==EEvent::ForwardStep&&ValidationAction.NextSubhit==0)ValidationAction.ForwardStepIssued=false;
  if(!ActionDataValid(ValidationAction)||E.ActionId!=E.Action.ActionId||E.InstanceId!=E.Action.InstanceId||static_cast<unsigned>(E.Kind)>static_cast<unsigned>(EEvent::ReloadCancelled)||!Finite(E.AtTime)||E.AtTime<E.Action.Start||!Finite(E.Origin.X)||!Finite(E.Origin.Y)||!Finite(E.Origin.Height)||E.Origin.Height<0)return false;
  const auto& A=E.Action;const bool Hit=E.Kind==EEvent::ActiveWindow||E.Kind==EEvent::ProjectileEmitted;
  if(A.Active){const auto Phase=A.Type==EAction::Reload?EPhase::Recovery:E.AtTime<A.ActiveAt?EPhase::Windup:E.AtTime<A.ActiveEnd?EPhase::Active:EPhase::Recovery;if(A.Phase!=Phase||E.AtTime>=A.End)return false;}
  if(Hit){if(!A.Locked||!A.Active||A.Type==EAction::Reload||E.SubhitId>=Subhits(A)||A.NextSubhit!=E.SubhitId+1||E.AtTime!=SubhitAt(A,E.SubhitId)||E.Kind!=(Timeline(A).Shape==EShape::Projectile?EEvent::ProjectileEmitted:EEvent::ActiveWindow))return false;}
  else if(E.SubhitId!=0)return false;
  if(E.Kind==EEvent::Started&&(A.Type==EAction::Reload||!A.Active||A.Locked||E.AtTime!=A.Start))return false;
  if(E.Kind==EEvent::Locked&&(!A.Active||!A.Locked||A.NextSubhit!=0||E.AtTime!=A.LockAt))return false;
  if(E.Kind==EEvent::ForwardStep&&(A.Type!=EAction::Skill||Def(A)->Skill.ForwardStep==0||!A.Locked||!A.Active||!A.ForwardStepIssued||E.AtTime!=A.ActiveAt))return false;
  if(E.Kind==EEvent::Completed&&(A.Active||A.Terminal!=EEvent::Completed||A.Type==EAction::Reload||!A.Locked||A.NextSubhit!=Subhits(A)||E.AtTime!=A.End))return false;
  if(E.Kind==EEvent::Interrupted&&(A.Active||A.Terminal!=EEvent::Interrupted||E.AtTime>A.End))return false;
  if(E.Kind==EEvent::LockFailed&&(A.Active||A.Locked||A.Terminal!=EEvent::LockFailed||E.AtTime!=A.LockAt))return false;
  if(E.Kind==EEvent::ReloadStarted&&(A.Type!=EAction::Reload||!A.Active||E.AtTime!=A.Start))return false;
  if(E.Kind==EEvent::ReloadCompleted&&(A.Type!=EAction::Reload||A.Active||A.Terminal!=EEvent::ReloadCompleted||E.AtTime!=A.End))return false;
  if(E.Kind==EEvent::ReloadCancelled&&(A.Type!=EAction::Reload||A.Active||A.Terminal!=EEvent::ReloadCancelled||E.AtTime>A.End))return false;
  // The step event deliberately precedes the window cursor increment.
  FAction ForPayload=A;if(E.Kind==EEvent::ForwardStep)ForPayload.NextSubhit=1;
  const auto P=BuildEvent(ForPayload,E.Kind,E.AtTime,E.SubhitId,E.Origin);
  return E.WindowEnd==P.WindowEnd&&E.Damage==P.Damage&&E.Stagger==P.Stagger&&E.MinRange==P.MinRange&&E.Range==P.Range&&E.Depth==P.Depth&&E.ProjectileSpeed==P.ProjectileSpeed&&E.SecondTargetRatio==P.SecondTargetRatio&&E.MaxTargets==P.MaxTargets&&E.BurnDps==P.BurnDps&&E.BurnDuration==P.BurnDuration&&E.ForwardStep==P.ForwardStep&&E.AmmoConsumed==P.AmmoConsumed&&E.FocusConsumed==P.FocusConsumed&&E.Shape==P.Shape&&E.OriginPolicy==P.OriginPolicy&&E.Origin.Height==P.Origin.Height;
 }
 static bool SameInstance(const FInstance& A,const FInstance& B){return A.Weapon==B.Weapon&&A.InstanceId==B.InstanceId&&A.Ammo==B.Ammo&&A.ReservedAmmo==B.ReservedAmmo&&A.CooldownDeadline==B.CooldownDeadline;}
 static bool ValidImportedInstance(const FInstance& I){const auto* D=DungeonContentCombat::GetWeaponDefinition(I.Weapon);return D&&I.InstanceId&&MagazineCount(I.Ammo,D->Magazine)&&I.ReservedAmmo==0&&Finite(I.CooldownDeadline)&&I.CooldownDeadline>=0;}
 static bool ValidWeaponRuntime(const FState& V){
  if(V.Registrations.size()!=V.Instances.size()||!V.NextImportReceiptId)return false;
  std::vector<FInstance> Balances;std::uint64_t LastReceipt=0;double BirthTime=0;
  for(std::size_t N=0;N<V.Registrations.size();++N){
   const auto& R=V.Registrations[N];const auto& I=V.Instances[N];
   if(!ValidImportedInstance(R.Initial)||R.Initial.InstanceId!=I.InstanceId||R.Initial.Weapon!=I.Weapon||!Finite(R.AtTime)||R.AtTime<BirthTime||R.AtTime>V.Time||!R.ActionCursor||R.ActionCursor>V.NextActionId||!R.EventCursor||R.EventCursor>V.NextEventId||static_cast<unsigned>(R.Kind)>static_cast<unsigned>(ERegistrationKind::ResolvedImport))return false;
   if(N==0){if(R.Kind!=ERegistrationKind::Initial||R.AtTime!=0||R.ReceiptId||R.ActionCursor!=1||R.EventCursor!=1||R.Initial.CooldownDeadline!=0)return false;}
   else if(R.Kind==ERegistrationKind::Initial)return false;
   if(R.Kind==ERegistrationKind::ResolvedImport){if(!R.ReceiptId||R.ReceiptId==std::numeric_limits<std::uint64_t>::max()||R.ReceiptId<=LastReceipt)return false;LastReceipt=R.ReceiptId;}
   else if(R.ReceiptId||R.Initial.CooldownDeadline!=0)return false;
   const auto ActionAfterBirth=[&R](const FAction& A){return !A.ActionId||A.InstanceId!=R.Initial.InstanceId||(A.Weapon==R.Initial.Weapon&&A.Start>=R.AtTime&&A.ActionId>=R.ActionCursor);};
   if(!ActionAfterBirth(V.Action))return false;
   for(const auto& E:V.Issued)if(!ActionAfterBirth(E.Action)||(E.InstanceId==I.InstanceId&&E.EventId<R.EventCursor))return false;
   for(const auto& E:V.PendingEvents)if(!ActionAfterBirth(E.Action)||(E.InstanceId==I.InstanceId&&E.EventId<R.EventCursor))return false;
   BirthTime=R.AtTime;Balances.push_back(R.Initial);
  }
  if(V.NextImportReceiptId!=(LastReceipt?LastReceipt+1:1))return false;
  std::uint64_t LastEvent=0;double LastTime=0;std::size_t Emissions=0;
  for(std::size_t N=0;N<V.WeaponRuntimeHistory.size();++N){
   const auto& R=V.WeaponRuntimeHistory[N];const auto& A=R.Action;
   if(!R.EventId||R.EventId<=LastEvent||R.EventId>=V.NextEventId||static_cast<unsigned>(R.Kind)>static_cast<unsigned>(EWeaponMutation::ReloadCompleted)||!ActionDataValid(A)||!A.ActionId||A.ActionId>=V.NextActionId||!Finite(R.AtTime)||R.AtTime<LastTime||R.AtTime>V.Time)return false;
   for(double Value:{R.BeforeAmmo,R.AfterAmmo,R.BeforeCooldown,R.AfterCooldown})if(!Finite(Value))return false;
   if(!MagazineCount(R.BeforeAmmo,Def(A)->Magazine)||!MagazineCount(R.AfterAmmo,Def(A)->Magazine))return false;
   std::size_t Index=0;while(Index<Balances.size()&&Balances[Index].InstanceId!=A.InstanceId)++Index;if(Index==Balances.size())return false;
   auto& I=Balances[Index];const auto& Birth=V.Registrations[Index];
   if(A.Weapon!=I.Weapon||A.Start<Birth.AtTime||A.ActionId<Birth.ActionCursor||R.EventId<Birth.EventCursor||R.BeforeAmmo!=I.Ammo||R.BeforeCooldown!=I.CooldownDeadline)return false;
   if(R.Kind==EWeaponMutation::SkillLock){
    if(A.Type!=EAction::Skill||!A.Locked||R.AtTime!=A.LockAt||R.AfterAmmo!=R.BeforeAmmo||R.BeforeCooldown>A.Start||R.AfterCooldown!=A.LockAt+A.CooldownDuration||R.SubhitId)return false;
   }else if(R.Kind==EWeaponMutation::Emission){
    if(A.Type==EAction::Reload||!A.Locked||R.SubhitId>=Subhits(A)||R.AtTime!=SubhitAt(A,R.SubhitId)||R.AfterCooldown!=R.BeforeCooldown||A.AmmoCost<=0||R.AfterAmmo!=R.BeforeAmmo-A.AmmoCost/Subhits(A))return false;
    bool Found=false;for(const auto& E:V.Issued)if(E.EventId==R.EventId&&E.SubhitId==R.SubhitId&&E.AtTime==R.AtTime&&SameFacts(A,E.Action)&&E.AmmoConsumed>0)Found=true;
    if(!Found)return false;++Emissions;
   }else if(A.Type!=EAction::Reload||A.Terminal!=EEvent::ReloadCompleted||A.Active||R.AtTime!=A.End||R.AfterAmmo!=Def(A)->Magazine||R.BeforeAmmo>=R.AfterAmmo||R.AfterCooldown!=R.BeforeCooldown||R.SubhitId)return false;
   for(std::size_t J=0;J<N;++J){const auto& P=V.WeaponRuntimeHistory[J];if(P.Action.ActionId==A.ActionId&&P.Kind==R.Kind&&(R.Kind!=EWeaponMutation::Emission||P.SubhitId==R.SubhitId))return false;}
   if(R.AfterAmmo<0||R.AfterAmmo>Def(A)->Magazine||R.AfterCooldown<0)return false;
   I.Ammo=R.AfterAmmo;I.CooldownDeadline=R.AfterCooldown;LastEvent=R.EventId;LastTime=R.AtTime;
  }
  std::size_t IssuedAmmo=0;for(const auto& E:V.Issued)if(E.AmmoConsumed>0)++IssuedAmmo;if(IssuedAmmo!=Emissions)return false;
  const auto HasSkillLock=[&V](const FAction& A){
   if(A.Type!=EAction::Skill||!A.Locked)return true;
   for(const auto& R:V.WeaponRuntimeHistory)if(R.Kind==EWeaponMutation::SkillLock&&R.Action.ActionId==A.ActionId&&R.Action.InstanceId==A.InstanceId&&R.AtTime==A.LockAt&&SameFacts(R.Action,A))return true;
   return false;
  };
  if(!HasSkillLock(V.Action))return false;
  for(const auto& E:V.Issued)if(!HasSkillLock(E.Action))return false;
  for(const auto& E:V.PendingEvents)if(!HasSkillLock(E.Action))return false;
  for(std::size_t N=0;N<Balances.size();++N)if(Balances[N].Ammo!=V.Instances[N].Ammo||Balances[N].CooldownDeadline!=V.Instances[N].CooldownDeadline)return false;
  return true;
 }
 static bool ValidState(const FState& V){
  if(V.Version!=3||!Finite(V.Time)||V.Time<0||!Finite(V.LastReloadCancelTime)||V.LastReloadCancelTime < -1||V.LastReloadCancelTime>V.Time||V.NextActionId==0||V.NextEventId==0||V.NextEventId>std::numeric_limits<std::uint64_t>::max()-16||V.Instances.empty())return false;
  const auto& B=V.Budget;if(!Finite(B.Focus)||B.Focus<0||B.Focus>100||!Finite(B.ReservedFocus)||B.ReservedFocus<0||B.ReservedFocus>B.Focus||!Finite(B.LastActualSpend)||B.LastActualSpend<0||B.LastActualSpend>V.Time||(!B.HasActualSpend&&B.LastActualSpend!=0))return false;
  const FInstance* Equipped=nullptr;
  for(std::size_t I=0;I<V.Instances.size();++I){const auto& W=V.Instances[I];const auto* D=DungeonContentCombat::GetWeaponDefinition(W.Weapon);if(!D||W.InstanceId==0||!MagazineCount(W.Ammo,D->Magazine)||!MagazineCount(W.ReservedAmmo,W.Ammo)||!Finite(W.CooldownDeadline)||W.CooldownDeadline<0)return false;if(W.InstanceId==V.EquippedId)Equipped=&W;for(std::size_t J=0;J<I;++J)if(W.InstanceId==V.Instances[J].InstanceId)return false;}
  if(!Equipped||!ActionDataValid(V.Action)||(B.Dead&&V.Action.Active))return false;
  const auto& A=V.Action;if(A.ActionId>=V.NextActionId||A.Start>V.Time)return false;
  if(A.ActionId){bool Found=false;for(const auto& W:V.Instances)if(W.InstanceId==A.InstanceId&&W.Weapon==A.Weapon)Found=true;if(!Found)return false;}
  if(A.Active){
   if(A.InstanceId!=V.EquippedId||V.Time>=A.End||A.Terminal!=EEvent::Started)return false;
   if(A.Type!=EAction::Reload){if(A.Locked!=(V.Time>=A.LockAt))return false;std::uint32_t Due=0;for(std::uint32_t N=0;N<Subhits(A);++N)if(SubhitAt(A,N)<=V.Time)++Due;if(A.NextSubhit!=Due)return false;}
   const auto Phase=A.Type==EAction::Reload?EPhase::Recovery:V.Time<A.ActiveAt?EPhase::Windup:V.Time<A.ActiveEnd?EPhase::Active:EPhase::Recovery;if(A.Phase!=Phase)return false;
  }else if(A.ActionId){if(A.Terminal!=EEvent::Completed&&A.Terminal!=EEvent::Interrupted&&A.Terminal!=EEvent::LockFailed&&A.Terminal!=EEvent::ReloadCompleted&&A.Terminal!=EEvent::ReloadCancelled)return false;if((A.Terminal==EEvent::Completed||A.Terminal==EEvent::ReloadCompleted)&&V.Time<A.End)return false;if(A.Terminal==EEvent::Completed&&(A.Type==EAction::Reload||!A.Locked||A.NextSubhit!=Subhits(A)))return false;if((A.Terminal==EEvent::ReloadCompleted||A.Terminal==EEvent::ReloadCancelled)&&A.Type!=EAction::Reload)return false;if(A.Terminal==EEvent::LockFailed&&(A.Type==EAction::Reload||A.Locked||V.Time<A.LockAt))return false;}
  const bool Reserved=A.Active&&A.Locked&&A.Type!=EAction::Reload;const double Remaining=Reserved?1-double(A.NextSubhit)/Subhits(A):0;
  if(B.ReservedFocus!=(Reserved?A.FocusCost*Remaining:0))return false;
  for(const auto& W:V.Instances){if(W.ReservedAmmo!=(Reserved&&W.InstanceId==A.InstanceId?A.AmmoCost*Remaining:0))return false;}
  if(A.ActionId&&A.Locked&&A.Type==EAction::Skill){for(const auto& W:V.Instances)if(W.InstanceId==A.InstanceId&&W.CooldownDeadline!=A.LockAt+A.CooldownDuration)return false;}
  if(A.Active&&A.StartedAirborne&&!B.Grounded&&!B.AirPrimarySpent)return false;
  if(V.AutoReloadPendingId&&(V.AutoReloadPendingId!=V.EquippedId||Equipped->Ammo!=0||DungeonContentCombat::GetWeaponDefinition(Equipped->Weapon)->Magazine<=0||A.Active))return false;
  std::uint32_t CurrentIssued=0;bool HasFocusSpend=false;double LastFocusSpend=0;
  for(std::size_t I=0;I<V.Issued.size();++I){const auto& E=V.Issued[I];if((E.Kind!=EEvent::ActiveWindow&&E.Kind!=EEvent::ProjectileEmitted)||!PayloadValid(E)||E.EventId==0||E.EventId>=V.NextEventId||E.ActionId>=V.NextActionId||E.AtTime>V.Time)return false;bool Registered=false;for(const auto& W:V.Instances)if(W.InstanceId==E.InstanceId&&W.Weapon==E.Action.Weapon)Registered=true;if(!Registered)return false;if(E.FocusConsumed>0){HasFocusSpend=true;LastFocusSpend=std::max(LastFocusSpend,E.AtTime);}if(E.ActionId==A.ActionId){if(!SameFacts(A,E.Action))return false;++CurrentIssued;}for(std::size_t J=0;J<I;++J)if(V.Issued[J].EventId==E.EventId||(V.Issued[J].ActionId==E.ActionId&&V.Issued[J].SubhitId==E.SubhitId))return false;}
  if(!Finite(V.InitialFocus)||V.InitialFocus<0||V.InitialFocus>100||!Finite(V.AccruedFocus)||V.AccruedFocus<0||V.NextFocusMutationId==0||V.NextFocusMutationId!=V.FocusHistory.size()+1)return false;
  double FocusBalance=V.InitialFocus,PreviousFocusTime=0;std::size_t EmissionFacts=0,FocusEmissions=0;
  for(const auto& E:V.Issued)if(E.FocusConsumed>0)++FocusEmissions;
  for(std::size_t I=0;I<V.FocusHistory.size();++I){
   const auto& R=V.FocusHistory[I];
   for(double N:{R.AtTime,R.Requested,R.Applied,R.Before,R.After,R.ReservedBefore,R.RegeneratedBefore})if(!Finite(N))return false;
   if(R.MutationId!=I+1||R.ReceiptId==0||static_cast<unsigned>(R.Kind)>static_cast<unsigned>(EFocusChange::ExternalRestore)||R.AtTime<PreviousFocusTime||R.AtTime>V.Time||R.Requested<=0||R.Applied<=0||R.Before<0||R.Before>100||R.After<0||R.After>100||R.ReservedBefore<0||R.ReservedBefore>R.Before||R.RegeneratedBefore<0||R.Before-FocusBalance!=R.RegeneratedBefore||(R.AtTime==PreviousFocusTime&&R.RegeneratedBefore!=0))return false;
   for(std::size_t J=0;J<I;++J){const auto& P=V.FocusHistory[J];if(P.ReceiptId==R.ReceiptId&&((P.Kind==EFocusChange::Emission)==(R.Kind==EFocusChange::Emission)))return false;}
   if(R.Kind!=EFocusChange::Emission){
    // External calls happen after StepTo has processed every due emission at this clock.
    const auto MatchesKnownReservation=[&R](const FAction& Known){
     std::uint32_t Due=0;for(std::uint32_t N=0;N<Subhits(Known);++N)if(SubhitAt(Known,N)<=R.AtTime)++Due;
     return R.ReservedBefore==Known.FocusCost*(1-double(Due)/Subhits(Known));
    };
    if(A.Active&&A.Locked&&A.Type!=EAction::Reload&&R.AtTime>=A.LockAt&&!MatchesKnownReservation(A))return false;
    for(const auto& E:V.Issued)if(E.FocusConsumed>0){
     if(R.AtTime>=E.Action.LockAt&&R.AtTime<E.AtTime&&!MatchesKnownReservation(E.Action))return false;
     if(R.AtTime==E.AtTime){bool AlreadyIssued=false;for(const auto& P:V.FocusHistory)if(P.Kind==EFocusChange::Emission&&P.ReceiptId==E.EventId&&P.MutationId<R.MutationId)AlreadyIssued=true;if(!AlreadyIssued)return false;}
    }
   }
   if(R.Kind==EFocusChange::ExternalRestore){
    const double After=R.Before+std::min(R.Requested,100-R.Before);
    if(R.After!=After||R.Applied!=R.After-R.Before)return false;
   }else{
    if(R.Applied!=R.Requested||R.After!=R.Before-R.Applied||R.After>=R.Before)return false;
    if(R.Kind==EFocusChange::ExternalSpend){
     if(R.Applied>R.Before-R.ReservedBefore||R.After<R.ReservedBefore)return false;
     HasFocusSpend=true;LastFocusSpend=std::max(LastFocusSpend,R.AtTime);
    }else{
     if(R.Applied>R.ReservedBefore)return false;
     bool Found=false;for(const auto& E:V.Issued)if(E.EventId==R.ReceiptId&&E.AtTime==R.AtTime&&E.FocusConsumed==R.Applied&&E.FocusConsumed>0&&R.ReservedBefore==E.Action.FocusCost*(1-double(E.SubhitId)/Subhits(E.Action)))Found=true;
     if(!Found)return false;++EmissionFacts;
    }
   }
   FocusBalance=R.After;PreviousFocusTime=R.AtTime;
  }
  if(EmissionFacts!=FocusEmissions||B.Focus-FocusBalance!=V.AccruedFocus||(V.Time==PreviousFocusTime&&V.AccruedFocus!=0))return false;
  if(B.HasActualSpend!=HasFocusSpend||B.LastActualSpend!=LastFocusSpend)return false;
  if(A.ActionId&&A.Type!=EAction::Reload&&CurrentIssued!=A.NextSubhit)return false;
  for(std::size_t I=0;I<V.PendingEvents.size();++I){const auto& E=V.PendingEvents[I];if(!PayloadValid(E)||E.EventId==0||E.EventId>=V.NextEventId||E.ActionId>=V.NextActionId||E.AtTime>V.Time)return false;if(I&&(V.PendingEvents[I-1].EventId>=E.EventId||V.PendingEvents[I-1].AtTime>E.AtTime))return false;for(std::size_t J=0;J<I;++J)if(V.PendingEvents[J].ActionId==E.ActionId&&V.PendingEvents[J].Kind==E.Kind&&V.PendingEvents[J].SubhitId==E.SubhitId)return false;if(E.ActionId==A.ActionId&&!SameFacts(A,E.Action))return false;if(E.Kind==EEvent::ActiveWindow||E.Kind==EEvent::ProjectileEmitted){bool Found=false;for(const auto& R:V.Issued)if(R.EventId==E.EventId&&R.ActionId==E.ActionId&&R.SubhitId==E.SubhitId&&SameFacts(R.Action,E.Action))Found=true;if(!Found)return false;}}
  return ValidWeaponRuntime(V);
 }
public:
 // ReceiptId belongs to one persistent per-character external domain shared by spend/restore.
 // The caller advances StepTo first. Failure consumes no ID; positive success is single-use.
 bool TrySpendExternalFocus(double Now,double Amount,std::uint64_t ReceiptId){
  if(!ExternalFocusReady(Now,Amount,ReceiptId)||Amount>S.Budget.Focus-S.Budget.ReservedFocus)return false;
  const double After=S.Budget.Focus-Amount;if(After>=S.Budget.Focus||After<S.Budget.ReservedFocus)return false;
  RecordFocus(EFocusChange::ExternalSpend,ReceiptId,Amount,Amount,S.Budget.Focus,After,S.Budget.ReservedFocus);
  S.Budget.Focus=After;S.Budget.HasActualSpend=true;S.Budget.LastActualSpend=S.Time;return true;
 }
 double RestoreExternalFocus(double Now,double Amount,std::uint64_t ReceiptId){
  if(!ExternalFocusReady(Now,Amount,ReceiptId))return 0;
  const double After=S.Budget.Focus+std::min(Amount,100-S.Budget.Focus),Applied=After-S.Budget.Focus;
  if(Applied<=0)return 0;
  RecordFocus(EFocusChange::ExternalRestore,ReceiptId,Amount,Applied,S.Budget.Focus,After,S.Budget.ReservedFocus);
  S.Budget.Focus=After;return Applied;
 }
 explicit FWeaponActionsKernel(EWeapon W=EWeapon::SWD001,std::uint64_t Id=1,double Ammo=0,double Focus=100){S.EquippedId=Id;S.Instances.push_back({W,Id,Ammo,0,0});S.Registrations.push_back({ERegistrationKind::Initial,S.Instances.back(),0,0,1,1});S.Budget.Focus=S.InitialFocus=Focus;}
 const FState& State()const{return S;}
 const FInstance* Instance(std::uint64_t Id)const{for(const auto& I:S.Instances)if(I.InstanceId==Id)return &I;return nullptr;}
 FImportResult ImportResolvedWeapon(double Now,const FInstance& Imported,std::uint64_t ReceiptId){
  if(!ValidState(S))return {};
  for(const auto& R:S.Registrations)if(R.Kind==ERegistrationKind::ResolvedImport&&R.ReceiptId==ReceiptId)return R.AtTime==Now&&SameInstance(R.Initial,Imported)?FImportResult{true,true}:FImportResult{};
  if(!Finite(Now)||Now!=S.Time||!ValidImportedInstance(Imported)||S.Budget.Dead||!ReceiptId||ReceiptId<S.NextImportReceiptId||ReceiptId==std::numeric_limits<std::uint64_t>::max()||Instance(Imported.InstanceId))return {};
  auto Next=S;Next.Instances.push_back(Imported);Next.Registrations.push_back({ERegistrationKind::ResolvedImport,Imported,Now,ReceiptId,S.NextActionId,S.NextEventId});Next.NextImportReceiptId=ReceiptId+1;
  if(!ValidState(Next))return {};S=std::move(Next);return {true,false};
 }
 bool RegisterWeapon(EWeapon W,std::uint64_t Id,double Ammo){const auto* D=DungeonContentCombat::GetWeaponDefinition(W);if(!D||Id==0||Instance(Id)||!MagazineCount(Ammo,D->Magazine))return false;S.Instances.push_back({W,Id,Ammo,0,0});S.Registrations.push_back({ERegistrationKind::Legacy,S.Instances.back(),S.Time,0,S.NextActionId,S.NextEventId});return true;}
 // Adapter calls this only after its real switch/equip action commits. No free Q action here.
 bool EquipCompleted(std::uint64_t Id){if(!Instance(Id)||S.Action.Active||S.Budget.Dead||!S.Budget.Grounded)return false;S.EquippedId=Id;S.AutoReloadPendingId=0;PendingPrimary=false;return true;}
 bool TryStart(EAction Type,double Now,const FContext& C={},bool Fresh=true){
  if(!Finite(Now)||Now!=S.Time||!ValidContext(C)||!Fresh||!C.CanStart||S.Budget.Dead||C.Grounded!=S.Budget.Grounded)return false;
  if(S.Action.Active){const auto& A=S.Action;if(Type==EAction::Primary&&A.Type==EAction::Primary&&!A.StartedAirborne&&S.Budget.Grounded&&S.Time>=A.ActiveEnd&&S.Time>=A.End-.12&&S.Time<A.End&&!PendingPrimary){PendingPrimary=true;return true;}return false;}
  return Start(Type,C);
 }
 // Context is constant over this interval. Split at stat, ground, origin and world changes.
 // Drain and consume returned events before capturing the enclosing world batch.
 std::vector<FEvent> StepTo(double Now,const FContext& C={}){
  if(!Finite(Now)||Now<S.Time||!ValidContext(C)||C.Grounded!=S.Budget.Grounded)return {};
  if(S.AutoReloadPendingId&&!S.Action.Active&&S.Budget.Grounded&&C.CanStart)StartReload(C);
  while(S.Action.Active){
   const auto& A=S.Action;const double Next=A.Type==EAction::Reload?A.End:!A.Locked?A.LockAt:A.NextSubhit<Subhits(A)?SubhitAt(A,A.NextSubhit):A.End;if(Next>Now)break;Advance(Next,C);
   if(S.Action.Type==EAction::Reload){auto* I=MutableInstance(S.Action.InstanceId);const double Previous=I->Ammo;I->Ammo=Def(S.Action)->Magazine;S.Action.Active=false;S.Action.Terminal=EEvent::ReloadCompleted;SetPhase();RecordWeaponRuntime(EWeaponMutation::ReloadCompleted,Previous,I->CooldownDeadline);Emit(EEvent::ReloadCompleted,S.Time);}
   else if(!S.Action.Locked)Lock(C);
   else if(S.Action.NextSubhit<Subhits(S.Action))Issue(C);
   else {
    const bool Buffered=PendingPrimary,Primary=S.Action.Type==EAction::Primary,Air=S.Action.StartedAirborne;const auto* I=Instance(S.Action.InstanceId);const bool Empty=I->Ammo==0&&S.Action.AmmoCost>0;
    S.Action.Active=false;S.Action.Terminal=EEvent::Completed;PendingPrimary=false;SetPhase();Emit(EEvent::Completed,S.Time);
    if(Empty){S.AutoReloadPendingId=I->InstanceId;if(S.Budget.Grounded)StartReload(C);}
    else if(Buffered&&Primary&&!Air&&S.Budget.Grounded&&C.CanStart)Start(EAction::Primary,C);
   }
  }
  Advance(Now,C);auto Events=std::move(S.PendingEvents);S.PendingEvents.clear();return Events;
 }
 bool PressReload(double Now,const FContext& C={},bool Fresh=true){if(!Finite(Now)||Now!=S.Time||!ValidContext(C)||!Fresh||C.Grounded!=S.Budget.Grounded)return false;if(S.Action.Active&&S.Action.Type==EAction::Reload){S.Action.Active=false;S.Action.Terminal=EEvent::ReloadCancelled;S.LastReloadCancelTime=S.Time;S.AutoReloadPendingId=0;PendingPrimary=false;SetPhase();Emit(EEvent::ReloadCancelled,S.Time);return true;}return StartReload(C);}
 bool Interrupt(EInterrupt Reason){
  if(static_cast<unsigned>(Reason)>static_cast<unsigned>(EInterrupt::ExclusiveAction))return false;
  if(Reason==EInterrupt::ReverseBeforeLock&&(!S.Action.Active||S.Action.Type!=EAction::Primary||S.Action.Locked||S.Time>=S.Action.LockAt))return false;
  if(S.Action.Active&&(Reason==EInterrupt::SwitchWeapon||Reason==EInterrupt::ExclusiveAction)&&S.Action.Type!=EAction::Reload)return false;
  if(S.Action.Active){ReleaseReservation();const bool Reload=S.Action.Type==EAction::Reload;S.Action.Active=false;S.Action.Terminal=Reload?EEvent::ReloadCancelled:EEvent::Interrupted;if(Reload)S.LastReloadCancelTime=S.Time;SetPhase();Emit(S.Action.Terminal,S.Time);}
  PendingPrimary=false;S.AutoReloadPendingId=0;if(Reason==EInterrupt::Death)S.Budget.Dead=true;return true;
 }
 // Damage at an endpoint preempts an event not yet processed at that same time.
 // Earlier real deadlines may never be skipped. The candidate is installed only
 // after a valid terminal state exists; no snapshot edits or emission refunds.
 bool InterruptAt(double Now,EInterrupt Reason,const FContext& C={}){
  if(!Finite(Now)||Now<S.Time||!ValidContext(C)||C.Grounded!=S.Budget.Grounded||!ValidState(S)
    ||static_cast<unsigned>(Reason)>static_cast<unsigned>(EInterrupt::ExclusiveAction))return false;
  const auto& A=S.Action;
  if(Reason==EInterrupt::ReverseBeforeLock&&(!A.Active||A.Type!=EAction::Primary||A.Locked||Now>=A.LockAt))return false;
  if(A.Active&&(Reason==EInterrupt::SwitchWeapon||Reason==EInterrupt::ExclusiveAction)&&A.Type!=EAction::Reload)return false;
  if(A.Active){const double Next=A.Type==EAction::Reload?A.End:!A.Locked?A.LockAt:A.NextSubhit<Subhits(A)?SubhitAt(A,A.NextSubhit):A.End;if(Now>Next)return false;}
  auto Candidate=*this;Candidate.Advance(Now,C);if(!Candidate.Interrupt(Reason)||!ValidState(Candidate.S))return false;
  *this=std::move(Candidate);return true;
 }
 bool TryReverseCancel(double Now,double Facing){return Finite(Now)&&Now==S.Time&&Finite(Facing)&&Facing!=0&&S.Action.Active&&Facing*S.Action.Facing<0&&Interrupt(EInterrupt::ReverseBeforeLock);}
 bool NotifyTakeoff(){if(!S.Budget.Grounded||S.Action.Active||S.Budget.Dead)return false;S.Budget.Grounded=false;S.Budget.AirPrimarySpent=false;PendingPrimary=false;return true;}
 // The caller commits endpoint damage first. The interval remains airborne until
 // Now; no earlier real action deadline may be skipped by this ground transition.
 FLandingResult LandAt(double Now,const FContext& AirContext){
  if(!Finite(Now)||Now<S.Time||!ValidContext(AirContext)||AirContext.Grounded||S.Budget.Grounded||!ValidState(S))return {};
  const auto& A=S.Action;
  if(A.Active){const double Next=A.Type==EAction::Reload?A.End:!A.Locked?A.LockAt:A.NextSubhit<Subhits(A)?SubhitAt(A,A.NextSubhit):A.End;if(Now>Next)return {};}
  auto Candidate=*this;auto Events=Candidate.StepTo(Now,AirContext);
  Candidate.S.Budget.Grounded=true;auto GroundContext=AirContext;GroundContext.Grounded=true;
  if(Candidate.S.AutoReloadPendingId&&!Candidate.S.Action.Active&&GroundContext.CanStart)Candidate.StartReload(GroundContext);
  Events.insert(Events.end(),Candidate.S.PendingEvents.begin(),Candidate.S.PendingEvents.end());Candidate.S.PendingEvents.clear();
  if(!ValidState(Candidate.S))return {};
  *this=std::move(Candidate);return {true,std::move(Events)};
 }
 void NotifyLand(){S.Budget.Grounded=true;}
 // Existing melee adapter must check this before its own accepted start and
 // immediately commit the accepted start in the same atomic character batch.
 bool CanAdmitExternalMeleePrimary()const{return !S.Budget.Dead&&!S.Action.Active&&(S.Budget.Grounded||!S.Budget.AirPrimarySpent);}
 bool RecordAcceptedExternalMeleePrimary(){if(!CanAdmitExternalMeleePrimary())return false;if(!S.Budget.Grounded)S.Budget.AirPrimarySpent=true;return true;}
 void ClearPendingInput(){PendingPrimary=false;}
 FState Capture()const{return S;}
 bool Restore(const FState& V){if(!ValidState(V))return false;S=V;PendingPrimary=false;return true;}
};
}
