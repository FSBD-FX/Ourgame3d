#if defined(DUNGEON_WEAPON_ACTIONS_ENDPOINT_STANDALONE)
#include "../DungeonWeaponActions.h"
#include <iostream>
#include <limits>
using namespace DungeonWeaponActions;
namespace
{
int Checks=0,Failures=0;
void Check(bool Pass,const char* Name){++Checks;if(!Pass)++Failures;std::cout<<(Pass?"PASS ":"FAIL ")<<Name<<'\n';}
FContext Context(){FContext C;C.FocusRegen=0;return C;}
bool Same(const FState& A,const FState& B)
{
 return A.Time==B.Time&&A.NextActionId==B.NextActionId&&A.NextEventId==B.NextEventId
  &&A.Budget.Focus==B.Budget.Focus&&A.Budget.ReservedFocus==B.Budget.ReservedFocus
  &&A.Budget.LastActualSpend==B.Budget.LastActualSpend&&A.Budget.HasActualSpend==B.Budget.HasActualSpend
  &&A.Budget.Dead==B.Budget.Dead&&A.AccruedFocus==B.AccruedFocus&&A.AutoReloadPendingId==B.AutoReloadPendingId
  &&A.Action.Active==B.Action.Active&&A.Action.Locked==B.Action.Locked&&A.Action.Terminal==B.Action.Terminal
  &&A.Action.NextSubhit==B.Action.NextSubhit&&A.Action.Phase==B.Action.Phase
  &&A.Instances[0].Ammo==B.Instances[0].Ammo&&A.Instances[0].ReservedAmmo==B.Instances[0].ReservedAmmo
  &&A.Instances[0].CooldownDeadline==B.Instances[0].CooldownDeadline&&A.PendingEvents.size()==B.PendingEvents.size()
  &&A.Issued.size()==B.Issued.size()&&A.FocusHistory.size()==B.FocusHistory.size()
  &&A.WeaponRuntimeHistory.size()==B.WeaponRuntimeHistory.size();
}
bool Restores(const FWeaponActionsKernel& K)
{
 FWeaponActionsKernel R;return R.Restore(K.Capture());
}
bool TerminalAt(FWeaponActionsKernel& K,double At,EEvent Kind,const FContext& C)
{
 const auto Events=K.StepTo(At,C);bool Found=false;
 for(const auto& E:Events)if(E.Kind==Kind)Found=E.AtTime==At;
 return Found&&Restores(K);
}
}
int main()
{
 const auto C=Context();
 for(const auto Weapon:{EWeapon::XBW001,EWeapon::STF001})for(const auto Reason:{EInterrupt::PoiseBreak,EInterrupt::Death})
 {
  FWeaponActionsKernel K(Weapon,1,Weapon==EWeapon::XBW001?1:0);K.TryStart(EAction::Primary,0,C);
  const auto A=K.State().Action;K.StepTo(A.LockAt,C);
  Check(K.InterruptAt(A.ActiveAt,Reason,C),"exact_emission_interrupt_accepted");
  Check(K.State().Time==A.ActiveAt&&!K.State().Action.Active&&K.State().Action.Terminal==EEvent::Interrupted
    &&K.State().Budget.Dead==(Reason==EInterrupt::Death),"terminal_clock_and_reason_exact");
  Check(K.State().Issued.empty()&&K.State().FocusHistory.empty()&&K.State().Budget.Focus==100
    &&!K.State().Budget.HasActualSpend&&K.State().Budget.ReservedFocus==0&&K.Instance(1)->ReservedAmmo==0
    &&K.Instance(1)->Ammo==(Weapon==EWeapon::XBW001?1:0),"unemitted_cost_and_receipts_absent");
  Check(TerminalAt(K,A.ActiveAt,EEvent::Interrupted,C),"exact_interrupt_timestamp_drains_once_and_restores");
  Check(K.StepTo(A.ActiveAt,C).empty(),"terminal_not_replayed_at_same_time");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.TryStart(EAction::Skill,0,C);const auto A=K.State().Action;
  Check(K.InterruptAt(A.LockAt,EInterrupt::PoiseBreak,C),"exact_unprocessed_lock_can_interrupt_before_lock");
  Check(!K.State().Action.Locked&&K.Instance(1)->CooldownDeadline==0&&K.State().Budget.ReservedFocus==0
    &&K.State().WeaponRuntimeHistory.empty(),"lock_deadline_interrupt_does_not_invent_cd_or_reservation");
  Check(TerminalAt(K,A.LockAt,EEvent::Interrupted,C),"prelock_interrupt_snapshot_valid");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.TryStart(EAction::Skill,0,C);const auto Before=K.Capture();
  Check(!K.InterruptAt(K.State().Action.ActiveAt,EInterrupt::PoiseBreak,C)&&Same(Before,K.State()),"cannot_skip_earlier_lock");
  K.StepTo(K.State().Action.LockAt,C);const auto Locked=K.Capture();
  Check(!K.InterruptAt(K.State().Action.End,EInterrupt::Death,C)&&Same(Locked,K.State()),"cannot_skip_earlier_unemitted_subhit");
  Check(K.InterruptAt(K.State().Action.ActiveAt,EInterrupt::PoiseBreak,C),"same_id_valid_retry_after_rejected_future_interrupt");
  Check(K.Instance(1)->CooldownDeadline==Locked.Instances[0].CooldownDeadline&&K.State().Action.Locked&&Restores(K),"genuinely_locked_cd_and_snapshot_survive_interrupt");
 }
 {
  FWeaponActionsKernel K(EWeapon::SPR001);K.TryStart(EAction::Skill,0,C);K.StepTo(.18,C);const auto Before=K.Capture();
  Check(!K.InterruptAt(.38,EInterrupt::Death,C)&&Same(Before,K.State()),"cannot_skip_earlier_independent_skill_subhit");
  Check(K.InterruptAt(.28,EInterrupt::PoiseBreak,C)&&K.State().Issued.size()==1&&K.State().Action.NextSubhit==1
    &&TerminalAt(K,.28,EEvent::Interrupted,C),"exact_second_subhit_keeps_first_and_releases_rest");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.TryStart(EAction::Primary,0,C);const auto A=K.State().Action;K.StepTo(A.ActiveAt,C);
  const auto Issued=K.State().Issued[0].EventId,Mutation=K.State().FocusHistory[0].MutationId;
  Check(K.InterruptAt(A.End,EInterrupt::PoiseBreak,C),"already_emitted_primary_interrupt_at_end");
  Check(K.State().Budget.Focus==90&&K.State().Budget.HasActualSpend&&K.State().Budget.LastActualSpend==A.ActiveAt
    &&K.State().Issued.size()==1&&K.State().Issued[0].EventId==Issued&&K.State().FocusHistory.size()==1
    &&K.State().FocusHistory[0].MutationId==Mutation&&Restores(K),"already_emitted_cost_and_history_never_refunded");
 }
 {
  FWeaponActionsKernel K(EWeapon::XBW001,1,1);K.TryStart(EAction::Primary,0,C);const auto A=K.State().Action;K.StepTo(A.ActiveAt,C);
  Check(K.InterruptAt(A.End,EInterrupt::PoiseBreak,C)&&K.State().NextActionId==2&&K.State().AutoReloadPendingId==0
    &&K.Instance(1)->Ammo==0&&TerminalAt(K,A.End,EEvent::Interrupted,C),"primary_end_damage_preempts_new_auto_reload_without_refill");
 }
 {
  FWeaponActionsKernel K(EWeapon::XBW001,1,1);K.TryStart(EAction::Primary,0,C);const auto End=K.State().Action.End;K.StepTo(End,C);
  const auto R=K.State().Action;
  Check(R.Type==EAction::Reload&&K.InterruptAt(R.End,EInterrupt::PoiseBreak,C)&&K.Instance(1)->Ammo==0
    &&K.State().LastReloadCancelTime==R.End&&TerminalAt(K,R.End,EEvent::ReloadCancelled,C),"exact_reload_completion_damage_cancels_without_free_refill");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.TryStart(EAction::Primary,0,C);K.StepTo(.04,C);
  for(const double Now:{-.01,.03,std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()})
  {const auto Before=K.Capture();Check(!K.InterruptAt(Now,EInterrupt::PoiseBreak,C)&&Same(Before,K.State()),"invalid_or_backward_clock_is_atomic_noop");}
  auto Bad=C;Bad.Grounded=false;auto Before=K.Capture();
  Check(!K.InterruptAt(.05,EInterrupt::PoiseBreak,Bad)&&Same(Before,K.State()),"mismatched_ground_context_is_noop");
  Bad=C;Bad.FocusRegen=-1;Before=K.Capture();
  Check(!K.InterruptAt(.05,EInterrupt::PoiseBreak,Bad)&&Same(Before,K.State()),"invalid_context_is_noop");
  Before=K.Capture();Check(!K.InterruptAt(.05,EInterrupt(99),C)&&Same(Before,K.State()),"invalid_reason_is_noop");
  Check(!K.InterruptAt(.05,EInterrupt::ExclusiveAction,C)&&Same(Before,K.State()),"exclusive_action_does_not_cancel_primary");
  Check(K.InterruptAt(.05,EInterrupt::ReverseBeforeLock,C)&&K.State().Time==.05&&Restores(K),"legal_prelock_reverse_has_exact_clock");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.TryStart(EAction::Primary,0,C);const auto A=K.State().Action;const auto Before=K.Capture();
  Check(!K.InterruptAt(A.LockAt,EInterrupt::ReverseBeforeLock,C)&&Same(Before,K.State()),"reverse_at_exact_lock_is_rejected_without_time_mutation");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001,1,0,50);auto Regen=C;Regen.FocusRegen=12;
  Check(K.InterruptAt(2,EInterrupt::PoiseBreak,Regen)&&K.State().Time==2&&K.State().Budget.Focus==74&&Restores(K),"idle_interrupt_integrates_authoritative_regen_once");
  Check(K.InterruptAt(2,EInterrupt::PoiseBreak,Regen)&&K.State().Budget.Focus==74,"same_clock_idle_interrupt_does_not_double_regen");
 }
 std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<'\n';return Failures?1:0;
}
#endif
