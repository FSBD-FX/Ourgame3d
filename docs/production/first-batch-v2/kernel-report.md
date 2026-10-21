# Task 1 动作连招核记录

状态：进行中，未接UE/未运行游戏。

依据：2026-10-14-first-content-runtime.md Task1、combo-spec.md（EV-036）。

Ruling: 遵守root限定ownership，不建立worktree、不提交Git、不改其他源码；以本报告和combat日志作本Task耐久记录。
Ruling: authored阶段以整数毫秒配置再转double，仿真时钟始终绝对double，不新设固定tickrate；这是避免十进制相加误差改变精确接段边界，不量化运行时间。
Ruling: 正式暂停/继续保D02/D11/D13清primary buffer；新增ClearPendingInput不取消活动动作/不抹掉段进度。Capture/Restore复制完整核状态，暂停适配须先清pending。

## 进度

准备RED：先写可运行空核与行为测试，失败须来自缺少动作行为而非编译/依赖错误。

RED-01：编译成功，48检查/35失败，真实缺行为，日志test-logs/combat-red-01.txt。
Ruling: double绝对deadline不以epsilon提前；多段小数相加的边界测试推进到已存End，再独立近似断言数学时点（.60/.54/.66）；不将1.14字面量误作二进制1.1400000000000001的相同bit值。

RED-02：double边界测试校准后仍48检查/35失败，编译成功。开始最小实现；未改任何其他源码。

自审RED-03：54检查/4失败。根因是Restore仅检查局部时轴，未联验排队事件ID唯一、已发窗cursor/receipt、未知shape和已结束动作counter；这会让损坏快照重复事件或复用ID。以四个真实失败测试先定位，再补四项一致性检查，不改变有效动作行为。

## 当前交付范围

- 已实现：SWD001/GSW001/SPR001普通三段9配置与完整动作核；9段总伤害/削韧/时长按生产v2守恒。
- 已提供配置：首批5武器的主攻/技能，含SPR技能三子窗、XBW有限穿透/成本、STF火线燃烧；4甲固有原始属性。未执行技能、弹仓/专注花费、投射物、燃烧或护甲伤害计算；这些是UE/后续战斗适配责任。
- Action仅3近战普通主攻。XBW/STF调用PressPrimary明确拒绝，防止未接资源时免费运行；其原配置可供后续适配。
- 未接UE、未构建UE、未启动Editor、未运行游戏；没有正式动作图/声音、真实来源、磁盘存档、联网或付费素材。

## 调用合同

namespace DungeonContentCombat（纯C++17）：

~~~cpp
FCombatKernel(EWeapon Weapon=EWeapon::SWD001, uint64_t WeaponInstanceId=1);
const FCombatState& State() const;
std::vector<FCombatEvent> StepTo(double Now, const FAttackContext& Context={});
bool PressPrimary(double Now, const FAttackContext& Context={}, bool FreshPress=true);
bool TryReverseCancel(double Now, double DesiredFacing);
void NotifyTakeoff();
void NotifyLand();
void ClearPendingInput();
bool Interrupt(EInterruptReason Reason);
bool ChangeWeapon(EWeapon Weapon, uint64_t InstanceId);
bool TryMarkHit(uint64_t AttackId, uint32_t SubhitId, uint64_t TargetId);
FCombatState Capture() const;
bool Restore(const FCombatState& State);
const FWeaponDefinition* GetWeaponDefinition(EWeapon);
const FArmorDefinition* GetArmorDefinition(EArmor);
~~~

EWeapon=SWD001/GSW001/SPR001/XBW001/STF001；EArmor=None/LGT001/MED001/HVY001/ROB001。无效配置枚举返回nullptr。

1. UE先StepTo同一权威Now并消费返回事件，再PressPrimary(Now)。Press不暗推时钟，否则调用者会丢失中间window。Press/Interrupt产生的Started/Interrupted事件排队，下一次StepTo（可以同时间）恰一次取出。
2. Context在StepTo区间内视为恒定；外部换装/属性/地面事实变化必须先分割到真实提交时间再Step。起攻仅冻结速度与完整时间轴，40%lock读取该时点Context并冻结伤害/削韧/射程/朝向/暴击结果；之后不重算。
3. EEventKind=Started/Locked/ActiveWindow/Completed/Interrupted。事件带EventId/AttackId/Stage/SubhitId/AtTime/WindowEnd与该事件Action快照。ActiveWindow是[AtTime,WindowEnd)合法区间；大步跨过整窗仍返回一次。UE须按实际区间/几何/扫掠处理，不可拿最终帧位置补造过去命中。
4. 持续active期可读State.Action.Phase与该窗口；TryMarkHit在已发窗口登记AttackID+SubhitID+TargetID唯一尝试，同目标重复拒绝。当前普通段只有SubhitId0；SPR技能3子击数据不等于普通链3个AttackID。
5. IDs为actor内单调uint64，UE需加稳定OwnerEntityID成为全局键；必须保NextAttackId/NextEventId，不用UObject地址或动画帧编号。
6. 每次新按最多一个意图，当前Recovery末0.12秒可收一个pending；完整end后才能自动接。第三段末pending可开新第一段。结束0.45秒精确截止先过期；空挥亦推进。
7. 普通未破韧伤害只触发外部反馈，不能调用Interrupt。真正PoiseBreak/Death才取消当前primary；ReverseBeforeLock仅lock前合法；SwitchWeapon/ExclusiveAction在活动primary中拒绝，避免无授权取消后摇。闲置接受其他独占动作时调用Interrupt(ExclusiveAction)清地面链。
8. NotifyTakeoff只接受闲置、地面、存活的真实起跳；清地面链并给新离地一次token。空中只能stage0；NotifyLand不取消/重起当前Action、不返还同次离地token。下一次合法takeoff才重置。
9. 正式暂停/保存：ClearPendingInput()后再Capture。继续Restore后保持UI暂停并松键，不调用StepTo推进离线；不注入物理按住状态。Clear不改活动动作、AttackID、已完成段NextComboStage/ComboExpiry。核Capture/Restore内部保全pending仅用于确定性复制；正式适配必须清除。
10. 核不拥有HP、韧性累积、CD、身体位置、技能资源、RNG源、声音或姿态停帧。Context.Critical是外部在该AttackID锁点提供的唯一结果；不得每帧抽新RNG。展示停帧只能覆盖Pose，不能暂停StepTo或改变窗口事件。

## 可保存状态字段

- 当前 Version=3（下文 R5 修订；早期验证记录为 Version=2）、Weapon/WeaponInstanceId、Time、NextAttackId/NextEventId。
- NextComboStage/ComboReady/ComboExpiry、PendingPrimary、Grounded/AirPrimarySpent/Dead。
- Action：Active/Phase/Weapon/Instance/AttackID/Stage、StartedAirborne/Locked/WindowIssued、Facing、Start/LockTime/ActiveStart/ActiveEnd/End、冻结ActionSpeedPct/Damage/Stagger/MinRange/Range/Depth/MoveMultiplier/Shape/Critical/CritMultiplier。
- IssuedWindows（每窗含 FrozenAction 值快照）、HitReceipts、尚未消费PendingEvents；不含UObject或资产指针。每条已发窗与命中receipt必须保留，当前核直到run结束才释放，因此不能无条件截断日志。
- Restore验证版本、有限时间/时轴、phase/cursor、窗口证据、未知geometry、已消费target、事件ID唯一和计数不复用；无效候选拒绝且不修改当前核。外层D13完整bundle/校验/版本/磁盘提交尚未实现。

## TDD证据

- combat-red-01.txt：实际编译成功，48检查35失败，缺失行为；不是编译错误。
- combat-red-02.txt：校准double精确边界后同48检查35失败。
- combat-green-01.txt：最小实现48/48通过，MSVC14.38 C++17 /W4 /WX。
- 自审发现4项损坏快照一致性缺口，combat-red-03.txt为54检查/4失败；在其后补Restore校验。
- combat-green-02.txt：54/54通过。
- combat-legacy-regression-01.txt：旧DungeonCombatRulesStandalone 11项通过（0 failures）。

没有运行UE自动化，因为本任务明确禁止启动Editor/构建UE；不能把standalone绿灯写成项目全套已绿。自审不是独立审查，root仍须审查并完成UE适配/运行证据。根目标保持未完成。

最终核验证：combat-green-final.txt，54/54通过，exit0；截至此记录已freeze，后续UE适配/独立review由root负责，本子任务不审阅或测试root改动。

## 独立审查修订：待发事件 Restore 联验

2026-10-14：独立 reviewer 发现，旧 Restore 对 PendingEvents 只验局部 ID/时间/字段对应，合法快照可以添入已有窗 EventId、篡改 Action.Damage=999 的 ActiveWindow，随后 StepTo 把伪窗交给调用者。此前 54 项通过未覆盖这一缺口，原冻结结论仅对应当时测试范围。

先追加真实组件测试：combat-red-review-04.txt 编译成功，75 检查中 16 失败；再最小修复，combat-green-review-04.txt 为 75 检查、0 失败、exit0，MSVC14.38 C++17 /W4 /WX。日志为新文件，旧证据未覆盖。

- 所有待发事件验证已知 Kind、子击、Action 的枚举/有限值/原阶段时间表/属性封顶和事件特定 phase、lock/window cursor、起止时点。Started 保留原起攻数据，合法属性变化仍允许在 Locked 才冻结。
- ActiveWindow 必须绑定已发 receipt 的 EventId、AttackId、SubhitId、ActiveStart/ActiveEnd；Completed 也必须有已发窗证据。禁止不同 receipt 复用 EventId，禁止把同一窗换一个 EventId 再排队。
- 相同 AttackId 的时间表、武器实例、几何等事实必须一致；两个已锁定 Action 的方向/伤害/削韧/射程/暴击冻结值必须一致。事件顺序、重复 kind 和互斥终止事件也校验；已发窗可确定同一攻击的 Started/Locked/终止 EventId 序列。
- 保护正常恢复：新增测试真实恢复 Started 单事件、锁点属性变化后的 Started/Locked/ActiveWindow/Completed 全批次、同点 Started→Interrupted，以及旧武器 Completed→新武器 Started。每批仅返回一次；拒绝坏候选不覆盖现有核的时钟或待发事件。

本修订不改变公开 API、FCombatState 布局、Version=2 或正常动作规则；未修改 UE 适配、未构建/运行 UE、未提交 Git。Restore 做内部事实一致性检查，不能认证攻击者同步改写全部相关合法历史的文件；完整 bundle 的内容完整性与来源校验仍属外层 D13。不能据此声称磁盘存档或运行游戏已验收。

## R5 复审修订：每个历史窗持有冻结事实

2026-10-14：复审给出更窄复现：军剑 A1 完成后换重剑启动 A2，快照只含 A2 Started；在队头加入旧 A1 ActiveWindow 并把伤害26改27。它虽符合属性区间，但旧 Locked 已不在队列、current 已变 A2，上一轮只比较同批快照仍漏过。新增单独历史窗/锁定/完成事件回归，combat-red-review-05.txt 实际编译成功，80 项检查中 4 失败（含旧布局拒绝测试）。修复后 combat-green-review-05.txt 为 80 项通过、0 失败、exit0。

本次状态布局变化：FWindowReceipt 追加按值保存的 FActionState FrozenAction。只有首次 Emit(ActiveWindow) 记录该窗口产生时的完整锁定事实；后续换武器、开新攻击或状态变化都不重算/覆盖它。Restore 验证 receipt 自身是匹配 ID/时间窗的合法 ActiveWindow，所有同 AttackId 的当前/待发事件再与它联验时间表、实例、几何和锁定属性。单独历史 ActiveWindow、Locked、Completed 无需依赖其他队列事件就能校验。Started 仍允许锁点前的合法属性与方向变化。

FCombatState.Version 从2升为3，公开方法签名不变。旧 Version=2 内存快照缺少这一证据，明确拒绝；本项目尚未实装磁盘存档，不补造或声称已做磁盘迁移。每窗额外持有一个无资产指针的动作值快照，随既有 receipt 保留到 Run 结束；未来若裁剪须先证明不会丢失未消费事件/命中去重事实。

测试保留合法历史单窗：已锁定78伤害/向左的军剑窗在重剑 A2 已开始时仍可恢复、仅返回一次。同步篡改全部一致性证据的文件认证继续由 D13 外层负责。本轮只改动作核、standalone 测试与本报告，新增日志未覆盖旧版；未改 root 源码、未启动或构建 UE、未提交 Git。
