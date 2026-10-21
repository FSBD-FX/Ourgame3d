Guard003 fixed-axe whole-frame plan v002

The enemy uses one complete transparent body plus fixed208axe sprite per frame. The original v001 split-hand/weapon rig was a proposal, not a mandatory skill rule; it remains preserved and is superseded here. Existing207 is empty neutral body identity only. Generate true two-hand ArmedReady4 from accepted207Idle0 +208, then acceptArmedReady0 as future armed row identity. Never reattach206base.

55 armed frames /11rows: Dormant1, Wake6, ArmedReady4, Move6, AxeWindup6, AxeFollow6, StompWindup6, StompFollow6, Stunned4, Death6, InterruptedRecovery4. Existingneutral207fourframes are extra identity studies.

Wake1000ms:167/166/167/167/166/167. AxeWindup1000ms (lock500); AxeFollow1600ms:100/100 active,300/350/350/400 recovery. StompWindup900ms (lock450); StompFollow1650ms:75/75 active,350/350/400/400 recovery. The extra300ms IdleReady gap and cooldownfromattackstart3100/3000ms remain native facts. Stunned400ms, native protection1000ms is not extra stun. OrdinaryDamaged feedback220ms is local material/FX, never a new Hurt kernelphase. Death disables body immediately;1000ms visual collapse proposal then lastframehold cannot delay reward or collision removal. InterruptedRecovery uses only remaining occupied deadline and never replaysActive. Move is presentation substate of actualIdle+bMoving at160world/s; no separatekernelMove or charge.

Single canonical right shallow elevatedthreequarter camera; runtime mirror whole body/axe/FX forleft. Artist size100.8px/hero72px=1.4 is an initial camera candidate, not physicaldefinition. Ground contact, crown/torso density and actual closed hands through continuous shaft must be viewed/measured from retainedcuratedpixels. No guessedbones, perframescale, paintedfingers or shaftpasting.

Standard SG preview uses uniform fps; native timing sidecar has exactphase sampling and is labeled separately. Existingtools remain untouched. Independent208 transparent prop is preserved, optional deathdetach FX stays separate and harmless.
