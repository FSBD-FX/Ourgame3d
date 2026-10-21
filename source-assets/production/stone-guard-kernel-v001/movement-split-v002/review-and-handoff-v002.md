# Movement first-entry correction v002

The v0019-group standalone result did not cover pursuit partition invariance. Independent review correctly found a real defect: after wake t1 with target(0,100), whole StepTo1.7 walks toY100, whereas split at1.1 stops atY16 because only the next call observes entry into the stomp ellipse. A zero-HP/zero-stagger receipt at1.1 also inserts that boundary and changes the trajectory. This was a kernel defect, not an input or checker error.

## RED evidence and fixed test

Own MSVC /W4 /WX compiled original4de8 production against a new independent regression:1 group,6 cases,66 checks,24 failures. It covers positive/negative Y stomp entry, positive/negative Y axe entry, and positive/negative two-axis approach controls. Real wake and every public operation prerequisite passed. A further curved ellipse standalone case (X80,Y±100) failed4/6. Both RED sources/logs/executables remain immutable.

Root actualUBT231123 explicitly compiled DungeonStoneGuard.cpp and new test. ActualFirstRoom231203 gives old3 UE groups Success0errors and new Movement group Fail24errors; total warnings/notRun/inProcess0. This report was independently read and pinned in independent-readonly-audit-v002.json. Root's sole new-fixture admission difference is include DungeonStoneGuard.h -> ../DungeonStoneGuard.h; semantics were compared equal. Do not replace any Root-admitted tests.

## Narrow production change

Only DungeonStoneGuard.cpp changes. Header, definitions, attacks, damage, wake, poise, reward, reset, IDs and existing tests do not change. The old Y-first/X-second direct approach policy remains.

For the current alignment axis, compute the closed cross-section of A1's rectangle and A2's ellipse, keeping the other coordinate fixed. Both are intervals centered on the target coordinate, so their union half-reach is the greater available reach. Intersect movement with that union before issuing the read-only sweep. The analytical entry coordinate is absolute (from the frozen target and fixed axis), so it does not accumulate intermediate-frame position rounding. After reaching the entry, advance the remaining clock without more movement. A sweep blocker still clamps movement normally; no contact damage is added.

Expected independent cases: target(0,100) stops atY10 /t1.0625; (150,100) stops atY35 /t1.21875; (300,100) first alignsY100 then stopsX120 /t2.375. Mirror cases use corresponding negative coordinates. Curved X80 entry isY22.05771365940052179 (100-45sqrt3). The new tests also compare trace samples against a separately hand-derived linear path, whole/split/zero-receipt positions, stop clock, actual inside-shape attack eligibility and unchanged HP/poise/attack IDs/cooldowns. Receipt counts legitimately differ and movement event segmentation may differ; this is trajectory invariance, not a false all-history/receipt-bitwise-equivalence claim.

If the analytical boundary rounds outside the existing exact containment predicate, bounded bisection finds adjacent representable outside/inside coordinates. No epsilon or fixed simulation microstep is introduced. Absolute reached goals are preserved directly rather than From+(Goal-From), which could reintroduce intermediate-position rounding. If a positive tiny distance has no later representable calculated deadline, nextafter(currentClock,requestedClock) supplies the earliest representable advancing clock without exceeding the request. Invalid query results still roll back the whole operation.

## Actual candidate validation

New movement66/66, curved6/6; unchanged originalmain125/125 and originalboundary16/16. All four standalone builds exit0, all runs exit0:11 groups213checks0fail. See standalone-results-v002.json for exact source/log/EXE pins. Candidate v002 has not been compiled/run in UE by this author; Root should replace only the CPP then actually compile4groups and full148. Existing original3 and newfourth Automation tests stay exactly Root-admitted.

The first generated patch artifact had CRLF context and git apply --check failed against an otherwise exact4de8 baseline. It is preserved. Use movement-first-entry-v002-lf.patch (byte-exact LF): git apply --check actually exits0. Candidate CPP itself has LF and unchanged content hash. If copying the CPP, refresh its destination mtime after writing exact bytes so UBT cannot reuse the prior DLL due copy2's old timestamp. Do not treat an up-to-date build as a compiled implementation.

This correction covers fixed-target, unblocked pure-kernel pursuit. It does not prove actual wall/contact CCD, moving targets, autonomous native AI attack start at the entry, actor/driver integration, save schema or rewards/media/full unit acceptance. The future central driver must observe the exact entry query boundary before choosing an automatic attack, just as it must sample aim locks and incoming/contact boundaries. No ActualSource/UE/UBT/tools/import/ledger/media/status write was made by this author. All old54 freeze entries and the old manifest hash were rechecked unchanged.
