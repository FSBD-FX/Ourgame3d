# Move7 bounded importer candidate

Only seven original RGBA512 component textures: Rest252 E565, Near2503 E553, Far2513 E556. Derived presentation type `GuardMoveSevenComponentRigDerived`; native batch IDs are component source owners only, never whole-body frame IDs. Namespace `/Game/Production/ArtTrials/EV048/v019/GuardMoveRig`, exact names `T_GuardMoveRig_{BodyRest,NearThigh,NearShin,NearFoot,FarThigh,FarShin,FarFoot}_v001`. Root E572 review988aad91… grants preparation only. No actual Source/Content/E/tool modification, UE/import/View by author.

Safe Root source-only command (writes nothing):
```powershell
$C='F:/Ourgame/source-assets/production/fairytale-guard-v001/Move7-import-candidate-v001'
& .\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 "$C/prepare-Move7-import-v001.py" --old-snapshot 'F:/Ourgame/source-assets/production/backups/v140-Dodge196G' --validate-only
```
Expected success fields: source7_RGBA512_verified / E565_E553_E556_members_verified_twice / old1364_exactset_unchanged_twice=true; expected_final_count1371; RootApproved=false, outputs_written=false, UE_started=false, TrialAllowed/FinalAccepted=false. Root then adds `--write-prepared --output-dir <NEW-Root-Move7-import-directory>` (omit validate-only) to create exact manifest and a rejecting approval template only.

Root must separately sign a NEW actual approval file after its review: schema `Root-GuardMove7-limited-import-approval-v001`; is_template=false, RootApproved=true, limited_import_approved=true, approval_method=`Root CLI --approve-limited-import`; manifest_pin must be exact newly generated manifest, source_closure_digest=`ddce87116ffff32694e183ad7d6f121c16619ed525b57d2caf0090346ec4a51e`, Root_source_review_pin988aad91…, counts1364/7/1371, replace_existing=false, TrialAllowed=false, RuntimeTrialAllowed=false, FinalAccepted=false. Candidate writes only false approval templates and does not create that Root signature. No runtime/nativePassed approval is implied by import.

```powershell
& "$C/import-GuardMove7-v001.ps1" -Manifest <prepared-manifest> -RootApproval <Root-actual-approved-file> -ValidateOnly
# After the above passes, Root explicitly uses -ExecuteImport (omit ValidateOnly).
```
PS defaults source-only; it refuses UE/UBT concurrency and preserves partial failures. Native save reads actual Texture2D512/class/import filename/UI/TC_EDITOR_ICON/sRGB/noMips/neverstream/bilinear after save, exact7 registry and exact old1364+new7 membership. Original old CM c3bae7da… and historical Dodge1364/Guard44+50 contract pins remain unchanged. Independent receipt re-decodes source7, checks original actual metadata receipt, and makes two saved-package SHA/membership passes; it does not claim fresh UE metadata or GPU/rig/footlock proof. Source preparation permits neither runtime trial nor final acceptance. Root should perform its separate runtime registration/testing after import. Existing source/geometry/transition risks from E572 remain.

Host source-only actually passed; all7 original bytes/RGBA,18 opaque author surface values and required E ZIP member bytes verified; old1364 exactset/SHA twice passed. Five host negative tests and Python/PS AST passed. Native import, actual1371/metadata and independent post-import receipt remain pending Root execution.
