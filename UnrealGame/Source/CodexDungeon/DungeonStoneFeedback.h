#pragma once
#include "DungeonStoneKnight.h"
#include <deque>

namespace DungeonStoneFeedback
{
struct FRecord
{
    DungeonStoneKnight::FEvent Event;
    DungeonStoneKnight::FPoint Position;
};

// Transient presentation only. Restores start at the saved next event ID and
// never replay historical attacks, sounds, damage or rewards.
class FJournal
{
    std::uint64_t Entity = 0, Last = 0;
    std::deque<FRecord> Records;
public:
    static constexpr std::size_t Capacity = 64;
    bool Begin(std::uint64_t EntityId, std::uint64_t NextEventId)
    {
        if(Entity || !EntityId || !NextEventId) return false;
        Entity=EntityId; Last=NextEventId-1; return true;
    }
    bool Observe(const std::vector<DungeonStoneKnight::FEvent>& Events, DungeonStoneKnight::FPoint Position)
    {
        if(!Entity || !std::isfinite(Position.X) || !std::isfinite(Position.Y)) return false;
        std::uint64_t Previous=0;
        for(const auto& E:Events)
        {
            if(!E.EventId || E.EventId<=Previous || E.EntityId!=Entity || !std::isfinite(E.AtTime)
                || E.AtTime<0 || !std::isfinite(E.EndTime) || !std::isfinite(E.Amount)
                || static_cast<unsigned>(E.Kind)>static_cast<unsigned>(DungeonStoneKnight::EEventKind::Died)) return false;
            Previous=E.EventId;
        }
        for(const auto& E:Events)
        {
            if(E.EventId<=Last) continue;
            Last=E.EventId;
            using DungeonStoneKnight::EEventKind;
            // Movement has its own continuous state and would fill the queue
            // several times per rendered frame. Completed phases need no cue.
            if(E.Kind==EEventKind::Movement || E.Kind==EEventKind::AttackCompleted || E.Kind==EEventKind::Hit) continue;
            Records.push_back({E,Position});
            if(Records.size()>Capacity) Records.pop_front();
        }
        return true;
    }
    std::uint64_t LastEventId() const { return Last; }
    const std::deque<FRecord>& Entries() const { return Records; }
};
}
