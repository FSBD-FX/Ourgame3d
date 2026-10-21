# Partial v129 Wake failure: representable entry candidate v003

事实：原 PID55804 的 native_v001 是 RED，WakeMask61/Ready15/Windup63，Dormant48，185HP、0 incoming receipts。原录像/JSON/log保留不改。日志 frame310 的 GM2021 `Batch.Accepted` ensure耗时2.297s；报告第一Wake0前wall gap2.3448464s，随后一次真实delta=.40000000596使Wake0直接跳Wake2。async writer1537全保存、0拒绝、peak1。

推理：HUD BeginPlay原本已经LoadFairytaleGuardTrial全部16张并FlushRenderingCommands，Draw内无LoadObject。缺少FinishCompilation是独立潜在首用风险，现无GPU trace不能证明其致因。本候选不做预载假修复。相同原始点/float速度/5ms central interval的独立数值复现显示：宽预览得Wake入界9.607490869337335；EarliestContact缩短后重算target终点，使解析root落9.607490869337333且R²=1.0000000000000004，仍在原椭圆外。再次切分加法舍入回Cursor，驱动的`!(Next>Cursor)`拒绝合法区间。实际UE driver测试还须Root运行确认，不把独立数值复现称原生验收。

风险：任意系统卡顿仍可能漏一次性Wake；不得重播/延长Wake/放宽WakeMask63/屏蔽ensure。此修复保留原生235x110/LOS/alive/whole-room wake gate、1秒警告、AI攻击窗、HP/receipt和旧partial selector/probe/verifier全部字节。

## Root准入次序

1. 只复制 `tests/DungeonGuardWakeEntryRoundingV003Tests.cpp` 到actual module Tests；现有生产Driver不变。Root编译后跑 `./tools/scripts/test-first-room.ps1 -TestFilter CodexDungeon.Content.StoneGuardNative.WakeEntryReplannedEndpointNeverRejectsLegalInterval`，保全真实RED。测试使用实际UWorld/GameMode/public Guard owner和实际driver，复现两组合法冻结观测；不mock kernel、不造State、不加expected ensure。Stage0是现有真实Driver，故没有stub源。
2. 应用 `patches/driver-representable-wake-entry-v003.patch`，只改Driver.cpp一处helper+原Dormant入界分段。helper把解析交点仅作括号，使用InputAt相同absolute PositionAt与原Kernel相同归一椭圆判定，二分到相邻可表示时刻；前一个仍外，接受点须确实内。无时钟强写、epsilon、Next强递增、强制Wake/重试或吞错。
3. Root编译后同一新增测试应GREEN：缩短区间通过、exact endpoint、首次合法representable sample/前邻点外侧、与宽预览同Wake、原1秒、无HP/actor写、外侧近失不Wake、CanBeginWake=false仍原队列语义。再跑全部原180+新增1=181 strict，实际注册数以Root最终源码快照为准。
4. 新Root compiled Source/Content/DLL/prereg精确snapshot后，用原v002 capture tooling启动NEW媒体版本/新进程，不改旧原件。原命令flags/正常Enter/E/A/D/W/S和原Wake63/Ready15/Windup63/185HP/0receipts全部保持。保全E后Root再View。候选没有提前宣称新UE/UBT/录制通过。

## Worker已做

- 独立Python数值original-replanned RED、候选数值GREEN，结果在analysis，明确非UE。
- `git apply --check`通过；Python AST通过；旧v001/v002冻结所有文件pins完整。
- 只写本NEW目录；actual Source/Content/tools/状态、原media和原freeze未改；未运行UE/UBT/导入或View媒体。
