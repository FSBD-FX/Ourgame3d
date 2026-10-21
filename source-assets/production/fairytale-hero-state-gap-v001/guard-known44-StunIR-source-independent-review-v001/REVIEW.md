# StunIR Source4 independent narrow review

Source freeze `8a00a68ec669fd1151c5191f2898929ac294faf732c7f154d51e4d16f1f9e916` was checked against all four members twice with zero differences. This review reads the candidate and current public interfaces; it does not run UE, UBT, native input, rendering, media or tests.

## Facts

No static private-field or public API blocker was found. The actor reads public `CanStartAttack()` and `GetMeleeCombatState()`; it does not read private `HurtTime`. The custom incomplete-state deleter/UCLASS pattern follows the existing compiled observer. Full startup still requires the real preloaded44 textures before Enter and keeps logical57 scope.

J is actual controller input. Candidate CPP391-394 requests a pending combo only after ActiveEnd and End-.10; the kernel allows End-.12 through End and owns the queue and original next start (`DungeonContentCombat.h:143,147-150`). `CombatContext` owns hurt/dodge/equipment admission (`DungeonFighter.cpp:631-641`); `CanStartAttack()` includes those action gates (`1325-1329`). No direct combat kernel start or clock call is used by this actor.

Candidate CPP108-120 binds the real PoiseBroken, same-time/current-AttackId AttackInterrupted and original AttackStarted. Kernel CPP681-691 establishes85 break, .4 stun and1s protection; original OccupiedUntil is authored RecoveryEnd (`731-743`), retained across interruption. IR SourceEventId0 is the real selector contract: `DungeonFairytaleGuardPose.h:42-43,74-78` calls the default zero-event Finish and normalizes the original positive remaining interval. Kernel CPP558-564 reaches that Recovery at StunUntil when OccupiedUntil remains later.

Masks are tied to that one native action/break, real alive spatial eligibility and unique completed DrawIds (candidate CPP100-105,298-311). Pinning happens in phase8 before capture Facts; completed draw is counted before original-window failure checks (323-325). A later action cannot supply missing bits. Stun is four100ms poses; IR is four quarters of the real remaining interval, required to be at least .4. These are meaningful original-window checks, not proof yet that a live trial will sample every phase.

Only Knight/Bat predecessors use explicitly disclosed public diagnostic damage (272-278); Guard uses normal J. No Guard/hero HP, poise, time, facing, RNG/stat reset or invulnerability write was found. The display LGT source is explicitly registered then committed by normal E. Hero damage stays real: LGT retains Poise30, Axe stagger30 can break it and interrupt J for .4s (`DungeonFighter.cpp:1486,1507-1528`).

## Findings and minimal next step

**P2 — Right approach does not establish attack facing.** Candidate CPP155/168 routes from left with D to Guard+128, then Y. CPP245 stops on reaching the waypoint;387-394 may press J without observing toward-Guard Facing. Real motion changes facing only from horizontal input when allowed (`DungeonFighter.cpp:1282-1284,1696-1699`); J lock uses that facing (`DungeonContentCombat.h:67,70`). A player on the right still facing+1 aims away; Guard DeltaX is negative and native forward contact rejects it (`DungeonFighter.cpp:713-722`). Both actor and launcher permit requested right. This is a supported possible failure route, not an assertion about a run not executed here. A specifically left-side milestone may proceed with its stated scope. To support right, a NEW candidate should use ordinary A/D to face toward Guard, then observe real Facing/locked facing; never assign Facing.

**P2 — The waypoint rectangle does not guarantee SWD ellipse contact.** Target128 with per-axis tolerance6 permits absDX134/absDY6. Native stage0 SWD135 by46 yields `(134/135)^2+(6/46)^2 = 1.002253287383862 > 1`. Thus X122..134 alone does not prove contact. True native receipts prevent a false pass, but this legal corner can miss and consume hero safety/time. A NEW candidate should qualify the actual toward-facing, weapon reach/depth ellipse before J and steer using ordinary input if needed. Keep the waypoint tolerance that avoids normal30FPS oscillation; do not replace it with blindly narrow tolerance.

## Inference and remaining risks

The85 scheduler only predicts when to request J. Default one complete SWD chain totals48 stagger and two total96 if actual inter-hit gaps do not exceed1s; real hurt/cancel/contact/pacing may change that. Poise can decay before a future hit. Native events and receipts, rather than a J count, must establish the break. Candidate requires the original interval and fails on loss of any phase; a native hitch can miss Stun0 despite valid code. Hero death/nonlethal Guard failure remains possible and must be retained. Existing hero state artwork/binding gaps must remain explicit in the captured appearance.

No actual native GREEN, arbitrary-side reliability, normal-J full room clear, Death coverage, all57 or art/audio acceptance is claimed. Root alone integrates/runs. The machine-readable companion includes exact candidate/baseline pins and source line evidence.
