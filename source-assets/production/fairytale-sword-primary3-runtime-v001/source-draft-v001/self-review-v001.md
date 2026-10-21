# Primary3 source draft v001 — UNAPPLIED

Three candidate copies and a minimal patch are based byte-for-byte on v115 HUD, Presentation and Probe. Actual Unreal Source is unchanged. Root's pinned Primary3V001 inline is a dependency, not authored here.

Either new Primary3 flag enables native171 P2V003 plus its existing 42-texture armor chain and the established Ready/Primary1 chain. Stage2 is supported only for living grounded SWD001 actions that did not start airborne, using the real GetPrimaryPoseFrame. Primary3Preview draws the full175 body plus independent sword and bounded source-hand UV replay; Primary3ArmorPreview selects its own seven source layers. The existing exact-UV draw suffix yields BodyRest→Far→Chest→NearArmWithoutHand→Near→Helmet→Sword→NearHand. No Ready armor is borrowed for Stage2.

HUD retains all48 P3 texture references in its existing UPROPERTY Frames cache and includes them in the existing targeted compilation wait before the existing render flush. The unchanged complete resource gate rejects missing/pending selected body, armor or sword resources before drawing any selected quad. Body size, mirror, .50 sword scale, input consumption and combat clocks are unchanged.

Probe adds a separate Third branch with six real J requests at1.10/1.60/2.16 and4.30/4.80/5.36, one A request at3.40, and stop6.60. The complete old Second/first input branches and old scope strings remain byte-identical. Native CRC/FIFO/flush behavior is unchanged. New scope distinguishes175 body-only from176/177/178 armor and explicitly withholds hit, equipment, grasp, footlock, fullmotion and audio acceptance.

Static assertions verify original suffixes and actual source hashes. These checks are not compilation or runtime proof. Root must admit/rebase the patch, import resources, compile and observe real gameplay before any visual conclusion. No marker coordinates or axes are invented here.
