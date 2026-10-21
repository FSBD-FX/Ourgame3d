# 猎弩 Actor socket 独立审查

日期：2026-10-15。职责：独立只读审查；仅新增 `Tests/DungeonWeaponPoseSocketReviewTests.cpp` 与本文。旧 72 组、生产代码、HUD、Probe 和美术均不由本审查改写；UE/UBT 由 root 独占运行。

## 事实

- 起点为 v036 的真实 UE72 GREEN。该历史通过不覆盖尚未加入的原生持弩 socket；本轮目前没有新增测试运行结果。
- 当前 `DungeonFighter.cpp` 的 `SyncWeaponMuzzleTransform` 只同步真实 JumpHeight 与 Facing 的 X 镜像；组件默认 relative0。`GetWeaponMuzzleOrigin` 返回组件 worldXYZ，默认射弹 Height 因而只有真实跳跃高度。
- `DungeonWeaponActions::FWeaponActionsKernel` 在实际发射 deadline 消耗一次资源并使用当次 Context.Muzzle。GameMode 先提交同点旧伤害，再推进 bound WA 到 endpoint，随后消费实际发射事件。新 socket 必须使用该 endpoint 的动作时刻，不能取推进前的 WA.Time。
- `DungeonWeaponPresentation.inl` 当前从 projectile.Source.Origin.Height × 0.70 得到画面抬高量；它只读世界事件，不拥有发射或伤害权限。
- HUD 地面投影是 X×0.65、Y×−0.38；native XBW 使用 512 原画、Root(256,472)、显示 Size160。Primary 发射对应 frame2 的 Emit(423.5311940307165,224.3741693502523)。该 X 差换算为世界前向约80.5438433cm，不能漏除0.65。原画 Y 差只定义独立 presentation 高度，不能直接并入 combat Height。
- 旧 `FractionalContactsUseActualMuzzleAndCausalTime` 使用公开真实组件 `SetRelativeLocation({24,7,0})`，断言事件 Origin 为 ActorXY+(24,7)。该合法作者覆盖必须保留；本审查不改旧断言。
- 旧 `ProjectileWallsCenterBoundsAndHeight` 的 Case1 固定目标(430,0)，要求420中心硬射程拒伤。若默认原生口前移约80.54且硬门继续相对 muzzle，该目标会进入射程。这一原点冲突已提交 root；下文裁定保留旧硬门，而非改写旧测试或隐去口位置。

## 推理与风险

1. 战斗平面的 Height 应继续是实际 jump-plane 高度，保持65命中门及 Bat40 body门；独立 PresentationHeight 可由 native EmitY 的固定投影约定得到。HUD只消费 Actor 冻结事实，不反写口或战斗状态。
2. 每次真实 emission 应冻结 socket 的 clip/frame/sampleTime、instance/action/facing、combat origin 与 presentation origin。之后的移动、转向、落地和 UI 缩放不能回写历史弹体。
3. 当前 QueryContact 从事件 Origin 开始向前查询。口向前移动后，Actor→口之间的真实墙或近身敌会落到射线后方；若不处理该发射段，就会越墙或产生 D02 禁止的人造近身盲区。需要明确合法 launch-segment 的首阻挡/接触及时间定义，而非仅将画面弹迹前移。
4. 自动原生 socket 与公开组件作者覆盖必须有通用、可观察的选择规则；不能识别 QA 名称、测试坐标或命令行来保留旧结果。

## 本轮显式合同及 RED 接口

root 已明确：默认 XBW 的 `Source.Origin` 为 Actor 原生手持口 XY；每发另存真实 Actor 地面 XY 的 `RangeAnchor`，420cm 仍从角色前向 X 测量，外射余程扣除枪口前移量。D02 未明确 X 起点，这是本轮显式设计决定。合法公开 custom component 覆盖继续保留旧口坐标与口相对射程语义。Actor→口间真实 WorldStatic/近身 body 要在同一次发射时刻裁定首接触，不增资源、事件或下一帧补命中。

公开 RED seam：`GetWeaponPoseSocket() const -> DungeonWeaponPoseSocket::FResolved`，`UseAuthoredWeaponPoseSocket()`。FResolved 记录实际 clip/frame/sampleTime/instance/action/facing、原画 root/bodySize/grip/support/emit、CombatOrigin 与 PresentationOrigin。WeaponMuzzle 实际组件 worldZ 是物理手口的 PresentationOrigin.Height；GetWeaponMuzzleOrigin 特意返回真实 jump-plane 的战斗高度。

World projectile、emission/hit/stop journal 和 hit receipt 新字段仅声明，未接行为：HasPoseSocket/PoseSocket/RangeAnchor；projectile 另有 UsesActorRangeAnchor/LaunchForwardDistance/LaunchClearancePending/LaunchObstructed。RED getter保留旧组件实际值且 Supported=false，不伪造原生手口成功。

本轮接口 SHA256：

- `DungeonWeaponPoseSocket.h`：`596b553de30be27d6582c6ee1e2af137ae284ae393f50d17ad1f3a5a1c3c512c`。
- `DungeonWorldProjectiles.h`：`6b656d7da7cb9f9266b34571129804936daadc2d39a6bb2bbb917218b35b5de8`。

## 独立实际 Actor 反例冻结

- 真实 E 取得 XBW 后正常 J，观察精确 ActiveAt 发射及 native frame2；左右分别通过真实移动设定 Facing，验证只镜像 X 一次、Y不追踪、Height不额外增高。
- 公开真实组件(24,7,0)覆盖保持实际发射坐标；显式恢复 authored socket 后才重新采用原生口。
- 实际 Jump 后发射，验证 combat Height 是当次真实 JumpHeight，PresentationHeight 独立且较高；落地及后续动作不改变原事件、资源或 projectile 的冻结事实。
- 注册真实 actor→口间墙50与近身敌50作为首接触反例，要求发射同点一次 Stop/Hit、Traveled0/LaunchObstructed；另有双向420±.001的真实目标，保留角色中心硬门。历史弩矢 Source仍是真实手口，不能挪回角色来通过测试。

新文件 `UnrealGame/Source/CodexDungeon/Tests/DungeonWeaponPoseSocketReviewTests.cpp`，25,828B，SHA256 `177220ff8aedb2c36bc237a437d363e1fb73e861b1b63679313a2bed65384c40`。实际4个独立 IMPLEMENT 宏：

1. `CodexDungeon.Content.WeaponPoseSocketReview.NativePrimaryEmissionSamplesEndpointAndMirrorsOnce`
2. `CodexDungeon.Content.WeaponPoseSocketReview.PublicComponentOverrideAndAuthoredReturnRemainReal`
3. `CodexDungeon.Content.WeaponPoseSocketReview.RealJumpCombatHeightStaysSeparateFromPresentation`
4. `CodexDungeon.Content.WeaponPoseSocketReview.NativeLaunchCannotSkipNearContactOrExtendActorRange`

全部使用有合法 WorldContext/碰撞场景的真实 GameMode、绑定 Run、注册 Ammo1 来源、Controller fresh E 事务取得、fresh J 发射；空中组用 fresh Space 与实际物理跳跃。左右朝向由真实 A/D 输入取得。每组先验证真实 Issued 发射存在，再检新 socket，避免夹具未进入动作却误称行为 RED。目标仅在创建时配置 MaxHP/ResetFighter，之后不改 liveHP、位置、装备或 kernel capture。观察 Getter不分配/消耗；历史 world PoseSocket 与真实 HitReceipt 不随 UseAuthored、落地或 reload漂移。Producer另有3组，不算入本审查的4组。

## 真实 RED 独立分类

已独立读取 `UnrealGame/Saved/Automation/FirstRoom-20261015-133252/index.json`：实际80组，72 Success、8 Fail、0 warnings、0 notRun。root保存 v037 源/DLL快照810files/62,749,839B；本审查未运行UE/UBT。独立新4组均为 Fail；其真实World/sourceE/ControllerJ/实际Issued前提没有报错，区别于夹具失败。

- NativePrimary：失败在 Supported/原生frame2/手口XY/独立高度/世界snapshot；真实发射、弹药和crit前提通过。
- PublicOverride：旧24/7实际origin正控通过，失败在新override声明、snapshot与显式UseAuthored恢复；未修改旧组件作者合同。
- CombatHeight：真实ground/air发射和jump-plane高度前提通过；失败在新presentation/snapshot。Ground hit联合断言包含HasPoseSocket，因此其报错不能被误写成旧实际地面伤害本身失败。
- LaunchAndRange：失败在真实native手口/RangeAnchor声明及新同发射时刻launch碰撞。旧脚底发射的420±.001正控与后续once-only资源断言未失败；不能将本次RED声称为旧射程规则坏了。

后续producer候选若引入pre-spend immutable emission pose与current empty0口分离，必须保留该RED和冻结177220ff；Current getter不能假返回历史来通过旧联合断言。任何必要版本化由root明确授权并保留原断言意图及历史来源，不能在尚未得到实际结果前悄悄改测试。

尚无本轮Socket Actor GREEN、画面或D13持久化验收；正式15项完成不据此增加。另新正常输入录制器是独立的实现职责，见 `xbw-reload-socket-normal-input-proof-plan.md`，不计入本审查4组。

## 候选81及 v002 断言绑定

已独立读取 `FirstRoom-20261015-135821/index.json`：76 Success、5 Fail、0 warnings/notRun。Root保留v038源/DLL899files/65,348,010B，旧177220ff原稿保持可追。独立第4 NativeLaunch/420实际Success；producer PrimaryUsesCurrentActorAndAcceptedPhase（包括真实neutral发射、currentempty0实体组件及精确420剩余寿命）Success。

原独立前三组失败逐项归因于本轮新94f2状态图的口差：

- 首发 Source/世界snapshot是pre-spend neutral Emit(423.531194…,224.374169…)；发射后currentempty0是(429.062553…,229.980044…)。Root/Grip仍原frame2，原联合断言将Current的Emit/Origin/Presentation与历史Source绑成同一个位置，导致失败。
- custom24/7与世界custom历史均通过；UseAuthored恢复的是耗弹后的真实empty0，旧断言却要求neutral80.5438cm口。
- Ground/air jump-plane、noDownAim及历史不漂移通过。GroundHP联合断言含HitPoseHeight与Current高度比较，故报错不证明实际ground伤害失败。旧Bat highheight组也只失败E.X/Y与post-spend CurrentMuzzle绑定，正式65与真实16x12命中门未因此失败。

Root批准v002将这些绑定拆为：真实 `FindWeaponEmissionPoseSocket(ActionId)` pre-spend neutral冻结口、真实Issued/World/HitReceipt，另独立检currentempty94f的组件/当前getter/坐标/高度。没有把current getter伪装成历史，没有降低E、65、HP、custom、资源或历史断言。旧Bat150由root单独版本化，本审查不改它。

## 七文件冻结候选独立只读审查

`weapon-pose-socket-integration/evidence/2026-10-15_GREEN-candidate-v002/source-freeze-sha256.json` 的7文件均逐项核实际SHA/size匹配。检查了Actor pre-spend精确endpoint准备、当前empty0同步、通用component变化检测/UseAuthored返回、getter无权威写入、世界冻结Pose、角色RangeAnchor与扣余程、同点旧伤先commit及新launch消费。没有在本审查修改生产或运行UE。

具体待反例P2：

1. LaunchContact同fraction用Rank<Priority，body2优于wall4；普通QueryContact同time用Rank>Priority，wall4优先。均无epsilon。重合墙nearface与hurt入口的优先级相反；精确夹具草稿保留在 `evidence/2026-10-15_launch-wall-body-tie/snippet.txt`，不是实际RED。
2. fresh emission初始launch/zero-time query继续用旧Body.bAlive及旧伤害准入；同点旧burn先杀近敌后，可能给新箭收尸体hitReceipt/TargetLimit而挡住后方活敌。不能通过改旧interval共享准入来修；root授权先做正常技能/切换/射击的真实同点反例。

## 新6组冻结，等待实际83

root批准在原4宏之外追加：`ExactLaunchWallBodyTieStopsAtWall`、`OldBurnDeathBeforeNewEmissionCannotBlockLiveRearTarget`。新 owned tests 41,536B，SHA256 `e6f8cdc9c00a52a57855d38307c40ef76091405984d9dc5fdbbe6f93372ca11f`，实际6宏；根总数预计83，但注册/结果仍以实际UE报告为准。

Tie组双向先normalJ得到实际accepted action，只读Resolve其ActiveAt几何，再在发射前创建真实WorldStatic盒/普通敌人于段中点。actualIssued后物理Hit.Time与实际hurt Entry双严格==.5才进入墙胜出断言；夹具不精确则明确失败，不冒称语义RED。

Death组近敌仅创建时HP22，真实E/Enter取得STF0、Q/K非crit18后HP4；完整技能恢复与Q跨firstburn后HP2。从实际Burn.NextTickAt取得第二tick，减正式Windup安排freshJ；要求实际Action.ActiveAt严格等于该tick、前一可表示时刻near仍alive2、当点真实burn先杀至0且BurnTick.Sequence<ProjectileEmitted.Sequence。此后才检查尸体无新receipt/阻挡、后方200活敌收到一次真实弩矢。若前提失败，不能声称该P2已实复现。未写liveHP、位置、装备或kernel capture。

以上两P2的生产修复暂不纳入本记录；等待root实际83 RED及其来源快照。

## 两次83：有效 tie RED 与 death 夹具修复

已独立读取 `FirstRoom-20261015-142136/index.json`：81 Success、2 Fail。Tie双向实际 physics Hit.Time=.5、hurt Entry=.5，nearHP966；墙胜出/无伤/无重复门失败，是真实生产排序RED。root保留v039950files/66,913,527B。

Death当次更早失败于slot0替换前提，不是死亡生产RED。源码GameMode424满槽默认SelectionSlot=当前ActiveSlot1；旧夹具直接Enter替换了XBW1，而非想保留的starter0。另已核正式STF技能450/120/450=1.02s，Q.35完成在firstburn1.45之前.08s；旧夹具误以为Q后已烧至HP2。这两个前提错误均如实保留，未改生产迁就夹具。

root释放第6组窄修：freshE观察default1，fresh正常UI Left明确slot0，freshEnter；真实Q完成后正常AdvanceTo实际FirstTick再严格检HP2。不改HP/Ammo/死亡同点等门；前5组及helpers与e6f8前缀逐字相同。新tests42,345B，SHA `cc1620cab96e8a1d1cea55287b895acecd7c957c9a174ef794402ff1e12a415f`，仍6宏/83。旧e6f8也保存为 `evidence/2026-10-15_launch-wall-body-tie/Tests-before-firsttick-fixture-fix.cpp.txt`，SHA一致。

## 第二次83：有效 death RED

已独立读取 `FirstRoom-20261015-142649/index.json`：82 Success、1 Fail、0 warnings/notRun；tie优先级修复已真实GREEN。Death实际前提：Kcycle1.02、Qcomplete2.4299999997764825、FirstBurn2.5099999997764826、Second3.5099999997764826、Jstart3.3499999997764824、Issued3.5099999997764826、nearHP0/bDead1、旧death burn seq8先于新emission seq11。只有尸体receipt/阻挡与后方弩伤断言失败，此次才是有效死亡因果生产RED。root保留v040950files/66,914,931B。

Producer随后最小候选 `DungeonWorldProjectiles.cpp` SHA `0bc43aaf55c8576b93f8fde87cd8db92f04153d682ba332aa2620ac547687fb9` 已只读核：NewProjectile仅去重后真实新增时为true；只在该批立即To/To查询复制SkillBatchBodies，将当前valid Fighter.bDead对应局部bAlive=false。LaunchContact及普通zero-query都会排除尸体；旧From/To interval、共享准入、已受理receipts、PendingDamage与原Bodies不改。此静态审查未见新增确定P1/P2，不等于候选83已GREEN；tests继续cc1620冻结，等待root真实结果。

Root已接管新20 recorder。对其hook、60fps真实上限、ReadyIdle路径修正、HUD自身SampleTime/ActionId/Instance/实际资源历史回放、左右mask和单次Check/取消重启流程再做只读核查，暂未发现另一个确定bug；尚不冒称录制20通过。

## 最终实际83 GREEN（v041）

已独立读取 `UnrealGame/Saved/Automation/FirstRoom-20261015-143046/index.json`：83 Success、0 Fail、0 warnings、0 notRun。报告 SHA256 为 `5f23830c316ff1e21d726c7d92571540b62c81fb912f4692705fa8c8a85a2577`；独立6组与producer Socket4组全部 Success。root运行 `build-editor-20261015-142939.log` 报exit0；已读快照内构建末尾，实际4 actions完成编译World、链接DLL/lib与WriteMetadata，总43.55秒。本审查没有启动UE/UBT。

双向launch tie仍严格 physics=.5、hurt Entry=.5，nearHP均1000，墙优先与无伤/去重断言通过。死亡因果组保留真实前提：SecondBurn与Issued均为3.5099999997764826，nearHP0/bDead1，旧burn seq8先于新emission seq11；尸体无新receipt/阻挡与后方活靶一次弩伤断言现全部通过。历史142136的death夹具失败、142649的有效生产RED与本次GREEN分别保留，没有倒填。

root保留 `source-assets/production/backups/2026-10-15_socket83-GREEN-reloadArmor128-v041`（root登记950files/66,914,427B；本审查未全量复算该目录）。已独立核快照Tests为 `cc1620cab96e8a1d1cea55287b895acecd7c957c9a174ef794402ff1e12a415f`，World.cpp为 `0bc43aaf55c8576b93f8fde87cd8db92f04153d682ba332aa2620ac547687fb9`，与本次冻结候选一致。Source继续冻结，旧72与新增11的实际Actor自动化门通过；此结论不包含20项录像的整体验收、艺术动作完整性、听感、D13或正式15项完成。

## 新20首录状态另记（尚未独立审图）

root随后报告v001真实玩法20/20，左右primary mask63、reload mask15；715电影帧加1预热帧共716PNG CRC通过，音画duration差.000337秒。外层PS缺allowlist，且firstFrame .1412178秒超过既有.1秒门，故整体验证失败、未mux；不能称玩法失败，也不能称20项视觉验收GREEN。root报告E v029保全726files/2,655,032,315B、两遍SHA零差，并准备修外层接线后保持原阈值复录v002。本审查未查看该片原帧，等待v002保全与明确选帧后再独立审看。
