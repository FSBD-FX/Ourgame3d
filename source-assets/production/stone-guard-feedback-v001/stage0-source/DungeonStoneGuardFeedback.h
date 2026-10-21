#pragma once
#include "DungeonStoneGuard.h"
#include <deque>
namespace DungeonGuardFeedback
{
enum class ECue { None, Wake, Step, AxeWindup, AxeRelease, StompWindup, StompImpact, HitStone, HitFleshLeather, HitMetal, Stun, Death };
enum class EFx { None, WakeCracks, FootDust, WindupGrit, AxeDustCut, StompBurst, StoneChips, HitSparks, StunChips, DeathChunks, CancelAttack };
enum class EMaterial { FleshLeather, Metal, Stone };
struct FRecord
{
 std::uint64_t Sequence=0,EventId=0,EntityId=0,AttackId=0,TargetId=0,FootOrdinal=0;
 DungeonStoneGuard::EEventKind SourceKind=DungeonStoneGuard::EEventKind::Movement;
 double AtTime=0,ActualHPLoss=0;
 DungeonStoneGuard::FPoint Position;
 int Facing=1;
 ECue Cue=ECue::None;EFx Effect=EFx::None;
};
class FJournal
{
public:
 // Stage0 witness stub. The production implementation is a separate admission.
 bool Begin(const DungeonStoneGuard::FState&) { return false; }
 bool Observe(const std::vector<DungeonStoneGuard::FEvent>&,DungeonStoneGuard::FPoint) { return false; }
 bool ConfirmHit(std::uint64_t,std::uint64_t,double,DungeonStoneGuard::FPoint,EMaterial,double) { return false; }
 std::uint64_t LastEventId() const { return 0; }
 std::uint64_t LastSequence() const { return 0; }
 const std::deque<FRecord>& Entries() const { return Records; }
private: std::deque<FRecord> Records;
};
}
