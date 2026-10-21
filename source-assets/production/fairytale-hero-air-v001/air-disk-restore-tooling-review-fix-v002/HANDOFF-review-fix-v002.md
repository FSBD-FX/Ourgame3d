# v144 independent tooling review fix v002

This NEW derivative replaces only the checker entry point for future Root use. Frozen v001 and all old failure reports remain unchanged. Parent freeze is `2537a9a46d743d1f32e4c7eb64f0ba232f24a28068fe09f4cf16925f3a36f5c8`. The current source freeze/protocol/actual-CM/admission/203/Production1419/OS/Codec/resource/PNG/audio requirements remain unchanged. Root must pin this NEW checker and this NEW freeze in a NEW actual prereg; FALSE templates are still not executable authorization.

Two reproduced blockers

1. The exact old 605-member executable freeze includes six intentionally empty negative-fixture WAVs. Its old freeze validator wrongly routes those metadata members through positive-length actual-evidence resolution. NEW `frozen_member` accepts only int nonnegative length and exact path/size/SHA; freeze traversal AND preflight member scans use it. The freeze JSON pin itself remains positive. Every actual native WAV/Codec/resource/source/receipt continues through unchanged `C.resolve_pin`, rejecting zero bytes. No evidence gates or frozen pure helpers are relaxed.
2. A geometrically valid prior Air trace could have missing/zero/different Air.draw_id while the same callback's old_draw ID is fresh. Every related Air callback now requires positive uint Air.draw_id equal old_draw.draw_id BEFORE the unchanged pure quad validator. No source or pixel/audio thresholds changed.

Host results: new 7-case RED retained (3 failures, 2 errors), then 7/7 GREEN; original 29/29 GREEN with its entire test body byte-exact. Core, dependencies and source binding are byte-exact v001. All existing checker function AST bodies are identical except freeze/preflight/inspect_draws; one new frozen_member function. Exact diff and machine-readable scope report accompany this handoff. Historical Frame2 geometry is only pinned data for the regression, never v144 native proof. Intentional empty WAV is only a host-negative fixture.

Final freeze will be checked using the NEW executable's own full closure function and its actual preflight-style member scan; independent PowerShell hashes also check every member. No actual preflight/UE/native/media/E/Source/Content/tools/Root approval was run or modified by this task. Root fresh scoped review and actual execution remain required.

CLI unchanged:

    python verify-air-disk-restore-native-v001.py --prereg P --preflight --out NEW
    python verify-air-disk-restore-native-v001.py --prereg P --source SOURCE_ARCHIVE --target TARGET_ARCHIVE --session PAIR_JSON --out NEW

Use the Python executable at F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe. Outputs are exclusive; reject exits 3. Main checker SHA256 `313f3130d7a069db88acc5aca3bb9826f0b4b4efd02f556b9d24d762ec3d2318`. Nothing here claims actual restored native PASS, full Profile continuity, audio queue continuity, visual or listening acceptance.
