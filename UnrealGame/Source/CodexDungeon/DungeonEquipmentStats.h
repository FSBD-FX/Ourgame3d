#pragma once
// Pure C++17. No UE, RNG, transaction, clock or mutable global state.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <optional>
#include <string_view>
#include <utility>
#include <vector>

namespace DungeonEquipmentStats {
enum class EStat : std::size_t { DamagePct, ActionSpeedPct, StaggerPct, ReachPct,
 CritChancePct, CritDamageBonusPct, SkillCooldownPct, ReloadSpeedPct, FocusCostPct,
 LifestealPct, ArmorFlat, WardFlat, PoiseFlat, MaxHealthPct, MoveSpeedPct,
 FocusRegenPct, HealingReceivedPct, PhysicalVulnerabilityPct, MagicVulnerabilityPct,
 BurnDps, SlowPct, ShockFlat, Count };
enum class ETalent : std::size_t { VIT, GRD, MED, ATK, BRK, CRT, MOV, FOC, RLD, Count };
enum class EKind { Weapon, Armor };
enum class EPackage { None, Beneficial, Mixed, Cursed };
enum class EError { None, UnknownTemplate, WrongSlot, InvalidGrade, InvalidPackage,
 InvalidTier, UnknownAffix, DuplicateGroup, IneligibleAffix, InvalidMagnitude,
 InvalidTalent, InvalidNumber, NotImplemented };
struct FRange { int Min=0, Max=-1; bool Valid() const { return Min>0 && Max>=Min; } };
struct FValues {
 std::array<double,static_cast<std::size_t>(EStat::Count)> Values{};
 double& operator[](EStat S) { return Values[static_cast<std::size_t>(S)]; }
 double operator[](EStat S) const { return Values[static_cast<std::size_t>(S)]; }
};
struct FTemplate {
 std::string_view Id,Family; EKind Kind=EKind::Weapon;
 double Armor=0,Ward=0,PoiseBonus=0,MoveBase=1,FocusRegen=12,FocusDelay=1;
 double ConditionalMove=0,ConditionalRegen=0;
 double PrimaryDamage=0,PrimaryStagger=0,MinReach=0,MaxReach=0,FocusCost=0;
 double SkillMinReach=0,SkillMaxReach=0,SkillFocusCost=0,Reload=0;
};
struct FAffixDefinition {
 std::string_view Id,Group; EStat Stat=EStat::DamagePct; int Direction=1;
 bool Beneficial=true,Weapon=false,Armor=false;
 std::uint32_t FamilyMask=0; std::array<FRange,5> Tiers{};
};
struct FStatDefinition { std::string_view Id; double Min=0,Max=0; };
struct FTalentDefinition {
 std::string_view Id; int MaxRank=0; FValues PerRank;
 int Prerequisite=-1,PrerequisiteRank=0;
};
struct FSource { std::string_view Path,Sha256; };
// BEGIN FROZEN EQUIPMENT DATA
// Generated only from the frozen design sources; do not edit this block by hand.
inline constexpr std::array<FSource,12> Sources={{
 {"docs/design/equipment-v2/00-属性附魔共同规则.md","12278ea720388723cbbc15408bc166e7ffe542aa4f3fe03ca455ad2f52974a17"},
 {"docs/design/equipment-v2/01-属性体系与计算.md","fe4027c4a177c7b4125ef0ea9dd8f27342c4b0a8fa573b34776008fb8e43811c"},
 {"docs/design/equipment-v2/04-逐件附魔适配与示例.md","ee6c5701d3a377c5fc9149b97497ad9235f9664ffffdaa87ca87e5563056edb7"},
 {"docs/design/equipment-v2/stat-definitions.json","2f8c3fe15aa2dc940f867be118b948e80ae9ae4c654bc70580021ade79d37bc9"},
 {"docs/design/equipment-v2/affixes.json","e6e3737cb15e64f0782dae0f0652dbac80ebaabf9ee9d97c46bd3e439402c75e"},
 {"docs/design/equipment-v2/equipment-profiles.json","1cace928f0f08c3f9afb3e093e1070785f59cd50a6210882a45d8d1b7597f85a"},
 {"docs/design/equipment-v2/enchant-rules.json","520214b7b3b8195f769f7a77c7ecc40baca2039746f7bc73cbe49b4445756a55"},
 {"docs/design/equipment-v1/weapons.json","95757819382832cfa31e6596f3ba90f1e983e83fbd69504da3c99d5ea2a272b4"},
 {"docs/design/equipment-v1/armor.json","9407e458aef80b9f0d8f0e958b089e7b7a6f4180aef41b7b7df97534fe780e9d"},
 {"docs/design/items-v1/common-rules.json","b5815a10f313b7364b1dde66b0eac9f703104ea260d4e4470094cffe31652e99"},
 {"docs/design/economy-v1/equipment-growth.json","4002351b1de27128f1a1db27020cdec8f46ab776bfc285be34742cbee23eedb9"},
 {"docs/design/progression-v1/talents.json","67f12dc215a628d94c41efa2a92e9a3929785036cab86d4cd11ec8dc958fb2f5"},
}};
inline constexpr std::array<FTemplate,45> Templates={{
 {"WPN-KNF-001","KNF",EKind::Weapon,0,0,0,1,12,1,0,0,12,6,0,88,0,0,120,0,0},
 {"WPN-KNF-002","KNF",EKind::Weapon,0,0,0,1,12,1,0,0,20,8,0,95,0,0,75,0,0},
 {"WPN-KNF-003","KNF",EKind::Weapon,0,0,0,1,12,1,0,0,14,5,0,100,0,0,115,0,0},
 {"WPN-DAO-001","DAO",EKind::Weapon,0,0,0,1,12,1,0,0,34,24,0,155,0,0,170,0,0},
 {"WPN-DAO-002","DAO",EKind::Weapon,0,0,0,1,12,1,0,0,26,18,0,125,0,0,130,0,0},
 {"WPN-DAO-003","DAO",EKind::Weapon,0,0,0,1,12,1,0,0,42,30,0,170,0,0,175,0,0},
 {"WPN-SWD-001","SWD",EKind::Weapon,0,0,0,1,12,1,0,0,26,16,0,135,0,0,145,0,0},
 {"WPN-SWD-002","SWD",EKind::Weapon,0,0,0,1,12,1,0,0,23,10,0,165,0,0,175,0,0},
 {"WPN-SWD-003","SWD",EKind::Weapon,0,0,0,1,12,1,0,0,30,18,0,125,0,0,135,0,0},
 {"WPN-GSW-001","GSW",EKind::Weapon,0,0,0,1,12,1,0,0,46,42,0,165,0,0,175,0,0},
 {"WPN-GSW-002","GSW",EKind::Weapon,0,0,0,1,12,1,0,0,40,32,55,205,0,0,195,0,0},
 {"WPN-GSW-003","GSW",EKind::Weapon,0,0,0,1,12,1,0,0,48,44,0,150,0,0,125,0,0},
 {"WPN-SPR-001","SPR",EKind::Weapon,0,0,0,1,12,1,0,0,21,10,45,230,0,0,240,0,0},
 {"WPN-SPR-002","SPR",EKind::Weapon,0,0,0,1,12,1,0,0,28,15,90,300,0,0,300,0,0},
 {"WPN-SPR-003","SPR",EKind::Weapon,0,0,0,1,12,1,0,0,25,18,60,250,0,0,160,0,0},
 {"WPN-HAL-001","HAL",EKind::Weapon,0,0,0,1,12,1,0,0,36,26,55,215,0,0,185,0,0},
 {"WPN-HAL-002","HAL",EKind::Weapon,0,0,0,1,12,1,0,0,32,24,75,230,0,0,245,0,0},
 {"WPN-HAL-003","HAL",EKind::Weapon,0,0,0,1,12,1,0,0,28,20,0,155,0,0,160,0,0},
 {"WPN-XBW-001","XBW",EKind::Weapon,0,0,0,1,12,1,0,0,34,12,0,420,0,0,520,0,1.1},
 {"WPN-XBW-002","XBW",EKind::Weapon,0,0,0,1,12,1,0,0,18,6,0,300,0,0,320,0,1.65},
 {"WPN-XBW-003","XBW",EKind::Weapon,0,0,0,1,12,1,0,0,52,30,0,580,0,0,380,0,1.75},
 {"WPN-PST-001","PST",EKind::Weapon,0,0,0,1,12,1,0,0,23,7,0,310,0,0,280,0,1.3},
 {"WPN-PST-002","PST",EKind::Weapon,0,0,0,1,12,1,0,0,28,10,0,280,0,0,260,0,1.1},
 {"WPN-PST-003","PST",EKind::Weapon,0,0,0,1,12,1,0,0,36,14,0,400,0,0,480,0,0.95},
 {"WPN-SGN-001","SGN",EKind::Weapon,0,0,0,1,12,1,0,0,42,18,0,230,0,0,170,0,1.4},
 {"WPN-SGN-002","SGN",EKind::Weapon,0,0,0,1,12,1,0,0,36,16,0,350,0,0,400,0,1.55},
 {"WPN-SGN-003","SGN",EKind::Weapon,0,0,0,1,12,1,0,0,40,16,0,200,0,0,180,0,2.1},
 {"WPN-RFL-001","RFL",EKind::Weapon,0,0,0,1,12,1,0,0,43,18,0,620,0,0,680,0,1.8},
 {"WPN-RFL-002","RFL",EKind::Weapon,0,0,0,1,12,1,0,0,39,18,0,470,0,0,540,0,2},
 {"WPN-RFL-003","RFL",EKind::Weapon,0,0,0,1,12,1,0,0,24,8,0,400,0,0,135,0,1.65},
 {"WPN-STF-001","STF",EKind::Weapon,0,0,0,1,12,1,0,0,24,8,0,360,10,0,240,24,0},
 {"WPN-STF-002","STF",EKind::Weapon,0,0,0,1,12,1,0,0,22,6,0,330,10,0,200,22,0},
 {"WPN-STF-003","STF",EKind::Weapon,0,0,0,1,12,1,0,0,20,6,0,420,9,0,480,25,0},
 {"ARM-LGT-001","LGT",EKind::Armor,14,12,0,1.08,12,1,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-LGT-002","LGT",EKind::Armor,22,6,4,1.04,12,1,1.12,0,0,0,0,0,0,0,0,0,0},
 {"ARM-LGT-003","LGT",EKind::Armor,10,20,0,1.06,12,1,1.14,0,0,0,0,0,0,0,0,0,0},
 {"ARM-MED-001","MED",EKind::Armor,32,18,10,1,12,1,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-MED-002","MED",EKind::Armor,38,8,22,0.96,12,1,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-MED-003","MED",EKind::Armor,26,36,8,0.98,12,1,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-HVY-001","HVY",EKind::Armor,85,12,40,0.84,12,1,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-HVY-002","HVY",EKind::Armor,65,6,55,0.8,12,1,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-HVY-003","HVY",EKind::Armor,60,40,28,0.86,12,1,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-ROB-001","ROB",EKind::Armor,6,50,0,1,16,1,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-ROB-002","ROB",EKind::Armor,10,42,2,1.03,12,0.45,0,0,0,0,0,0,0,0,0,0,0},
 {"ARM-ROB-003","ROB",EKind::Armor,8,70,4,0.96,14,1.4,0,20,0,0,0,0,0,0,0,0,0},
}};
inline constexpr std::array<FAffixDefinition,36> Affixes={{
 {"AFF-P-001","damage_pct",EStat::DamagePct,1,true,true,false,2047u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-002","action_speed_pct",EStat::ActionSpeedPct,1,true,true,false,2047u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-P-003","stagger_pct",EStat::StaggerPct,1,true,true,false,2047u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-004","reach_pct",EStat::ReachPct,1,true,true,false,1791u,{{{1,3},{4,6},{7,9},{10,12},{13,15}}}},
 {"AFF-P-005","crit_chance_pct",EStat::CritChancePct,1,true,true,false,2047u,{{{1,3},{4,6},{7,9},{10,12},{13,15}}}},
 {"AFF-P-006","crit_damage_bonus_pct",EStat::CritDamageBonusPct,1,true,true,false,2047u,{{{1,10},{11,20},{21,30},{31,40},{41,50}}}},
 {"AFF-P-007","skill_cooldown_pct",EStat::SkillCooldownPct,-1,true,true,false,2047u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-P-008","reload_speed_pct",EStat::ReloadSpeedPct,1,true,true,false,960u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-009","focus_cost_pct",EStat::FocusCostPct,-1,true,true,false,1024u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-P-010","lifesteal_pct",EStat::LifestealPct,1,true,true,false,2047u,{{{1,1},{2,2},{3,3},{4,4},{5,5}}}},
 {"AFF-P-011","elemental",EStat::BurnDps,1,true,true,false,2047u,{{{2,2},{3,3},{4,4},{5,5},{6,6}}}},
 {"AFF-P-012","elemental",EStat::SlowPct,1,true,true,false,2047u,{{{5,5},{10,10},{15,15},{20,20},{25,25}}}},
 {"AFF-P-013","elemental",EStat::ShockFlat,1,true,true,false,2047u,{{{2,2},{4,4},{6,6},{8,8},{10,10}}}},
 {"AFF-P-014","armor_flat",EStat::ArmorFlat,1,true,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-015","ward_flat",EStat::WardFlat,1,true,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-016","poise_flat",EStat::PoiseFlat,1,true,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-017","max_health_pct",EStat::MaxHealthPct,1,true,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-018","focus_regen_pct",EStat::FocusRegenPct,1,true,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-019","healing_received_pct",EStat::HealingReceivedPct,1,true,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-P-020","move_speed_pct",EStat::MoveSpeedPct,1,true,true,true,2047u,{{{1,3},{4,6},{7,9},{10,12},{13,15}}}},
 {"AFF-N-001","damage_pct",EStat::DamagePct,-1,false,true,false,2047u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-N-002","action_speed_pct",EStat::ActionSpeedPct,-1,false,true,false,2047u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-N-003","stagger_pct",EStat::StaggerPct,-1,false,true,false,2047u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-N-004","reach_pct",EStat::ReachPct,-1,false,true,false,1791u,{{{1,3},{4,6},{7,9},{10,12},{13,15}}}},
 {"AFF-N-005","skill_cooldown_pct",EStat::SkillCooldownPct,1,false,true,false,2047u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-N-006","reload_speed_pct",EStat::ReloadSpeedPct,-1,false,true,false,960u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-N-007","focus_cost_pct",EStat::FocusCostPct,1,false,true,false,1024u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-N-008","armor_flat",EStat::ArmorFlat,-1,false,false,true,0u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-N-009","ward_flat",EStat::WardFlat,-1,false,false,true,0u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-N-010","poise_flat",EStat::PoiseFlat,-1,false,false,true,0u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-N-011","max_health_pct",EStat::MaxHealthPct,-1,false,false,true,0u,{{{1,4},{5,8},{9,12},{13,16},{17,20}}}},
 {"AFF-N-012","focus_regen_pct",EStat::FocusRegenPct,-1,false,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-N-013","healing_received_pct",EStat::HealingReceivedPct,-1,false,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-N-014","physical_vulnerability_pct",EStat::PhysicalVulnerabilityPct,1,false,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-N-015","magic_vulnerability_pct",EStat::MagicVulnerabilityPct,1,false,false,true,0u,{{{1,5},{6,10},{11,15},{16,20},{21,25}}}},
 {"AFF-N-016","move_speed_pct",EStat::MoveSpeedPct,-1,false,true,true,2047u,{{{1,3},{4,6},{7,9},{10,12},{13,15}}}},
}};
inline constexpr std::array<FStatDefinition,22> StatDefinitions={{
 {"damage_pct",-30,50 },
 {"action_speed_pct",-20,20 },
 {"stagger_pct",-25,25 },
 {"reach_pct",-15,15 },
 {"crit_chance_pct",0,20 },
 {"crit_damage_bonus_pct",-50,50 },
 {"skill_cooldown_pct",-20,25 },
 {"reload_speed_pct",-25,25 },
 {"focus_cost_pct",-20,25 },
 {"lifesteal_pct",0,5 },
 {"armor_flat",0,150 },
 {"ward_flat",0,150 },
 {"poise_flat",30,120 },
 {"max_health_pct",-40,50 },
 {"move_speed_pct",-25,25 },
 {"focus_regen_pct",-25,25 },
 {"healing_received_pct",-25,25 },
 {"physical_vulnerability_pct",0,25 },
 {"magic_vulnerability_pct",0,25 },
 {"burn_dps",0,6 },
 {"slow_pct",0,25 },
 {"shock_flat",0,10 },
}};
inline constexpr std::array<FTalentDefinition,9> Talents={{
 {"TAL-VIT",3,FValues{{0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0}},-1,0},
 {"TAL-GRD",3,FValues{{0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0}},0,1},
 {"TAL-MED",3,FValues{{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0}},0,2},
 {"TAL-ATK",4,FValues{{2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}},-1,0},
 {"TAL-BRK",3,FValues{{0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}},3,1},
 {"TAL-CRT",2,FValues{{0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}},3,2},
 {"TAL-MOV",3,FValues{{0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0}},-1,0},
 {"TAL-FOC",3,FValues{{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0}},6,1},
 {"TAL-RLD",3,FValues{{0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0}},6,1},
}};
inline constexpr std::array<double,4> WeaponGradePct={0,5,10,15};
inline constexpr std::array<double,4> ArmorGradeRatio={0,0.05,0.1,0.15};
inline constexpr std::array<int,5> WorkshopCaps={1,1,2,2,3};
inline constexpr std::array<int,5> NaturalDropCaps={0,1,1,2,2};
// END FROZEN EQUIPMENT DATA
struct FAffixRoll { std::string_view Id; int Magnitude=0; };
struct FEnchant { EPackage Package=EPackage::None; int Tier=0; std::vector<FAffixRoll> Affixes; };
struct FInstance { std::string_view TemplateId; int Grade=0; FEnchant Enchant; };
struct FContext {
 FValues Other; // Caller supplies already source-eligible active item/relic/status contributions.
 std::array<int,static_cast<std::size_t>(ETalent::Count)> TalentRanks{};
 bool ArmorConditionalActive=false; // Caller owns its genuine trigger and lifetime.
 double MovementConstraint=1; // Existing action/air/hurt/slow constraints, applied after idle cap.
};
struct FLoadout {
 std::optional<FInstance> Weapon,Armor,BackupWeapon;
 FContext Context; double PreviousHP=100;
};
struct FResolved {
 EError Error=EError::None;
 FValues RawBonus,Final; // Final includes base crit, armor/ward and base poise; other entries are capped bonuses.
 double DamageMultiplier=1,StaggerMultiplier=1,ActionTimeScale=1,ReachMultiplier=1;
 double CritChancePct=5,CritMultiplier=1.5,SkillCooldownMultiplier=1,FocusCostMultiplier=1;
 double ReloadSeconds=0,PrimaryFocusCost=0,SkillFocusCost=0;
 double Armor=0,Ward=0,Poise=30,PhysicalMitigation=0,MagicMitigation=0;
 double MaxHP=100,CurrentHP=100,IdleMoveMultiplier=1,MoveSpeed=265;
 double FocusRegen=12,FocusDelay=1,HealingMultiplier=1;
 double PhysicalVulnerabilityMultiplier=1,MagicVulnerabilityMultiplier=1;
 bool Ok() const { return Error==EError::None; }
};
struct FQuantile { std::int64_t Numerator=0,Denominator=0; bool Valid() const { return Numerator>0 && Numerator<Denominator; } };
inline const FTemplate* FindTemplate(std::string_view Id) {
 for(const auto& T:Templates)if(T.Id==Id)return &T;
 return nullptr;
}
inline const FAffixDefinition* FindAffix(std::string_view Id) {
 for(const auto& A:Affixes)if(A.Id==Id)return &A;
 return nullptr;
}
inline std::uint32_t FamilyBit(std::string_view Family) {
 constexpr std::array<std::string_view,11> Families={"KNF","DAO","SWD","GSW","SPR","HAL","XBW","PST","SGN","RFL","STF"};
 for(std::size_t I=0;I<Families.size();++I)if(Families[I]==Family)return std::uint32_t{1}<<I;
 return 0;
}
inline FRange LegalAffixRange(const FTemplate& Original,const FAffixDefinition& A,int Tier) {
 if(Tier<1||Tier>5)return {};
 if(Original.Kind==EKind::Weapon){
  if(!A.Weapon||(A.FamilyMask&FamilyBit(Original.Family))==0)return {};
 }else if(Original.Kind==EKind::Armor){if(!A.Armor)return {};}
 else return {};
 auto Band=A.Tiers[static_cast<std::size_t>(Tier-1)];
 if(Original.Kind==EKind::Armor&&A.Direction<0){
  double Limit=std::numeric_limits<double>::infinity();
  if(A.Stat==EStat::ArmorFlat)Limit=Original.Armor;
  if(A.Stat==EStat::WardFlat)Limit=Original.Ward;
  if(A.Stat==EStat::PoiseFlat)Limit=Original.PoiseBonus; // Never the character's base30.
  if(Limit<Band.Max)Band.Max=static_cast<int>(std::floor(Limit));
 }
 if(!Band.Valid())return {};
 FRange Legal;
 for(int M=Band.Min;M<=Band.Max;++M){
  const double Factor=1+M*A.Direction/100.;
  bool Allowed=true;
  if(Original.Kind==EKind::Weapon&&A.Stat==EStat::ReachPct)
   Allowed=Original.MaxReach*Factor>Original.MinReach&&Original.SkillMaxReach*Factor>Original.SkillMinReach;
  if(Original.Kind==EKind::Weapon&&A.Stat==EStat::FocusCostPct){
   for(double Cost:{Original.FocusCost,Original.SkillFocusCost})
    if(Cost*Factor>100||(Cost>0&&Cost*Factor<=0))Allowed=false;
  }
  if(Allowed){if(!Legal.Valid())Legal.Min=M;Legal.Max=M;}
 }
 return Legal;
}
inline FRange LegalAffixRange(std::string_view TemplateId,std::string_view AffixId,int Tier) {
 const auto* T=FindTemplate(TemplateId);const auto* A=FindAffix(AffixId);
 return T&&A?LegalAffixRange(*T,*A,Tier):FRange{};
}
inline EError ValidateEnchant(const FTemplate& Original,const FEnchant& E) {
 if(E.Package==EPackage::None)return E.Tier==0&&E.Affixes.empty()?EError::None:EError::InvalidPackage;
 if(E.Package!=EPackage::Beneficial&&E.Package!=EPackage::Mixed&&E.Package!=EPackage::Cursed)return EError::InvalidPackage;
 if(E.Tier<1||E.Tier>5)return EError::InvalidTier;
 const std::size_t Count=E.Package==EPackage::Mixed?3:1;
 if(E.Affixes.size()!=Count)return EError::InvalidPackage;
 std::array<std::string_view,3> Groups{};std::size_t Used=0,Positives=0;
 for(const auto& Roll:E.Affixes){
  const auto* A=FindAffix(Roll.Id);if(!A)return EError::UnknownAffix;
  for(std::size_t I=0;I<Used;++I)if(Groups[I]==A->Group)return EError::DuplicateGroup;
  Groups[Used++]=A->Group;
  const auto Band=LegalAffixRange(Original,*A,E.Tier);
  if(!Band.Valid())return EError::IneligibleAffix;
  if(Roll.Magnitude<Band.Min||Roll.Magnitude>Band.Max)return EError::InvalidMagnitude;
  if(A->Beneficial)++Positives;
 }
 const std::size_t Required=E.Package==EPackage::Beneficial?1:(E.Package==EPackage::Mixed?2:0);
 return Positives==Required?EError::None:EError::InvalidPackage;
}
inline EError ValidateInstance(const FInstance& I,EKind Required) {
 const auto* T=FindTemplate(I.TemplateId);if(!T)return EError::UnknownTemplate;
 if(T->Kind!=Required)return EError::WrongSlot;
 if(I.Grade<0||I.Grade>3)return EError::InvalidGrade;
 return ValidateEnchant(*T,I.Enchant);
}
inline EError ValidateTalents(const FContext& C) {
 for(std::size_t I=0;I<Talents.size();++I){
  const auto Rank=C.TalentRanks[I];const auto& T=Talents[I];
  if(Rank<0||Rank>T.MaxRank)return EError::InvalidTalent;
  if(Rank>0&&T.Prerequisite>=0&&C.TalentRanks[static_cast<std::size_t>(T.Prerequisite)]<T.PrerequisiteRank)return EError::InvalidTalent;
 }
 return EError::None;
}
inline FResolved Resolve(const FLoadout& L) {
 FResolved R;
 const auto Fail=[&R](EError Error){R.Error=Error;return R;};
 if(!std::isfinite(L.PreviousHP)||L.PreviousHP<0||!std::isfinite(L.Context.MovementConstraint)||L.Context.MovementConstraint<0)return Fail(EError::InvalidNumber);
 for(double Value:L.Context.Other.Values)if(!std::isfinite(Value))return Fail(EError::InvalidNumber);
 for(const auto& Pair:{std::pair<const std::optional<FInstance>*,EKind>{&L.Weapon,EKind::Weapon},
                         {&L.Armor,EKind::Armor},{&L.BackupWeapon,EKind::Weapon}}){
  if(Pair.first->has_value()){
   const auto Error=ValidateInstance(Pair.first->value(),Pair.second);if(Error!=EError::None)return Fail(Error);
  }
 }
 const auto TalentError=ValidateTalents(L.Context);if(TalentError!=EError::None)return Fail(TalentError);
 R.RawBonus=L.Context.Other;
 for(std::size_t I=0;I<Talents.size();++I)for(std::size_t S=0;S<StatDefinitions.size();++S)
  R.RawBonus.Values[S]+=Talents[I].PerRank.Values[S]*L.Context.TalentRanks[I];
 const FTemplate* Weapon=L.Weapon?FindTemplate(L.Weapon->TemplateId):nullptr;
 const FTemplate* Armor=L.Armor?FindTemplate(L.Armor->TemplateId):nullptr;
 // Validate all instances, but only the active weapon and armor contribute. No iteration over BackupWeapon here.
 for(const auto* Active:{&L.Weapon,&L.Armor})if(Active->has_value()){
  const auto& I=Active->value();
  for(const auto& Roll:I.Enchant.Affixes){
   const auto* A=FindAffix(Roll.Id);R.RawBonus[A->Stat]+=Roll.Magnitude*A->Direction;
  }
 }
 if(Weapon)R.RawBonus[EStat::DamagePct]+=WeaponGradePct[static_cast<std::size_t>(L.Weapon->Grade)];
 if(Armor){
  const auto Ratio=ArmorGradeRatio[static_cast<std::size_t>(L.Armor->Grade)];
  R.RawBonus[EStat::ArmorFlat]+=Armor->Armor*Ratio;
  R.RawBonus[EStat::WardFlat]+=Armor->Ward*Ratio;
 }
 for(std::size_t S=0;S<StatDefinitions.size();++S){
  if(!std::isfinite(R.RawBonus.Values[S]))return Fail(EError::InvalidNumber);
  double Value=R.RawBonus.Values[S];
  const auto Stat=static_cast<EStat>(S);
  if(Stat==EStat::CritChancePct)Value+=5;
  if(Stat==EStat::ArmorFlat)Value+=Armor?Armor->Armor:0;
  if(Stat==EStat::WardFlat)Value+=Armor?Armor->Ward:0;
  if(Stat==EStat::PoiseFlat)Value+=30+(Armor?Armor->PoiseBonus:0);
  if(!std::isfinite(Value))return Fail(EError::InvalidNumber);
  R.Final.Values[S]=std::clamp(Value,StatDefinitions[S].Min,StatDefinitions[S].Max);
 }
 const auto Factor=[&R](EStat S){return 1+R.Final[S]/100.;};
 R.DamageMultiplier=Factor(EStat::DamagePct);R.StaggerMultiplier=Factor(EStat::StaggerPct);
 R.ActionTimeScale=1/Factor(EStat::ActionSpeedPct);
 // Shotgun shape/range is expressly excluded, including non-affix caller contributions.
 R.ReachMultiplier=Weapon&&Weapon->Family=="SGN"?1:Factor(EStat::ReachPct);
 R.CritChancePct=R.Final[EStat::CritChancePct];R.CritMultiplier=1.5+R.Final[EStat::CritDamageBonusPct]/100.;
 R.SkillCooldownMultiplier=Factor(EStat::SkillCooldownPct);
 R.FocusCostMultiplier=Weapon&&Weapon->Family=="STF"?Factor(EStat::FocusCostPct):1;
 if(Weapon){
  R.PrimaryFocusCost=Weapon->FocusCost*R.FocusCostMultiplier;
  R.SkillFocusCost=Weapon->SkillFocusCost*R.FocusCostMultiplier;
  if(Weapon->Family=="XBW"||Weapon->Family=="PST"||Weapon->Family=="SGN"||Weapon->Family=="RFL")
   R.ReloadSeconds=Weapon->Reload/Factor(EStat::ReloadSpeedPct);
 }
 R.Armor=R.Final[EStat::ArmorFlat];R.Ward=R.Final[EStat::WardFlat];R.Poise=R.Final[EStat::PoiseFlat];
 R.PhysicalMitigation=std::min(.6,R.Armor/(100+R.Armor));R.MagicMitigation=std::min(.6,R.Ward/(100+R.Ward));
 R.MaxHP=100*Factor(EStat::MaxHealthPct);
 // The sole HP clipping point: no intermediate per-source clipping, healing, floor1 or revival.
 R.CurrentHP=std::min(L.PreviousHP,R.MaxHP);
 double Move=Armor?Armor->MoveBase:1,Regen=Armor?Armor->FocusRegen:12;
 if(Armor&&L.Context.ArmorConditionalActive){
  if(Armor->ConditionalMove>0)Move=Armor->ConditionalMove;
  if(Armor->ConditionalRegen>0)Regen=Armor->ConditionalRegen;
 }
 R.IdleMoveMultiplier=std::clamp(Move*Factor(EStat::MoveSpeedPct),.65,1.25);
 R.MoveSpeed=265*R.IdleMoveMultiplier*L.Context.MovementConstraint;
 if(!std::isfinite(R.MoveSpeed))return Fail(EError::InvalidNumber);
 R.FocusRegen=Regen*Factor(EStat::FocusRegenPct);R.FocusDelay=Armor?Armor->FocusDelay:1;
 R.HealingMultiplier=Factor(EStat::HealingReceivedPct);
 R.PhysicalVulnerabilityMultiplier=Factor(EStat::PhysicalVulnerabilityPct);
 R.MagicVulnerabilityMultiplier=Factor(EStat::MagicVulnerabilityPct);
 return R;
}
inline FQuantile OriginalQuantile(FRange Band,int Magnitude) {
 if(!Band.Valid()||Magnitude<Band.Min||Magnitude>Band.Max)return {};
 return {2*(static_cast<std::int64_t>(Magnitude)-Band.Min)+1,2*(static_cast<std::int64_t>(Band.Max)-Band.Min+1)};
}
inline std::optional<int> MapOriginalQuantile(FQuantile Q,FRange Band) {
 if(!Q.Valid()||!Band.Valid())return std::nullopt;
 const auto Count=static_cast<std::int64_t>(Band.Max)-Band.Min+1;
 if(Q.Numerator>std::numeric_limits<std::int64_t>::max()/Count)return std::nullopt;
 return static_cast<int>(Band.Min+Q.Numerator*Count/Q.Denominator);
}
inline int WorkshopGradeCap(int Chapter) { return Chapter>=1&&Chapter<=5?WorkshopCaps[static_cast<std::size_t>(Chapter-1)]:-1; }
inline int NaturalDropGradeCap(int Chapter) { return Chapter>=1&&Chapter<=5?NaturalDropCaps[static_cast<std::size_t>(Chapter-1)]:-1; }
// Returns the capped HP amount only; caller must atomically consume actual budgets at the heal point.
inline double HealingAmount(const FResolved& R,double BaseHP,double ActualHP,double SourceBudget) {
 if(!R.Ok()||!std::isfinite(BaseHP)||!std::isfinite(ActualHP)||!std::isfinite(SourceBudget)||BaseHP<=0||ActualHP<=0||SourceBudget<=0)return 0;
 return std::max(0.,std::min({BaseHP*R.HealingMultiplier,SourceBudget,R.MaxHP-ActualHP}));
}
// R is the current recipient; the attack's locked lifesteal rate is deliberately separate.
inline double LifestealAmount(const FResolved& R,double SnapshotLifestealPct,double EligibleDirectHPLoss,double AttackRemaining,double RollingRemaining,double ActualHP) {
 if(!R.Ok()||!std::isfinite(SnapshotLifestealPct)||SnapshotLifestealPct<0||SnapshotLifestealPct>5||!std::isfinite(AttackRemaining)||!std::isfinite(RollingRemaining)||AttackRemaining<=0||RollingRemaining<=0)return 0;
 const auto Budget=std::min({3.,6.,AttackRemaining,RollingRemaining});
 return HealingAmount(R,EligibleDirectHPLoss*SnapshotLifestealPct/100.,ActualHP,Budget);
}
} // namespace DungeonEquipmentStats
