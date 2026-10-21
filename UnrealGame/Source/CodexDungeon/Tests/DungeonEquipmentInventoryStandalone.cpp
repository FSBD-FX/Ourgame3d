#if defined(DUNGEON_EQUIPMENT_INVENTORY_STANDALONE)
#include "../DungeonEquipmentInventory.h"
#include <iostream>
#include <limits>
using namespace DungeonEquipmentInventory;
namespace {
int Checks=0,Failures=0;
void Check(bool V,const char* N){++Checks;if(!V){++Failures;std::cout<<"FAIL "<<N<<'\n';}}
bool Near(double A,double B){return std::abs(A-B)<1e-8;}
FItem Item(FId Id,std::string Name="WPN-SWD-001"){FItem I;I.InstanceId=Id;I.ContentId=std::move(Name);return I;}
const FItem* Find(const FState& S,FId Id){for(const auto& I:S.Items)if(I.InstanceId==Id)return &I;return nullptr;}
const FSource* Source(const FState& S,FId Id){for(const auto& I:S.Sources)if(I.SourceId==Id)return &I;return nullptr;}
const FCommitContext Granted{true,true};
void EmptyPickupAndIdentity(){
 auto Starter=Item(1);Starter.SkillCooldownDeadline=7.5;FEquipmentInventory K(100,200,Starter);
 auto Bow=Item(2,"WPN-XBW-001");Bow.SkillCooldownDeadline=12.5;
 Check(K.RegisterWorldSource(20,Bow).Ok(),"world source registers once");const auto Revision=K.State().Revision;
 Check(K.RegisterWorldSource(20,Bow).Replayed&&K.State().Revision==Revision,"identical world callback is idempotent");
 auto Different=Bow;Different.Grade=1;Check(K.RegisterWorldSource(20,Different).Error==EError::SourceConflict,"same source with different result rejected");
 Check(K.RegisterWorldSource(21,Bow).Error==EError::DuplicateInstance,"same instance cannot appear at another source");
 const auto P=K.PreparePickup(20);K.Cancel(P.Plan);
 Check(P.Ok()&&P.Plan.Slot==1&&K.State().Weapons[1]==0&&Source(K.State(),20)&&Source(K.State(),20)->Available,"prepare cancel leaves ownership and world source unchanged");
 Check(K.Commit(1,P.Plan,{}).Error==EError::AdmissionDenied&&K.State().Weapons[1]==0,"default context cannot commit pickup");
 const auto R=K.Commit(1,P.Plan,Granted);
 Check(R.Ok()&&K.State().Weapons[1]==2&&K.State().ActiveSlot==1&&Source(K.State(),20)&&!Source(K.State(),20)->Available,"empty weapon pickup activates and consumes source atomically");
 const auto* B=Find(K.State(),2);const auto* A=Find(K.State(),1);
 Check(B&&A&&B->Ammo==0&&B->SkillCooldownDeadline==12.5&&A->SkillCooldownDeadline==7.5,"pickup preserves independent ammo and cooldown data");
 const auto After=K.Capture();Check(K.Commit(1,P.Plan,{}).Replayed&&K.State().Revision==After.Revision&&K.State().Items.size()==After.Items.size(),"committed replay returns old result without granting again");
 Check(K.PreparePickup(20).Error==EError::SourceUnavailable,"new operation cannot pick consumed source");
 Check(K.RegisterWorldSource(20,Bow).Replayed&&!Source(K.State(),20)->Available,"spawn callback after pickup does not respawn source");
 const auto Q=K.PrepareSwitch();Check(K.Commit(2,Q.Plan,Granted).Ok()&&K.State().ActiveSlot==0&&K.State().Weapons[0]==1&&K.State().Weapons[1]==2,"Q switches existing slots without creating instances");
 const auto Back=K.PrepareSwitch();K.Commit(3,Back.Plan,Granted);B=Find(K.State(),2);A=Find(K.State(),1);
 Check(K.State().ActiveSlot==1&&B&&A&&B->SkillCooldownDeadline==12.5&&A->SkillCooldownDeadline==7.5&&B->Version==2&&A->Version==1,"Q roundtrip leaves instance versions and resources unchanged");
 Check(K.Commit(1,Back.Plan,Granted).Error==EError::OperationConflict,"OperationID reused for different request rejected before stale validation");
}
void ReplacementAndDrop(){
 FEquipmentInventory K(1,2,Item(1));auto B=Item(2,"WPN-XBW-001");K.RegisterWorldSource(20,B);K.Commit(1,K.PreparePickup(20).Plan,Granted);
 K.RegisterWorldSource(30,Item(3,"WPN-GSW-001"));
 Check(K.PreparePickup(30).Error==EError::SelectionRequired,"full weapons require explicit destination");
 const auto P=K.PreparePickup(30,0);const auto Before=K.Capture();
 Check(K.Commit(2,P.Plan,{true,false},40).Error==EError::DropDenied&&K.State().Revision==Before.Revision&&K.State().Weapons[0]==1&&Source(K.State(),30)->Available,"invalid old drop point rejects entire replacement");
 Check(K.Commit(2,P.Plan,Granted,40).Ok()&&K.State().Weapons[0]==3&&K.State().ActiveSlot==1&&Source(K.State(),40)&&Source(K.State(),40)->InstanceId==1&&Source(K.State(),40)->Available,"replacement of backup drops exact old instance and keeps active");
 const auto D=K.PrepareDrop(1);Check(K.Commit(3,D.Plan,Granted,41).Ok()&&K.State().Weapons[1]==0&&K.State().ActiveSlot==0&&Source(K.State(),41)&&Source(K.State(),41)->InstanceId==2,"dropping active switches to other existing weapon");
 Check(K.PrepareDrop(0).Error==EError::LastWeapon,"manual last weapon drop prohibited");
 K.RegisterWorldSource(31,Item(4,"WPN-SPR-001"));const auto LastReplace=K.PreparePickup(31,0);
 Check(K.Commit(4,LastReplace.Plan,Granted,42).Ok()&&K.State().Weapons[0]==4&&K.State().Weapons[1]==0&&Source(K.State(),42)&&Source(K.State(),42)->InstanceId==3,"explicit free replacement of last weapon is allowed");
 const auto Repick=K.PreparePickup(41);Check(K.Commit(5,Repick.Plan,Granted).Ok()&&K.State().Weapons[1]==2&&K.State().ActiveSlot==1&&!Source(K.State(),41)->Available,"dropped item can be repicked with same stable instance");
}
void ArmorStatsAndOwning(){
 FEquipmentInventory K(1,2,Item(1));auto Sword=Item(2);Sword.Grade=3;Sword.Package=DungeonEquipmentStats::EPackage::Beneficial;Sword.Tier=5;Sword.Affixes={{"AFF-P-001",25,{9,10}}};
 K.RegisterWorldSource(20,Sword);Sword.ContentId.assign(500,'x');Sword.Affixes[0].Id.assign(500,'y');
 Check(K.Commit(1,K.PreparePickup(20).Plan,Granted).Ok()&&Near(K.ResolveStats({},88).DamageMultiplier,1.4),"registry owns content and affix strings after caller mutation");
 K.Commit(2,K.PrepareSwitch().Plan,Granted);Check(Near(K.ResolveStats({},88).DamageMultiplier,1),"backup grade and enchant do not contribute to Stats");
 auto Armor=Item(3,"ARM-LGT-001");Armor.Package=DungeonEquipmentStats::EPackage::Beneficial;Armor.Tier=5;Armor.Affixes={{"AFF-P-017",25,{9,10}}};K.RegisterWorldSource(30,Armor);
 Check(K.Commit(3,K.PreparePickup(30).Plan,Granted).Ok()&&K.State().Armor==3&&Near(K.ResolveStats({},88).MaxHP,125)&&Near(K.ResolveStats({},88).CurrentHP,88),"armor pickup uses frozen Stats without healing or own HP state");
 K.RegisterWorldSource(31,Item(4,"ARM-HVY-001"));Check(K.PreparePickup(31).Error==EError::SelectionRequired,"existing armor needs explicit replacement choice");
 Check(K.Commit(4,K.PreparePickup(31,2).Plan,Granted,40).Ok()&&K.State().Armor==4&&Near(K.ResolveStats({},88).Armor,85)&&Source(K.State(),40)&&Source(K.State(),40)->InstanceId==3,"armor replacement drops old armor atomically");
 Check(K.Commit(5,K.PrepareDrop(2).Plan,Granted,41).Ok()&&K.State().Armor==0&&Near(K.ResolveStats({},88).Armor,0),"manual armor removal preserves old instance on ground");
}
void StaleInvalidAndRestore(){
 FEquipmentInventory K(1,2,Item(1));auto Bad=Item(2);Bad.Grade=4;const auto Before=K.Capture();
 Check(K.RegisterWorldSource(20,Bad).Error==EError::InvalidItem&&K.State().Revision==Before.Revision&&K.State().Sources.empty(),"invalid grade consumes no world source identity");
 Bad=Item(2,"WPN-XBW-001");Bad.Ammo=2;Check(K.RegisterWorldSource(20,Bad).Error==EError::InvalidItem,"ammo over original magazine rejected");
 Bad.Ammo=0;Bad.SkillCooldownDeadline=std::numeric_limits<double>::quiet_NaN();Check(K.RegisterWorldSource(20,Bad).Error==EError::InvalidItem,"nonfinite cooldown rejected");
 Bad=Item(2);Bad.Package=DungeonEquipmentStats::EPackage::Beneficial;Bad.Tier=1;Bad.Affixes={{"AFF-P-014",1,{1,10}}};Check(K.RegisterWorldSource(20,Bad).Error==EError::InvalidItem,"illegal armor affix on weapon rejected through Stats");
 Bad=Item(2);Bad.Package=DungeonEquipmentStats::EPackage::Beneficial;Bad.Tier=1;Bad.Affixes={{"AFF-P-001",1,{0,0}}};Check(K.RegisterWorldSource(20,Bad).Error==EError::InvalidItem,"missing original q rejected");
 Bad=Item(2);Bad.Package=DungeonEquipmentStats::EPackage::Beneficial;Bad.Tier=5;Bad.Affixes={{"AFF-P-001",25,{1,10}}};
 Check(K.RegisterWorldSource(20,Bad).Error==EError::InvalidItem&&K.State().Revision==Before.Revision&&K.State().Sources.empty(),"legal magnitude inconsistent with preserved original q rejected without consuming source");
 Check(K.RegisterWorldSource(20,Item(2)).Ok(),"failed source registration can retry same stable IDs");const auto Old=K.PreparePickup(20);K.RegisterWorldSource(30,Item(3,"ARM-LGT-001"));const auto Stable=K.Capture();
 Check(K.Commit(10,Old.Plan,Granted).Error==EError::StalePlan&&K.State().Revision==Stable.Revision&&Source(K.State(),20)->Available,"stale transaction does not consume operation or source");
 Check(K.Commit(10,K.PreparePickup(20).Plan,Granted).Ok(),"failed operation ID can retry a freshly validated uncommitted intent");
 const auto Good=K.Capture();FEquipmentInventory Copy(1,2,Item(1));Check(Copy.Restore(Good)&&Copy.State().Weapons==Good.Weapons&&Copy.State().ActiveSlot==Good.ActiveSlot&&Copy.State().Operations.size()==Good.Operations.size(),"owning snapshot restores inventory world tombstones and operation results");
 Check(Copy.Commit(10,K.State().Operations.empty()?FPlan{}:K.State().Operations.back().Request,Granted).Replayed,"restored operation journal still deduplicates successful request");
 auto Corrupt=Good;Corrupt.RunId=2;Check(!Copy.Restore(Corrupt)&&Copy.State().Revision==Good.Revision,"cross run restore rejected atomically");
 Corrupt=Good;Corrupt.Weapons[0]=Corrupt.Weapons[1];Check(!Copy.Restore(Corrupt),"same instance in both slots rejected");
 Corrupt=Good;if(!Corrupt.Sources.empty())Corrupt.Sources[0].Available=true;Check(!Copy.Restore(Corrupt),"source tombstone cannot resurrect owned instance");
 Corrupt=Good;Corrupt.ActiveSlot=4;Check(!Copy.Restore(Corrupt),"invalid active slot rejected");
 Corrupt=Good;Corrupt.Revision=0;Check(!Copy.Restore(Corrupt),"invalid revision rejected");
 Corrupt=Good;if(!Corrupt.Operations.empty())Corrupt.Operations[0].Request.Slot=2;
 Check(!Copy.Restore(Corrupt)&&Copy.State().Revision==Good.Revision&&Copy.State().Weapons==Good.Weapons,"historical weapon pickup cannot claim armor destination on restore");
 FEquipmentInventory Invalid(0,2,Item(1));Check(!Invalid.RegisterWorldSource(20,Item(2)).Ok()&&!Invalid.ResolveStats({},100).Ok(),"invalid construction cannot mutate or return valid stats");
}
void RuntimeTransfer(){
 FEquipmentInventory K(1,2,Item(1));auto Bow=Item(2,"WPN-XBW-001");Bow.Ammo=1;Bow.SkillCooldownDeadline=4;
 K.RegisterWorldSource(20,Bow);K.Commit(1,K.PreparePickup(20).Plan,Granted);const auto OldSwitch=K.PrepareSwitch();
 const auto R=K.CommitResolvedWeaponRuntime(5,2,2,0,11,7);
 Check(R.Ok()&&Find(K.State(),2)&&Find(K.State(),2)->Version==3&&Find(K.State(),2)->Ammo==0&&Find(K.State(),2)->SkillCooldownDeadline==11&&K.State().NextRuntimeReceiptId==8,"resolved owned weapon runtime commits once with persistent receipt");
 Check(Source(K.State(),20)&&Source(K.State(),20)->SpawnItem.Ammo==1&&Source(K.State(),20)->SpawnItem.SkillCooldownDeadline==4,"runtime update preserves immutable original source result");
 const auto Stable=K.Capture();Check(K.CommitResolvedWeaponRuntime(5,2,2,0,11,7).Replayed&&K.State().Revision==Stable.Revision,"identical runtime receipt replays without consuming again");
 Check(K.CommitResolvedWeaponRuntime(5,2,2,1,11,7).Error==EError::RuntimeReceiptConflict&&K.State().Revision==Stable.Revision,"same runtime receipt with changed payload conflicts");
 Check(K.RegisterWorldSource(20,Bow).Replayed&&Source(K.State(),20)&&!Source(K.State(),20)->Available,"old immutable spawn callback stays deduplicated after real runtime change");
 Check(K.Commit(2,OldSwitch.Plan,Granted).Error==EError::StalePlan,"runtime version change invalidates prior equipment plan");
 K.Commit(2,K.PrepareSwitch().Plan,Granted);K.Commit(3,K.PrepareSwitch().Plan,Granted);K.Commit(4,K.PrepareDrop(1).Plan,Granted,30);
 Check(Source(K.State(),30)&&Source(K.State(),30)->Available&&Source(K.State(),30)->SpawnItem.Ammo==0&&Source(K.State(),30)->SpawnItem.SkillCooldownDeadline==11,"drop snapshots latest runtime rather than original spawn resources");
 Check(K.CommitResolvedWeaponRuntime(6,2,4,1,11,8).Error==EError::NotOwnedWeapon,"ground weapon cannot receive an owned runtime update");
 K.Commit(5,K.PreparePickup(30).Plan,Granted);
 Check(K.CommitResolvedWeaponRuntime(6,2,5,1,11,9).Ok()&&Find(K.State(),2)&&Find(K.State(),2)->Ammo==1&&Find(K.State(),2)->SkillCooldownDeadline==11,"repicked same instance accepts resolved reload with preserved cooldown");
 const auto Good=K.Capture();FEquipmentInventory Copy(1,2,Item(1));Check(Copy.Restore(Good)&&Copy.State().NextRuntimeReceiptId==10&&Copy.State().RuntimeUpdates.size()==2,"runtime receipts ownership chain and resources survive capture restore");
 Check(Copy.CommitResolvedWeaponRuntime(5,2,2,0,11,7).Replayed&&Copy.State().Revision==Good.Revision,"old runtime receipt remains idempotent after restoration and repick");
 auto Bad=Good;for(auto& I:Bad.Items)if(I.InstanceId==2)I.Ammo=0;
 Check(!Copy.Restore(Bad)&&Copy.State().Revision==Good.Revision,"raw valid-range ammo edit without runtime receipt rejected atomically");
 Bad=Good;if(!Bad.RuntimeUpdates.empty())Bad.RuntimeUpdates[0].BeforeAmmo=0;
 Check(!Copy.Restore(Bad),"forged runtime before balance rejected");
 Bad=Good;Bad.RuntimeUpdates.clear();Check(!Copy.Restore(Bad),"missing runtime history cannot preserve edited resources");
 Bad=Good;Bad.NextRuntimeReceiptId=1;Check(!Copy.Restore(Bad),"runtime receipt cursor rewind rejected");
 Bad=Good;if(!Bad.RuntimeUpdates.empty())Bad.RuntimeUpdates[0].Result.ActiveSlot=0;
 Check(!Copy.Restore(Bad),"runtime receipt result must preserve actual historical active slot");
 Bad=Good;Bad.Schema=1;Check(!Copy.Restore(Bad),"legacy schema without runtime facts explicitly rejected");
}
void InvalidRuntime(){
 const double NaN=std::numeric_limits<double>::quiet_NaN();FEquipmentInventory K(1,2,Item(1));auto B=Item(2,"WPN-XBW-001");B.Ammo=1;B.SkillCooldownDeadline=4;K.RegisterWorldSource(20,B);
 Check(K.CommitResolvedWeaponRuntime(1,2,1,0,4,1).Error==EError::NotOwnedWeapon,"unpicked source cannot be mutated as owned runtime");K.Commit(1,K.PreparePickup(20).Plan,Granted);
 const auto Before=K.Capture();
 Check(K.CommitResolvedWeaponRuntime(NaN,2,2,0,4,7).Error==EError::InvalidRuntime&&K.State().Revision==Before.Revision,"nonfinite runtime timestamp rejects atomically");
 Check(K.CommitResolvedWeaponRuntime(1,2,1,0,4,7).Error==EError::StalePlan,"stale instance version cannot overwrite newer runtime");
 Check(K.CommitResolvedWeaponRuntime(1,2,2,2,4,7).Error==EError::InvalidRuntime&&K.CommitResolvedWeaponRuntime(1,2,2,0,3,7).Error==EError::InvalidRuntime,"overfull ammo and cooldown rollback consume no receipt");
 Check(K.CommitResolvedWeaponRuntime(5,2,2,0,4,7).Ok()&&K.State().NextRuntimeReceiptId==8,"failed receipt retries successfully with legitimate data");
 Check(K.CommitResolvedWeaponRuntime(4,2,3,1,4,8).Error==EError::InvalidRuntime,"runtime observation timestamp cannot move backwards");
 Check(K.CommitResolvedWeaponRuntime(6,2,3,1,4,6).Error==EError::InvalidRuntime,"older unused runtime receipt rejected after cursor advancement");
 Check(K.CommitResolvedWeaponRuntime(8,2,3,1,6,8).Ok(),"new observed cooldown may already be expired without being reset");
}
void IntegerMagazines(){
 FEquipmentInventory K(1,2,Item(1));auto Bow=Item(2,"WPN-XBW-001");Bow.Ammo=.5;Bow.SkillCooldownDeadline=4;
 Check(K.RegisterWorldSource(20,Bow).Error==EError::InvalidItem&&K.State().Sources.empty()&&K.State().Revision==1,"fractional ground magazine rejects without consuming source identity");
 Bow.Ammo=1;Check(K.RegisterWorldSource(20,Bow).Ok(),"fractional source rejection permits same IDs with integer ammo");K.Commit(1,K.PreparePickup(20).Plan,Granted);const auto Before=K.Capture();
 Check(K.CommitResolvedWeaponRuntime(5,2,2,.5,4,7).Error==EError::InvalidRuntime&&K.State().Revision==Before.Revision&&K.State().NextRuntimeReceiptId==1,"fractional runtime rejects atomically without consuming receipt or revision");
 Check(K.CommitResolvedWeaponRuntime(5,2,2,0,4,7).Ok(),"fractional runtime rejection permits corrected same receipt");const auto OneUpdate=K.Capture();
 auto Bad=OneUpdate;for(auto& I:Bad.Items)if(I.InstanceId==2)I.Ammo=.5;for(auto& S:Bad.Sources)if(S.InstanceId==2)S.SpawnItem.Ammo=.5;for(auto& R:Bad.RuntimeUpdates){R.BeforeAmmo=.5;R.Ammo=.5;}
 FEquipmentInventory L(1,2,Item(1));Check(!L.Restore(Bad),"coordinated fractional current source and runtime snapshot rejected");
 Check(K.CommitResolvedWeaponRuntime(6,2,3,1,4,8).Ok(),"integer reload remains valid after corrected runtime receipt");Bad=K.Capture();if(Bad.RuntimeUpdates.size()==2){Bad.RuntimeUpdates[0].Ammo=.5;Bad.RuntimeUpdates[1].BeforeAmmo=.5;}
 Check(!L.Restore(Bad),"fractional intermediate runtime ledger rejected even when source and current ammo are integer");
}
}
int main(){EmptyPickupAndIdentity();ReplacementAndDrop();ArmorStatsAndOwning();StaleInvalidAndRestore();RuntimeTransfer();InvalidRuntime();IntegerMagazines();std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<'\n';return Failures?1:0;}
#endif
