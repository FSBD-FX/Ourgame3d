# Hurt4 shared-plan production candidate v001

Candidate only, based on the actual admitted Stage0 sources pinned by `before-pins-v001.json`. No actual Source, Content, tools, tests, README or ledger was changed. Root alone applies, compiles and runs UE. No Canvas/native/visual pass is claimed here.

## Evidence and retained tests

Root observed a successful actual Stage0 editor build and exactly three semantic RED groups in `UnrealGame/Saved/Automation/FirstRoom-20261018-160223/index.json`, each one TARGET error and no warning/fixture/compile failure. Those source/test bytes remain frozen in `hurt-runtime-integration-candidate-v001/Hurt-stage0-freeze-v001.json`; its SHA is `2a2f6c20d223dfe111a251670c3d76097a576ae7d14faca253aa1954e89b3b80`.

The exact unchanged tests are:

- `CodexDungeon.Content.FairytaleSwordHurtV001.ActualPoiseBreakFourPhasesAndExclusions`
- `CodexDungeon.Content.FairytaleSwordHurtV001.RealBindingSource32MirrorAndAtomicRejection`
- `CodexDungeon.Content.FairytaleSwordHurtV001.RealCodecPauseContinueKeepsAgeAndEquipment`

The current imported32 receipt is `UnrealGame/Saved/Bootstrap/hurt32-v002-import-20261018-080500-460471.json`; its independent verification records old1254 and new32 two-SHA invariance and total1286. This is import evidence, not GPU residency or actual draw evidence. The source/profile closure remains `38e3a3c90eeda66842a2f2d5c53260832c226d18ca58640ee0720dc9271a1f28`. Source profile and all three test groups are inputs, not replacements in this production candidate.

## Admission

Recheck all six actual `before` hashes and three new-path absences, then apply `patches/Hurt-production-shared-plan-HUD-v001.patch` narrowly. The patch includes all three new files. The complete changed files are also supplied for review, but do not overwrite later Root/peer HUD changes with whole-file copies. The patch passed read-only `git apply --check` against the pinned actual baseline; see `static-preflight-v001.json` for final check and dependency pins.

Changed existing Source files (six):

- `DungeonFighter.cpp`: only the Stage0 read-only query implementation, no gameplay timing changes.
- `DungeonFairytaleSwordHurtPlan.cpp`: replaces both unsupported stubs with the one shared pure planner and the real World entry.
- `DungeonHUD.h`: exact draw observation seam/getter plus private Hurt consumer declaration.
- `DungeonHUD.cpp`: explicit Hurt opt-in and startup preload/FinishCompilation in the current Ready texture batch, before the existing render flush.
- `DungeonFairytaleSwordPresentation.cpp`: a Hurt branch before the unchanged Ready/Walk/primary path, with per-draw trace reset.
- `DungeonFairytaleSwordDrawState.h`: comment only, documenting layer authority for Hurt (no whole Body texture).

New Source files (three):

- `DungeonFairytaleSwordHurtDrawState.h`
- `DungeonFairytaleSwordHurtTextures.inl`
- `DungeonFairytaleSwordHurtPresentation.cpp`

No Build.cs change, GameMode change, actual probe startup, test replacement, asset modification or runtime count assertion is included. Root's later actual snapshot determines counts. Independent native observer/checker is owned by walk_art_fit and must merge its startup after the existing `FinishCompilation` and `FlushRenderingCommands` boundary.

Enable with `-DungeonFairytaleSwordEquipmentBoundPreview -DungeonFairytaleSwordHurtPreview` together with the existing normal trial options. The first flag still enables Ready/Walk/primary source routing; this candidate introduces only the second flag. There is no QA SpawnGuard-only game route and no automatic input in this candidate.

## Timing and ownership

`QueryHurtPresentation` reports actual native `AnimationName`, `AnimationTime`, `HurtTime`, death and driver facts. Query failure preserves every output field. It creates no time or state and does not authorize the actor. The production `BuildDrawPlan` resolves the actual World/main-player committed Binding, requires SWD001 and LGT001, reads the query and uses the same pure planner used by the frozen tests. Failure preserves the output Plan and only writes its diagnostic.

Actual positive Hurt remaining owns the end. The selector uses native age thresholds .1/.2/.3 and otherwise clamps to phase3 while genuinely active, including an observed tiny positive float tail. It neither treats nominal `.4double` as the gameplay deadline nor holds after actual native eligibility ends. `runtime-timing-authority-v001.json` clarifies the nominal400ms frozen offline metadata without changing it. Query/plan remain observable on a published paused owner, without opening Continue, altering time, reinterpreting saved age or changing equipment identities.

## Complete source and actual drawing

The frozen profile is 5 body owners plus 3 armor components times4 =32 textures. There is no WholeBody/Body import; BodyRest is a partition. The pure planner validates all32 exact retained paths, source SHA/RGBA SHA/alpha declarations, phase markers and source closure before constructing any output. It keeps the actual binding, native sample and Context in one atomic Plan.

Each phase declares nine slots in this exact order: BodyRest, ShoulderFar, Chest, NearArmWithoutHand, ShoulderNear, HelmetForeground, FarHandForeground, IndependentSword, NearHand. FarHand1/2/3 have actual declared/imported transparent sources; they load/validate then skip DrawTexture. Actual submitted counts are9/8/8/8. A missing transparent texture is not accepted as an empty layer. No Ready mask, old human body or whole-body substitution is used.

Startup preloads all32 exact object paths and the existing independent sword into the UPROPERTY-owned Frames cache. Under WITH_EDITOR they join the existing `FTextureCompilingManager::FinishCompilation` batch before the existing `FlushRenderingCommands`. Draw uses only that cache, with no first-use LoadObject. Every Hurt draw preflights the whole32 plus sword resource readiness, exact path and512x512 dimensions before any quad. A bad source, unsupported gear, missing resource or absent Canvas produces a diagnostic and zero Hurt quad submissions. The explicit opt-in route owns this failure; it does not conceal it by showing a partial pose or Ready0.

Geometry uses standing416 to display72, one constant512 canvas, actual HUD Ground/Screen/UIscale/JumpHeight and the exact frame Root/Grip/artist Axis. Body canvas size is72*512/416; the independent sword is .50 of that canvas. Left uses one UV reflection, -theta rotation and reflected pivot `(1-99/512,.5)`; right uses native UV, theta and `(99/512,.5)`. Actor collision, HP, hit kernels, IDs and inventory remain untouched. The rendering helper adds existing ActorQuads in the exact submitted order so the current occlusion path still sees the actual partitions.

## Agreed actual draw seam

`ADungeonHUD::GetFairytaleSwordHurtDraw()` returns `const FDungeonFairytaleSwordHurtDraw&` declared in the new DrawState header. It records DrawId/PlayerEntityId/SimulationTime, OptIn/Drawn/AtomicPreflightReady/MissingReason, actual Context, the SAME Plan consumed by renderer, ActualRenderedStack, Tint and nine declared Slots. Each Slot records requested/actual object path, component/index/empty/readiness/drawn, and exact float arguments submitted to DrawTexture: Top, Size, UV, UVSize, RotationDegrees, RotationPivot, DrawScale and ScalePosition. Known empty slots remain Drawn=false and never enter ActualRenderedStack. Metadata only marks a slot drawn after the real DrawTexture call; absence of Canvas never increments the draw serial or claims drawing.

The Plan retains double geometry; actual AHUD arguments are float, so an independent oracle must allow float submission rounding (for ordinary viewport coordinates around1e-4px is sufficient), not require bitwise equality to the Plan. UV, pivot and order remain exact. The existing sword record stays the Ready/Walk join witness; for Hurt its whole-body TexturePath is empty and its layer stack is authoritative. No elapsed=sim-hitAt assumption is introduced: batching may put a real hit within a simulation interval, so native query values remain the clock oracle.

## Root verification still required

First compile this exact candidate and rerun the same frozen three groups, then the appropriate full native registry. Preserve any new failure before a new version fix. A native observer must verify a real Guard issued hit and confirmed HP loss/poise break, all four actual Hurt phases, complete resident32+sword, exact shared Plan and actual slot submissions, mirrors/ground/scale/pivot, and Ready/Walk return. Source alpha, pure geometry and successful tests do not prove Canvas pixels, hilt contact, armor fit, no-pop or final visual acceptance. Root should retain fresh snapshots and all native media through the existing F/E gate before viewing or accepting.
