# 首个真实装备接入切片计划

2026-10-15，Asia/Shanghai。下文主体保留接线前只读规划；当前已由root分配Actor实施与独立UE测试所有权，接口约定和实际RED/GREEN见末节与report。目标：SWD001、GSW001、LGT001通过真实地面来源E拾取、双武器Q、显式满槽替换及旧物落地进入当前Actor；属性使用冻结Stats，保留当前唯一Focus权威。首批完整内容仍未验收，本计划不能算Actor获取或D13完成。

## 2026-10-15 05:29 前置纯接口状态

库存运行态桥与武器完整实例导入已补齐并冻结：Inventory schema2、77/0；WeaponActions schema3、179/0，联合纯API10/0（含整数弹仓P2修复）。具体API与限制见 [equipment-inventory-plan.md](equipment-inventory-plan.md)、[weapon-instance-import-plan.md](weapon-instance-import-plan.md) 及对应report。以下“尚缺合法更新/导入API”的原审阅文字保留为接入前历史；当前无需再用raw snapshot编辑补它们，外层应以普通候选kernel副本调用公开API。

实际Actor接线、真实地面来源ID、E/Q动作/取消/安全与HP只截一次、D13稳定Run身份/磁盘同代仍未完成。同步真实运行态会推进库存Revision，必须在同批同步后重新Prepare，不能把同步前的过期计划直接Commit。已注册动作实例重拾须复用，不以新import覆盖。Stats与Focus权威保持原计划。

## 已核实事实与影响

| 当前位置 | 事实 | 接入时的最小改变 |
| --- | --- | --- |
| `DungeonGameMode.h::FDungeonPickup` | 只有Position/Kind/bConsumed，没有SourceID、InstanceID或版本 | 增加设备来源只读投影视图，权威来源由库存＋按RoomID保存的世界设备表共同约束；不能继续以TArray下标当身份。 |
| `DungeonGameMode.cpp::TryInteract`（801起） | E循环收集附近多个原型物，85×45范围，斧头直接改WeaponId；无动作时长、LOS或显式替换 | 新接入分支只作用一个已展示稳定目标，范围80×40、LOS和地面重验；武器.35s/甲.50s后提交。旧原型路径仅保留给原QA。 |
| `RestartRun/SpawnRoom/NextRoom` | 新局直接设置sword/无甲/0金币；每房Pickups.Reset；跨房只移动同角色 | 新切片显式创建Run身份、starter实例和库存；SpawnRoom只重建当前房可见投影，不能销毁整个Run来源事实。NextRoom保留库存/CD/Focus/时钟，不调用ResetFighter。 |
| `Fighter::BeginAttack/ResetFighter` | Combat实例ID取武器枚举+1，Reset重建Combat/WeaponSkills/Dodge并回满Focus | 正式绑定时用真实InstanceID；ChangeWeapon只在提交点调用。Reset限定新局/显式QA，不能用于Q、拾取、换甲或续档。 |
| `SwitchWeapon`（589起） | bHasAxe条件下瞬间切sword/axe，不是两槽.35s动作 | 正式分支调用PrepareSwitch，保留旧当前至.35s提交；实例CD/Ammo不重建，Q过程不能被dodge取消。 |
| `BeginArmorChange/SimulateMotion` | TemplateId直设QA换甲，.5s尾在motion阶段直接写ArmorId | 保留显式QA入口；正式装备动作使用统一Pending事务，在同点伤害/死亡之后提交，避免先穿甲再吃同点伤害。 |
| `CombatContext/WeaponSkillContext` | 尚未填Stats贡献；技能只允许SWD；Focus仍由Fighter更新，技能C.FocusRegen=0 | 同步读取同一Stats结果，沿现有锁点传入伤害/动作/削韧/距离等；GSW必须使用本身definition，不能发SWD技能。Focus仍只由Fighter积分。 |
| `GetArmorRating/GetMoveSpeed/GetPoiseThreshold/SimulateMotion` | 玩家属性仍从ContentCombat基础甲表读 | 正式分支改读唯一Stats派生值；敌人/石骑仍沿原定义。甲提交前用旧Stats积分，到提交边界后才用新Stats。 |

## 切片及兼容默认

优先新增一个明确的 `EquipmentPickupProof` 集成配置，开局只有一把SWD001、grade0/no enchant/no armor。三类设备通过冻结的真实地面对象转移，另外放一把有独立InstanceID的同名SWD作为“满两槽”的替换验证来源；玩家仍须走近、选定和完成E动作。它验证实际获取桥，不冒充正式掉落/N03/N04来源或免费全装开局。

现有29项自动化及Explore26录制继续使用原明确QA配置：原型sword/axe和BeginArmorChange保留，Explore原26输入/检查、旧出口与QA换甲不改写。新配置的E/Q过程另做新录制，不把旧QA直设的成功重标成真实获取。正式DEV-REG01-PACK-v1后续接来源门：起始SWD+0/no affix/no armor/20金币一次；N03的5武器/4甲候选与2:1权重、N04的GSW32/甲28及其他商品不变。不能只因当前三件已接就过滤/重抽到这三件，也不静默把原型axe改名GSW。

建议Fighter加入显式 `bEquipmentInventoryBound`，只有新初始化入口绑定；默认QA不绑定。正式绑定后WeaponId/ArmorId仅作为HUD/动画镜像，不作为所有权来源；bHasAxe只服务旧QA。C++直接写WeaponId不得在正式分支生成实例或绕过库存，下次同步应校验/纠正镜像并给开发诊断。`sword→SWD001`仅允许显式旧QA映射，`axe`保持原型定义。

## 必须先补的纯核接口缺口

### 1. 真实实例运行数据交接

冻结Inventory没有运行数据更新入口，`ValidState`对所有历史Source的SpawnItem与当前Item比较时仍包含Ammo/CD。SWD技能锁点已经会改变WeaponSkills实例CD；直接把新CD写入Inventory快照再Restore会破坏来源一致性，也违反“不能用篡改Restore充API”。

默认方案：WeaponActions继续拥有实例Ammo/CD权威，Inventory只持提交/保存所需的当前传递快照。先由各核负责人加受身份、期望版本、时刻与专域凭据约束的“已解析运行数据交接”接口。当前持有实例才能更新；成功不改装备、HP/Focus、冷却事实，不给新CD或装填。历史SpawnItem保留原生成结果供同源回调去重，校验应区分不可变定义与可合法变化的运行数据；可用地面源须与其落地快照一致，不能被凭据绕过更新。交接及其游标同Run保存。

Q/拾取/旧物落地前先把已发生真实动作数据纳入当前基线，再Prepare。取消不回滚已发生技能CD；未提交装备事务不改双方归属。不得每帧双向覆盖两个表。

### 2. 新注册武器完整导入

`WeaponActions::RegisterWeapon(W,Id,Ammo)`总把CD置0，不能导入带已有deadline的地面新实例。建议增加经过验证的完整实例导入入口（显式deadline、ReservedAmmo必须0、唯一InstanceID），并核对Capture/Restore；已注册同实例不得重注册刷新。保留已丢地实例在动作registry的历史，避免旧窗口/事件引用失效。Q只调用已有 `EquipCompleted`，不是重新构造kernel。

### 3. 属性与一次暴击抽样

当前contexts的Critical默认false。Stats基础暴击5%是正式规则，不能仅让面板显示5%而真实分支永不暴击。新正式切片需一个Run内战斗RNG流及按 `{Owner,动作域,AttackId}` 的锁点结果凭据；先预备本次锁点候选，只有实际锁定被接受后消费一次，失败/查询不耗光标。现有时间细分已经包含两核LockTime/LockAt，可复用，不能每次CombatContext调用都抽一次或每帧RandBool。QA保持原确定性上下文。RNG整批保存仍待D13，必须标明内存验证边界。

上述接口需单独TDD后再冻结，不在Actor用公开字段写入或重建核绕过。

## 稳定身份与可保存结构

新增Run根身份和各域分配器：完整RunGUID（新局一次创建，继续沿原值）、玩家OwnerID、逻辑RoomInstanceID、单调NextInstanceID/NextSourceID/NextOperationID/RuntimeReceiptID。uint64是各Run域稳定数值键；Inventory::RunId作为显式保存的数值别名，与完整RunGUID的映射同批保存。未来D13装载必须先核对完整Profile/Run身份再Restore子核，不能只比较一个从1重来的别名。

无现成Profile磁盘账本时，新配置可以先持有这些owning字段和同批内存快照，诚实标为“Run内稳定、尚无磁盘继续”；没有保存就不声称跨进程稳定。真正接D13时保存RunGUID/映射/所有Next游标以及实例、世界来源、操作结果、动作registry和共同SimulationTime；只在新局生成GUID，加载不重新分配或散列旧ID。

`GetUniqueID`、指针、TArray下标、武器枚举、RoomNumber和RunRestartSerial均不能当D13身份。RunRestartSerial保留用于HUD探索缓存失效。正式设备来源使用 `{RunGUID,RoomInstanceID,逻辑来源键}` 登记并冻结一次结果，重复死亡/箱子回调返回同Source/Instance；旧物落地使用该装备事务预留的新SourceID。玩家/敌人的持久EntityID也需来自逻辑实体表；当前GetRuntimeEntityId及Stone预览GetUniqueID仍只算QA，不在此文档假称已迁移。

按RoomInstanceID保存世界设备表，至少包含SourceID、InstanceID、源版本、落点、settled、consumed及生成来源键。当前Pickups只是当前房投影；换房不重发来源、不重置分配器，不把留地物变金币或自动入包。是否能返房沿路线合同，不能因暂不可返就删除核的来源去重事实。

## 准入、时序与一次提交

建议GameMode统一持有库存、世界源投影、选中目标、PendingEquipmentAction和ID分配器；Fighter只提供动作准入/运行数据与提交后的属性镜像。避免世界源和槽归属分属两个各自先提交的入口。

1. E选定同房、settled、存活地面、距离80×40、无遮挡且在同一逻辑地面的一个Source；按 `(dx/80)^2+(dy/40)^2` 与稳定SourceID排序，Tab仅显式换目标。满槽/已有甲进入选槽，Enter新按确认，Esc取消；开层E不能同时确认，容量不足不透传出口。
2. 从地面待机站定（速度≤1cm/s且无移动意图）开启Pending，绑定Prepare结果、源/实例/目的版本、OperationID、起点/完成绝对时刻和已选旧物落点。Q .35、拾武器 .35、拾甲 .50；旧装备/属性始终保留至提交。开始已合法动作才清连段/输入缓冲与相应甲条件，不因失败动作清除。
3. 把Pending完成时刻加入 `NextSimulationBoundary`。GameMode当前Tick在两次 `CommitPendingDamage` 后才可处理装备提交：所有同点伤害/死亡、到期、旧装备合法治疗先结清，再取消/重验/提交。不能在SimulateMotion倒计时归零时先改甲。未来DoT也必须走相同损伤取消入口。
4. 移动意图（即使被墙挡）、正HP损失含DoT、目标/版本失效、死亡或合法dodge取消未提交equip；失败dodge不取消。Q切换是另一种独占动作，不可被dodge取消。手动丢/卸甲另要求完整安全谓词，战斗拾武器/甲不要求清房。
5. 提交点重新验证当前源/选槽/动作门/距离/LOS及落点。旧物落点沿D04固定候选序列验证房间地面/障碍，不用中心Clamp假装合法；没有合法点整次拒绝。
6. 以当前post-damage/regen基线构造Inventory、Combat、WeaponSkills和世界源候选副本。候选先完成真实实例导入/`ChangeWeapon(ContentWeapon,ActualInstanceId)`/`EquipCompleted`及Inventory::Commit，重新调用唯一Stats一次，所有检查通过后一起安装。任一失败不占Operation/source、不删旧物、不发获得音效，不自动重试或换目标。相同已成功OperationID只返回原结果，不再落地旧物。
7. Stats输入为当前active/backup/body、既有合法贡献及当前实际HP。安装时仅一次 `MaxHealth=R.MaxHP; Health=R.CurrentHP`，不把每个来源的中间上限先应用；加上限不回血，0不复活。新韧性阈值低于当前积累时按既有保护规则破韧一次，不清积累逃避。Focus与FocusConsumeAge不改、不从WeaponSkills budget回灌；当前Fighter恢复路径仅把rate/delay改读R，并在甲提交点分段积分。

玩家GetArmorRating/GetMoveSpeed/GetPoiseThreshold以及主攻/技能contexts共用当前Stats结果；伤害预算只在锁点传入一次，命中取目标当前减伤/易伤。动作倍率映射使用Stats.Final百分数，不能又乘一次DamageMultiplier；旧攻击快照不随Q改写。Dodge固定185/.40与跳高保持原值。

## 文件与执行顺序

本轮只写此计划。未来写码所有权必须由root明确分配：

1. 纯核负责人补Inventory运行快照交接、WeaponActions完整导入/RNG锁点桥需要的接口及独立RED/GREEN；保留Inventory45项和Stats16,406项。两核冻结后交还root统一构建。
2. Actor集成人负责Fighter.h/.cpp、GameMode.h/.cpp和新 `Tests/DungeonEquipmentAdapterTests.cpp`：显式Run/实例初始化、来源表、Pending动作、同点提交与单Stats镜像。`BeginAttack`取消正式分支枚举ID回填，`TryBeginWeaponSkill`允许已注册SWD/GSW真实definition；不得让GSW调用SWD技能。先保主攻/技能逻辑正确，再单独验GSW视觉，不算整件完成。
3. HUD负责人只读新增槽/选中源/预览/提交反馈：修改 `DrawHUD` 拾取物分支、`DrawInterface`，不反向改所有权；显示实际名称、当前/备用、剩余CD、正负词条和容量/失败原因。相机、角色比例、探索Reveal及当前26输入不改。
4. 输入桥在 `UpdatePlayerInput` 合并别名，按dodge→jump→skill→primary→Q→E，只接纳一个成功动作。选槽层消费Enter/E/方向键并要求释放重按，移动关闭层仍可移动。Q/E失败不自动获得低优先级物品/出口。
5. root统一取得新组RED后实现GREEN，再跑原29＋新组；已有脚本ExpectedTests默认仍22，实际执行要传真实总数，不能把计数不符当逻辑回归。Explore原26输入/检查与新的装备正常输入录像分别保留，音画/同步验收门不放宽。

必要运行用例限于真实边界：.35/.50提交前后；满槽默认拒绝、替换备用不激活/旧物完整落地；同名不同实例；Q来回保SWD技能CD；旧物再拾不刷新CD；同点正伤害/死亡先取消；合法/失败dodge对equip的不同结果；墙后/超距/移动被挡拒绝或取消；重复回调/Operation与过期版本不消源；换甲上限只截一次/Focus持续；跨房保实例与探索原换房行为。新场景测试按实际创建数量更新ExpectedTests，本文不预报已通过数量。

## root需要安排的真实缺口

无需再问用户常规实现选择。合理默认：先独立集成QA配置证明E/Q事务，再接既有DEV正式来源；先补有凭据的运行数据交接和完整导入；以RunGUID＋显式域游标设计内存身份，D13另排完整IO；GSW沿其真实技能definition而非别名替换；原QA路径保持隔离以保29/Explore26。

root需做的是分配上述冻结核与运行四文件的后续所有权、统一构建窗口及RNG/来源模块交接顺序。没有这些接口时，不能宣称三件装备的真实闭环已完成，也不能拿临时全装、篡改Restore或旧原型axe替代。

## 本次只读源码指纹

| 文件 | SHA256 |
| --- | --- |
| DungeonFighter.h | `6dbd603e1aa727d864bcf0ec07f23b690454e8ff8b1348b891c56f651f2ed102` |
| DungeonFighter.cpp | `536c76d081c19d218e0872f28ee3b82b2db6c263bc162bdcd1d4f11e92373f53` |
| DungeonGameMode.h | `9b86fc16c8368ad3f4d51c2761607ac70f978da9c5625fb8d4853926cebdcd79` |
| DungeonGameMode.cpp | `dbb606c932e114d9330a08f136ed750af2f4f57f0af3bcbf82f04b3c99f45d70` |
| DungeonEquipmentInventory.h | `c41316635d2e41044cca175d61a48e7fec91e6dd33f4be05c0fda88fca34f3c8` |
| DungeonEquipmentStats.h | `c33671c5a4fd6cf0c68ede77c473d649692dc9718f7fbd3fb9a1896a26dcb9e7` |

这些是本次读取时的源码事实，root并行构建/实录不由本任务启动。没有修改冻结核/Actor/HUD/Probe或测试，没有运行UE/UBT、生成资产或调用API。


## 本轮真实UE集成测试分工与关键边界

根任务独占UE/UBT与运行证据；save_state独占Fighter.h/.cpp、GameMode.h/.cpp；stats_review仅拥有新`Tests/DungeonEquipmentAdapterTests.cpp`及本plan/report。冻结Inventory77、WeaponActions179、Stats16,406不在本轮改动；旧29项和Explore26不放宽、不删除、不改原型axe定义。先由Actor owner给出可编译接口空桩，再由root取得真实运行RED，后续实现GREEN；不能把缺符号编译错误或测试代码存在算行为RED。

| UE组 | 正常生产路径及独立预期 |
| --- | --- |
| RealPickupTimelinesAndStats | GameMode实际地面source→E→武器.35/甲.50前后提交，GSW真实definition/InstanceID，旧装在完成前保持；最终属性与冻结Stats一致。 |
| SameTemplateAndBackupReplacement | 同名SWD不同稳定实例；满槽默认不自动替换，显式替换备用仍保active；旧物以原InstanceID完整落地。 |
| InstanceCooldownSurvivesTransfers | 真实SWD技能锁点产生CD；Q、替换落地和同实例再拾均不刷新，动作/所有权用公开API操作。 |
| FailedAdmissionPreservesDomains | 超距、墙挡LOS或非法来源失败不消源、不占实例/来源/操作域ID；纠正后仍可正常操作。 |
| SamePointDamageAndDeathBeforeCommit | 真实石骑Shield动作伤害与装备完成同点；旧甲减伤、正HP损失取消，死亡优先且无提交/消费。 |
| FinalHPAndContinuousFocus | HP+25甲→另一件HP+25甲替换保120/125，不先脱甲截100；再换HP-20甲只截到80，加上限不回血；Focus实际消费年龄连续。 |
| WallBlockedMovementCancels | 已开启装备动作时正常MoveOnGround意图被真实墙挡，实际不位移也必须取消；以后Tick不迟发提交。 |
| LegalAndFailedDodgeAdmission | 失败dodge不取消拾取，合法dodge取消；Q切换仍不允许被dodge取消，不偷改Focus或动作恢复门。 |
| CritDrawFollowsRealLocks | 只读查询/未锁windup不耗；真实主攻/技能Locked各耗一次，同次发射与重复查询不重抽，E/Q保Run流游标。 |

同点时钟不硬凑`.46f-.35`：先走真实石骑唤醒/盾击，读取driver的ActiveAt；以多个正float `GameMode.Tick`精确到`ActiveAt-duration`，正常E开始后断言公开double Deadline等于ActiveAt，再跨过端点。这样两事件共享实际公共时钟，而非误把邻近几纳秒写成同点。若生产行为无法给出该精确条件，则测试应报告前置不足，不弱化成宽容差声称已验同点。

本切片仅SWD001/GSW001/LGT001，前两者弹匣为0。可验它们携带的0弹药字段未被重置，但不能声称非零弹药射击/装填的Actor通路已测试；那属于XBW等真实远程接入后用例。非零弹匣合法运行转移目前只在纯核与独立19项审查中通过。测试允许设置公开Health为合法初始受损HP、设置真实关卡清空前置，不允许改Inventory Capture制造成功或直接写WeaponId绕过获取。


### 精确API、Focus裁定与首次RED就绪

save_state已落`DungeonEquipmentRuntime.h`精确view/registration类型及GameMode/Fighter无行为空桩：BeginEquipmentRun/注册/交互/确认/Q均false，view Bound=false、InventoryState=nullptr。独立测试文件已按这些可链接接口完成，root将取得实际UE行为RED；尚未运行不预写通过/失败数。

root明确裁定：新绑定分支以WeaponActions::Budget唯一拥有Focus，Fighter.Focus只镜像；Spend/Restore经专域receipt，StepTo按Stats且在甲提交边界分段，旧QA保历史行为。此裁定替代主体历史规划中的“Fighter唯一Focus”，理由是同一权威未来可支持STF真实资源，不能在新分支两次regen或从Q/装备重置LastActualSpend。

新测试9组，原29未改，总预期38；测试文件`UnrealGame/Source/CodexDungeon/Tests/DungeonEquipmentAdapterTests.cpp`初次冻结SHA256 `450391f49c6b2d17165244b1e54661789d310ce31eed6e90af4109e687b5a99c`，31591字节。首次RED阶段源码冻结，root唯一构建运行。API对照：GameMode正常RegisterEquipmentSource、SelectEquipmentSource、TryInteractEquipment、ConfirmEquipmentSlot、TrySwitchEquipment；Fighter正常BeginAttack/TryBeginWeaponSkill/MoveOnGround/TryBeginDodge/SpendFocus；GetEquipmentView/GetEquipmentInventoryState/GetWeaponActionsState/Deadline仅只读断言。

失败请求不得耗各域ID；已经接纳后取消的EquipmentActionId属于真实开始事实允许保留，库存OperationID只成功提交占用。测试不把取消动作开始事实当“失败应回滚全部已发生事实”。D04目标范围是80×40矩形，归一平方只用于排序；Actor不得改成椭圆。外层完整掉落固定候选不可用Clamp假落点。


### 首次构建后的测试规格校正

首轮root build失败于本Tests的Stats alias与UE全局符号冲突，没有行为RED。当前alias为EquipStats，源/旧物读取有空指针保护；Dodge组纠正为真实CD未到拒绝、合法零Focus也可取消装备且不花/回Focus，生产规则不变。同9组补矩形角合法与RestoreFocus专域边界。当前源码SHA `97e31995c3337a5000c95365f8e95db8074d563f0afa9c416389233ecd5b5375`，33598字节，待root重构建/运行，不预写结果。


### 实际RED与当前冻结交接

root实际统一build exit0后，`Saved/Automation/FirstRoom-20261015-061538/index.json`为原29 Success＋新9 Fail/notRun0，执行源97e；失败在尚缺正常BeginEquipmentRun绑定行为，不声称后置断言已逐条运行。root已准Actor owner实现GREEN。本Tests随后仅按root许可给Dodge三fixture补显式setup TestTrue，业务预期/9组不变，当前SHA `a4af489011fa89c7a3d531898a05fee0415ec30aaa7bf8542ded941e24449a3f`，33832字节，继续冻结。所有实际路径/计数/哈希见report；不把当前源码替代旧RED源证据。

### 首版实现运行与警告夹具修复交接

上述a4af为历史版本。只读审查发现房外位置注册/准入缺少共享bounds检查后，Actor owner补finite与房内范围验证；同9组Admission补MaxX外、MaxY外和NaN断言（没有独立RED）。该执行版本871b8b5c4b522914aaa004ac28a9d8d278cbb37a852395802bb711461c892b4d实际取得FirstRoom-20261015-063205全部38 State Success，但37 succeeded＋1 succeededWithWarnings，严格脚本未放行。

唯一警告由fixture清障`Wall->Destroy()`产生无WorldContext警告，root批准最小改为`SetActorEnableCollision(false)`；真实墙挡LOS拒绝与清障后同源E拾取断言保留。当前Tests冻结为34803字节、SHA256 `a13c1a86a7892f81ade4cfb8025cc5d8587cc3eea10c0b3cccf5bf36bb20c172`，待root二次build/运行。所有版本、实际日志和正常输入proof审查见report；此时仍不宣称严格38/0、正常输入实录通过、非零弹药Actor覆盖或全首批完成。

### 二次实际严格GREEN与剩余边界

上段待二次运行状态现已更新：root真实`build-editor-20261015-063702.log`构建exit0，`Saved/Automation/FirstRoom-20261015-063742/index.json`独立核对38/38 State Success，succeeded38、succeededWithWarnings0、failed0、notRun0、inProcess0；原29＋新9均无警告。Tests a13c…c172保持冻结，本次只更新plan/report，不改Source、不运行UE/UBT。

可以认定SWD001＋GSW001＋LGT001实际Actor获取/切换/替换切片GREEN，具体时轴与同点边界及原始日志SHA见report。首批内容完成数仍0/15；全装备/敌人单元、非零弹药Actor、真实来源链和D13同代磁盘闭环仍待后续工作。Explore26未改，本次38不是其重新执行结果。root下一步实际正常控制器输入capture9目前待运行，不因自动化GREEN提前认定录像通过或结束总目标。
