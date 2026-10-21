# StunIR v004 source addendum

Reviewed the NEW Source4 freeze `2c820bfbcd6aadcf600ca7decf5e18c58d1edb275175149dceac68fae0c120ea` against all four members twice:0 differences. The old v003 source and independent review remain frozen.

Both reported geometry gaps are addressed in v004. `ReachNormalStrikePoint` (CPP122-132) approaches staging140 with normal input and then uses actual inward A/D until observed player Facing equals `-ApproachSide` and actual signedDX is110..132 with absDY<=6. J is only requested after that returns true (398-405). The whole permitted default SWD rectangle is inside135x46 ellipse: maximum squared radius 0.973062615230227<1. No Facing/ActorXY/HP/poise/time/stat write is introduced.

The helper's short-circuit recursive expression has a bounded second invocation. `MoveTo(staging140,0)` only returns true within per-axis6, so its immediate same-state next invocation is already inside110..150/dy6 and cannot enter that recursive branch again. Movement remains asynchronous real controller input; a failed move does not recurse.

Header/HUD patch are byte-equal to v003. Actual break pinning, scheduling premise, spatial mask qualification and original-window failfast blocks are unchanged. No new static public API/private-field/C++ blocker was found in this narrow diff. UHT/UBT and actual native Stun4/IR4 reachability remain Root-only verification; hero damage/hurt interruption, contact, poise decay and normal frame hitches remain real possible failures. Keep failures and do not extend/replay original windows.

The protocol keeps runtime/schema v003 and explicitly records source candidate v004. The new whole tooling/prereg must bind this v004 exact freeze; tooling is not certified by this source review.

One source-line correction to the original machine JSON: Fighter CombatContext Facing is line630, not631 (which is Grounded). Other motion/lock/hit-shape evidence and the old finding are unchanged; the old artifact was preserved.

Result: the two source geometry findings are resolved by v004. No remaining static source blocker was identified within the requested scope. This does not claim native success, both-side reliability, Death/full57/full room clear, or art/audio acceptance.
