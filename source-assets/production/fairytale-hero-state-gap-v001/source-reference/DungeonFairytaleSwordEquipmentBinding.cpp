#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "Engine/World.h"

namespace DungeonFairytaleSwordEquipmentBinding
{
namespace
{
namespace IV=DungeonEquipmentInventory;
namespace Stats=DungeonEquipmentStats;
namespace FC=DungeonContentCombat;
bool Reject(FString& Diagnostic,const TCHAR* Reason)
{
    Diagnostic=Reason;
    return false;
}
const IV::FItem* UniqueItem(const IV::FState& Inventory,uint64 Id)
{
    const IV::FItem* Result=nullptr;
    for(const auto& Item:Inventory.Items)
    {
        if(Item.InstanceId!=Id)continue;
        if(Result)return nullptr;
        Result=&Item;
    }
    return Result;
}
// Reuse the real Stats/quantile rules, never recompute rolls or substitute grade0.
// This validates the selected item's definition and view; it is not a whole
// inventory history replay, which belongs to Inventory/Aggregate rather than
// running once per presentation draw.
bool MatchesItem(const FDungeonEquipmentSlotView& Slot,const IV::FItem& Item,Stats::EKind Kind)
{
    const auto* Definition=Stats::FindTemplate(Item.ContentId);
    if(!Definition||Definition->Kind!=Kind||!Item.InstanceId||!Item.Version||Item.Version==TNumericLimits<uint64>::Max()
        ||Slot.InstanceId!=Item.InstanceId||Slot.Version!=Item.Version
        ||Slot.ContentId!=UTF8_TO_TCHAR(Item.ContentId.c_str())||Slot.Grade!=Item.Grade||Slot.Tier!=Item.Tier||Slot.Package!=Item.Package
        ||Slot.Ammo!=Item.Ammo||Slot.CooldownDeadline!=Item.SkillCooldownDeadline
        ||!FMath::IsFinite(Item.Ammo)||!FMath::IsFinite(Item.SkillCooldownDeadline)||Item.Ammo<0.||Item.SkillCooldownDeadline<0.
        ||static_cast<std::size_t>(Slot.Affixes.Num())!=Item.Affixes.size())return false;
    if(Kind==Stats::EKind::Armor&&(Item.Ammo!=0.||Item.SkillCooldownDeadline!=0.))return false;
    Stats::FInstance StatItem;StatItem.TemplateId=Item.ContentId;StatItem.Grade=Item.Grade;
    StatItem.Enchant.Package=Item.Package;StatItem.Enchant.Tier=Item.Tier;
    for(std::size_t Index=0;Index<Item.Affixes.size();++Index)
    {
        const auto& Affix=Item.Affixes[Index];const auto& ViewAffix=Slot.Affixes[static_cast<int32>(Index)];
        if(!Affix.OriginalQ.Valid()||(Index&&Item.Affixes[Index-1].Id>=Affix.Id)
            ||ViewAffix.Id!=UTF8_TO_TCHAR(Affix.Id.c_str())||ViewAffix.Magnitude!=Affix.Magnitude
            ||ViewAffix.OriginalQ.Numerator!=Affix.OriginalQ.Numerator||ViewAffix.OriginalQ.Denominator!=Affix.OriginalQ.Denominator)return false;
        const auto Range=Stats::LegalAffixRange(Item.ContentId,Affix.Id,Item.Tier);
        const auto Mapped=Stats::MapOriginalQuantile(Affix.OriginalQ,Range);
        if(!Mapped||*Mapped!=Affix.Magnitude)return false;
        StatItem.Enchant.Affixes.push_back({Affix.Id,Affix.Magnitude});
    }
    return Stats::ValidateInstance(StatItem,Kind)==Stats::EError::None;
}
bool EmptySlot(const FDungeonEquipmentSlotView& Slot)
{
    return Slot.InstanceId==0&&Slot.Version==0&&Slot.ContentId.IsEmpty()&&Slot.Affixes.IsEmpty()
        &&Slot.Grade==0&&Slot.Tier==0&&Slot.Package==Stats::EPackage::None&&Slot.Ammo==0.&&Slot.CooldownDeadline==0.;
}
bool CurrentMeleeMatches(const FC::FCombatState& Melee,uint64 WeaponId)
{
    if(Melee.Version!=3||Melee.Weapon!=FC::EWeapon::SWD001||Melee.WeaponInstanceId!=WeaponId
        ||!FMath::IsFinite(Melee.Time)||Melee.Time<0.)return false;
    const auto& Action=Melee.Action;
    if(!Action.Active)return true; // An inactive historical action may belong to an older weapon.
    if(Melee.Dead||Action.Weapon!=FC::EWeapon::SWD001||Action.WeaponInstanceId!=WeaponId||!Action.AttackId||Action.Stage>=3
        ||(Action.Facing!=1.&&Action.Facing!=-1.))return false;
    for(double Time:{Action.Start,Action.LockTime,Action.ActiveStart,Action.ActiveEnd,Action.End})if(!FMath::IsFinite(Time))return false;
    return Action.Start>=0.&&Action.Start<=Melee.Time&&Action.Start<Action.LockTime&&Action.LockTime<Action.ActiveStart
        &&Action.ActiveStart<Action.ActiveEnd&&Action.ActiveEnd<Action.End&&Melee.Time<Action.End;
}
}

bool ValidateCommitted(const FDungeonEquipmentView& View,const IV::FState& Inventory,
    const FC::FCombatState& Melee,const FString& WeaponMirror,const FString& ArmorMirror,
    FBinding& Out,FString& Diagnostic)
{
    // Check bounds before any active-slot indexing. All sources/pending fields
    // are deliberately irrelevant: only committed slots can authorize a skin.
    if(!View.Bound||!View.RunGuid.IsValid()||!View.RunAlias||!View.OwnerId||!View.RoomInstanceId||!View.Revision
        ||View.Revision==TNumericLimits<uint64>::Max()||Inventory.Schema!=2||Inventory.RunId!=View.RunAlias
        ||Inventory.OwnerId!=View.OwnerId||Inventory.Revision!=View.Revision||Inventory.ActiveSlot!=View.ActiveSlot
        ||View.ActiveSlot<0||View.ActiveSlot>1)
        return Reject(Diagnostic,TEXT("Committed Run owner, revision or active slot does not match"));
    if((Inventory.Weapons[0]&&Inventory.Weapons[0]==Inventory.Weapons[1])
        ||(Inventory.Armor&&(Inventory.Armor==Inventory.Weapons[0]||Inventory.Armor==Inventory.Weapons[1])))
        return Reject(Diagnostic,TEXT("One committed instance occupies more than one equipment slot"));
    const IV::FItem* Items[3]={};
    for(int32 SlotIndex=0;SlotIndex<3;++SlotIndex)
    {
        const uint64 Expected=SlotIndex==2?Inventory.Armor:Inventory.Weapons[static_cast<std::size_t>(SlotIndex)];
        const auto& Slot=View.Slots[SlotIndex];
        if(Slot.InstanceId!=Expected)return Reject(Diagnostic,TEXT("Committed inventory and displayed slot instance differ"));
        if(!Expected)
        {
            if(!EmptySlot(Slot))return Reject(Diagnostic,TEXT("Absent equipment slot contains stale item values"));
            continue;
        }
        Items[SlotIndex]=UniqueItem(Inventory,Expected);
        if(!Items[SlotIndex]||!MatchesItem(Slot,*Items[SlotIndex],SlotIndex==2?Stats::EKind::Armor:Stats::EKind::Weapon))
            return Reject(Diagnostic,TEXT("Committed item is missing, duplicated, stale or differs from its slot view"));
    }
    const auto* Weapon=Items[View.ActiveSlot];const auto* Armor=Items[2];
    if(!Weapon||Weapon->ContentId!="WPN-SWD-001"||WeaponMirror!=TEXT("WPN-SWD-001")
        ||WeaponMirror!=View.Slots[View.ActiveSlot].ContentId||!CurrentMeleeMatches(Melee,Weapon->InstanceId))
        return Reject(Diagnostic,TEXT("Actual active sword, mirror or Melee action instance is unsupported or inconsistent"));
    // SWD has no magazine. Its runtime deadline remains legal and unchanged.
    if(Weapon->Ammo!=0.)return Reject(Diagnostic,TEXT("Committed military sword has an invalid magazine value"));
    if(Armor)
    {
        if(Armor->ContentId!="ARM-LGT-001"||ArmorMirror!=TEXT("ARM-LGT-001")||ArmorMirror!=View.Slots[2].ContentId)
            return Reject(Diagnostic,TEXT("Actual committed armor is unsupported or differs from its mirror"));
    }
    else if(!ArmorMirror.IsEmpty())return Reject(Diagnostic,TEXT("No-armor inventory retains a stale player armor mirror"));

    FBinding Candidate;Candidate.RunGuid=View.RunGuid;Candidate.RunAlias=View.RunAlias;Candidate.OwnerId=View.OwnerId;
    Candidate.Revision=View.Revision;Candidate.ActiveSlot=View.ActiveSlot;
    Candidate.WeaponInstanceId=Weapon->InstanceId;Candidate.WeaponVersion=Weapon->Version;Candidate.WeaponContentId=View.Slots[View.ActiveSlot].ContentId;
    Candidate.Armor=Armor?EArmor::LightArmor:EArmor::NoArmor;
    if(Armor){Candidate.ArmorInstanceId=Armor->InstanceId;Candidate.ArmorVersion=Armor->Version;Candidate.ArmorContentId=View.Slots[2].ContentId;}
    Out=MoveTemp(Candidate);Diagnostic.Reset();return true;
}

bool Resolve(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,FBinding& Out,FString& Diagnostic)
{
    if(!IsInGameThread())return Reject(Diagnostic,TEXT("Actual equipment presentation must read owners on the game thread"));
    if(!IsValid(&Game)||!IsValid(&Fighter)||Game.IsActorBeingDestroyed()||Fighter.IsActorBeingDestroyed())
        return Reject(Diagnostic,TEXT("Equipment presentation owner is no longer a live native actor"));
    const auto* World=Game.GetWorld();
    if(!World||Fighter.GetWorld()!=World||World->GetAuthGameMode<ADungeonGameMode>()!=&Game||!Game.HasAuthority()
        ||!Fighter.HasAuthority()||Game.PlayerFighter!=&Fighter||Fighter.bEnemy||Fighter.GetStoneKnightDriver()||Fighter.GetStoneBatDriver())
        return Reject(Diagnostic,TEXT("Fighter is not the actual authoritative player of this World and GameMode"));
    const auto* Inventory=Game.GetEquipmentInventoryState();
    if(!Inventory)return Reject(Diagnostic,TEXT("Actual player has no committed equipment inventory"));
    const auto& View=Game.GetEquipmentView();
    const auto& WeaponActions=Fighter.GetWeaponActionsState();
    if(View.ActiveSlot<0||View.ActiveSlot>1||!View.Bound||WeaponActions.EquippedId!=View.Slots[View.ActiveSlot].InstanceId
        ||(WeaponActions.Action.Active&&(WeaponActions.Action.InstanceId!=WeaponActions.EquippedId
            ||WeaponActions.Action.Weapon!=DungeonWeaponActions::EWeapon::SWD001)))
        return Reject(Diagnostic,TEXT("Actual weapon-action equipped instance differs from committed player equipment"));
    // No gate override and no blanket rejection of Preparing/AwaitExplicitContinue:
    // an already-published valid player still owns its committed static skin.
    return ValidateCommitted(View,*Inventory,Fighter.GetMeleeCombatState(),Fighter.WeaponId,Fighter.ArmorId,Out,Diagnostic);
}
}
