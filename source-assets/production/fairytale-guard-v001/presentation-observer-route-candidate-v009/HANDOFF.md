# v009：真实侧向路线与空间核验候选

事实：旧右侧 PID53660 的 actual_approach_side=+1 只是所选意图/朝向。原生坐标最大 dx=1.6022676888578644，末 dy=44，HP=26.31578826904297；严格 Ready 位置 mask=0、前摇前三相 mask=0。旧左侧 PID55528 的对应 mask=15/7，末 dx=-151.03835876860694、dy=-2.2095527745469212、HP100。原报告/核验 passed 原样保留；右侧范围更正为 RightFacingOnly_NotRightSpatialApproach。旧 metadata review 关于双侧空间的推论撤回，新纠正 JSON 独立留档。

推理：旧 MoveTo 首选 Y-first，路径规划只检查房间障碍；接近守卫时正常身体碰撞阻止横穿，朝向检查仍给计数。v009 用已出生守卫与玩家的实际 GetCombatBodyHalfExtent，加8 world余量，选择 GuardY±140 的合法上下通道。三段均由普通 WASD 到达：原X→外侧通道、通道横移至 GuardX+Side*150、再纵向接近 GuardY。原生移动/碰撞决定实际位置；路线点不能写 actor、守卫、HP、时钟、状态或无敌。

新增空间门：实达三段之后 Ready 与 AxeWindup0..2 的每个计数样本必须 Facing==Side，真实 signedDx 在[120,180]，半径≤180，absDy≤12。AxeWindup3..5 可在真实同 AttackId、原生 Locked=true、SampleTime≥原 LockAt 后纵向避让，但 signedDx 仍在[120,180]。Wake63/Ready15/Windup63 与一次 Wake 失败快退保持。任何玩家受伤都失败，保留伤害结果，不恢复HP。Guard185/0incoming 仍硬约束。

源文件：new-source/DungeonGuardArtPartialProbe.cpp 基于当前实际29131B ee9706ff2b0dd6f4608862507d62e2c5950ac706dfaf2044f76b82a3a5ed87e8；source-route-freeze-v009.json 锁源码/最小diff/基线pin。H逐字复用，既有 actor 与 DungeonGuardArtPartialProof 入口不变，无 HUD 改动、无新测试注册。Root 按 patch 或冻结 CPP 合入，其他 Source 不覆盖。

核验与启动：tooling/verify-guard-art-partial-v009.py 保留 v002 所有原生事件、时钟、16纹理、镜像floor、单层、观察帧和CRC/FIFO检查，独立重算每帧实际空间资格并比较 native SpatialCoverageEligible。三段实际到达点必须在原观察记录中有同sim/同坐标见证。tooling/verify-native-pixels-v002.py 是旧依赖逐字副本。新冻结仅约束新候选；Root 新 compiled snapshot 和 typed prereg 必须精确绑定实际全部 Source/Content/DLL/构建/全回归，含新实际 Probe pin。不能拿旧v130 snapshot启动新路线。

Root 准入后示例（Snapshot 与 RootPrereg 换成实际新冻结路径；不要使用虚构 hash/count）：

```powershell
$tool='F:/Ourgame/source-assets/production/fairytale-guard-v001/presentation-observer-route-candidate-v009/tooling/capture-guard-art-partial-v009.ps1'
& $tool -Version sideL_route_v009 -Snapshot $Snapshot -RootPrereg $RootPrereg -ApproachSide -1 -ValidateOnly
& $tool -Version sideL_route_v009 -Snapshot $Snapshot -RootPrereg $RootPrereg -ApproachSide -1
& $tool -Version sideR_route_v009 -Snapshot $Snapshot -RootPrereg $RootPrereg -ApproachSide 1
```

两次必须fresh PID，原件目录不能存在。全部当前棕皮Ready/P1/P2/P3、LGT/Walk与partial Guard flags逐字继承旧启动器，正常t.MaxFPS30，无手调Tick。原生或独立核验失败保留原件，不编辑报告、不降低几何/coverage门。新 schema=guard-art-partial-native-observer-v009，session schema=guard-art-partial-native-session-v009，新 receipt=independent-guard-art-partial-v009.json。

只读重现旧报告空间问题：

```powershell
& 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-guard-v001/presentation-observer-route-candidate-v009/tooling/audit-existing-spatial-core-v009.py' --report 'F:/Ourgame/过程图稿与视频/2026-10-18_石守卫三行整身原生试样_v003/原件/runtime-report.json'
```

这只检查旧真实位置核心，不是新路线通过。old-original-spatial-regression-v009.json 留左15/7、右0/0见证。candidate-static-validation-v009.json 只证明15个空间反例、Python AST、PowerShell AST、patch check与依赖pin；无 UE/UBT 或新运行结论。

风险/范围：上下通道是当前正式 FirstBatchGuardRoom 的已知几何候选；实际路线与安全避让仍待 Root 编译/真实捕获，不宣称可玩通过。Guard只有房间计划出生，Knight/Bat仍为明确公开伤害诊断清除，不称全战。只有209/210/212三行partial试样，其他动作仍程序gap，无完整敌人/最终美术/声音验收。已有36样本仅30张实际View，剩6张按Root优先路线任务暂停；不把未看样本写成已审。所有旧freeze/report/tool/media不改，本目录只新增候选；Root负责E保全后再View新媒体。

展示选帧门：新 Ready/Windup PNG 必须从独立 receipt 的 coverage_witnesses / SpatialCoverageEligible=true 选择，同 DrawId 与 observation；不能继续使用仅Facing的最早样本筛选。Dormant/Wake按原真实观察保留，视频保持全部原始帧和原始wall offsets，不剪掉路线或失败。
