#if defined(DUNGEON_STONE_FEEDBACK_STANDALONE)
#include "../DungeonStoneFeedback.h"
#include <iostream>
#include <limits>
using namespace DungeonStoneKnight;
namespace { int Checks=0,Failures=0;
void Check(bool Pass,const char* Label){++Checks;if(!Pass){++Failures;std::cerr<<"FAIL "<<Label<<'\n';}}
FEvent Event(std::uint64_t Id,EEventKind Kind,std::uint64_t Entity=77){FEvent E;E.EventId=Id;E.EntityId=Entity;E.Kind=Kind;E.AtTime=double(Id)*.01;return E;}
}
int main()
{
    DungeonStoneFeedback::FJournal Journal;
    Check(!Journal.Begin(0,1),"zero entity rejected");
    Check(!Journal.Begin(77,0),"zero next event rejected");
    Check(Journal.Begin(77,1),"spawn initializes empty stream");
    Check(!Journal.Begin(77,1),"same instance cannot silently reset cursor");
    const auto Wake=Event(1,EEventKind::WakeStarted);
    Check(Journal.Observe({Wake},{300,20}),"real wake accepted");
    Check(Journal.Entries().size()==1,"wake creates one feedback record");
    if(!Journal.Entries().empty()) Check(Journal.Entries().front().Position.X==300 && Journal.Entries().front().Position.Y==20,"authoritative ground position preserved");
    Check(Journal.Observe({Wake},{300,20}),"duplicate batch is harmless");
    Check(Journal.Entries().size()==1,"duplicate cannot repeat audio or VFX");
    Check(Journal.Observe({Event(2,EEventKind::Movement)},{310,20}),"non-feedback movement still advances cursor");
    Check(Journal.LastEventId()==2 && Journal.Entries().size()==1,"movement does not flood effects journal");
    Check(!Journal.Observe({Event(3,EEventKind::Died,78)},{310,20}),"foreign entity rejected");
    Check(Journal.LastEventId()==2,"foreign batch cannot consume event IDs");
    Check(!Journal.Observe({Event(4,EEventKind::Died),Event(3,EEventKind::Damaged)},{310,20}),"out-of-order batch rejected atomically");
    Check(Journal.LastEventId()==2 && Journal.Entries().size()==1,"invalid batch leaves prior output intact");
    Check(!Journal.Observe({Event(3,EEventKind::Died)},{std::numeric_limits<double>::quiet_NaN(),20}),"invalid position rejected");
    auto Invalid=Event(3,EEventKind::Died);Invalid.AtTime=std::numeric_limits<double>::infinity();
    Check(!Journal.Observe({Invalid},{310,20}),"invalid event time rejected");
    Check(Journal.Observe({Event(3,EEventKind::ChargeStarted),Event(4,EEventKind::ChargeStopped),Event(5,EEventKind::Damaged),Event(6,EEventKind::Died)},{310,20}),"real contact and death records accepted");
    Check(Journal.Entries().size()==5 && Journal.LastEventId()==6,"each actual feedback event appears once");
    for(std::uint64_t Id=7;Id<=100;++Id) Journal.Observe({Event(Id,EEventKind::Damaged)},{310,20});
    Check(Journal.Entries().size()==64 && Journal.Entries().front().Event.EventId==37 && Journal.Entries().back().Event.EventId==100,"long fights retain bounded latest 64 cues");
    DungeonStoneFeedback::FJournal Restored;
    Check(Restored.Begin(77,101),"restore can initialize at saved next ID");
    Check(Restored.Observe({Event(100,EEventKind::Died)},{310,20}) && Restored.Entries().empty(),"old saved events cannot replay on restore");
    // Real kernel events, not only manually constructed event fixtures.
    FKnightKernel Knight(88,0,{300,0}); Knight.BeginCombat();
    FWorldInput W;W.HasTarget=true;W.Target={100,0};
    DungeonStoneFeedback::FJournal Real;
    Real.Begin(88,1);const auto Before=Knight.Capture();
    const auto Result=Knight.StepTo(.1,W);
    Check(Result.Accepted && Real.Observe(Result.Events,Knight.State().Position),"actual production wake batch is consumable");
    Check(Real.Entries().size()==1 && Real.Entries().front().Event.Kind==EEventKind::WakeStarted,"actual .85 wake warning receives exactly one record");
    const auto After=Knight.Capture();Real.Observe(Result.Events,After.Position);
    Check(Knight.State().Time==After.Time && Knight.State().NextEventId==After.NextEventId && Knight.State().HP==Before.HP,"feedback consumption cannot advance clock, HP or event authority");
    std::cout<<"Stone feedback checks="<<Checks<<" failures="<<Failures<<'\n';return Failures?1:0;
}
#endif
