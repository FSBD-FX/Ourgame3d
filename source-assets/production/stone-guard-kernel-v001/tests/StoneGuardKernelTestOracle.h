#pragma once
#include "DungeonStoneGuard.h"
#include <iomanip>
#include <sstream>
#include <string>
namespace StoneGuardKernelTestOracle
{
using namespace DungeonStoneGuard;
void Point(std::ostream& O,FPoint P){O<<P.X<<','<<P.Y<<','<<P.Z<<';';}
void Action(std::ostream& O,const FAction& A)
{
 O<<A.AttackId<<','<<int(A.Kind)<<','<<A.InProgress<<A.Locked<<A.WindowIssued<<A.Interrupted<<';'
  <<A.Start<<','<<A.LockAt<<','<<A.ActiveAt<<','<<A.ActiveEnd<<','<<A.RecoveryEnd<<','<<A.CooldownEnd<<','
  <<A.InterruptedAt<<','<<A.CompletedAt<<','<<A.Damage<<','<<A.Stagger<<','<<A.Facing<<';';
 Point(O,A.Origin);Point(O,A.LockedCenter);Point(O,A.Target);
}
// Independent full-state oracle for rejected-call atomicity, including all receipts/events.
std::string Signature(const FState& S)
{
 std::ostringstream O;O<<std::setprecision(17)<<S.Version<<','<<S.EntityId<<','<<S.NextAttackId<<','<<S.NextEventId<<','<<S.LastDamageReceiptId<<';'
 <<S.InitialTime<<','<<S.Time<<','<<S.HP<<','<<S.PoiseAccum<<','<<S.PoiseDecayOrigin<<','<<S.LastPoiseAt<<','<<S.ProtectionUntil<<','<<S.StunUntil<<','
 <<S.CombatStartedAt<<','<<S.WakeStartedAt<<','<<S.WakeEnd<<','<<S.AxeReadyAt<<','<<S.StompReadyAt<<','<<S.OccupiedUntil<<','<<S.IdleReadyAt<<';'
 <<S.WakeQueued<<S.Awakened<<S.RewardClaimed<<','<<int(S.Phase)<<','<<S.Facing<<';';
 Point(O,S.InitialPosition);Point(O,S.Position);Action(O,S.Action);
 O<<S.Windows.size()<<';';for(const auto& W:S.Windows){O<<W.AttackId<<','<<W.EventId<<','<<int(W.Kind)<<','<<W.Start<<','<<W.End<<','<<W.Damage<<','<<W.Stagger<<','<<W.Facing<<';';Point(O,W.Center);}
 O<<S.Closures.size()<<';';for(const auto& C:S.Closures)O<<C.AttackId<<','<<C.AtTime<<';';
 O<<S.HitReceipts.size()<<';';for(const auto& H:S.HitReceipts)O<<H.AttackId<<','<<H.TargetId<<','<<H.AtTime<<';';
 O<<S.ReceivedHits.size()<<';';for(const auto& H:S.ReceivedHits)O<<H.ReceiptId<<','<<H.AtTime<<','<<H.ActualHPLoss<<','<<H.Stagger<<';';
 O<<S.Issued.size()<<';';for(const auto& E:S.Issued){O<<E.EventId<<','<<E.EntityId<<','<<E.TargetId<<','<<int(E.Kind)<<','<<E.AtTime<<','<<E.EndTime<<','<<E.Amount<<';';Point(O,E.From);Point(O,E.To);Action(O,E.Action);}
 return O.str();
}
}
