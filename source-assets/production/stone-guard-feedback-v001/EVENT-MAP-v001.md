# Guard feedback candidate scope

Facts: the real ENM-STN-003 kernel already issues immutable event IDs. Guard `Hit` authorizes a contact before target damage is committed. The accepted save contains the complete Guard event/movement history, but the existing saved audio seeds intentionally cover Knight only. This candidate adds a transient Guard presentation journal; no saved schema, old audio journal, old Knight journal or gameplay deadline changes. Source pins are in `baseline-pins.json`.

| Accepted source | Audio cue | Finite effect | Admission and limit |
| --- | --- | --- | --- |
| WakeStarted | GUARD_WAKE_01 | WakeCracks | once per actual EventId |
| Movement | GUARD_STEP_01 | FootDust | every proposed64cm of accepted planar distance; one ordinal per crossing, at movement receipt time |
| AttackStarted / AxeSweep | GUARD_AXE_WINDUP_01 | WindupGrit | once; stoppable audio component is cancelled by same attack interruption/death |
| ActiveWindow / AxeSweep | GUARD_AXE_RELEASE_01 | AxeDustCut | once per accepted window; air/grit accent is proposed presentation, not a fabricated ground or target collision |
| AttackStarted / Stomp | GUARD_STOMP_WINDUP_01 | WindupGrit | once; same cancellation rule |
| ActiveWindow / Stomp | GUARD_STOMP_IMPACT_01 | StompBurst | once at immutable locked center; no repeated active-frame playback |
| Damaged with actual Amount>0 | GUARD_HIT_STONE_01 | StoneChips | existing incoming resolved HP receipt; stone body material |
| Hit plus same pending-damage actual Loss>0 | GUARD_HIT_FLESH_LEATHER_01 / GUARD_HIT_METAL_01 / GUARD_HIT_STONE_01 | StoneChips or HitSparks | confirm exact original Hit EventId, target/time, actual HP loss; never audio on mere overlap or rejected damage |
| PoiseBroken | GUARD_STUN_01 | StunChips | once; does not synthesize any extra damage |
| AttackInterrupted | none | CancelAttack control request | remove same attack windup, stop its component; never reissue old active window |
| Died | GUARD_DEATH_01 | DeathChunks | once; stop windup and replace current owner effects with finite fracture |
| WakeCompleted/AimLocked/RecoveryStarted/AttackCompleted/RewardClaimed | none | none | advance event cursor only |

Material inference: current actors do not expose an actual collision physical material. Stone enemy owners classify as Stone; ARM-MED-001/ARM-HVY-001 classify equipment Metal; other targets classify FleshLeather. This is an explicit equipment/body presentation category, not a claim that a physical material query exists.

The64cm stride is a feedback proposal and must be reviewed with the new Guard locomotion art. `Movement.AtTime` equals its completed receipt boundary in the current kernel; it is not an interval-start timestamp. The candidate never invents an authoritative contact time. Positions of foot puffs interpolate only the accepted From/To segment.

Restoration: Actor restore seeds from saved `NextEventId` and reconstructs total accepted planar movement in original order. It emits no old records, retains the original foot ordinal/remainder and accepts only future source facts. Native HUD attachment starts at each existing journal tail, while newly spawned guards enter at sequence0. No audio/FX is serialized and no saved owner is replayed through gameplay.

Audio:11 original deterministic local PCM16 WAV trials exist under `audio-v001`. All are provisional voices awaiting real device audition and mix approval. They use no samples or external calls. Existing lawful project stone/weapon WAV and Kenney CC0 sources were inspected as alternative reuse interfaces; this candidate chooses distinct original voices without changing those resources. The silent proof MP4, if recorded by Root, cannot prove device audio. An offline mix made from actual native play requests is labelled a timeline reconstruction, never recorded loopback audio.

Risks and limits: event/request correctness does not establish timbre, readability at game scale or final content acceptance. Axe dust is an accepted-window accent rather than verified ground collision. Finite primitive shard/dust geometry is a runnable effect trial, not the finished hand-painted effect set. Formal room/reward integration remains owned by Root and the room agent.
