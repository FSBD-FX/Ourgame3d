# Stable fast gate diagnostic plan

Fact: Root v001 ValidateOnly exited0 with all checks passed; approximately02:24–02:26, no precise full-run stopwatch. Actual staged core is10957B SHA f94a28e6064973781292897089fce7d92b1ab1021f82e400ef0331e3133026f1. Later developerSource298 does not affect this stableCM52f stage.

Hypothesis: repeated PowerShell provider Test-Path/Get-Item/LinkType over every ancestor dominates filesystem-check overhead, rather than143MB SHA itself. Trace: AssertStagePin→StagePath→full ancestor assert→another full ancestor assert→providerLength; exact-membership enumeration calls full ancestor assert again.

Minimal experiment: three actual representative staged files, few repetitions, compare exact v001 function with .NET attribute traversal plus unchanged provider leaf hardlink check. Measure queries only, not full launch or UE. Then preserve all1778hashes/exact hidden membership/links/engine/native/Rootapproval gates and change only the confirmed hot filesystem-query implementation.

Scope: NEWcandidate only. No stage/tools/E/Source writes, no Root approval, no full gate/native rerun. Parent directories remain freshly checked on every call; no directory cache or asynchronous validation.
