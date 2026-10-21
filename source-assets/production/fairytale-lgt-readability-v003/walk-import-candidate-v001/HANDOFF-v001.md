# Exact48 Walk native import candidate

Root only owns actual tool admission and UE execution. This directory is the
reviewable candidate; no asset or source pixels have been imported/changed here.

One authoritative manifest is `import-walk48-v001.json` (48 assets and six phase
object-path maps). Destination is the previously unused
`/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk`.

Runtime source mapping is RevisedWhole→Body, BodyLayers names→same runtime
component, Armor/FarShoulder→ShoulderFar, Armor/NearShoulder→ShoulderNear and
Armor/Chest→Chest. Names are `T_Fairytale_Walk_<Component>_<000..005>_v001`.
The Body whole is a reference/preload pin; the runtime renderer must continue to
emit only the exclusive body partitions plus actual matching armor and sword.

For native admission copy these four files together to Root's actual tools folder:

* `ue-import-fairytale-walk48-v001.py`
* `ue_walk48_checks_v001.py`
* `walk_png_decoder_v001.py`
* `import-fairytale-walk48-v001.ps1`

The scripts pin the one manifest in this candidate directory. The PowerShell
wrapper defaults to offline validation; Root explicitly passes `-ExecuteNative`
after admission. It starts hidden UE sequentially, demands one fresh successful
receipt, then verifies source/pixel pins, saved disk hashes and old inventory.

Offline command (no Unreal module/startup):

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 source-assets/production/fairytale-lgt-readability-v003/walk-import-candidate-v001/ue-import-fairytale-walk48-v001.py --validate-only
```

Source preparation and offline preflight each verified old Production1151 all-file
size/SHA twice. The native script refuses all object replacement, requires actual
Texture2D512x512, UI group, TC_EDITOR_ICON, no mips, never stream and sRGB, and saves
exact48. It checks target registry/disk sets and global all-file set old1151+new48
(1199 total), with two old-file size/SHA passes after save. Partial failure is
retained in a timestamped receipt; no rollback/deletion occurs automatically.

Root's E342 static review authorizes a native trial. Import does not certify live
six-phase motion, grip, physical stride, directional slip, footlock or formal unit.
80 is explicitly an art-tuned **cycle distance**, preserving game movement speed.
The frozen art marker field `locomotion_world_speed_design` is misleadingly named;
its source bytes remain unchanged and must not be interpreted as speed mutation.
