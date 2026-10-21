# 军剑 K 进身脚声原生观察候选 v001

状态：**Draft / NotReady，不是 Approved，不是原生通过。** 本任务没有启动 UE、编译 UE、查看图片、生成媒体或修改实际 Source/Content/tools/E/status/ledger。首单元正式完成数量不变。当前 candidate 仅为后续有真实 K8 资源时可复核、准入的具体入口。

## 事实

已有 `DungeonContentProbe.cpp:650` 的 `UnitPulse(EKeys::K)` 是真实正常输入 K；699 的额外 K 是原动作期间拒绝重入检查。该路线绑定首单元实际石像骑士，包含三段 J、伤害和恢复，并非安全的障碍边界路线。`DungeonFairytaleEquipmentBoundProbe` 现有路线没有 K。旧 v125 secondary retention 指附属归档，不能称为当前 K 动作/新脚声证明。旧 `DungeonActionAudioCaptureProbe.inl` 的 Record() 未序列化这次新 ForwardStep DTO。Landing observer 只接受 J/Shift，其六 cue locomotion ring 不接收这次 K 脚声。

当前真实生产点是 `F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWorldProjectiles.cpp:282–309`：先读 Before，执行原 Sweep、原 BatchSkillStepAt/Delta 累加、原 SetActorLocation 和 SyncWeaponMuzzleTransform，再读 After；只有合格的正位移追加 ActionAudio 记录，并附 DTO。观察器不重新执行这段业务，也不写这些字段。HUD `DungeonHUD.cpp:378–385` 调用实际 PlaySound2D 并保存 Source 的副本，脚声用已有 SoundWave、gain .25、pitch 1。这条“调用请求”不是设备发声起点。

真实 K 冷却经 `DungeonGameMode.cpp:1039–1041` 的原 CommitResolvedWeaponRuntime 落库存；`DungeonEquipmentInventory.h:189–202` 会让同一军剑实例 Version +1。初始 unlocked Action 的 CooldownDuration 真实为 0，不能从该初始快照捏造 locked 的 4；候选另存首次真实 locked action/source time。观察器只读该 locked 源及对应实际 RuntimeUpdates，核对一次 +1、ammo 不变及 LockAt+4 的冷却，保留原实例和护甲版本约束；不照搬 J 的版本全程不变门，也不替业务更新库存。

K8 typed interface 来自 runtime-plan-candidate-v001，已复制其三个 API 头为本地 references 并记录 origin pins。`GetFairytaleSwordSecondaryDraw()` 的 Sample.Action、八边界、真实 8 Slots、57 Residents、ActualRenderedStack、Binding、Geometry、ProfileReady/AtomicPreflightReady/Drawn 都按字段直接序列化。**该 runtime Profile 当前仍 NotAdmitted/runtime_not_ready；这些字段是未准入接口，不是实际当前能力。**

## 具体候选与最小准入 seam

`projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV001.{h,cpp}` 为独立默认关闭的正常输入观察器。只需 **新增 2 个 Source 文件及 3 个 opt-in inserts**，详见 exact-seams-v001.json：GameMode include、StartPlay 选择新 observer、HUD 安装 lossless capture 后抑制旧 ContentProbe。不会替换整个 HUD 或 GameMode，须与 K runtime 最新独立审阅结果按精确 seam 合成。

原始 writer 与 GPU capture lambda 从本地 before/Landing 快照按 token 提取，留在 source/ 供核对，并已内联到新 cpp；无需新增 helper 源文件。读取固定 K57 + Ready24 的 81 个真实 512px 资源，保留原 GPU BGRA8、编辑器 source BGRA8、CRC 和 metadata。纹理加载、针对这 81 个资源的 FinishCompilation、Flush、GPU/source 原件读回均先于音频、movie 和输入；不把 UObject 存在当 residency。

输入为真实 InputKey 队列 Enter → QA display LGT source → E → 正常 WASD 路线 → 至少三个 Ready 实际回调 → 单次 K → 实际 K0..7 → 原 End 后两个 Ready 回调。记录 E PickupArmor 的 Source/Instance/Action/Start/Deadline 与真实提交。只登记一个 display source，不称合法掉落/获取来源。**没有石像骑士诊断命中、HP/位置/AI/动作/时间赋值、跳跃或 J 输入。** 敌人保留正常行为；如果干扰 K、改变 scope 或导致动作中断，证据必须失败，不静默清敌。

正常右/左 full、partial、blocked-zero 已列独立 route cases。readiness-v001.json 中所有 waypoint 都标为 **PROPOSED_ONLY_NOT_NATIVE_VERIFIED**；尚未在实际 map 验证，不能因为数值看似合理而打开运行。最后位移方向已正确时不额外走一个面对方向脉冲，防止把 partial 的余量吃掉。根节点随后应在实际地图确认各条正常输入路线，并用实际 DTO 分类 full≈30、partial∈(0,30)。

## 可执行入口

在 F:/Ourgame 工作目录，用现有 Python：

```powershell
./tools/runtime/asset-gen/Scripts/python.exe -B -X utf8 source-assets/production/fairytale-sword-secondary-v001/forward-step-native-observer-candidate-v001/check-candidate-v001.py --against-current
./tools/runtime/asset-gen/Scripts/python.exe -B -X utf8 source-assets/production/fairytale-sword-secondary-v001/forward-step-native-observer-candidate-v001/tests/test-causal-boundaries-v001.py
./tools/runtime/asset-gen/Scripts/python.exe -B -X utf8 source-assets/production/fairytale-sword-secondary-v001/forward-step-native-observer-candidate-v001/drive-swd-forward-step-native-v001.py --case full_right
```

第三条当前必须 NotReady / exit 2，native_run_attempted=false。六个 case 都已验证这一点。只解析 JSON 和 pins，不启动进程，不创建外部证据目录。未来根节点完成 source/art review、source admission、Editor compile、全部测试、实际 DLL/完整 compiled manifest pins、81 source/uasset pins、正常路线验证、实际像素 checker 后，应写 **NEW prereg 文件**，不编辑当前冻结候选。再显式传 `--prereg NEW.json --case ... --run --archive NEW_ABSOLUTE_DIR`。driver 再核当前完整 Source/compiled manifest、DLL、review 和资源 pins，只接受固定真实 map 与固定 argv，使用隐藏进程。该动作本任务没有执行。

checker 将独立核 source parent Run/Room/Owner/Action/Instance 与 EventId/SubhitId、真实 DTO Present、Before+CommittedDelta=After、实际 signed 30cm 请求与实际 full/partial 分类、ActiveAt、唯一 append/request、HUD Source 深拷贝、真实 SoundWave/.25/pitch1、来源回调 sim/wall bounds、原 action deadlines、冷却版本实际库存回执、K8 原时轴/八层/57 residency、Ready 入口/原 End join。随后复用原完整 MainMix PCM checker 和完整 native PNG CRC/FIFO checker，核每个真实 source PNG 与 GPU/editor 像素一致。

当前尚无 K 的实际 PNG layered composition verifier；prereg 必须给带 pin 的 `checker_dependencies.K_pixel_composition`，其 `audit(archive,prereg)` 必须返回 actual_native_pixel_composition_verified=true。缺失不能靠布局公式、layer 名称、空 true 字段或复用 J 的通过值替代。整体 MainMix 非静音与真 request/source 因果链仍不能证明单独脚声波形已被识别、听感已验收或设备起点已测量；这些结论明确 false。

## 零位移缺口与最小下一步

正位移 DTO 是可用的实际 placement witness；完全 blocked-zero 没有 append，故没有 DTO。CompletedGroundMotion 是整个 callback 的移动观测，不能替代该 ForwardStep 事件 Set/Sync 后的独立 Before/After。**候选 source 与 driver 无条件将 blocked-zero 两案拒为 NotReady**，checker 对“无 fact、无 request”也返回 NotReady，绝不伪造 Present=false 的零 DTO 或调用 kernel 重放。

若要完整做零案，需要另一个小型只读观测 seam：在原 ForwardStep 的 SetActorLocation/Sync 后，保存该事件真实 Run/Room/Owner/Action/Instance/EventId/SubhitId、AtTime、Before、After、RequestedSignedDistance、Grounded、Commit observed；包括零位移，由只读 getter 提供。不要改变 BatchSkillStepDelta、cadence、Append 签名或加入假音频事件。这需要根节点另行具体制作、独立审阅、准入和原生运行；当前候选没有偷偷补此业务字段。full/partial 四案可在其余门满足后先独立运行，不能算 blocked-zero 通过。

## 已完成的有限验证

reports/host-causal-boundaries-v001.json 为 **36 项 host 模型检查 / 0 失败**。包含四个左右 full/partial 正例及 parent、DTO、真假零、actual request copy/gain/path、source callback、重复/缺口、K8/slot/resident/End、库存 +1/cooldown 等反例。它们不创建 native 声画，也不是 UE 编译或原生结果。reports/driver-current-NotReady-v001.json 为六案未启动 UE 的 fail-closed 实录。reports/structural-candidate-v001.json 为两目标插入后字节逆变换、禁止 forcing/ring seam 和 Python AST 检查。初始提取脚本的缩进假设失败保留在 preparation-failure-v001.json，按 token 修正；不是游戏 RED 运行。

风险/限制：新 cpp/h **未 UHT/Editor 编译**，未独立代码 Approved，未实际 map 运行；真实 K Profile/层图及当前 compiled manifest 未到位。不得直接准入冻结草案并宣称完成。最小推进是先完成和审阅真实 K8 资源/运行接入，再 fresh review 本 observer、按三个 inserts 合成、编译与全套回归，补 NEW prereg 后跑左右 full/partial；零案要先做上述独立 placement 观测。
