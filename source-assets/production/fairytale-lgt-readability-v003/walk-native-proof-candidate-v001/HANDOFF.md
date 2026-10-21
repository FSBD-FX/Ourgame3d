# Native brown-leather Sword Walk proof candidate

事实：旧 equipment-bound Probe 的正常 Enter/E/实例/J 三段及原生 CRC 捕获可复用为API骨架，但其 A/D 只有80ms Pulse，没有连续Walk窗口；LeatherComboOnly 把非Idle视作Primary，旧Python核验器锁定七阶段/11次按键/四种clip，不能原样作为新Walk证明。历史141观察是某次实际结果，不能当新流程目标或硬编码门。此目录提供独立 ADungeonFairytaleWalkProbe、最小HUD分支补丁、新启动器/核验器；旧Probe/六项旧工具SHA全部保持。未启动UE/UBT，未改实际Source/tools/README/台账。

推理：最少稳定方案是独立小Probe，直接使用当前真实Controller InputKey、公开 RegisterEquipmentSource、真实E提交及真实J recovery缓冲。Native GameMode继续独占时钟、移动、装备与攻击。新的 CompletedGroundMotion 纯getter 和同draw的 WalkPose/phase/cycle/path/actualRenderedstack 提供证据，不引入另一套移动或动画状态机。

风险与边界：v003才是当前准入版本。v001/v002保留；独立审查曾指出跨phase/direction提前计数和重复纯getter witness风险，v003以phase独立窗口/清计数、ExpectedSide+真实A XOR D+X方向、唯一DrawId/新Motion.ToTime和native phase→frame门修复。当前只读复审允许Root继续编译/运行准备，没有native成功。首版不录停墙；停墙视觉结论保持false，已有native逻辑测试由Root另列。公开QA来源不是正式掉落/商店；全动作、正式奖励、音频、存档和完整内容仍未接受。

## 精确准入

仅复制 `candidate-source/DungeonFairytaleWalkProbe.h` 和 **`count-boundaries-v003/DungeonFairytaleWalkProbe.cpp`**。两者SHA见 `native-code-freeze-v003.json`。仅合并 `patches/hud-walk-probe-startup-v001.patch`，不覆盖整个HUD。Walk专用 `-DungeonFairytaleWalkProof` 分支优先于已准入Guard分支；不传旧 `DungeonFairytaleEquipmentBoundProof` 或 LeatherComboOnlyProof。没有新模块依赖。

源码需要当前公开接口：`ADungeonFighter::QueryCompletedGroundMotion`、`IsOrdinaryGroundWalkPose`、`GetMeleeCombatState`、`GetPrimaryPoseFrame`，HUD的 `GetFairytaleSwordDraw`、`GetRenderedPlayerDrawStack`、`GetRenderedArmorLayerPaths`、`GetRenderedArmorLayersUsed`，及 `DungeonFairytaleSwordWalkV001::Profile/Valid/Find`。Profile无效/未配置直接exit3并保留报告；缺纹理/资源/实际层也失败，不替代旧图或伪造成功。

## 原生流程

真实Enter；原地右24cm公开注册同一QA LGT，真实E的.5s安装；同一LGT/SWD保持至结束。左A连续走至少一个80cm cycle并实际看六相mask63；松键Idle至少3个新draw；左真实J三段各六相、原始End相接，链自然过期后再次真实A Walk至少20cm/3draw；松键Idle；右D完成同流程；最终松键Idle。两侧共六个不同真实AttackId、36个attack phase/facing组合。没有瞬移、直接穿甲、强改AnimationTime、直接MoveOnGround或手动GameMode Tick。

Walk每个draw检查当前Profile的完整8层实际顺序：BodyRest, ShoulderFar, Chest, NearArmWithoutHand, ShoulderNear, HelmetForeground, Sword, NearHand；直接实际RenderedPlayerDrawStack必须相等，实际RenderedArmorLayerPaths必须是Far/Chest/Near三项。独立核验器再对外部冻结实测48个objectpath/marker、实际资源snapshot、距离/phase/按键/实例/真实J链复核。Ready/P1/P2/P3仍用当前棕皮3甲精确stack，避免灰甲回退。

## 配置输入与命令

Root先把80world/.498s/六duration、6×8真实objectpath和测量marker写进当前编译Profile、导入48纹理、编译并跑当前严格检查，再冻结新的 compiled-source-manifest.json。请同一实测配置生成器独立输出与 `expected-profile-template-v001.json` **形状完全一致**的JSON；必须 configured/source_closure_verified=true，6个duration和6帧全部填齐。template保持false空表，不能直接用于Run，也不能从native report反向倒填预期。

默认仅语法/工具检查，不启动UE：

```powershell
& .\source-assets\production\fairytale-lgt-readability-v003\walk-native-proof-candidate-v001\tooling\capture-walk-native-proof-v001.ps1
```

Root独占UE/UBT后执行：

```powershell
& .\source-assets\production\fairytale-lgt-readability-v003\walk-native-proof-candidate-v001\tooling\capture-walk-native-proof-v001.ps1 -Run -Version v001 -SnapshotManifest '<新冻结绝对路径>/compiled-source-manifest.json' -ExpectedProfile '<独立实测绝对路径>/expected-walk-profile.json'
```

启动器已核准并带上实际旧combo工具使用的四旗：DungeonFairytaleLeatherReadyPreview、DungeonFairytaleLeatherPrimary1Preview、DungeonFairytaleLeatherPrimary2Preview、DungeonFairytaleLeatherPrimary3Preview；再加 SwordWalkPreview、SwordEquipmentBoundPreview、WalkProof 和原生ContentProof/FastLossless/Async。不存在 LeatherComboPreview 旗。角色保持72px/剑.5；.498是cycle秒数。

独立只读重核：

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\fairytale-lgt-readability-v003\walk-native-proof-candidate-v001\tooling\verify-walk-native-proof-v001.py --original '<原件绝对路径>' --snapshot-manifest '<新manifest绝对路径>' --expected-profile '<独立profile绝对路径>'
```

成功技术核验后可生成短静音VFR审看录像（使用真实native frame offsets、不重绘像素，H264展示副本有常规有损编码）：

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\fairytale-lgt-readability-v003\walk-native-proof-candidate-v001\tooling\render-walk-proof-review-v001.py --archive '<包含原件/展示副本的绝对根目录>'
```

任何图/录像/派生页展示前，Root须按 `E:/OurGame/Knight/过程图稿与视频` 的README留存原件、展示副本和来源/版本/状态索引并核SHA。编码/解码通过不等于已看录像；实际回放审看后再给出有限视觉判断。

输出为runtime-report.json、prewarm和每原生MovieFrame PNG、native-frame-pixels.jsonl/async summary/lossless metadata、independent-walk-proof-verification-v001.json，及独立encode/decode日志/derivative receipt。任何失败用新版本/新archive重试，保留所有旧原件和失败。
