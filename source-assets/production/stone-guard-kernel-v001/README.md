# Stone guard kernel candidate v001

READY for Root pure-kernel Stage0 UE admission only. Read `docs/production/first-batch-v2/evidence/stone-guard-kernel-v001/ue-stage0-admission-freeze-v001.json` for4 new file destinations,3 registrations and pins. Admit `ue-stage0-admission-v001` first; its CPP is an honest false stub. Do not skip actualUBT/3 cleanRED by copying candidate productionCPP first.

Production candidate is `candidate-source/DungeonStoneGuard.h/.cpp`. Same Automation test candidates and full independent state oracle are in `tests/`. Standalone driver builds only inside `standalone/<unique-version>` with `/W4 /WX`; no UE and no ActualSource writes. Both original stub and first implementation failures remain under immutable version directories.

Current actual standalone:9 groups141 checks0 fail. Candidate UE tests:3, not run. No actor/driver/save/reward/media/full-unit acceptance. Exact design/proposal split and boundaries are in evidence/design-contract-v001.json and contract-and-self-review-v001.md.
