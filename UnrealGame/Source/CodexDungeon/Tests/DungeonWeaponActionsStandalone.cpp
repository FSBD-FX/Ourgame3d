#if defined(DUNGEON_WEAPON_ACTIONS_STANDALONE)
#include "../DungeonWeaponActions.h"
#include <iostream>
#include <limits>
using namespace DungeonWeaponActions;
int Checks=0,Failures=0;
void Check(bool Pass,const char* Name){++Checks;if(!Pass)++Failures;std::cout<<(Pass?"PASS ":"FAIL ")<<Name<<'\n';}
bool Near(double A,double B){return std::abs(A-B)<1e-9;}
FContext C(){FContext R;R.FocusRegen=0;return R;}
int Count(const std::vector<FEvent>& Events,EEvent Kind){int N=0;for(const auto& E:Events)if(E.Kind==Kind)++N;return N;}
const FEvent* Find(const std::vector<FEvent>& Events,EEvent Kind,std::uint32_t Sub=0){for(const auto& E:Events)if(E.Kind==Kind&&E.SubhitId==Sub)return &E;return nullptr;}
void ExternalFocusCases(){
 {FWeaponActionsKernel K;auto X=C();X.FocusRegen=12;
  Check(K.TrySpendExternalFocus(0,50,7001)&&Near(K.State().Budget.Focus,50)&&K.State().Budget.HasActualSpend&&Near(K.State().Budget.LastActualSpend,0),"external_real_spend50_has_receipt_and_updates_actual_timer");
  Check(K.State().Version==3&&K.State().FocusHistory.size()==1,"focus_snapshot_schema3_retains_external_facts");
  K.StepTo(1,X);Check(Near(K.State().Budget.Focus,50),"external_spend_has_same_one_second_recovery_delay");
  Check(Near(K.RestoreExternalFocus(1,45,7002),45)&&Near(K.State().Budget.Focus,95)&&Near(K.State().Budget.LastActualSpend,0),"external_restore45_does_not_restart_spend_delay");
  K.StepTo(1.25,X);Check(Near(K.State().Budget.Focus,98),"current_recovery_integrates_once_after_external_restore");
  const auto Focus=K.State().Budget.Focus;const auto Size=K.State().FocusHistory.size();
  Check(!K.TrySpendExternalFocus(1.25,10,7001)&&Near(K.RestoreExternalFocus(1.25,1,7002),0)&&Near(K.State().Budget.Focus,Focus)&&K.State().FocusHistory.size()==Size,"spend_and_restore_receipt_replay_has_no_second_effect");
  Check(!K.TrySpendExternalFocus(1.25,1,7002)&&Near(K.RestoreExternalFocus(1.25,1,7001),0),"external_receipt_domain_is_shared_across_both_operations");
  FWeaponActionsKernel L;Check(L.Restore(K.Capture())&&Near(L.State().Budget.Focus,98),"external_history_and_trailing_regeneration_survive_restore");
  Check(!L.TrySpendExternalFocus(1.25,10,7001)&&Near(L.RestoreExternalFocus(1.25,10,7002),0),"restored_external_receipts_remain_single_use");
 }
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Skill,0,X);K.StepTo(.181,X);
  Check(!K.TrySpendExternalFocus(.181,77,8001)&&Near(K.State().Budget.Focus,100)&&Near(K.State().Budget.ReservedFocus,24)&&!K.State().Budget.HasActualSpend&&K.State().FocusHistory.empty(),"failed_external_spend_cannot_invade_locked_reservation_or_leave_receipt");
  Check(K.TrySpendExternalFocus(.181,76,8001)&&Near(K.State().Budget.Focus,24)&&Near(K.State().Budget.ReservedFocus,24),"external_spend_uses_only_available_focus_and_failed_id_can_retry");
  K.StepTo(.45,X);Check(Near(K.State().Budget.Focus,0)&&Near(K.State().Budget.ReservedFocus,0)&&Near(K.State().Budget.LastActualSpend,.45)&&K.State().FocusHistory.size()==2,"actual_emission_after_external_spend_consumes_reserved_focus_once");
  FWeaponActionsKernel L;Check(L.Restore(K.Capture())&&L.StepTo(.45,X).empty(),"issued_and_external_spends_are_both_validated_without_replay");
  const auto Event=K.State().Issued.empty()?0:K.State().Issued[0].EventId;
  Check(Event!=0&&Near(K.RestoreExternalFocus(.45,10,Event),10),"external_receipt_and_internal_event_ids_have_explicit_distinct_domains");
 }
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Skill,0,X);
  Check(K.TrySpendExternalFocus(0,90,1),"external_spend_before_lock_is_real");auto R=K.StepTo(.181,X);
  Check(Count(R,EEvent::LockFailed)==1&&Near(K.State().Budget.Focus,10)&&Near(K.State().Budget.ReservedFocus,0)&&K.State().Budget.HasActualSpend,"external_spend_can_make_later_lock_fail_without_refund");
  FWeaponActionsKernel L;Check(L.Restore(K.Capture()),"external_only_actual_spend_no_issued_event_restores_legally");
 }
 {FWeaponActionsKernel K(EWeapon::STF001,1,0,40);auto X=C();K.TryStart(EAction::Skill,0,X);K.StepTo(.181,X);
  Check(Near(K.RestoreExternalFocus(.181,80,6),60)&&Near(K.State().Budget.ReservedFocus,24)&&!K.State().Budget.HasActualSpend,"restore_while_locked_caps_total100_without_releasing_reservation_or_inventing_spend");
  FWeaponActionsKernel L;Check(L.Restore(K.Capture())&&Near(L.State().Budget.ReservedFocus,24),"restore_receipt_and_unemitted_reservation_survive_together");
  L.StepTo(.45,X);Check(Near(L.State().Budget.Focus,76)&&Near(L.State().Budget.ReservedFocus,0),"restored_external_recovery_does_not_duplicate_real_emission");
 }
 {FWeaponActionsKernel K(EWeapon::SWD001,1,0,80);
  Check(Near(K.RestoreExternalFocus(0,50,9001),20)&&Near(K.State().Budget.Focus,100)&&!K.State().Budget.HasActualSpend,"restore_returns_actual_cap20_not_requested50_and_does_not_invent_spend");
  const auto Size=K.State().FocusHistory.size();Check(Near(K.RestoreExternalFocus(0,50,9002),0)&&K.State().FocusHistory.size()==Size,"full_focus_no_effect_restore_does_not_claim_receipt");
  K.TrySpendExternalFocus(0,10,9003);Check(Near(K.RestoreExternalFocus(0,50,9002),10),"failed_full_cap_receipt_can_retry_when_real_restore_exists");
  K.TrySpendExternalFocus(0,10,9004);Check(Near(K.RestoreExternalFocus(0,50,9001),0)&&Near(K.State().Budget.Focus,90),"successful_old_restore_cannot_refund_again_after_later_spend");
 }
 {FWeaponActionsKernel K(EWeapon::SWD001,1,0,50);
  for(double Amount:{0.,-1.,std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),1e-300})
   Check(!K.TrySpendExternalFocus(0,Amount,1)&&Near(K.RestoreExternalFocus(0,Amount,1),0),"invalid_or_no_actual_amount_rejected_without_receipt");
  for(double Now:{-1.,.001,std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()})
   Check(!K.TrySpendExternalFocus(Now,1,1)&&Near(K.RestoreExternalFocus(Now,1,1),0),"noncurrent_or_nonfinite_clock_rejected");
  Check(!K.TrySpendExternalFocus(0,1,0)&&Near(K.RestoreExternalFocus(0,1,0),0)&&Near(K.State().Budget.Focus,50)&&K.State().FocusHistory.empty(),"zero_receipt_and_invalid_calls_leave_no_partial_fact");
  Check(K.TrySpendExternalFocus(0,1,1),"valid_retry_after_invalid_call_uses_same_receipt");
  const auto Size=K.State().FocusHistory.size();K.Interrupt(EInterrupt::Death);
  Check(!K.TrySpendExternalFocus(0,1,2)&&Near(K.RestoreExternalFocus(0,1,2),0)&&K.State().FocusHistory.size()==Size,"dead_character_cannot_spend_or_receive_external_focus");
 }
 {FWeaponActionsKernel K(EWeapon::SWD001,1,0,50);auto Bad=K.Capture();
  FFocusReceipt R;R.MutationId=1;R.ReceiptId=1;R.Kind=EFocusChange::ExternalSpend;R.Requested=R.Applied=1e-300;R.Before=R.After=50;
  Bad.FocusHistory.push_back(R);Bad.NextFocusMutationId=2;Bad.Budget.HasActualSpend=true;
  Check(!K.Restore(Bad),"saved_spend_fact_must_have_representable_real_decrease");
 }
 {FWeaponActionsKernel K(EWeapon::SWD001,1,0,101);K.StepTo(1);
  Check(!K.TrySpendExternalFocus(1,1,1)&&Near(K.RestoreExternalFocus(1,1,1),0)&&K.State().FocusHistory.empty(),"invalid_original_focus_cannot_be_laundered_by_regen_cap_before_external_receipt");
  FWeaponActionsKernel BadRegistry(EWeapon::SWD001,1,1,50);BadRegistry.RegisterWeapon(EWeapon::SWD001,2,0);BadRegistry.EquipCompleted(2);
  Check(!BadRegistry.TrySpendExternalFocus(0,1,1)&&Near(BadRegistry.RestoreExternalFocus(0,1,1),0)&&BadRegistry.State().FocusHistory.empty(),"equipping_valid_instance_cannot_hide_invalid_original_registry_for_external_receipt");
 }
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Skill,0,X);K.StepTo(.2,X);
  K.TrySpendExternalFocus(.2,70,1);K.RestoreExternalFocus(.2,10,2);K.StepTo(1,X);K.RegisterWeapon(EWeapon::SWD001,2,0);K.EquipCompleted(2);K.TryStart(EAction::Skill,1,X);auto Bad=K.Capture();
  if(Bad.FocusHistory.size()!=3)Check(false,"reservation_cross_fact_fixture_has_all_receipts");
  else {
   Bad.FocusHistory[0].Requested=Bad.FocusHistory[0].Applied=90;Bad.FocusHistory[0].After=10;Bad.FocusHistory[0].ReservedBefore=0;
   Bad.FocusHistory[1].Before=10;Bad.FocusHistory[1].Requested=Bad.FocusHistory[1].Applied=30;Bad.FocusHistory[1].ReservedBefore=0;
   Check(!K.Restore(Bad),"historical_external_spend_must_respect_reservation_proved_by_future_issued_action");
  }
 }
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);
  Check(K.TrySpendExternalFocus(0,5,1001),"full_state_guard_accepts_external_spend_after_start_before_step");
  K.StepTo(K.State().Action.LockAt,X);const auto LockTime=K.State().Time;
  Check(K.TrySpendExternalFocus(LockTime,5,1002)&&Near(K.State().Budget.ReservedFocus,10),"full_state_guard_accepts_spend_at_exact_locked_clock");
  K.StepTo(.22,X);Check(Near(K.RestoreExternalFocus(.22,10,1003),10)&&K.TrySpendExternalFocus(.22,1,1004),"same_emission_clock_external_changes_follow_real_emission_fact");
  FWeaponActionsKernel L;Check(L.Restore(K.Capture()),"exact_lock_and_same_emission_clock_receipts_roundtrip");
  K.StepTo(.67,X);K.RegisterWeapon(EWeapon::SWD001,2,0);K.EquipCompleted(2);K.TryStart(EAction::Skill,.67,X);K.StepTo(K.State().Action.LockAt,X);
  Check(K.TrySpendExternalFocus(K.State().Time,1,1005)&&L.Restore(K.Capture()),"historical_focus_reservations_roundtrip_after_different_current_action");
 }
 {FWeaponActionsKernel K(EWeapon::STF001,1,0,75);auto X=C();X.FocusRegen=12;
  K.TrySpendExternalFocus(0,20,1);K.StepTo(1.5,X);K.RestoreExternalFocus(1.5,10,2);K.TryStart(EAction::Primary,1.5,X);K.StepTo(1.72,X);K.StepTo(2,X);
  const auto Good=K.Capture();FWeaponActionsKernel L;Check(L.Restore(Good),"combined_initial_external_emission_and_regeneration_snapshot_restores");
  if(Good.FocusHistory.size()<3){Check(false,"combined_focus_fixture_has_all_three_discrete_facts");}
  else {
   auto Bad=Good;Bad.Version=1;Check(!L.Restore(Bad),"old_v1_shape_not_silently_accepted_as_v2");
   Bad=Good;Bad.FocusHistory.erase(Bad.FocusHistory.begin());Check(!L.Restore(Bad),"missing_external_spend_fact_rejected");
   Bad=Good;Bad.FocusHistory.erase(Bad.FocusHistory.begin()+1);Check(!L.Restore(Bad),"missing_external_restore_fact_rejected");
   Bad=Good;Bad.FocusHistory.pop_back();Check(!L.Restore(Bad),"issued_consumption_requires_corresponding_focus_fact");
   Bad=Good;Bad.Budget.Focus+=1;Check(!L.Restore(Bad),"bare_budget_focus_increase_rejected_without_accrual_fact");
   Bad=Good;Bad.Budget.LastActualSpend=0;Check(!L.Restore(Bad),"last_spend_must_cover_external_and_emission_facts");
   Bad=Good;Bad.InitialFocus-=1;Check(!L.Restore(Bad),"forged_initial_balance_rejected_against_receipt_chain");
   Bad=Good;Bad.FocusHistory[0].Applied+=1;Check(!L.Restore(Bad),"forged_external_spend_amount_rejected");
   Bad=Good;Bad.FocusHistory[1].After+=1;Check(!L.Restore(Bad),"forged_external_refund_rejected");
   Bad=Good;Bad.FocusHistory[1].ReceiptId=Bad.FocusHistory[0].ReceiptId;Check(!L.Restore(Bad),"duplicate_external_receipt_rejected_in_saved_state");
   Bad=Good;Bad.FocusHistory[1].AtTime=Good.Time+1;Check(!L.Restore(Bad),"future_focus_fact_rejected");
   Bad=Good;Bad.FocusHistory[1].AtTime=-1;Check(!L.Restore(Bad),"backward_focus_fact_rejected");
   Bad=Good;Bad.FocusHistory[1].Kind=static_cast<EFocusChange>(99);Check(!L.Restore(Bad),"unknown_focus_fact_kind_rejected");
   Bad=Good;Bad.FocusHistory[1].RegeneratedBefore+=1;Check(!L.Restore(Bad),"forged_integrated_regeneration_before_receipt_rejected");
   Bad=Good;Bad.NextFocusMutationId=1;Check(!L.Restore(Bad),"focus_mutation_cursor_rewind_rejected");
   Bad=Good;Bad.AccruedFocus=std::numeric_limits<double>::quiet_NaN();Check(!L.Restore(Bad),"nonfinite_trailing_focus_accrual_rejected");
   Check(Near(L.State().Time,Good.Time)&&Near(L.State().Budget.Focus,Good.Budget.Focus)&&L.State().FocusHistory.size()==Good.FocusHistory.size(),"invalid_focus_restore_is_atomic_and_keeps_live_state");
  }
 }
}
void ImportedWeaponCases(){
 {FWeaponActionsKernel K(EWeapon::SWD001,11);auto X=C();K.TrySpendExternalFocus(0,30,7001);K.StepTo(2,X);const auto Before=K.Capture();const FInstance Imported{EWeapon::XBW001,22,1,0,10};
  const auto R=K.ImportResolvedWeapon(2,Imported,7);Check(R.Accepted&&!R.Replayed&&K.Instance(22)&&K.Instance(22)->CooldownDeadline==10&&K.Instance(22)->Ammo==1,"complete_import_keeps_source_ammo_and_absolute_cooldown");
  Check(K.State().EquippedId==Before.EquippedId&&K.State().NextActionId==Before.NextActionId&&K.State().NextEventId==Before.NextEventId&&K.State().Budget.Focus==70&&K.State().FocusHistory.size()==Before.FocusHistory.size(),"import_does_not_equip_reset_focus_or_action_event_cursors");
  K.StepTo(3,X);const auto Stable=K.Capture();Check(K.ImportResolvedWeapon(2,Imported,7).Replayed&&K.State().Instances.size()==Stable.Instances.size()&&K.State().NextImportReceiptId==8,"old_exact_import_receipt_replays_without_mutating_current_time_or_instance");
  auto Changed=Imported;Changed.CooldownDeadline=11;Check(!K.ImportResolvedWeapon(2,Changed,7).Accepted&&!K.ImportResolvedWeapon(3,Imported,8).Accepted,"changed_receipt_and_new_receipt_for_existing_ID_cannot_overwrite_instance");
  Changed=Imported;Changed.InstanceId=33;Check(!K.ImportResolvedWeapon(2,Changed,8).Accepted&&K.State().NextImportReceiptId==8,"fresh_import_requires_exact_kernel_clock_and_failure_preserves_receipt");
  Changed.ReservedAmmo=1;Check(!K.ImportResolvedWeapon(3,Changed,8).Accepted,"imported_instance_cannot_carry_unbacked_reservation");
  Changed.ReservedAmmo=0;Changed.Ammo=2;Check(!K.ImportResolvedWeapon(3,Changed,8).Accepted,"import_ammo_must_fit_real_weapon_magazine");
  Changed.Ammo=0;Changed.CooldownDeadline=-1;Check(!K.ImportResolvedWeapon(3,Changed,8).Accepted,"import_negative_cooldown_rejected");
  Changed.CooldownDeadline=1;Check(K.ImportResolvedWeapon(3,Changed,8).Accepted&&K.Instance(33)&&K.Instance(33)->CooldownDeadline==1,"failed_import_receipt_retries_with_legal_already_expired_deadline");
  Check(K.EquipCompleted(22)&&!K.TryStart(EAction::Skill,3,X),"imported_future_cooldown_blocks_skill_without_fresh_reset");
  K.StepTo(10,X);const bool Started=K.TryStart(EAction::Skill,10,X);const double End=K.State().Action.End;K.StepTo(End+1.1,X);
  Check(Started&&K.Instance(22)&&K.Instance(22)->CooldownDeadline>10&&Near(K.Instance(22)->Ammo,1),"imported_instance_can_spend_ammo_lock_new_CD_and_reload_normally");
  const auto Good=K.Capture();FWeaponActionsKernel L;Check(L.Restore(Good)&&L.Instance(22)&&L.Instance(22)->CooldownDeadline==K.Instance(22)->CooldownDeadline,"import_receipts_and_later_runtime_survive_capture_restore");
  Check(L.ImportResolvedWeapon(2,Imported,7).Replayed&&L.State().Instances.size()==Good.Instances.size(),"restored_import_receipt_cannot_duplicate_registered_item");
  auto Bad=Good;Bad.Registrations.clear();Check(!L.Restore(Bad),"missing_registration_origin_records_rejected");
  Bad=Good;Bad.NextImportReceiptId=1;Check(!L.Restore(Bad),"import_receipt_cursor_rewind_rejected");
  Bad=Good;if(Bad.Registrations.size()>1)Bad.Registrations[1].Initial.ReservedAmmo=1;Check(!L.Restore(Bad),"forged_import_initial_reservation_rejected");
  Bad=Good;Bad.Version=2;Check(!L.Restore(Bad),"schema2_missing_import_provenance_requires_explicit_migration");
  Bad=Good;for(auto& I:Bad.Instances)if(I.InstanceId==22)I.CooldownDeadline=0;Check(!L.Restore(Bad),"imported_and_later_locked_CD_cannot_be_erased_by_raw_snapshot");
 }
 {FWeaponActionsKernel K(EWeapon::STF001,11);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.1,X);const auto Before=K.Capture();const FInstance New{EWeapon::XBW001,22,1,0,8};
  Check(K.ImportResolvedWeapon(.1,New,1).Accepted&&K.State().Action.Active&&K.State().Action.ActionId==Before.Action.ActionId&&K.State().Budget.ReservedFocus==10&&K.State().Budget.Focus==100,"registering_inactive_import_preserves_existing_action_and_focus_reservation");
  FWeaponActionsKernel L;Check(L.Restore(K.Capture())&&L.State().Budget.ReservedFocus==10&&L.State().NextEventId==Before.NextEventId,"import_during_other_action_does_not_drop_old_pending_receipts");
 }
 {FWeaponActionsKernel K;auto X=C();K.TryStart(EAction::Skill,0,X);K.StepTo(K.State().Action.End,X);K.RegisterWeapon(EWeapon::SWD001,2,0);K.EquipCompleted(2);K.TryStart(EAction::Skill,K.State().Time,X);
  auto Bad=K.Capture();Bad.WeaponRuntimeHistory.erase(std::remove_if(Bad.WeaponRuntimeHistory.begin(),Bad.WeaponRuntimeHistory.end(),[](const FWeaponRuntimeReceipt& R){return R.Action.InstanceId==1&&R.Kind==EWeaponMutation::SkillLock;}),Bad.WeaponRuntimeHistory.end());for(auto& I:Bad.Instances)if(I.InstanceId==1)I.CooldownDeadline=0;
  FWeaponActionsKernel L;Check(!L.Restore(Bad),"old_zero_ammo_skill_CD_cannot_lose_lock_receipt_after_another_unlocked_action_starts");
 }
}
void IntegerMagazineCases(){
 {FWeaponActionsKernel K;FInstance Bow{EWeapon::XBW001,22,.5,0,2};Check(!K.ImportResolvedWeapon(0,Bow,1).Accepted&&K.State().NextImportReceiptId==1&&K.State().Instances.size()==1,"fractional_import_magazine_rejects_without_consuming_ID_or_receipt");
  Bow.Ammo=1;Check(K.ImportResolvedWeapon(0,Bow,1).Accepted,"fractional_import_rejection_permits_integer_same_receipt_retry");
 }
 {FWeaponActionsKernel K;Check(!K.RegisterWeapon(EWeapon::XBW001,22,.5),"legacy_registration_also_rejects_fractional_magazine");Check(K.RegisterWeapon(EWeapon::XBW001,22,1),"failed_fractional_legacy_registration_does_not_consume_instance_ID");}
 {FWeaponActionsKernel K(EWeapon::XBW001,1,.5);FWeaponActionsKernel L;Check(!L.Restore(K.Capture()),"fractional_constructor_origin_and_current_magazine_snapshot_rejected");Check(!K.PressReload(0,C()),"fractional_constructor_resources_cannot_begin_reload");}
 {FWeaponActionsKernel K;K.ImportResolvedWeapon(0,{EWeapon::XBW001,22,1,0,2},1);auto Bad=K.Capture();for(auto& I:Bad.Instances)if(I.InstanceId==22)I.Ammo=.5;for(auto& R:Bad.Registrations)if(R.Initial.InstanceId==22)R.Initial.Ammo=.5;FWeaponActionsKernel L;
  Check(!L.Restore(Bad),"coordinated_fractional_import_origin_and_current_ammo_rejected");
 }
 {FWeaponActionsKernel K(EWeapon::XBW001,1,0);auto X=C();K.PressReload(0,X);K.StepTo(K.State().Action.End,X);auto Bad=K.Capture();Bad.Registrations[0].Initial.Ammo=.5;if(!Bad.WeaponRuntimeHistory.empty())Bad.WeaponRuntimeHistory[0].BeforeAmmo=.5;FWeaponActionsKernel L;
  Check(!L.Restore(Bad),"fractional_reload_before_ledger_rejected_even_with_integer_current_magazine");
 }
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();X.FocusCostPct=.5;K.TryStart(EAction::Primary,0,X);K.StepTo(.1,X);FWeaponActionsKernel L;
  Check(Near(K.State().Budget.ReservedFocus,10.05)&&L.Restore(K.Capture()),"integer_ammo_validation_preserves_fractional_focus_reservation");K.StepTo(.22,X);
  Check(Near(K.State().Budget.Focus,89.95)&&L.Restore(K.Capture()),"integer_ammo_validation_preserves_fractional_focus_spend");
 }
}
int main(){
 {FWeaponActionsKernel K;auto X=C();Check(K.TryStart(EAction::Skill,0,X),"sword_skill_accepts_idle_ground_start");auto R=K.StepTo(.20,X);const auto* W=Find(R,EEvent::ActiveWindow);Check(Count(R,EEvent::Locked)==1&&W&&Near(W->Damage,32)&&Near(W->Stagger,22)&&Near(W->Range,145)&&Near(W->Depth,40)&&Near(W->WindowEnd,.30),"sword_skill_issues_single_32_damage_window");const auto* Step=Find(R,EEvent::ForwardStep);Check(Step&&W&&Near(Step->ForwardStep,30)&&Step->EventId<W->EventId&&Near(Step->AtTime,.20),"sword_step_request_precedes_window_without_fake_collision");Check(Near(K.Instance(1)->CooldownDeadline,4.08),"sword_cooldown_starts_at_point08_lock");}
 {FWeaponActionsKernel K(EWeapon::GSW001);auto X=C();K.TryStart(EAction::Skill,0,X);auto R=K.StepTo(1.69,X);const auto* W=Find(R,EEvent::ActiveWindow);Check(W&&Near(W->AtTime,.68)&&Near(W->Damage,68)&&Near(W->Stagger,65)&&Near(W->WindowEnd,.84)&&Count(R,EEvent::Completed)==1&&!K.State().Action.Active,"heavy_skill_full_1690ms_timeline_once");Check(Near(K.Instance(1)->CooldownDeadline,8.272),"heavy_skill_cd_from_point272_lock");}
 {FWeaponActionsKernel K(EWeapon::SPR001);auto X=C();K.TryStart(EAction::Skill,0,X);auto R=K.StepTo(.81,X);const auto* A=Find(R,EEvent::ActiveWindow,0);const auto* B=Find(R,EEvent::ActiveWindow,1);const auto* D=Find(R,EEvent::ActiveWindow,2);Check(A&&B&&D&&Near(A->AtTime,.18)&&Near(A->WindowEnd,.22)&&Near(B->AtTime,.28)&&Near(B->WindowEnd,.32)&&Near(D->AtTime,.38)&&Near(D->WindowEnd,.42)&&Near(A->Damage+B->Damage+D->Damage,36)&&A->MaxTargets==1,"spear_three_independent_short_windows_under_large_step");Check(K.StepTo(.81,X).empty(),"same_time_never_reemits_consumed_windows");}
 {FWeaponActionsKernel K(EWeapon::SPR001);auto X=C();K.TryStart(EAction::Skill,0,X);K.StepTo(.23,X);Check(K.Interrupt(EInterrupt::PoiseBreak),"poise_break_interrupts_skill_between_subhits");auto R=K.StepTo(1,X);Check(Count(R,EEvent::Interrupted)==1&&Count(R,EEvent::ActiveWindow)==0&&Near(K.Instance(1)->CooldownDeadline,4.572),"interruption_cancels_future_thrusts_but_keeps_lock_cd");}
 {FWeaponActionsKernel K(EWeapon::XBW001,8,1);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.064,X);Check(Near(K.Instance(8)->Ammo,1)&&Near(K.Instance(8)->ReservedAmmo,1),"crossbow_lock_reserves_without_spending");X.Muzzle={12,37,55};auto R=K.StepTo(.16,X);const auto* P=Find(R,EEvent::ProjectileEmitted);Check(P&&Near(P->Damage,34)&&Near(P->ProjectileSpeed,950)&&P->MaxTargets==1&&Near(P->Origin.Y,37)&&Near(P->Origin.Height,55)&&Near(P->AmmoConsumed,1)&&Near(K.Instance(8)->Ammo,0)&&Near(K.Instance(8)->ReservedAmmo,0),"crossbow_single_actual_emission_consumes_one_at_current_muzzle");Check(!K.PressReload(.16,X)&&!K.TryStart(EAction::Skill,.16,X),"cannot_reload_or_skill_cancel_primary_recovery");K.StepTo(.68,X);Check(K.State().Action.Type==EAction::Reload&&K.State().Action.Active&&Near(K.State().Action.End,1.78),"empty_crossbow_auto_reload_only_after_full_recovery");K.StepTo(1.781,X);Check(Near(K.Instance(8)->Ammo,1)&&!K.State().Action.Active,"reload_refills_only_after_complete_1100ms");}
 {FWeaponActionsKernel K(EWeapon::XBW001,1,1);auto X=C();K.TryStart(EAction::Skill,0,X);auto R=K.StepTo(.55,X);const auto* P=Find(R,EEvent::ProjectileEmitted);Check(P&&P->MaxTargets==2&&Near(P->SecondTargetRatio,.6)&&Near(P->Damage,50)&&Near(P->Stagger,24)&&Near(P->Range,520)&&Near(P->ProjectileSpeed,1100)&&Near(K.Instance(1)->CooldownDeadline,6.22),"piercing_bolt_payload_keeps_two_target_60percent_policy");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.089,X);Check(Near(K.State().Budget.Focus,100)&&Near(K.State().Budget.ReservedFocus,10)&&!K.State().Budget.HasActualSpend,"staff_lock_is_not_actual_focus_spend");auto R=K.StepTo(.22,X);const auto* P=Find(R,EEvent::ProjectileEmitted);Check(P&&Near(P->Damage,24)&&Near(P->ProjectileSpeed,600)&&Near(P->BurnDps,0)&&Near(P->FocusConsumed,10)&&Near(K.State().Budget.Focus,90)&&Near(K.State().Budget.LastActualSpend,.22),"staff_primary_emits_one_fireball_without_implicit_burn");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();X.DamagePct=50;X.Critical=true;X.CritMultiplier=2;K.TryStart(EAction::Skill,0,X);auto R=K.StepTo(.45,X);const auto* W=Find(R,EEvent::ActiveWindow);Check(W&&Near(W->Damage,54)&&Near(W->BurnDps,2)&&Near(W->BurnDuration,3)&&Near(W->Origin.Height,0)&&W->Shape==EShape::GroundRectangle&&Near(K.State().Budget.Focus,76)&&Near(K.Instance(1)->CooldownDeadline,7.18),"fireline_direct_snapshot_does_not_scale_fixed_burn_or_create_projectile");}
 {FWeaponActionsKernel K(EWeapon::STF001,1,0,20);auto X=C();X.FocusCostPct=-20;Check(K.TryStart(EAction::Skill,0,X),"discount_allows_initial_full_budget_validation");X.FocusCostPct=25;auto R=K.StepTo(.181,X);Check(Count(R,EEvent::LockFailed)==1&&!K.State().Action.Active&&Near(K.State().Budget.Focus,20)&&Near(K.State().Budget.ReservedFocus,0)&&Near(K.Instance(1)->CooldownDeadline,0),"expired_discount_at_lock_cancels_with_no_spend_or_cd");}
 {FWeaponActionsKernel K(EWeapon::XBW001,1,0);auto X=C();Check(!K.TryStart(EAction::Primary,0,X)&&!K.TryStart(EAction::Skill,0,X)&&K.State().NextActionId==1,"insufficient_initial_ammo_rejects_without_action_or_id");FWeaponActionsKernel L(EWeapon::STF001,1,0,9);Check(!L.TryStart(EAction::Primary,0,X)&&Near(L.State().Budget.Focus,9),"insufficient_initial_focus_has_no_free_primary");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Skill,0,X);K.StepTo(.181,X);K.Interrupt(EInterrupt::PoiseBreak);auto R=K.StepTo(1,X);Check(Near(K.State().Budget.Focus,100)&&Near(K.State().Budget.ReservedFocus,0)&&!K.State().Budget.HasActualSpend&&Near(K.Instance(1)->CooldownDeadline,7.18)&&Count(R,EEvent::ActiveWindow)==0,"preemission_break_releases_reservation_without_resetting_cd_or_focus_timer");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.22,X);K.Interrupt(EInterrupt::Death);auto R=K.StepTo(8,X);Check(K.State().Budget.Dead&&Near(K.State().Budget.Focus,90)&&K.State().Issued.size()==1&&Count(R,EEvent::ProjectileEmitted)==0&&!K.TryStart(EAction::Primary,8,X),"death_keeps_spent_focus_and_issued_projectile_receipt_without_new_emissions");}
 {FWeaponActionsKernel K(EWeapon::XBW001,1,1);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.063,X);Check(K.TryReverseCancel(.063,-1)&&Near(K.Instance(1)->Ammo,1)&&Near(K.Instance(1)->ReservedAmmo,0),"primary_reverse_cancel_before_lock_spends_nothing");FWeaponActionsKernel L(EWeapon::XBW001,1,1);L.TryStart(EAction::Primary,0,X);L.StepTo(.064,X);Check(!L.TryReverseCancel(.064,-1)&&L.State().Action.Locked,"exact_40percent_boundary_has_already_locked");FWeaponActionsKernel M;M.TryStart(EAction::Skill,0,X);Check(!M.TryReverseCancel(0,-1)&&!M.Interrupt(EInterrupt::ExclusiveAction)&&!M.Interrupt(EInterrupt::SwitchWeapon),"skill_gains_no_unwritten_reverse_or_exclusive_cancel");}
 {FWeaponActionsKernel K;auto X=C();X.ActionSpeedPct=20;K.TryStart(EAction::Skill,0,X);X.ActionSpeedPct=-20;X.DamagePct=50;X.Critical=true;X.CritMultiplier=2;X.SkillCooldownPct=-20;K.StepTo(.067,X);X.DamagePct=-30;X.Critical=false;auto R=K.StepTo(.167,X);const auto* W=Find(R,EEvent::ActiveWindow);Check(W&&Near(W->Damage,96)&&Near(W->AtTime,1./6.)&&Near(K.State().Action.End,17./30.)&&Near(K.Instance(1)->CooldownDeadline,3.2666666666666666),"timeline_frozen_at_start_and_damage_cd_frozen_at_lock");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();X.FocusCostPct=100;X.ActionSpeedPct=100;K.TryStart(EAction::Primary,0,X);auto R=K.StepTo(.22/1.2,X);const auto* P=Find(R,EEvent::ProjectileEmitted);Check(P&&Near(P->FocusConsumed,12.5)&&Near(K.State().Budget.Focus,87.5),"v2_caps_apply_once_to_speed_and_focus_cost");}
 {FWeaponActionsKernel K(EWeapon::XBW001,1,0);auto X=C();X.ReloadSpeedPct=25;Check(K.PressReload(0,X),"manual_reload_can_start_empty");K.StepTo(.4,X);Check(Near(K.Instance(1)->Ammo,0)&&Near(K.State().Action.End,.88),"reload_speed_affix_freezes_full_reload_deadline");Check(K.PressReload(.4,X)&&!K.TryStart(EAction::Primary,.4,X),"reload_cancel_clears_progress_and_blocks_same_time_attack");K.StepTo(.5,X);Check(!K.State().Action.Active&&Near(K.Instance(1)->Ammo,0),"cancelled_empty_reload_does_not_auto_restart");K.PressReload(.5,X);K.StepTo(1.381,X);Check(Near(K.Instance(1)->Ammo,1),"fresh_manual_reload_restarts_full_duration");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();Check(K.NotifyTakeoff(),"takeoff_opens_shared_air_primary_budget");X.Grounded=false;Check(K.TryStart(EAction::Primary,0,X)&&K.State().Budget.AirPrimarySpent,"air_primary_spent_on_accepted_start");K.TryReverseCancel(0,-1);Check(!K.TryStart(EAction::Primary,0,X)&&!K.TryStart(EAction::Skill,0,X),"air_cancel_never_refunds_slot_and_air_skill_remains_illegal");K.NotifyLand();K.StepTo(.01,C());Check(K.NotifyTakeoff()&&!K.State().Budget.AirPrimarySpent,"only_new_takeoff_resets_air_slot");}
 {FWeaponActionsKernel K(EWeapon::STF001,1,0,8);auto X=C();X.FocusCostPct=-20;K.NotifyTakeoff();X.Grounded=false;K.TryStart(EAction::Primary,0,X);X.FocusCostPct=25;auto R=K.StepTo(.089,X);Check(Count(R,EEvent::LockFailed)==1&&K.State().Budget.AirPrimarySpent,"failed_lock_does_not_refund_air_slot");FWeaponActionsKernel L;L.NotifyTakeoff();Check(L.CanAdmitExternalMeleePrimary()&&L.RecordAcceptedExternalMeleePrimary()&&!L.CanAdmitExternalMeleePrimary()&&!L.RecordAcceptedExternalMeleePrimary(),"one_shared_external_melee_acceptance_blocks_second_air_start");}
 {FWeaponActionsKernel K(EWeapon::XBW001,1,1);auto X=C();K.NotifyTakeoff();X.Grounded=false;K.TryStart(EAction::Primary,0,X);K.StepTo(.68,X);Check(!K.State().Action.Active&&K.State().AutoReloadPendingId==1&&!K.PressReload(.68,X),"air_empty_primary_defers_ground_only_auto_reload");K.NotifyLand();K.StepTo(.68,C());Check(K.State().Action.Type==EAction::Reload&&K.State().Action.Active,"landing_allows_pending_reload_without_restarting_attack");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.22,X);X.FocusRegen=16;X.FocusDelay=1;K.StepTo(1.22,X);Check(Near(K.State().Budget.Focus,90),"focus_delay_uses_last_actual_emission_not_lock");K.StepTo(1.72,X);Check(Near(K.State().Budget.Focus,98)&&Near(K.State().Budget.LastActualSpend,.22),"current_robe_regen_integrates_once_without_resetting_spend_time");K.StepTo(1.72,X);Check(Near(K.State().Budget.Focus,98),"same_time_or_paused_step_never_regenerates_twice");K.StepTo(8,X);Check(Near(K.State().Budget.Focus,100),"focus_regeneration_caps_at100");}
 {FWeaponActionsKernel K(EWeapon::STF001,11);auto X=C();K.RegisterWeapon(EWeapon::SWD001,22,0);K.TryStart(EAction::Skill,0,X);K.StepTo(1.02,X);Check(K.EquipCompleted(22)&&K.EquipCompleted(11)&&Near(K.State().Budget.Focus,76)&&Near(K.Instance(11)->CooldownDeadline,7.18)&&!K.TryStart(EAction::Skill,1.02,X),"switch_commit_preserves_shared_focus_and_instance_cooldown");Check(!K.RegisterWeapon(EWeapon::XBW001,11,1)&&!K.RegisterWeapon(EWeapon::XBW001,0,1)&&!K.EquipCompleted(99),"stable_registry_rejects_duplicate_or_unknown_identity");}
 {FWeaponActionsKernel K(EWeapon::SPR001);auto X=C();K.TryStart(EAction::Skill,0,X);K.StepTo(.23,X);const auto S=K.Capture();FWeaponActionsKernel L;Check(L.Restore(S),"valid_mid_multihit_snapshot_restores");auto R=L.StepTo(.81,X);Check(Count(R,EEvent::ActiveWindow)==2&&Find(R,EEvent::ActiveWindow,1)&&Find(R,EEvent::ActiveWindow,2)&&!Find(R,EEvent::ActiveWindow,0),"restored_multihit_keeps_cursor_and_emits_only_future_subhits");Check(Near(L.State().Time,.81)&&Near(L.Instance(1)->CooldownDeadline,4.572),"restore_never_advances_offline_clock_or_resets_cd");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.10,X);FWeaponActionsKernel L;Check(L.Restore(K.Capture())&&Near(L.State().Budget.ReservedFocus,10)&&Near(L.State().Budget.Focus,100),"save_preserves_whole_reserved_unemitted_budget");L.StepTo(.22,X);Check(Near(L.State().Budget.Focus,90)&&Near(L.State().Budget.ReservedFocus,0)&&L.State().Issued.size()==1,"restored_reservation_is_consumed_once_at_actual_emission");auto S=L.Capture();FWeaponActionsKernel M;Check(M.Restore(S)&&M.StepTo(.22,X).empty(),"restore_consumed_event_does_not_replay_same_time");}
 {FWeaponActionsKernel K;auto X=C();K.TryStart(EAction::Skill,0,X);auto S=K.Capture();FWeaponActionsKernel L;const bool Restored=L.Restore(S);auto R=L.StepTo(0,X);Check(Restored&&Count(R,EEvent::Started)==1&&L.StepTo(0,X).empty(),"queued_accepted_event_survives_capture_then_drains_once");}
 {FWeaponActionsKernel K(EWeapon::XBW001,1,0);auto X=C();K.PressReload(0,X);K.StepTo(.5,X);FWeaponActionsKernel L;Check(L.Restore(K.Capture())&&Near(L.State().Action.End,1.1)&&Near(L.Instance(1)->Ammo,0),"reload_snapshot_preserves_actual_progress_no_free_refill");L.StepTo(1.1,X);Check(Near(L.Instance(1)->Ammo,1),"restored_reload_refills_only_at_original_deadline");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.1,X);const auto Good=K.Capture();FWeaponActionsKernel L;auto Bad=Good;Bad.Action.ActiveAt+=.1;Check(!L.Restore(Bad),"restore_rejects_forged_timeline");Bad=Good;Bad.Budget.ReservedFocus=0;Check(!L.Restore(Bad),"restore_rejects_missing_reservation");Bad=Good;Bad.Instances.push_back(Bad.Instances[0]);Check(!L.Restore(Bad),"restore_rejects_duplicate_instance");Bad=Good;Bad.Time=std::numeric_limits<double>::quiet_NaN();Check(!L.Restore(Bad),"restore_rejects_nonfinite_clock");Bad=Good;Bad.Version=99;Check(!L.Restore(Bad),"restore_rejects_unknown_version_without_mutating_live_state");Check(L.State().Time==0&&L.State().EquippedId==1,"invalid_restore_keeps_previous_state");}
 {FWeaponActionsKernel K(EWeapon::SPR001);auto X=C();K.TryStart(EAction::Skill,0,X);K.StepTo(.23,X);auto Bad=K.Capture();FWeaponActionsKernel L;Bad.Action.NextSubhit=0;Check(!L.Restore(Bad),"restore_rejects_emission_cursor_rewind");Bad=K.Capture();if(Bad.Issued.empty()){Check(false,"restore_rejects_duplicate_emission_receipt");Check(false,"restore_rejects_forged_emission_damage");}else{Bad.Issued.push_back(Bad.Issued[0]);Check(!L.Restore(Bad),"restore_rejects_duplicate_emission_receipt");Bad=K.Capture();Bad.Issued[0].Damage=999;Check(!L.Restore(Bad),"restore_rejects_forged_emission_damage");}}
 {FWeaponActionsKernel K;auto X=C();X.CanStart=false;Check(!K.TryStart(EAction::Skill,0,X),"external_common_exclusive_action_gate_is_required");X=C();Check(!K.TryStart(EAction::Primary,0,X)&&!K.TryStart(EAction::Skill,0,X,false),"melee_primary_stays_existing_kernel_and_held_input_does_not_autorepeat");X.ActionSpeedPct=std::numeric_limits<double>::infinity();Check(!K.TryStart(EAction::Skill,0,X)&&K.StepTo(1,X).empty()&&Near(K.State().Time,0),"nonfinite_context_rejected_without_clock_mutation");X=C();K.StepTo(1,X);Check(!K.TryStart(EAction::Skill,0,X)&&K.StepTo(.5,X).empty()&&Near(K.State().Time,1),"stale_input_and_reverse_time_rejected");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.55,X);Check(K.TryStart(EAction::Primary,.55,X),"ground_primary_last120ms_accepts_one_pending_press");Check(!K.TryStart(EAction::Primary,.55,X),"primary_buffer_has_only_one_slot");auto R=K.StepTo(.67,X);Check(Count(R,EEvent::Completed)==1&&Count(R,EEvent::Started)==1&&K.State().Action.Active&&K.State().Action.ActionId==2,"buffer_executes_after_complete_with_fresh_resource_validation");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.1,X);auto Bad=K.Capture();Bad.Action.Active=false;Bad.Action.Phase=EPhase::Idle;Bad.Action.Terminal=EEvent::Completed;Bad.Time=1;Bad.Budget.ReservedFocus=0;FWeaponActionsKernel L;Check(!L.Restore(Bad),"restore_cannot_drop_unemitted_action_by_forging_completed_state");}
 {FWeaponActionsKernel K;auto X=C();K.TryStart(EAction::Skill,0,X);auto Bad=K.Capture();auto Duplicate=Bad.PendingEvents[0];Duplicate.EventId=Bad.NextEventId++;Bad.PendingEvents.push_back(Duplicate);FWeaponActionsKernel L;Check(!L.Restore(Bad),"restore_rejects_duplicate_started_receipt_with_distinct_event_ids");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.22,X);auto Bad=K.Capture();Bad.Budget.HasActualSpend=false;Bad.Budget.LastActualSpend=0;FWeaponActionsKernel L;Check(!L.Restore(Bad),"restore_cannot_erase_actual_focus_spend_delay");Bad=K.Capture();Bad.Issued[0].Action.Phase=EPhase::Windup;Check(!L.Restore(Bad),"restore_rejects_emission_snapshot_with_wrong_phase");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.67,X);K.TryStart(EAction::Primary,.67,X);K.StepTo(.9,X);auto Bad=K.Capture();Bad.Issued[0].InstanceId=999;Bad.Issued[0].Action.InstanceId=999;FWeaponActionsKernel L;Check(!L.Restore(Bad),"restore_rejects_historical_projectile_with_unregistered_weapon_instance");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.NotifyTakeoff();X.Grounded=false;K.TryStart(EAction::Primary,0,X);K.TryReverseCancel(0,-1);K.NotifyLand();K.NotifyTakeoff();FWeaponActionsKernel L;Check(L.Restore(K.Capture())&&!L.State().Budget.AirPrimarySpent,"valid_new_takeoff_budget_is_not_confused_with_old_air_action");}
 {FWeaponActionsKernel K(EWeapon::STF001);auto X=C();K.TryStart(EAction::Primary,0,X);K.StepTo(.55,X);K.TryStart(EAction::Primary,.55,X);FWeaponActionsKernel L;const bool Restored=L.Restore(K.Capture());auto R=L.StepTo(.67,X);Check(Restored&&Count(R,EEvent::Completed)==1&&Count(R,EEvent::Started)==0,"unaccepted_input_buffer_is_cleared_on_restore");}
 {FWeaponActionsKernel K;auto Bad=K.Capture();Bad.Action.End=std::numeric_limits<double>::quiet_NaN();FWeaponActionsKernel L;Check(!L.Restore(Bad),"restore_rejects_nonfinite_placeholder_action_data");auto X=C();K.TryStart(EAction::Skill,0,X);K.Interrupt(EInterrupt::PoiseBreak);Bad=K.Capture();Bad.Action.Terminal=EEvent::ReloadCancelled;Bad.PendingEvents.clear();Check(!L.Restore(Bad),"restore_rejects_reload_terminal_on_skill_action");}
 {FWeaponActionsKernel K;auto X=C();K.StepTo(1e308,X);const auto Id=K.State().NextActionId;Check(!K.TryStart(EAction::Skill,1e308,X)&&K.State().NextActionId==Id,"finite_clock_precision_loss_cannot_create_zero_duration_action");}
 ExternalFocusCases();
 ImportedWeaponCases();
 IntegerMagazineCases();
 std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<'\n';return Failures?1:0;
}
#endif
