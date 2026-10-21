# Guard wake v003 独立只读审查

事实：实际 `FirstRoom-20261018-113329/index.json` 是 0 成功、1 失败、1 error、0 warning，唯一失败在原生测试第70行的 endpoint-inside 前置。两次 driver `StepTo` 尚未调用。它不是 Driver semantic RED，不能据此准入生产修复。

事实：v003 使用实际 `PositionAt` 查询绝对时间，保留235×110椭圆，无 epsilon、强制递增、时钟强写或警告重播。真正醒来仍由 kernel 的目标存活、LOS、队列门及 `WakeAt+1` 决定。补丁调用处没有修改 native 输入或状态。候选9文件（包括freeze）已独立两遍读取；原freeze中8项均完全一致。详细 before pins 和实际源码/引擎头文件/RSP pins 在 `read-input-pins-v001.json`。

推理：对于连续直线段，若 outside→inside 谓词在 bracket 内单调，二分保持外/内两端，直到本地相邻浮点时间。回传前重新检查 `At>Begin && At<=End && Inside(At)`，可阻止原先解析 root 舍入回 Cursor 的非进展路径。它不会自行保证 kernel 一定醒来；真实 kernel 仍复查输入。

P2（测试已证实）：测试第68–70行由固定旧实测时间重造 narrow 终点，在当前 UE 的实际编译下 positive premise 已失败。第91–93行还要求 wide/narrow `WakeStartedAt` bitwise 相同；GameMode 第1923–1925行实际缩短后重算预测终点，所以这是两个独立舍入后的仿射映射，不能将相同 WakeAt 当作一般合同。应保留旧失败，在 NEW 测试中逐条确认实际 kernel 的合法前提，分别验证每条映射的首合法点、前邻外、一次 Wake、一秒警告及无 HP/receipt/actor 副作用。只有映射完全相同时才硬比 WakeAt。

FMath 与 FMA：本机 UE5.5 `UnrealMathUtility.h:1187–1189` 的 Lerp 是 `A + Alpha*(B-A)`；`FVector2D` 是 `TVector2<double>`，没有在已查 Core/Public/Math 找到自定义 Lerp。因此不能把差异归咎于未知特殊 FVector2D lerp。driver/kernel/test 三个实际 RSP 第39行均 `/fp:fast`，分开优化、收缩/重排与常量处理仍可能使边界值不同。但未反汇编，不证明实际用了 FMA；独立正确舍入的 FMA 模拟并未改变这组原始 endpoint/Lerp 值。实际失败究竟来自哪种编译取值，现有报告没有足够数字诊断。Python split 算法不能替代 native positive premise。自写 At 还省略 clamp 和 motion-segment 选择，今后扩展 fixture 必须使用同一绝对映射。

P2（首点完整性缺口，尚非原生拒绝证据）：patch 第25–26行在 `EllipseContact` false 时提前返回，未检查真实 `Inside(End)`，所以解析公式依然是 gate。独立 binary64 模型找到项目量级见证：中心(-800,-160)，P0=(-918.1300909769152,-64.90809692502127)在外，P1=(-918.1300940936361,-64.9080977733508)满足原椭圆，但解析 Disc=-8.866186313341173e-32。实际 driver 仍会采 End，可能只晚到 End 才醒；不能把它说成实测拒绝。patch 第36行“没有可表示合法入界”也比三点采样能证明的范围更大。应将本轮修复合同限制到已获得真实 bracket 的普通入界；若要声称所有切线/极短段均得最早点，先补真实 kernel 见证并让 endpoint 真值独立于解析 root 成败。本审查不提交生产 patch。

离散时间边界：二分终点相邻只证本地 crossing；全局最早还要求谓词单调。`NextBoundary` 会切分 motion 段，但 `PositionAt` 在 joint 使用倒序段选择，Validate 又不要求段之间位置连续。常规项目预测通常连续；不连续或 end-exclusive 段及浮点切线孔洞尚未由当前 fixture 覆盖。这是现有接口范围，不宣称新 patch 已造成原生回归。

性能：循环上限是2102，不是无限二分；独立原始 scalar 模型用40轮到相邻点（非 native benchmark）。无接触一般做3次 PositionAt，Begin重复查询；入界二分只有数值查询，不做 LOS、actor 写、分配或 kernel Step。单次 PositionAt 最坏会扫描65536段，故段数极大时新增成本显著；不能仅以“二分”宣称常数成本，也没有证据表明普通40轮接近2.297秒 ensure 开销。

风险与下一步：当前不能依据113329认定修复通过或进行生产准入。先冻结 NEW 合法 fixture，Root 真正跑出 baseline Driver semantic RED，再执行最小修复后的同测和全量、真实画面抓取。新测试的 PASS 也不能证明任意系统停顿下 Wake 所有帧都可见。本审查仅写本 NEW 目录文本/JSON，没有修改任何候选/Source/tools、执行 UE/UBT、观看或生成媒体。
