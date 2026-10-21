#pragma once
#include "DungeonEquipmentStats.h"
#include <array>
#include <cstdint>
#include <string>
#include <vector>

namespace DungeonEquipmentInventory {
using FId=std::uint64_t;
struct FStoredAffix { std::string Id;int Magnitude=0;DungeonEquipmentStats::FQuantile OriginalQ; };
struct FItem {
 FId InstanceId=0,Version=1;std::string ContentId;int Grade=0;
 DungeonEquipmentStats::EPackage Package=DungeonEquipmentStats::EPackage::None;int Tier=0;
 std::vector<FStoredAffix> Affixes;
 double Ammo=0,SkillCooldownDeadline=0;
};
enum class EAction { Pickup,Switch,Drop };
enum class EError { None,InvalidState,InvalidItem,UnknownSource,SourceUnavailable,SourceConflict,DuplicateInstance,InvalidSlot,SelectionRequired,LastWeapon,StalePlan,AdmissionDenied,DropDenied,DuplicateSource,InvalidOperation,OperationConflict,InvalidRuntime,RuntimeReceiptConflict,NotOwnedWeapon };
struct FPlan {
 EAction Action=EAction::Pickup;int Slot=-1;FId BaseRevision=0,SourceId=0,SourceVersion=0,InstanceId=0,InstanceVersion=0,ReplacedId=0;
};
struct FPrepared { EError Error=EError::InvalidState;FPlan Plan;bool Ok() const { return Error==EError::None; } };
struct FCommitContext { bool AdmissionGranted=false,DropPointGranted=false; };
struct FResult {
 EError Error=EError::InvalidState;bool Replayed=false;FId Revision=0,AcquiredId=0,DroppedId=0,DroppedSourceId=0;int ActiveSlot=-1;
 bool Ok() const { return Error==EError::None; }
};
struct FSource { FId SourceId=0,Version=1,InstanceId=0;bool Available=true;FItem SpawnItem;FId CreatedRevision=0; };
struct FOperation { FId OperationId=0;FPlan Request;FId DropSourceId=0;FResult Result; };
struct FRuntimeReceipt {
 FId ReceiptId=0,BaseRevision=0,InstanceId=0,BeforeVersion=0,AfterVersion=0;double AtTime=0;
 double BeforeAmmo=0,Ammo=0,BeforeCooldown=0,SkillCooldownDeadline=0;FResult Result;
};
struct FState {
 std::uint32_t Schema=2;FId RunId=0,OwnerId=0,Revision=1,StarterId=0;
 std::array<FId,2> Weapons{};FId Armor=0;int ActiveSlot=0;
 std::vector<FItem> Items;std::vector<FSource> Sources;std::vector<FOperation> Operations;
 FItem InitialStarter;FId NextRuntimeReceiptId=1;std::vector<FRuntimeReceipt> RuntimeUpdates;
};
class FEquipmentInventory {
 FState S;
 static constexpr FId Max=std::numeric_limits<FId>::max();
 static bool MagazineCount(double Value,double Capacity){return std::isfinite(Value)&&Value>=0&&Value<=Capacity&&std::floor(Value)==Value;}
 static const FItem* FindItem(const FState& V,FId Id){for(const auto& I:V.Items)if(I.InstanceId==Id)return &I;return nullptr;}
 static FItem* FindItem(FState& V,FId Id){for(auto& I:V.Items)if(I.InstanceId==Id)return &I;return nullptr;}
 static const FSource* FindSource(const FState& V,FId Id){for(const auto& I:V.Sources)if(I.SourceId==Id)return &I;return nullptr;}
 static FSource* FindSource(FState& V,FId Id){for(auto& I:V.Sources)if(I.SourceId==Id)return &I;return nullptr;}
 static FId SlotItem(const FState& V,int Slot){return Slot==2?V.Armor:V.Weapons[static_cast<std::size_t>(Slot)];}
 static FId& SlotItem(FState& V,int Slot){return Slot==2?V.Armor:V.Weapons[static_cast<std::size_t>(Slot)];}
 // Only original magazine metadata is copied here; all final attribute rules remain Stats-owned.
 static double Magazine(std::string_view Id){
  constexpr std::array<std::pair<std::string_view,double>,12> Data={{{"WPN-XBW-001",1},{"WPN-XBW-002",3},{"WPN-XBW-003",1},{"WPN-PST-001",6},{"WPN-PST-002",2},{"WPN-PST-003",1},{"WPN-SGN-001",2},{"WPN-SGN-002",2},{"WPN-SGN-003",4},{"WPN-RFL-001",4},{"WPN-RFL-002",9},{"WPN-RFL-003",5}}};
  for(const auto& D:Data)if(D.first==Id)return D.second;return 0;
 }
 // Borrowed strings exist only inside a synchronous validation/Resolve call.
 static DungeonEquipmentStats::FInstance View(const FItem& I){
  DungeonEquipmentStats::FInstance V;V.TemplateId=I.ContentId;V.Grade=I.Grade;V.Enchant.Package=I.Package;V.Enchant.Tier=I.Tier;
  for(const auto& A:I.Affixes)V.Enchant.Affixes.push_back({A.Id,A.Magnitude});return V;
 }
 static bool ValidItem(const FItem& I){
  const auto* D=DungeonEquipmentStats::FindTemplate(I.ContentId);
  if(!I.InstanceId||!I.Version||I.Version==Max||!D||!MagazineCount(I.Ammo,Magazine(I.ContentId))||!std::isfinite(I.SkillCooldownDeadline)||I.SkillCooldownDeadline<0||(D->Kind==DungeonEquipmentStats::EKind::Armor&&I.SkillCooldownDeadline!=0))return false;
   for(std::size_t N=0;N<I.Affixes.size();++N){
    const auto& A=I.Affixes[N];
    if(!A.OriginalQ.Valid()||(N&&I.Affixes[N-1].Id>=A.Id))return false;
    const auto Band=DungeonEquipmentStats::LegalAffixRange(I.ContentId,A.Id,I.Tier);
    const auto Mapped=DungeonEquipmentStats::MapOriginalQuantile(A.OriginalQ,Band);
    if(!Mapped||*Mapped!=A.Magnitude)return false;
   }
  return DungeonEquipmentStats::ValidateInstance(View(I),D->Kind)==DungeonEquipmentStats::EError::None;
 }
 static bool SameItem(const FItem& A,const FItem& B,bool Version=true,bool Runtime=true){
  if(A.InstanceId!=B.InstanceId||(Version&&A.Version!=B.Version)||A.ContentId!=B.ContentId||A.Grade!=B.Grade||A.Package!=B.Package||A.Tier!=B.Tier||(Runtime&&(A.Ammo!=B.Ammo||A.SkillCooldownDeadline!=B.SkillCooldownDeadline))||A.Affixes.size()!=B.Affixes.size())return false;
  for(std::size_t N=0;N<A.Affixes.size();++N){const auto& X=A.Affixes[N];const auto& Y=B.Affixes[N];if(X.Id!=Y.Id||X.Magnitude!=Y.Magnitude||X.OriginalQ.Numerator!=Y.OriginalQ.Numerator||X.OriginalQ.Denominator!=Y.OriginalQ.Denominator)return false;}return true;
 }
 static bool SamePlan(const FPlan& A,const FPlan& B){return A.Action==B.Action&&A.Slot==B.Slot&&A.BaseRevision==B.BaseRevision&&A.SourceId==B.SourceId&&A.SourceVersion==B.SourceVersion&&A.InstanceId==B.InstanceId&&A.InstanceVersion==B.InstanceVersion&&A.ReplacedId==B.ReplacedId;}
 static bool ReplayValid(const FState& V){
  FState W;W.InitialStarter=V.InitialStarter;W.Items.push_back(V.InitialStarter);W.Weapons[0]=V.StarterId;
  for(FId Revision=2;Revision<=V.Revision;++Revision){
   const FSource* Created=nullptr;const FOperation* O=nullptr;const FRuntimeReceipt* Runtime=nullptr;
   for(const auto& X:V.Sources)if(X.CreatedRevision==Revision)Created=&X;
   for(const auto& X:V.Operations)if(X.Result.Revision==Revision)O=&X;
   for(const auto& X:V.RuntimeUpdates)if(X.BaseRevision+1==Revision)Runtime=&X;
   if(Runtime){
    if(Created||O)return false;auto* I=FindItem(W,Runtime->InstanceId);
    if(!I||(W.Weapons[0]!=I->InstanceId&&W.Weapons[1]!=I->InstanceId)||I->Version!=Runtime->BeforeVersion||I->Ammo!=Runtime->BeforeAmmo||I->SkillCooldownDeadline!=Runtime->BeforeCooldown||Runtime->Result.ActiveSlot!=W.ActiveSlot)return false;
    I->Version=Runtime->AfterVersion;I->Ammo=Runtime->Ammo;I->SkillCooldownDeadline=Runtime->SkillCooldownDeadline;
   }else if(O){
    const auto& P=O->Request;auto* I=FindItem(W,P.InstanceId);const FId BeforeSlot=SlotItem(W,P.Slot);
    if(P.BaseRevision!=Revision-1||!I||I->Version!=P.InstanceVersion)return false;
    if(P.Action==EAction::Pickup){
     auto* Source=FindSource(W,P.SourceId);
     if(!Source||!Source->Available||Source->Version!=P.SourceVersion||Source->InstanceId!=P.InstanceId||P.ReplacedId!=BeforeSlot)return false;
     Source->Available=false;++Source->Version;++I->Version;SlotItem(W,P.Slot)=P.InstanceId;
     if(P.Slot<2&&!BeforeSlot)W.ActiveSlot=P.Slot;
    }else if(P.Action==EAction::Switch){if(P.Slot!=1-W.ActiveSlot||BeforeSlot!=P.InstanceId)return false;W.ActiveSlot=P.Slot;}
    else {if(BeforeSlot!=P.InstanceId||(P.Slot<2&&!W.Weapons[static_cast<std::size_t>(1-P.Slot)]))return false;SlotItem(W,P.Slot)=0;if(P.Slot<2&&W.ActiveSlot==P.Slot)W.ActiveSlot=1-P.Slot;}
    if(O->Result.ActiveSlot!=W.ActiveSlot)return false;
    if(O->Result.DroppedId){
     auto* Old=FindItem(W,O->Result.DroppedId);if(!Old||!Created||Created->SourceId!=O->DropSourceId||FindSource(W,Created->SourceId))return false;
     ++Old->Version;if(!SameItem(*Old,Created->SpawnItem))return false;auto Copy=*Created;Copy.Available=true;Copy.Version=1;W.Sources.push_back(std::move(Copy));
    }else if(Created)return false;
   }else {
    if(!Created||FindItem(W,Created->InstanceId))return false;
    W.Items.push_back(Created->SpawnItem);auto Copy=*Created;Copy.Available=true;Copy.Version=1;W.Sources.push_back(std::move(Copy));
   }
   W.Revision=Revision;
  }
  if(W.Weapons!=V.Weapons||W.Armor!=V.Armor||W.ActiveSlot!=V.ActiveSlot||W.Items.size()!=V.Items.size()||W.Sources.size()!=V.Sources.size())return false;
  for(const auto& I:V.Items){const auto* Known=FindItem(W,I.InstanceId);if(!Known||!SameItem(I,*Known))return false;}
  for(const auto& Source:V.Sources){const auto* Known=FindSource(W,Source.SourceId);if(!Known||Known->Version!=Source.Version||Known->Available!=Source.Available||Known->InstanceId!=Source.InstanceId)return false;}
  return true;
 }
 bool ValidState(const FState& V) const {
  if(V.Schema!=2||!V.RunId||!V.OwnerId||V.RunId!=S.RunId||V.OwnerId!=S.OwnerId||!V.StarterId||V.StarterId!=S.StarterId||!V.Revision||V.Revision==Max||V.ActiveSlot<0||V.ActiveSlot>1||!V.Weapons[static_cast<std::size_t>(V.ActiveSlot)]||V.Items.empty()||!ValidItem(V.InitialStarter)||V.InitialStarter.InstanceId!=V.StarterId||!SameItem(V.InitialStarter,S.InitialStarter)||!V.NextRuntimeReceiptId)return false;
  if(!FindItem(V,V.StarterId))return false;
  for(std::size_t N=0;N<V.Items.size();++N){
   const auto& I=V.Items[N];if(!ValidItem(I))return false;
   for(std::size_t J=0;J<N;++J)if(V.Items[J].InstanceId==I.InstanceId)return false;
   std::size_t Locations=0;
   for(int Slot=0;Slot<3;++Slot)if(SlotItem(V,Slot)==I.InstanceId)++Locations;
   for(const auto& Source:V.Sources)if(Source.Available&&Source.InstanceId==I.InstanceId)++Locations;
   if(Locations!=1)return false;
  }
  for(int Slot=0;Slot<3;++Slot){const auto Id=SlotItem(V,Slot);if(!Id)continue;const auto* I=FindItem(V,Id);if(!I||DungeonEquipmentStats::FindTemplate(I->ContentId)->Kind!=(Slot==2?DungeonEquipmentStats::EKind::Armor:DungeonEquipmentStats::EKind::Weapon))return false;}
  for(std::size_t N=0;N<V.Sources.size();++N){
   const auto& Source=V.Sources[N];const auto* I=FindItem(V,Source.InstanceId);
   if(!Source.SourceId||Source.Version!=(Source.Available?1u:2u)||Source.CreatedRevision<2||Source.CreatedRevision>V.Revision||(N&&V.Sources[N-1].CreatedRevision>=Source.CreatedRevision)||!ValidItem(Source.SpawnItem)||!I||Source.InstanceId!=Source.SpawnItem.InstanceId||I->Version<Source.SpawnItem.Version||!SameItem(*I,Source.SpawnItem,false,false)||(Source.Available&&!SameItem(*I,Source.SpawnItem)))return false;
   for(std::size_t J=0;J<N;++J)if(V.Sources[J].SourceId==Source.SourceId)return false;
  }
  FId LastRevision=0;std::size_t DropCount=0;
  for(std::size_t N=0;N<V.Operations.size();++N){
   const auto& O=V.Operations[N];const auto& P=O.Request;const auto& R=O.Result;const auto* I=FindItem(V,P.InstanceId);
   if(!O.OperationId||!R.Ok()||R.Replayed||!P.BaseRevision||P.BaseRevision>=V.Revision||R.Revision!=P.BaseRevision+1||R.Revision<=LastRevision||R.Revision>V.Revision||R.ActiveSlot<0||R.ActiveSlot>1||P.Slot<0||P.Slot>2||!I||!P.InstanceVersion||P.InstanceVersion>I->Version||static_cast<unsigned>(P.Action)>static_cast<unsigned>(EAction::Drop))return false;
    if((DungeonEquipmentStats::FindTemplate(I->ContentId)->Kind==DungeonEquipmentStats::EKind::Armor)!=(P.Slot==2))return false;
   for(std::size_t J=0;J<N;++J)if(V.Operations[J].OperationId==O.OperationId||(O.DropSourceId&&V.Operations[J].DropSourceId==O.DropSourceId))return false;
   LastRevision=R.Revision;
   if(P.Action==EAction::Pickup){const auto* Source=FindSource(V,P.SourceId);if(!Source||Source->Available||P.SourceVersion!=1||Source->InstanceId!=P.InstanceId||Source->SpawnItem.Version!=P.InstanceVersion||R.AcquiredId!=P.InstanceId||R.DroppedId!=P.ReplacedId)return false;}
   else if(P.SourceId||P.SourceVersion||P.ReplacedId||R.AcquiredId||R.DroppedId!=(P.Action==EAction::Drop?P.InstanceId:0))return false;
   if(P.Action==EAction::Switch&&P.Slot==2)return false;
   if(R.DroppedId){const auto* Source=FindSource(V,O.DropSourceId);if(!Source||Source->InstanceId!=R.DroppedId||R.DroppedSourceId!=O.DropSourceId)return false;++DropCount;}
   else if(O.DropSourceId||R.DroppedSourceId)return false;
  }
  if(DropCount>V.Sources.size()||V.Items.size()!=1+V.Sources.size()-DropCount)return false;
  FId LastRuntimeId=0,LastRuntimeRevision=0;double LastRuntimeTime=0;
  for(const auto& R:V.RuntimeUpdates){
   const auto* I=FindItem(V,R.InstanceId);
   if(!I||DungeonEquipmentStats::FindTemplate(I->ContentId)->Kind!=DungeonEquipmentStats::EKind::Weapon||!R.ReceiptId||R.ReceiptId==Max||R.ReceiptId<=LastRuntimeId||!R.BaseRevision||R.BaseRevision>=V.Revision||R.BaseRevision<=LastRuntimeRevision||!R.BeforeVersion||R.BeforeVersion>=Max-1||R.AfterVersion!=R.BeforeVersion+1||R.AfterVersion>I->Version)return false;
   for(double Value:{R.AtTime,R.BeforeAmmo,R.Ammo,R.BeforeCooldown,R.SkillCooldownDeadline})if(!std::isfinite(Value))return false;
   if(R.AtTime<LastRuntimeTime||!MagazineCount(R.BeforeAmmo,Magazine(I->ContentId))||!MagazineCount(R.Ammo,Magazine(I->ContentId))||R.BeforeCooldown<0||R.SkillCooldownDeadline<R.BeforeCooldown||!R.Result.Ok()||R.Result.Replayed||R.Result.Revision!=R.BaseRevision+1||R.Result.AcquiredId||R.Result.DroppedId||R.Result.DroppedSourceId||R.Result.ActiveSlot<0||R.Result.ActiveSlot>1)return false;
   LastRuntimeId=R.ReceiptId;LastRuntimeRevision=R.BaseRevision;LastRuntimeTime=R.AtTime;
  }
  if(V.NextRuntimeReceiptId!=(LastRuntimeId?LastRuntimeId+1:1))return false;
  return V.Revision==1+static_cast<FId>(V.Sources.size()-DropCount)+static_cast<FId>(V.Operations.size())+static_cast<FId>(V.RuntimeUpdates.size())&&ReplayValid(V);
 }
 static FResult Error(EError E){FResult R;R.Error=E;return R;}
 static FPrepared Failed(EError E){FPrepared P;P.Error=E;return P;}
public:
 FEquipmentInventory(FId RunId,FId OwnerId,const FItem& Starter) { S.RunId=RunId;S.OwnerId=OwnerId;S.StarterId=Starter.InstanceId;S.Weapons[0]=Starter.InstanceId;S.Items.push_back(Starter);S.InitialStarter=Starter; }
 const FState& State() const { return S; }
 FResult RegisterWorldSource(FId SourceId,const FItem& Item) {
  if(!ValidState(S))return Error(EError::InvalidState);
  if(!SourceId||!ValidItem(Item))return Error(EError::InvalidItem);
  if(const auto* Existing=FindSource(S,SourceId)){if(!SameItem(Existing->SpawnItem,Item))return Error(EError::SourceConflict);FResult R;R.Error=EError::None;R.Replayed=true;R.Revision=S.Revision;R.ActiveSlot=S.ActiveSlot;return R;}
  if(FindItem(S,Item.InstanceId))return Error(EError::DuplicateInstance);
  auto Next=S;Next.Items.push_back(Item);Next.Sources.push_back({SourceId,1,Item.InstanceId,true,Item,Next.Revision+1});++Next.Revision;
  if(!ValidState(Next))return Error(EError::InvalidState);S=std::move(Next);FResult R;R.Error=EError::None;R.Revision=S.Revision;R.ActiveSlot=S.ActiveSlot;return R;
 }
 FPrepared PreparePickup(FId SourceId,int Slot=-1) const {
  if(!ValidState(S))return Failed(EError::InvalidState);
  const auto* Source=FindSource(S,SourceId);if(!Source)return Failed(EError::UnknownSource);if(!Source->Available)return Failed(EError::SourceUnavailable);
  const auto* I=FindItem(S,Source->InstanceId);const auto Kind=DungeonEquipmentStats::FindTemplate(I->ContentId)->Kind;
  if(Slot==-1){if(Kind==DungeonEquipmentStats::EKind::Armor){if(S.Armor)return Failed(EError::SelectionRequired);Slot=2;}else{if(!S.Weapons[0])Slot=0;else if(!S.Weapons[1])Slot=1;else return Failed(EError::SelectionRequired);}}
  if(Slot<0||Slot>2||(Kind==DungeonEquipmentStats::EKind::Armor)!=(Slot==2))return Failed(EError::InvalidSlot);
  FPrepared P;P.Error=EError::None;P.Plan={EAction::Pickup,Slot,S.Revision,SourceId,Source->Version,I->InstanceId,I->Version,SlotItem(S,Slot)};return P;
 }
 FPrepared PrepareSwitch() const {
  if(!ValidState(S))return Failed(EError::InvalidState);const int Slot=1-S.ActiveSlot;const auto* I=FindItem(S,SlotItem(S,Slot));if(!I)return Failed(EError::InvalidSlot);
  FPrepared P;P.Error=EError::None;P.Plan={EAction::Switch,Slot,S.Revision,0,0,I->InstanceId,I->Version,0};return P;
 }
 FPrepared PrepareDrop(int Slot) const {
  if(!ValidState(S))return Failed(EError::InvalidState);if(Slot<0||Slot>2)return Failed(EError::InvalidSlot);const auto* I=FindItem(S,SlotItem(S,Slot));if(!I)return Failed(EError::InvalidSlot);
  if(Slot<2&&!S.Weapons[static_cast<std::size_t>(1-Slot)])return Failed(EError::LastWeapon);
  FPrepared P;P.Error=EError::None;P.Plan={EAction::Drop,Slot,S.Revision,0,0,I->InstanceId,I->Version,0};return P;
 }
 void Cancel(const FPlan&) const {}
 // Observation of already resolved action-kernel facts. Never computes firing,
 // reload or cooldown rewards. Save this receipt domain with the common world clock.
 FResult CommitResolvedWeaponRuntime(double Now,FId InstanceId,FId ExpectedVersion,double Ammo,double SkillCooldownDeadline,FId ReceiptId) {
  if(!ValidState(S))return Error(EError::InvalidState);
  for(const auto& R:S.RuntimeUpdates)if(R.ReceiptId==ReceiptId){
   if(R.AtTime!=Now||R.InstanceId!=InstanceId||R.BeforeVersion!=ExpectedVersion||R.Ammo!=Ammo||R.SkillCooldownDeadline!=SkillCooldownDeadline)return Error(EError::RuntimeReceiptConflict);
   auto Result=R.Result;Result.Replayed=true;return Result;
  }
  if(!std::isfinite(Now)||Now<0||(!S.RuntimeUpdates.empty()&&Now<S.RuntimeUpdates.back().AtTime)||!std::isfinite(Ammo)||!std::isfinite(SkillCooldownDeadline)||!ReceiptId||ReceiptId<S.NextRuntimeReceiptId||ReceiptId==Max)return Error(EError::InvalidRuntime);
  const auto* Item=FindItem(S,InstanceId);
  if(!Item||(S.Weapons[0]!=InstanceId&&S.Weapons[1]!=InstanceId))return Error(EError::NotOwnedWeapon);
  if(Item->Version!=ExpectedVersion)return Error(EError::StalePlan);
  if(!MagazineCount(Ammo,Magazine(Item->ContentId))||SkillCooldownDeadline<Item->SkillCooldownDeadline)return Error(EError::InvalidRuntime);
  auto Next=S;auto* Updated=FindItem(Next,InstanceId);++Updated->Version;Updated->Ammo=Ammo;Updated->SkillCooldownDeadline=SkillCooldownDeadline;++Next.Revision;
  FResult Result;Result.Error=EError::None;Result.Revision=Next.Revision;Result.ActiveSlot=Next.ActiveSlot;
  Next.RuntimeUpdates.push_back({ReceiptId,S.Revision,InstanceId,Item->Version,Updated->Version,Now,Item->Ammo,Ammo,Item->SkillCooldownDeadline,SkillCooldownDeadline,Result});Next.NextRuntimeReceiptId=ReceiptId+1;
  if(!ValidState(Next))return Error(EError::InvalidState);S=std::move(Next);return Result;
 }
 FResult Commit(FId OperationId,const FPlan& Plan,FCommitContext Context,FId DropSourceId=0) {
  if(!ValidState(S))return Error(EError::InvalidState);if(!OperationId)return Error(EError::InvalidOperation);
  for(const auto& O:S.Operations)if(O.OperationId==OperationId){if(!SamePlan(O.Request,Plan)||O.DropSourceId!=DropSourceId)return Error(EError::OperationConflict);auto R=O.Result;R.Replayed=true;return R;}
  if(Plan.BaseRevision!=S.Revision)return Error(EError::StalePlan);
  FPrepared Current;
  switch(Plan.Action){case EAction::Pickup:Current=PreparePickup(Plan.SourceId,Plan.Slot);break;case EAction::Switch:Current=PrepareSwitch();break;case EAction::Drop:Current=PrepareDrop(Plan.Slot);break;default:return Error(EError::InvalidOperation);}
  if(!Current.Ok())return Error(Current.Error);if(!SamePlan(Current.Plan,Plan))return Error(EError::StalePlan);
  if(!Context.AdmissionGranted)return Error(EError::AdmissionDenied);
  const FId Dropped=Plan.Action==EAction::Drop?Plan.InstanceId:Plan.ReplacedId;
  if(Dropped){if(!Context.DropPointGranted||!DropSourceId)return Error(EError::DropDenied);if(FindSource(S,DropSourceId))return Error(EError::DuplicateSource);}
  else if(DropSourceId)return Error(EError::InvalidOperation);
  auto Next=S;const bool Empty=SlotItem(Next,Plan.Slot)==0;
  if(Plan.Action==EAction::Pickup){auto* Source=FindSource(Next,Plan.SourceId);Source->Available=false;++Source->Version;++FindItem(Next,Plan.InstanceId)->Version;SlotItem(Next,Plan.Slot)=Plan.InstanceId;if(Plan.Slot<2&&Empty)Next.ActiveSlot=Plan.Slot;}
  else if(Plan.Action==EAction::Switch)Next.ActiveSlot=Plan.Slot;
  else {SlotItem(Next,Plan.Slot)=0;if(Plan.Slot<2&&Next.ActiveSlot==Plan.Slot)Next.ActiveSlot=1-Plan.Slot;}
  if(Dropped){auto* Old=FindItem(Next,Dropped);++Old->Version;Next.Sources.push_back({DropSourceId,1,Dropped,true,*Old,Next.Revision+1});}
  ++Next.Revision;FResult R;R.Error=EError::None;R.Revision=Next.Revision;R.AcquiredId=Plan.Action==EAction::Pickup?Plan.InstanceId:0;R.DroppedId=Dropped;R.DroppedSourceId=DropSourceId;R.ActiveSlot=Next.ActiveSlot;
  Next.Operations.push_back({OperationId,Plan,DropSourceId,R});if(!ValidState(Next))return Error(EError::InvalidState);S=std::move(Next);return R;
 }
 DungeonEquipmentStats::FResolved ResolveStats(const DungeonEquipmentStats::FContext& Context,double ActualHP) const {
  if(!ValidState(S)){DungeonEquipmentStats::FResolved R;R.Error=DungeonEquipmentStats::EError::InvalidNumber;return R;}
  DungeonEquipmentStats::FLoadout L;L.Context=Context;L.PreviousHP=ActualHP;
  if(const auto* I=FindItem(S,S.Weapons[static_cast<std::size_t>(S.ActiveSlot)]))L.Weapon=View(*I);
  if(const auto* I=FindItem(S,S.Weapons[static_cast<std::size_t>(1-S.ActiveSlot)]))L.BackupWeapon=View(*I);
  if(const auto* I=FindItem(S,S.Armor))L.Armor=View(*I);
  return DungeonEquipmentStats::Resolve(L);
 }
 FState Capture() const { return S; }
 bool Restore(const FState& V) { if(!ValidState(V))return false;S=V;return true; }
};
}
