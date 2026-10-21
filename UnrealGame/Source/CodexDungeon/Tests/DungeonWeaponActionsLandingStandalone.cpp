#if defined(DUNGEON_WEAPON_ACTIONS_LANDING_STANDALONE)
#include "../DungeonWeaponActions.h"
#include <iostream>
#include <limits>
using namespace DungeonWeaponActions;
namespace
{
int Checks=0,Failures=0;
void Check(bool Pass,const char* Name){++Checks;if(!Pass)++Failures;std::cout<<(Pass?"PASS ":"FAIL ")<<Name<<'\n';}
FContext Air(){FContext C;C.Grounded=false;C.FocusRegen=0;return C;}
FContext Ground(){auto C=Air();C.Grounded=true;return C;}
bool Same(const FState& A,const FState& B)
{
 return A.Time==B.Time&&A.NextActionId==B.NextActionId&&A.NextEventId==B.NextEventId
  &&A.AutoReloadPendingId==B.AutoReloadPendingId&&A.LastReloadCancelTime==B.LastReloadCancelTime
  &&A.Budget.Grounded==B.Budget.Grounded&&A.Budget.AirPrimarySpent==B.Budget.AirPrimarySpent
  &&A.Budget.Dead==B.Budget.Dead&&A.Budget.Focus==B.Budget.Focus&&A.Budget.ReservedFocus==B.Budget.ReservedFocus
  &&A.Budget.LastActualSpend==B.Budget.LastActualSpend&&A.Budget.HasActualSpend==B.Budget.HasActualSpend
  &&A.AccruedFocus==B.AccruedFocus&&A.NextFocusMutationId==B.NextFocusMutationId
  &&A.Action.ActionId==B.Action.ActionId&&A.Action.Active==B.Action.Active&&A.Action.Locked==B.Action.Locked
  &&A.Action.Type==B.Action.Type&&A.Action.Terminal==B.Action.Terminal&&A.Action.Start==B.Action.Start
  &&A.Action.End==B.Action.End&&A.Action.NextSubhit==B.Action.NextSubhit&&A.Action.Phase==B.Action.Phase
  &&A.Instances[0].Ammo==B.Instances[0].Ammo&&A.Instances[0].ReservedAmmo==B.Instances[0].ReservedAmmo
  &&A.Instances[0].CooldownDeadline==B.Instances[0].CooldownDeadline&&A.PendingEvents.size()==B.PendingEvents.size()
  &&A.Issued.size()==B.Issued.size()&&A.FocusHistory.size()==B.FocusHistory.size()
  &&A.WeaponRuntimeHistory.size()==B.WeaponRuntimeHistory.size();
}
bool Restores(const FWeaponActionsKernel& K){FWeaponActionsKernel R;return R.Restore(K.Capture());}
std::size_t Count(const std::vector<FEvent>& Events,EEvent Kind,double At)
{std::size_t N=0;for(const auto& E:Events)if(E.Kind==Kind&&E.AtTime==At)++N;return N;}
std::size_t Refills(const FWeaponActionsKernel& K)
{std::size_t N=0;for(const auto& R:K.State().WeaponRuntimeHistory)if(R.Kind==EWeaponMutation::ReloadCompleted)++N;return N;}
void CompleteAirCrossbow(FWeaponActionsKernel& K,const FContext& C)
{K.NotifyTakeoff();K.TryStart(EAction::Primary,0,C);K.StepTo(.68,C);}
}
int main()
{
 const auto C=Air(),G=Ground();
 {
  // A mutation that starts a pending reload before landing must fail this case.
  FWeaponActionsKernel K(EWeapon::XBW001,1,1);CompleteAirCrossbow(K,C);K.StepTo(.695,C);
  Check(!K.State().Action.Active&&K.State().Action.Terminal==EEvent::Completed&&!K.State().Budget.Grounded
   &&K.State().AutoReloadPendingId==1&&K.Instance(1)->Ammo==0,"complete_air_primary_waits_without_reload_progress");
  const auto Shot=K.State().Issued[0].EventId,NextAction=K.State().NextActionId,NextEvent=K.State().NextEventId;
  const auto R=K.LandAt(.70,C);
  Check(R.Accepted&&K.State().Time==.70&&K.State().Budget.Grounded,"landing_commits_exact_endpoint_clock");
  Check(K.State().Action.Active&&K.State().Action.Type==EAction::Reload&&K.State().Action.Start==.70
   &&K.State().Action.End==.70+1.10&&K.State().AutoReloadPendingId==0,"pending_reload_uses_full_landing_relative_1100ms");
  Check(Count(R.Events,EEvent::ReloadStarted,.70)==1&&K.State().NextActionId==NextAction+1
   &&K.State().NextEventId==NextEvent+1&&R.Events.size()==1,"landing_allocates_only_one_reload_action_and_event");
  Check(K.Instance(1)->Ammo==0&&K.State().Issued.size()==1&&K.State().Issued[0].EventId==Shot
   &&K.State().FocusHistory.empty()&&K.State().Budget.Focus==100&&Restores(K),"landing_keeps_spent_ammo_and_existing_event_identity");
  K.StepTo(std::nextafter(.70+1.10,-std::numeric_limits<double>::infinity()),G);
  Check(K.Instance(1)->Ammo==0&&Refills(K)==0,"last_representable_time_before_reload_end_has_no_refill");
  const auto EndEvents=K.StepTo(.70+1.10,G);
  Check(K.Instance(1)->Ammo==1&&Refills(K)==1&&Count(EndEvents,EEvent::ReloadCompleted,.70+1.10)==1
   &&K.State().WeaponRuntimeHistory.back().AtTime==.70+1.10,"actual_refill_and_receipt_occur_once_at_full_deadline");
  Check(K.StepTo(.70+1.10,G).empty()&&Refills(K)==1&&Restores(K),"same_clock_does_not_duplicate_refill_or_events");
 }
 {
  // A mutation that cancels/restarts an active air primary on landing must fail.
  FWeaponActionsKernel K(EWeapon::STF001);K.NotifyTakeoff();K.TryStart(EAction::Primary,0,C);K.StepTo(.02,C);
  const auto A=K.State().Action;const auto Cursor=K.State().NextActionId;
  FWeaponActionsKernel Saved;Check(Saved.Restore(K.Capture()),"active_air_primary_roundtrips_before_landing");
  const auto R=K.LandAt(.04,C);
  Check(R.Accepted&&K.State().Action.Active&&K.State().Action.ActionId==A.ActionId
   &&K.State().Action.Start==A.Start&&K.State().Action.End==A.End&&K.State().Action.StartedAirborne
   &&K.State().Budget.AirPrimarySpent&&K.State().NextActionId==Cursor,"landing_preserves_active_air_primary_timeline_and_id");
  Check(R.Events.empty()&&Restores(K),"predeadline_landing_emits_no_invented_action_event");
  Check(Saved.LandAt(.04,C).Accepted&&Same(K.State(),Saved.State()),"restored_air_primary_has_same_landing_continuation");
  auto CritGround=G;CritGround.Critical=true;K.StepTo(A.ActiveAt,CritGround);
  Check(K.State().Issued.size()==1&&K.State().Issued[0].ActionId==A.ActionId&&K.State().Issued[0].Action.StartedAirborne
   &&K.State().Issued[0].Action.Critical&&K.State().Issued[0].Origin.Height==0,"ground_emission_retains_air_start_and_one_crit_identity");
  Check(K.State().Budget.Focus==90&&K.State().FocusHistory.size()==1&&K.State().FocusHistory[0].MutationId==1
   &&K.State().FocusHistory[0].ReceiptId==K.State().Issued[0].EventId&&Restores(K),"staff_actual_emission_spends_focus_once_after_landing");
  K.StepTo(A.End,CritGround);
  Check(!K.State().Action.Active&&K.State().Action.Terminal==EEvent::Completed&&K.State().Issued.size()==1
   &&K.State().NextActionId==Cursor&&Restores(K),"landed_air_action_finishes_without_restart_or_extra_shot");
 }
 {
  FWeaponActionsKernel K(EWeapon::XBW001,1,1);K.NotifyTakeoff();K.TryStart(EAction::Primary,0,C);
  const auto A=K.State().Action;const auto R=K.LandAt(A.LockAt,C);
  Check(R.Accepted&&K.State().Time==A.LockAt&&K.State().Budget.Grounded&&K.State().Action.Locked
   &&K.Instance(1)->ReservedAmmo==1&&K.Instance(1)->Ammo==1,"exact_lock_landing_processes_reservation_without_spend");
  Check(Count(R.Events,EEvent::Started,0)==1&&Count(R.Events,EEvent::Locked,A.LockAt)==1
   &&K.State().Issued.empty()&&K.State().NextActionId==2&&Restores(K),"exact_lock_events_keep_original_action_and_restore_validity");
  Check(K.StepTo(A.LockAt,G).empty(),"exact_lock_landing_does_not_replay_crit_lock");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.NotifyTakeoff();K.TryStart(EAction::Primary,0,C);
  const auto A=K.State().Action;K.StepTo(A.LockAt,C);auto Emission=C;Emission.Muzzle={12,34,0};
  const auto R=K.LandAt(A.ActiveAt,Emission);
  Check(R.Accepted&&Count(R.Events,EEvent::ProjectileEmitted,A.ActiveAt)==1&&K.State().Budget.Grounded
   &&K.State().Issued.size()==1&&K.State().Issued[0].Origin.X==12&&K.State().Issued[0].Origin.Y==34
   &&K.State().Issued[0].Origin.Height==0,"samepoint_landing_emission_uses_actual_ground_muzzle_once");
  Check(K.State().Budget.Focus==90&&K.State().FocusHistory.size()==1&&K.State().Budget.LastActualSpend==A.ActiveAt
   &&K.StepTo(A.ActiveAt,G).empty()&&Restores(K),"samepoint_landing_emission_has_unique_focus_receipt");
 }
 {
  FWeaponActionsKernel K(EWeapon::XBW001,1,1);K.NotifyTakeoff();K.TryStart(EAction::Primary,0,C);K.StepTo(.16,C);
  const auto R=K.LandAt(.68,C);
  Check(R.Accepted&&Count(R.Events,EEvent::Completed,.68)==1&&Count(R.Events,EEvent::ReloadStarted,.68)==1
   &&K.State().Action.Start==.68&&K.State().Action.End==.68+1.10&&Restores(K),"primary_end_landing_completes_then_starts_full_reload_at_samepoint");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.NotifyTakeoff();K.TryStart(EAction::Primary,0,C);K.StepTo(.02,C);
  for(const double Now:{-.01,.01,std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()})
  {const auto Before=K.Capture();const auto R=K.LandAt(Now,C);Check(!R.Accepted&&R.Events.empty()&&Same(Before,K.State()),"invalid_or_backward_landing_clock_is_atomic_noop");}
  auto Bad=C;Bad.Grounded=true;auto Before=K.Capture();
  auto R=K.LandAt(.03,Bad);Check(!R.Accepted&&R.Events.empty()&&Same(Before,K.State()),"landing_requires_matching_prelanding_air_context");
  Bad=C;Bad.FocusRegen=-1;Before=K.Capture();R=K.LandAt(.03,Bad);
  Check(!R.Accepted&&R.Events.empty()&&Same(Before,K.State()),"invalid_landing_context_is_atomic_noop");
  Before=K.Capture();R=K.LandAt(K.State().Action.ActiveAt,C);
  Check(!R.Accepted&&R.Events.empty()&&Same(Before,K.State()),"landing_cannot_skip_an_earlier_real_lock_deadline");
  Check(K.LandAt(.03,C).Accepted&&Restores(K),"valid_landing_retry_after_rejections_keeps_original_action");
  Before=K.Capture();R=K.LandAt(.03,C);
  Check(!R.Accepted&&R.Events.empty()&&Same(Before,K.State()),"duplicate_landing_cannot_reset_air_slot_or_action");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.NotifyTakeoff();K.TryStart(EAction::Primary,0,C);
  const auto A=K.State().Action;K.StepTo(A.LockAt,C);const auto Before=K.Capture();
  const auto R=K.LandAt(A.End,C);
  Check(!R.Accepted&&R.Events.empty()&&Same(Before,K.State()),"landing_cannot_skip_an_earlier_actual_emission_deadline");
  Check(K.LandAt(A.ActiveAt,C).Accepted&&Restores(K),"landing_at_next_real_emission_deadline_is_valid_retry");
 }
 {
  FWeaponActionsKernel K(EWeapon::XBW001,1,1);CompleteAirCrossbow(K,C);K.StepTo(.695,C);
  const auto Saved=K.Capture();FWeaponActionsKernel R;
  Check(R.Restore(Saved)&&R.LandAt(.70,C).Accepted&&R.State().Action.Start==.70&&Restores(R),"restored_pending_air_reload_still_starts_at_actual_landing");
 }
 for(const auto Reason:{EInterrupt::PoiseBreak,EInterrupt::Death})
 {
  FWeaponActionsKernel K(EWeapon::XBW001,1,1);CompleteAirCrossbow(K,C);K.StepTo(.695,C);
  Check(K.InterruptAt(.70,Reason,C)&&K.State().AutoReloadPendingId==0,"damage_first_clears_air_pending_reload_at_landing_clock");
  const auto R=K.LandAt(.70,C);
  Check(R.Accepted&&K.State().Budget.Grounded&&!K.State().Action.Active&&K.Instance(1)->Ammo==0
   &&Count(R.Events,EEvent::ReloadStarted,.70)==0&&K.State().NextActionId==2&&Restores(K),"landing_after_damage_does_not_start_reload_or_refill");
 }
 for(const auto Reason:{EInterrupt::PoiseBreak,EInterrupt::Death})
 {
  FWeaponActionsKernel K(EWeapon::STF001);K.NotifyTakeoff();K.TryStart(EAction::Primary,0,C);
  const auto A=K.State().Action;K.StepTo(A.LockAt,C);
  Check(K.InterruptAt(A.ActiveAt,Reason,C),"samepoint_landing_damage_can_preempt_unprocessed_air_emission");
  const auto R=K.LandAt(A.ActiveAt,C);
  Check(R.Accepted&&K.State().Budget.Grounded&&!K.State().Action.Active&&K.State().Budget.Focus==100
   &&K.State().Issued.empty()&&K.State().FocusHistory.empty()&&Count(R.Events,EEvent::ProjectileEmitted,A.ActiveAt)==0
   &&Count(R.Events,EEvent::Interrupted,A.ActiveAt)==1&&Restores(K),"damage_before_landing_never_emits_or_refunds_unemitted_cost");
 }
 {
  FWeaponActionsKernel K(EWeapon::STF001,1,0,50);K.NotifyTakeoff();auto Regen=C;Regen.FocusRegen=12;
  const auto R=K.LandAt(2,Regen);
  Check(R.Accepted&&K.State().Time==2&&K.State().Budget.Focus==74&&Restores(K),"idle_landing_integrates_only_actual_prelanding_regeneration");
  const auto Before=K.Capture();const auto Again=K.LandAt(2,Regen);
  Check(!Again.Accepted&&Same(Before,K.State()),"duplicate_idle_landing_does_not_double_regenerate");
 }
 std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<'\n';return Failures?1:0;
}
#endif
