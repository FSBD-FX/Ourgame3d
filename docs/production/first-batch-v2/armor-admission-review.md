# 四甲与近战准入静态复核

2026-10-14，Asia/Shanghai。仅只读复核Fighter/GameMode与原设计；本轮未改实现、旧测试或冻结StoneDriver，未启动UE/构建。下述3项是具体代码路径推断，独立反例已写但尚未由本子任务实跑，不登记为真实RED/GREEN。

## 发现1：旧无敌先消耗命中凭据，过期后同有效窗仍永久漏伤（P1）

事实：`DungeonGameMode.cpp:167` 在近战分支先调用MarkContentHit；`DungeonFighter.cpp:125` 随后通过Combat.TryMarkHit写入AttackId/Target凭据。到GameMode的Apply闭包 `:159` 才验CanReceiveDirectHit，旧无敌因此只阻止扣HP，不能撤掉此前已消费的凭据。

触发：同纵深80cm目标先实际受1伤，建立原型敌0.18s无敌；立即启动军剑，其有效窗为[.17,.29)。.17处几何命中而无敌尚在，凭据被消费；.18之后旧无敌已过，但同挥砍不能再接纳该目标。本来可合法结算的一次26伤害整段丢失，目标停在99HP，预期73HP。SPR的每段单目标预算也受同一提前消费影响。

依据：装备v1 `00-共同规则.md:18` 的同挥砍同目标一次真实命中；`:24` 的旧无敌拒绝攻击不造成伤害/削韧/装备触发；D02 `/hurt`。本问题涉及准入与凭据顺序，不建议删掉旧无敌或允许重复伤害。

最小修订：在写命中凭据前验证该目标的本批直接伤害资格；保留同批已经接纳的伤害不被新无敌吞掉的既有规则。反例 `CodexDungeon.Content.ArmorAdmission.ExpiredIframesDoNotConsumeReceipt` 先用同一真实GameMode.Tick路径作无旧无敌阳性对照（100→74），再验证交叠旧无敌场景（99→73）。

## 发现2：换甲期间移动被吞掉，没有取消未提交换装（P2）

事实：BeginArmorChange在 `DungeonFighter.cpp:167` 起0.5s动作；MoveOnGround `:195` 因ArmorChangeRemaining>0直接return，不清PendingArmorId；SimulateMotion `:491` 后续仍提交新ArmorId。正实际伤害则在 `:312` 正确清掉未完成换装。

触发：开始穿轻甲，走过0.25s后给真实非零移动意图。当前移动被阻止，0.5s到点仍穿上轻甲；旧D02要求该移动取消未提交换装，保留原装备。

依据：D02 `player-combat-rules.json#/equipment/uncommitted_equip_cancel` 明确为 `movement_damage_or_valid_dodge_preserves_old_ownership`。root已据原规则纠正此前“换甲阻止移动”的实现取舍；普通攻击继续禁止与换甲重叠，不因此授权攻击取消换甲。

最小修订：合法非零移动意图先取消未提交换甲，再按正常移动边界处理；零输入不能误取消。反例 `CodexDungeon.Content.ArmorAdmission.MovementCancelsPendingArmor` 只检查取消与旧装备保留，不额外规定同次输入必须走多少距离。

## 发现3：普通小房出口复用新局Reset，免费回血/回专注并刷新状态（P1）

事实：`DungeonGameMode.cpp:137` 的NextRoom调用ResetFighter，`:138` 再加25HP。ResetFighter在 `DungeonFighter.cpp:354` 回HP、`:358` 起清动作/CD/受伤无敌、`:368` 重建Combat、`:373` 清韧性/保护、`:375` 把Focus设100和FocusConsumeAge设1。它是普通房间出口，未创建新Run。

触发：清房后HP60、真实专注消耗后Focus50/消耗年龄0.10s，并带尚余0.55s的旧受击无敌，地面待机从正常免费出口离开。当前HP变85、Focus100，旧无敌立即消失；即使只保Focus而重置消耗年龄，下一0.5s也会提前回复。本应保有的角色状态/CD和单调动作身份亦被新局初始化覆盖。

依据：D04 `inventory-rules.json#/exit/player_statuses_and_cooldown_deadlines_persist`；装备v1共同规则“角色最后一次实际消耗”及ARM-ROB-001 `/9/trait`。root明确普通小房未授权免费25HP恢复；真实跨章入口的既定恢复须另走D08对应规则。

最小修订：普通出口只搬迁地面位置并执行本房绑定攻击清理，不走新局Reset，不赠HP/专注，不清角色状态或最后消耗时间。反例 `CodexDungeon.Content.ArmorAdmission.RoomTransitionPreservesFocusAndIframes` 走真实TryInteract→NextRoom，同一测试检查房号推进、HP60、Focus50、旧受击无敌，以及总消耗年龄0.60s时仍未回专注。

## 未发现问题的范围

四甲固有属性映射与原配置相符：LGT14甲/12抗/1.08移速，MED32/18/1.0与总韧40，HVY85/12/.84与总韧70，ROB6/50/1.0与16/s专注恢复。GetArmorRating按物理/魔法分取，减伤式 `min(.6,Rating/(100+Rating))` 对这四项值正确，没有多乘固有特性。四甲当前FocusDelay均1s，SimulateMotion按本步跨越等待线的剩余时间回复，SpendFocus只有成功实际消耗才清年龄；换甲本身未清年龄，也未直接返专注。真实伤害取消尚未完成换甲的路径存在且正确。未把未来其它甲或未接入的附魔上限缺口当作本轮问题。

新增反例文件：`UnrealGame/Source/CodexDungeon/Tests/DungeonArmorAdmissionReviewTests.cpp`，经root确认恰3项，拟纳入18项统一suite；未改旧测试。由root安排真实RED后再修实现，本复核不先宣称这些测试已经失败。

审计源快照SHA256：Fighter.cpp `2b818026329e0d563324fb9d266c628d07f8f14d50f46716b64792120df622b8`；GameMode.cpp `6c3104afcc26b342d2758e365138b2aae05e04612d61a7e3f883ba95cf51988e`。行号对应这次快照，后续root改动应以方法名追踪。新测试SHA256 `5a72acf665168fcc7f7a793395ca4527c2e1aaca8fde5f0a2ba71468fd7feebb`；StoneDriver.cpp仍为冻结值 `2f9bb1f2a708d65ef7bd1f3f00690d1c2ee3266813d8a4e35be5eb57476598e7`。
