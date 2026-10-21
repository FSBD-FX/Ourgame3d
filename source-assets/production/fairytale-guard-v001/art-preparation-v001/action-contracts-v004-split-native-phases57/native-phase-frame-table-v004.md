Guard003:57stateframeentries/13rows, maximum56uniqueRGBA becauseDormantaliasesWake0.

| State | Frames | Native/display clock |
|---|---:|---|
| right_dormant | 1 | Indefinite static statue;1s is preview hold only, not activation time. |
| right_wake | 6 | S.Time-S.WakeStartedAt;clamp at WakeEnd-WakeStartedAt=1.0s |
| right_armed_ready | 4 | Artist250ms×4 idle loop; not a gameplay deadline. |
| right_move | 6 | Primary framephase is actual accepted collision-resolved cumulative traveled distance modulo128world, not elapsedtime or input speed×time. 800ms is uniform-speed160preview only, not a new kerneldeadline. |
| right_axe_windup | 6 | S.Time-A.Start;A.LockAt=A.Start+.50;A.ActiveAt=A.Start+1.00 |
| right_axe_active | 4 | S.Time-A.ActiveAt, Active[0,200ms) only |
| right_axe_recovery | 4 | S.Time-A.ActiveEnd, exact1400ms untiloriginalRecoveryEnd |
| right_stomp_windup | 6 | S.Time-A.Start;A.LockAt=A.Start+.45;A.ActiveAt=A.Start+.90 |
| right_stomp_active | 2 | S.Time-A.ActiveAt, StompActive[0,150ms) only |
| right_stomp_recovery | 4 | S.Time-A.ActiveEnd, exact1500ms originalrecovery |
| right_stunned | 4 | S.Time-(S.StunUntil-.4),exact400ms;protection1s is not extra stun. |
| right_death | 6 | From actual Died event timestamp. Visual1s proposal then lastframehold; gameplay death/body disable is immediate. |
| right_interrupted_recovery | 4 | Variable remaining original OccupiedUntil after StunUntil. Normalize remaining presentation interval; do not create new attack/recovery deadline. |

All gameplayphase deadlines unchanged. Move128world actualacceptedpath, contacts0/3/audio64world proposal. OrdinarypositiveDamaged220ms material/FX isnotHurtfullbody; Stunned400ms only actualPoiseBroken. Deathvisualfirst100msafterglowamended, deathgameplayimmediate. Sourcepose internal locks andpixelQA do notreplace perrowgroundregistration trials or running fullunitacceptance.
