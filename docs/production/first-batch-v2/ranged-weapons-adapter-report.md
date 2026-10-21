# 弩杖与世界武器事件接入：独立测试记录

2026-10-15，Asia/Shanghai。当前已认证：root构建082345 exit0，082722严格52/52 Success，逐组warnings/errors均0，包含未改88fecbea新增XBW落地完整装填case。端点P1与落地P2真实RED→GREEN、首轮夹具错误及各版原件独立保留。v020的585份载荷/51,392,132字节已独立逐项bytes/SHA核对零差异；其后未编译源码另算。首批正式完整内容仍0/15。

## 已实际完成的检查

- 独立读取了D02 `player-combat-rules.json`、D03 `common-rules.json`/`states.json`、D04 `inventory-rules.json`、冻结 `equipment-v1/weapons.json`、`DungeonContentCombat.h`/`DungeonWeaponActions.h`、真实Fighter/GameMode和装备Actor报告。
- 实际预检确认bound非近战主攻与XBW/STF技能尚未进入生产动作；世界事件消费尚无飞行弹；SPR技能循环命中所有合法目标。这些是源代码事实，尚未冒充UE行为RED。
- 与owner冻结可编译DTO/接口，root裁定真实muzzle组件默认偏移0及Run单调EntityID；测试通过真实组件偏移/移动核对发射样本，未硬造固定武器偏移。
- 首次冻结的新文件实际包含13个测试宏、13个唯一 `CodexDungeon.Content.RangedWeaponsAdapter.*` 名称。PowerShell读取文件长度/SHA并枚举确认；`git diff --check`无文本错误。后经root许可追加第14边界组，历次freeze如下；本任务未运行UE/UBT或修改原38组。
- 独立读取旧基线 `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-064514/index.json`：tests38、succeeded38、succeededWithWarnings0、failed0、notRun0、inProcess0，SHA256 `d255088df5ed14e211c25210e3ee52c5a785274de16f10caad7006013e18d5b9`。该旧结果不认证新13。

| 测试源码原件 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Source/CodexDungeon/Tests/DungeonRangedWeaponsAdapterTests.cpp` | 43339 | `1696097c2b3ed497b70cd03fd0ad7df4c3e7b7c0ed353e087c7a73f22971cde2` |

首次13组完整名称与用例范围见同目录 `ranged-weapons-adapter-plan.md`。当时根线程已有38项，候选总51来自实际13项相加，以下保留当时的运行注册核验过程。各组均用真实GameMode/World/碰撞/来源E事务/Q/.35时轴，绑定后调用Fighter主攻、技能、T装填或实际控制器输入，观察WA预算/CD/crit、世界receipt/journal与实际HP，不改Capture或直接spawn弹体。

root于07:19启动统一构建 `UnrealGame/Saved/Bootstrap/build-editor-20261015-071905.log`，root报告exit0；本任务独立读原件确认新Tests编译、DLL链接与26action完成，耗时94.47秒。测试源码在构建/首次运行期间保持上述freeze。

## 首次51组运行与夹具前提勘误

独立完整读取 `FirstRoom-20261015-072053/index.json`：tests51、succeeded38、succeededWithWarnings0、failed13、notRun0、inProcess0。原38全部Success，新13全部Fail，逐项warnings0/errors1；每组唯一错误都是自己的首个 `Create` TestTrue失败，未进入后面的武器时轴/世界伤害/状态断言。

定位到两个测试前提问题，不能修改生产规则迎合它们：

1. `FEquipmentInventory::Commit` 空武器槽拾取会自动激活取得的武器，原EquipmentAdapter测试也直接验证该行为。新fixture在E完成后只按一次Q，结果切回starterSWD，最终期望新武器而返回false。应增加正常Q回切，让E→Q starter→Q acquired保持真实操作覆盖。
2. QA来源Item的默认Ammo是0，Inventory保留来源的真实Ammo。需要在初始弩来源显式作者Ammo1，不能让生产拾取偷偷免费补满。

这次运行是真实可编译的失败记录，但失败来自新测试夹具，不能将它写成13项生产后置行为RED。修正前已将发现发root/owner，源码未擅自解冻；需要新SHA和新的统一运行。原失败原件保持。

root随后明确许可只修夹具：XBW001 QA来源显式Ammo1；E空槽自动激活后走两个正常.35秒Q事务，回到同一个新武器实例；补Create分阶段 `AddError`，再次失败可定位注册/E/Q/最终实例等阶段。原13组业务期望、原38、生产激活/弹药规则均不改。修后新文件44,437字节，SHA256 `ace5824a0c2db9144a8637267363f18a58d01c012c51570bc734a6549c0bf7ca`，宏13不变，已重新freeze交root第二次构建/行为RED。此版本尚无运行结果，owner仍保持行为桩。

| 原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-071905.log` | 5645 | `3f7c4a217f0f4ee65efae4fefd1c15109dbc2349064d4387785d6530545133a4` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-072053.log` | 220711 | `b7290f5c7a04a81c564f1428ddabdb81d7082a52260c24ddfbe639dddf7c3ebb0` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-072053/index.json` | 29753 | `ded65dee9b115a4f0e4ec018007bc3823c8613020bd543b030ef169afdf0785c` |

## 后续结果登记规则

只有root实际构建exit0后的Automation `index.json` 才能登记业务RED/GREEN；原件路径、字节、SHA、succeeded/succeededWithWarnings/failed/notRun/inProcess及逐组结果须独立读取。编译错误不能当行为RED。失败原件不覆盖，owner取得root明确GREEN许可前保持行为桩。

未来GREEN也仅证明本切片的规则、实际碰撞、世界发射消费和输入入口；不能由此认证正式美术socket、声音表现、正常操作录像、D13同代磁盘、全部正式来源或总15单元完成。

## 第二次统一运行：真正行为RED

root执行 `build-editor-20261015-072344.log` 并报告exit0；独立读原件确认重新编译新Tests、GameMode及root HUD/Probe，8action含DLL链接全部完成，耗时44.10秒。新Tests保持44,437字节/`ace5824a0c2db9144a8637267363f18a58d01c012c51570bc734a6549c0bf7ca`。

独立完整读取 `FirstRoom-20261015-072535/index.json`：tests51、succeeded38、succeededWithWarnings0、failed13、notRun0、inProcess0。原38全Success；新13全Fail且warnings0。第二轮没有任何fixture stage/Create错误，失败发生在真实生产入口或SPR已进入的实际窗口断言。

| 新组后缀 | 实际失败分类 |
| --- | --- |
| AirEmissionUsesActualHeightWithoutDownAim | 真实空中STF主攻未被WA接纳 |
| AirPrimaryCancellationDoesNotRefundToken | 真实空中STF主攻及共用token接纳失败 |
| ControllerAliasesHeldEdgesAndManualT | 真Controller J/鼠标别名未进入WA主攻 |
| CrossbowPrimaryTimelineWorldAndReload | 真XBW主攻未进入WA域 |
| CrossbowSkillNearestTwoAndPhysicalDefense | 装有真实1发的XBW技能准入失败 |
| FailedResourceReloadAndAirSkillPreserveDomains | 已验证失败资源等前置，恢复到实际折扣8Focus后空中STF主攻仍未接纳 |
| FirelineFixedBurnIgnoresDirectMultipliersAndIframes | 真STF火线技能准入失败 |
| FirelineFullWindowLateEntryLOSAndGroundHeight | generic fail；按该组首个bareguard为 `!TryBeginWeaponSkill()`，尚未进入late-entry后置 |
| FractionalContactsUseActualMuzzleAndCausalTime | generic fail；fixture/muzzle/getter控制已成功，首个bareguard为 `!WA.Action.Active`，尚未进入fractional后置 |
| ProjectileWallsCenterBoundsAndHeight | 实际XBW投射主攻准入失败 |
| ReloadCancellationNoRefillAndFreshRestart | generic fail；首个bareguard为 `!WA.Action.Active`，尚未进入reload后置 |
| SpearSkillNearestOnePerIndependentSubhit | 真SPR技能进入窗口，最近一个/收杆间隔计数/第二第三目标/三份world receipt/同目标三段六项后置断言失败；现存all-target逻辑和缺world journal被真实运行覆盖 |
| StaffPrimaryMagicFocusAndNoImplicitBurn | 真STF主攻未进入WA |

9组有明确准入TestTrue失败，3组generic失败按已读源码的最早bareguard定位，1组SPR有6项真实后置失败。不能把尚未执行到的弩/杖伤害、burn和reload后置写成已逐条RED。本次足以证明正常来源/装备前置通过而真实武器入口尚缺行为；root收到分类后释放owner最小GREEN。测试未根据失败删项、改弱期望或改原38。

| 原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-072344.log` | 4015 | `c61fdafdc5b3774d3b1194f55713b75cb4ed77bbcdecae05123a269f9891e0db` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-072535.log` | 222284 | `05d0e52070cacb7c943742c5466c9c9b1dd9b1db1dbfc45d82ffd8ae4a072737` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-072535/index.json` | 32301 | `44e1f322bfa7fff042b65000143fd3153ec224f5d74eabeb14838ea6f9708af6` |

## 协作只读审查：四甲显示层

root追加委派对 `armor-layer-runtime-plan-v001.md`、HUD、ArmorLayerProof、Probe flags及严格脚本的只读审查；没有写这些文件或查看未留存新媒体。发现并提交一项P2：初版Layered总分支限SWD，导致已穿四甲的其他武器连现有idle都退回旧整身LGT候选。root接受并改为所有武器可用已有idle组件，P1仍仅SWD；独立读修后条件确认，运行验证待root重编译，不能由源码修复认证。

Frozen idle6和P1六帧与V007的Root/Grip/Angle实际逐项12/12匹配，scale均.4；idle .15秒分帧和P1实际阶段采样匹配冻结时段。单UV镜像、原512画布统一Root、back/far/front→独立剑→near、Layered禁止旧手ROI重播、真实已画层进入遮挡和地面Y排序均符合读取的合同。HUD未写战斗/库存权威。Armor profile实际16个唯一required names与PowerShell生成一致，显式flags默认false、旧unit/Explore名称分支保留。此范围修后未发现新增P1/P2；不代表全部状态/20搭配或媒体视觉验收。

## 候选只读审查：同点未发射却扣资源的P1

实际候选Tick先调用玩家 `SimulateActionsTo(ToTime,&Deferred)`，WA真实 `StepTo` 在发射点已经消费Ammo/Focus、记录Issued；随后提交敌人同点已准入伤害。若该伤害破韧或致死，WA被Interrupt，而端点Deferred消费条件拒绝Interrupted/死亡，于是实际世界无投射物但发射成本已扣。该事实与冻结D02 `actual_emitted_only` / 未发预留释放不一致。审查已将具体路径发root/owner，编译窗口不改生产。

root明确许可追加独立第14组 `SamePointPoiseOrDeathPreventsUnemittedCost`，并要求取得真实边界RED后才修此P1。新增四case覆盖XBW/STF×非致死破韧/致死：正常E/Q取得满弹/满Focus武器；石骑X80正常proximity wake后读取真实Shield动作ActiveAt；仅用公开受伤入口建立29点未破韧积累和真实.65秒旧无敌（在Shield前自然结束），致死case另设初始QA HP10；在真实Shield ActiveAt减武器冻结windup处正常起攻，断言两者严格同double端点，实际锁点整轮预留，随后真实Shield receipt与HP86/0证明命中。没有篡改kernel、预制命中、直接生成弹或人工退款。

冻结行为期望沿现有damage-first端点策略：无世界发射且无WA实际发射Issued/FocusHistory；XBW仍1发、STF仍100Focus，预留归零；已经发生的锁点/暴击draw保留。原13断言不改。当前新Tests实际14宏/14唯一名称，48,650字节，SHA256 `b96ef11b1a1d0c9969c18de29fe40a798498632091847a60546c7b7a52bffa59`；候选总52只是按实际名称相加，仍以root真实报告为准。该版本尚未运行，不能声称P1已有测试反例或已修复。

## 首版52项候选：48 Success、4 Fail，端点P1尚未取得有效反例

root首次候选构建 `build-editor-20261015-073923.log` 因两个局部Owner名称隐藏AActor成员的C4458失败，未计行为RED；owner仅修编译命名后 `build-editor-20261015-074405.log` 重新编译并链接完成，root报告exit0，独立读原件耗时28.45秒。

独立读 `FirstRoom-20261015-074508/index.json` 为52项、succeeded48、succeededWithWarnings0、failed4、notRun0、inProcess0。原38均Success，新14有10 Success、4 Fail。不能把全局succeededWithWarnings0写成无任何日志警告：失败的CrossbowPrimary组含1警告/29错误条目，主要来自1056行 `Contact subdivision made no authority progress` ensure及其栈。

三个XBW实际行为失败为：主攻实际接触零步循环及后续reload无法进展；技能路径两目标/.6/终止三项后置失败；中心射程外hurtbox不得扩界的实体终止断言失败。owner独立定位同一几何根因：解析entry重建实际PositionAt可仍在受击面外一ULP，preview回到同一时刻而真实消费拒绝。源码修为在真实交集内寻找第一个可表示inside时刻，二分到相邻double、不加空间epsilon或扩大硬边界；只读复核该方法符合实际位置公式，运行待后续。

第14组四case的“实际Shield receipt/HP/WAInterrupted”复合前置均失败，同时世界确实有发射，因此本轮**不能认证端点P1已复现**。原fixture在Tick(.9)后预击，距Shield恰约.65秒，与真实.65f旧无敌贴边；浮点多步倒计时可能导致保护仍覆盖该端点，这是待诊断推理，非既定运行事实。冻结Shield Damage13已核对，99−13=86期望不改，不能无依据改85。

root许可仅将该fixture预击提前到Tick(.86)，留.04秒余量；在Impact−.001通过公开CanReceiveDirectHit确认旧保护已经自然结束，不设置timer；加精确sim/shield/emission时间、HP、hit/ID、terminal、发射/资源等分项诊断。原14核心期望均保留。当前Tests50,033字节，SHA256 `1a7c137bc2a9683a6a63963ad75c7612bd109c8661ebdf9dcc58aed68f24a1aa`，14组，待root统一新运行。owner保持端点成本问题未修，先取得有效反例。

| 原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-073923.log` | 6539 | `0d72c6197753433c69d7312db1bc9933dcfb10daa500358afc93517c1794fa38` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-074405.log` | 3525 | `c3b005c72fb2af3c16409c9f96be5990aa98e4e14f8efed2fd39c3860e715b44` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-074508.log` | 238029 | `6b1fef9da50aa929d918b969827f2032e33b38b9b7915fa1c399f33ee2efd72d` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-074508/index.json` | 43100 | `1e8cef33472fb270e1609620983da187a15288ffed7f2a5b2394937a912c286a` |

## 第二版52项：原51通过，第14取得有效同点P1RED

root执行 `build-editor-20261015-074926.log`，报告exit0。独立读原件11action全部完成，实际重编译新Tests与世界投射物等并链接DLL，耗时35.20秒；Tests保持50,033字节/`1a7c137bc2a9683a6a63963ad75c7612bd109c8661ebdf9dcc58aed68f24a1aa`。

独立完整读取 `FirstRoom-20261015-075033/index.json`：tests52、succeeded51、succeededWithWarnings0、failed1、notRun0、inProcess0；所有组warnings0。原38和原新增13全Success，表明3个XBW几何根因修复已实际通过，而不是放宽门禁。唯一失败为新增端点组，errors4均来自同一个未发成本断言。

该组四case均通过旧无敌已自然结束、实际Shield receipt、HP、终止/死亡和无世界发射前提，诊断绝对时刻一致：`sim=shield=emission=2.5999999999999996`。实际结果如下：

| 实际case | HP | EnemyHit | WA terminal / active | 世界发射 | Ammo | Focus | Issued |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| XBW 非致死破韧 | 86 | 1 | Interrupted(6) / 0 | 0 | 0 | 100 | 1 |
| XBW 致死 | 0 | 1 | Interrupted(6) / 0 | 0 | 0 | 100 | 1 |
| STF 非致死破韧 | 86 | 1 | Interrupted(6) / 0 | 0 | 0 | 90 | 1 |
| STF 致死 | 0 | 1 | Interrupted(6) / 0 | 0 | 0 | 90 | 1 |

这次明确复现实际无弹但已经按发射扣资源/Issued；不再是前一版未确认Shield准入的fixture失败。root已许可新增合法WA绝对时刻中断接口与Actor批次次序修复，禁止Capture篡改、事后退款伪造消耗history；原14测试继续freeze，待API审查与新实际52项结果。

| 原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-074926.log` | 4303 | `a061405e4531f0d2b77562ad7b315a95bc884011b37e929825bccce7fdc9dc16` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-075033.log` | 227276 | `9298ce1272ad9e8a12a623e0a07fc6e2420786da4296a1b51bf0b286ec7b3b10` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-075033/index.json` | 28616 | `c753c2c248fea9914d0a0ff26ac51f2f9df08e2c9d1f4662de2e2c649fe61cd4` |

## P1修复候选与纯核证据只读核验

独立读取新WA `e5a24e9e1637aacd17ac85232a6e3954bd16a4b39ae1febfa5cb253ec581fa3e`：`InterruptAt` 先验证finite/不倒退时间、context、Grounded、当前ValidState和Reason；活动动作拒绝越过更早的锁点/子击/reload完成/动作结束，只允许到当前下一deadline（含精确相等）。内部复制完整核候选，合法Advance→原Interrupt→ValidState后才原子安装；失败不改活态，不篡改Capture、不退款改写Issued/资源history。锁点CD和已发事实保留，未发reservation由原Interrupt释放。Interrupted/ReloadCancelled payload改为仅 `AtTime>End` 拒绝，故精确End合法且不伪移时间。

Actor bound批次现在先提交旧世界/敌伤害，再唯一推进WA到ToTime；真实破韧/死亡通过Game当前同一SimulationTime调用InterruptAt，不造成endpoint发射消费。非打断生命损失仍随后正常推进并发射。只读未发现该候选新增P1/P2，最终由真实52项验证，不由源码判断宣称修复完成。

独立读取 `evidence/2026-10-15_weapon-endpoint-v001/index.json` 并核对全部8条原件/副本字节和SHA全部一致：纯边界RED45/26、中间45/3、GREEN45/0、原WA179/0；endpoint测试源自RED未变，宏关闭预处理输出是空翻译单元。历史临时RED stub头没有单独留存，index明确这一缺口，未重构冒充；真实UE端点RED源码/DLL由root v017另保留。当前UE14测试继续为50,033字节/1a7c，未改断言。

## 四甲v002保全原始帧独立抽查

root确认v002的F/E完整留存后，本任务只查看F原件 `2026-10-15_四甲实际换装待机首斩左右分层运行_v002/原件` 中75/103、235/263、400/428、566/594、736/764十帧，分别为无甲/LGT/MED/HVY/ROB的左向walk/P1。共同圆盔、肢体尺寸与画布一致；棕内层、皮革、链甲、板片、法袍长下摆可区分且与HUD身份一致。所抽P1脚底基线稳定，近手盖住独立剑持握处，剑刃朝左，未见多手、二次镜像、旧整身轻甲露出或明显画布裁切。MED/HVY/ROB的旧甲地面来源/比较UI保留当前穿戴身份。

这十静帧未发现新增P1/P2，但不能由此认证完整六帧连续衔接、footlock、所有动作或20搭配。root独立检查其余右向/idle及21项实际proof，本任务不冒充自行运行或全录像审查。

另只读发现新增武器VFX源级P2：统一在所有Fighter后绘制active弹体，会让远Y真实弹体压到近Y人物前。root接受，改为ground效果先于人物、active core进入同一个按groundY排序的DepthEntries，spark/burn仅为overlay；源码复核已解决顺序，尚未用ranged媒体认证。Sequence音频消费和所有VFX均只读世界事实，无生成弹/伤害/库存写。

## 最终实际52项：严格GREEN

root执行 `build-editor-20261015-075915.log` 并确认exit0；独立读取原件28action全部完成，实际DLL链接/metadata成功，耗时65.64秒。独立完整读取 `FirstRoom-20261015-080108/index.json`：tests52、succeeded52、succeededWithWarnings0、failed0、notRun0、inProcess0；原38与新增14全Success，所有逐组warnings/errors均0。本任务不运行UE/UBT，结论来自root实际运行原件及独立读取。

测试源码继续50,033字节/SHA256 `1a7c137bc2a9683a6a63963ad75c7612bd109c8661ebdf9dcc58aed68f24a1aa`，与有效P1RED075033完全一致。最终端点四case诊断仍为 `sim=shield=emission=2.5999999999999996`、EnemyHit1、terminal6/active0、世界发射0；真实HP仍86或0。XBW两case现在Ammo1/Focus100/Issued0，STF两caseFocus100/Issued0；未发reservation释放，真实锁点与暴击draw断言保留。这是同一实际生产反例通过合法因果次序修复后的GREEN，没有删除失败断言、事后退款或改Capture。

| 最终原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-075915.log` | 5924 | `bb7aa812a7cd34bfdba031ea272319a786f1f26b4bb59c71fee2cd4fb324e5d8` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-080108.log` | 225539 | `58ff1d45763f88b5fdc9fafe9d85a2797388d1e3bd276e1093973c06f34f6fe5` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-080108/index.json` | 26844 | `1277f9f8216190b29a8756af4148729942187ab9193618a74658c9da83dc03f2` |

| 独立复核的080108 GREEN版本源码 | SHA256 |
| --- | --- |
| `DungeonWeaponActions.h` | `e5a24e9e1637aacd17ac85232a6e3954bd16a4b39ae1febfa5cb253ec581fa3e` |
| `DungeonFighter.cpp` | `91ee36492b8992ea4dc0ced6770a9b29c8b52c00c1c8bfba4fdf0d177d361d6e` |
| `DungeonGameMode.cpp` | `49cee9056cbaf9add27acbccf51251fea9a4aee1853c5fcb2e0ea77a9de42b7c` |
| `DungeonWorldProjectiles.cpp` | `bf37b5a540a70a3944919dce81cd0b6f9f83b6f28fdff807c872a06b495a1b30` |

root v017源/DLL快照早于端点修复，保存的是前述真实端点RED版本；不得回标为080108的新GREEN DLL。root随后报告v018实际strict52版本544文件已保全；本任务引用以上实际build/run与080108版本源码SHA，不将v017与v018混代。

## 未覆盖边界与交接

owner提出空中XBW最后一发结束后自动装填的落地时序边界，本任务独立核对实际源码：`DungeonWeaponActions.h:352` 的StepTo开头可能先以旧S.Time调用StartReload，而bound落地批 `DungeonGameMode.cpp:997` 已先NotifyLand，再于1041推进WA到ToTime。若真实起跳立即主攻，.68完整结束时仍空中，.70落地才准装填，Start可能被写成早于落地一个≤.005批步。这是具体源码推理，当前52的空中用例为STF、未包含此组合，尚无真实UE反例或修复结论。已报root，按其本轮指令保持测试和生产冻结，交接后另取实际证据。

本切片已完成独立测试、有效RED→GREEN、API/Actor源码与10张保全原始帧复核。root下一步继续正常输入弩杖proof，实际声音/VFX与录像F/E保全仍须各自证据；本报告不认证正式muzzle美术socket、完整motion/footlock、20搭配、D13同代磁盘或全部15单元。

## 新增未运行case：XBW真实落地才开始完整自动装填

上述52GREEN及1a7c源码由root v018另行保全后，root许可仅向现有 `AirEmissionUsesActualHeightWithoutDownAim` 追加该组合，原14组旧断言完全保留、组数仍14/总52。生产由新owner `landing_reload_adapter`负责，必须先保持基线等待真实RED，本任务不改生产或运行UE/UBT。

实际追加代码经文本检查：55,512字节、14宏/14唯一名，SHA256 `88fecbea5fa633f22dabd060e457e080f1e52bcfc77a51a94e01dc2f1e6046b3`。正常StartJump与BeginAttack同点，完整A.End后实查真实H>0/V<0、WA未落地、主攻Completed、空匣和pending；使用当前公开H/V与正常GameMode float Tick观察首次落地，不手设clock、Grounded、跳跃或装填timer。每步不超过实际ballistic root；若root已舍入到当前绝对clock，才用一个相邻可表示double步，循环cap128以诊断停滞。首次Grounded要求H0/V0/GetLandingVisualAge0，记录beforeSimulation、beforeWAclock、H/V、landing、reloadStart/End，严格核对Start==真实firstgrounded和End==landing+1.10，最后可表示末点前无补弹、精确末点仅一次补弹receipt/无重复发射。

这仍是尚未编译/运行的候选反例；可能出现的夹具停滞、近地context阈值或实际早起装填必须依据新原件分类，不能预写P2已复现。旧080108严格GREEN按原范围保留，不能据新增代码扩大覆盖。

## 081524：新增XBW落地装填取得有效P2RED

独立读取 `build-editor-20261015-081327.log`：实际新Tests编译、DLL链接与metadata四action全部完成，35.95秒；独立完整读081524 Automation index：tests52、succeeded51、succeededWithWarnings0、failed1、notRun0、inProcess0，逐组warnings总0/errors总3。唯一Fail为原 `AirEmissionUsesActualHeightWithoutDownAim` 新追加XBW case，旧STF高度/固定轨迹断言与其他51组均通过。

所有实际起跳、.68完整主攻结束仍空中、pending空匣、无提前reload、时钟前进和真实firstgrounded前提均通过，未出现fixture停滞或不明Create失败。日志为：

| 观察事实 | 实际值 |
| --- | --- |
| 最后空中simulation / WA clock | 1.7500000080812781 / 1.7449999996647239 |
| 最后空中H / V | 1.59857479e-15 / −630 |
| 首次grounded simulation，实际H0/V0/age0 | 1.7500000080812783 |
| 实际reload Start / End | 1.7449999996647239 / 2.8449999996647239 |
| 正确完整1.10 grounded deadline | 2.8500000080812784 |

唯一三错误恰为“reload必须从实际落地起算”“正确完整末点前不得已补弹”“真实refill receipt须落地+1.10”。提前量约.0050000084秒；结合已核对源码，近地context先Grounded令WA推进拒绝并落后，再在实际落地时以旧WA clock起reload，形成真实早起/早补弹。旧52GREEN不覆盖该组合，不能以旧通过否认新反例。

Tests继续55,512字节/`88fecbea5fa633f22dabd060e457e080f1e52bcfc77a51a94e01dc2f1e6046b3`，原断言未减弱。本任务已将有效RED及精确事实报root与新owner，生产在root明确GREEN许可前继续冻结。

| 原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-081327.log` | 3479 | `0227da8f6f9f4ca70543969d8e33c59e086deee9fad3ccc78d8744f9f6f3a5f8` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-081524.log` | 227177 | `000afc1de03c0f6a1133b0a3562f4028111e725cbf5a18961ddb2d9b9cfd37cb` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-081524/index.json` | 28662 | `c90bb0bc865ca0d86541e9c11b8ff75f3547ba399fdde487e408526c659a5e9d` |

## 落地修复候选独立只读复核

owner取得root许可后冻结候选，独立核对新 `LandAt(Now,AirContext)`：拒绝非finite/倒退、context已ground、预算非air或非法活态；活动动作不允许Now越过当前下一lock/emission/end。候选内StepTo到Now仍按air积分和处理同点动作事实，然后Grounded并按同一Now启动pending自动装填，候选ValidState后原子安装；失败不改变活态。进行中的air primary保留ID、StartedAirborne、timeline/锁点及已发资源事实，不重启或退款。无pending的idle落地不编造action/event/ID。

Actor bound `WeaponSkillContext.Grounded` 沿唯一WA预算，真实H0/V0后于同点伤害提交之后调用LandAt；两个physics NotifyLand路径仅保留legacy即时通知，bound不再提前改变预算。伤害先InterruptAt清掉pending/未发预留，随后LandAt不能重发或起reload；未打断动作仍正常推进，落地同点发射读取真实ground muzzle。该候选未发现新增具体P1/P2，真实UE新增case仍待root新运行；本任务未改生产。

| 已复核候选源码 | SHA256 |
| --- | --- |
| `DungeonWeaponActions.h` | `e8d6d2366c26b87eecc14b660b8020b31a4e7c674c7256479a536ba8d2b91586` |
| `DungeonFighter.cpp` | `4e7dda66120687bdd5cfa5c1fce058676e18e58b6dd8704a305bcf155260b6db` |
| `DungeonGameMode.cpp` | `8ec527b159d9bf0b2a034850237e570e52b885dc5db17f12e77339d49b75d1c6` |

独立读 `evidence/2026-10-15_landing-reload-v001-081233` 原件：landing RED日志43checks/23fail/exit1（SHA `bd6178e37f904f72b465ff5c65dc62dbd3bc556b399d20589360eb8f761ec6fb`）、GREEN43/0/exit0（`dacab84205279f3b587bdd313f2e592f65f561d97ebb4475bd4ffabf3d3c81f5`）；原179与endpoint45在baseline及green都0fail/exit0，日志各自SHA前后一致。此轮拒绝型RED stub头SHA `79736d42381c5391d6ac59047f72e685aa1f5b19818c28e402dfcbd22822b67b` 与080108 baseline头e5a24e9e均实际保留，未复刻历史缺失原件。pure测试源原件/当前SHA同为 `38b6e57b939e9c19134ea7d4c5f271794d09950d9b594b9621826f904f74e393`。这些纯核证据不替代081524真实Actor RED及后续UE GREEN。

## 082722：未改XBW落地case实际GREEN，严格52项全部通过

root执行 `build-editor-20261015-082345.log` 并确认exit0；独立读原件28action全部完成/DLL链接与metadata完成，81.91秒。独立完整读 `FirstRoom-20261015-082722/index.json`：tests52、succeeded52、succeededWithWarnings0、failed0、notRun0、inProcess0；原38与新增14全部Success，逐组warnings/errors总数均0。没有重复旧测试或本任务另行运行UE/UBT。

同一55,512字节/`88fecbea5fa633f22dabd060e457e080f1e52bcfc77a51a94e01dc2f1e6046b3`测试保持不变。新增XBW case诊断现在为：

| 真实观察 | 修复后实际值 |
| --- | --- |
| 最后空中simulation / WA clock | 1.7500000080812781 / 1.7500000080812781 |
| 最后空中H / V | 1.59857479e-15 / −630 |
| 首次grounded simulation，实际H0/V0/age0 | 1.7500000080812783 |
| 实际Reload.Start | 1.7500000080812783 |
| 实际Reload.End / 完整landing+1.10 | 2.8500000080812784 / 2.8500000080812784 |

旧STF空中高度/固定轨迹断言、新XBW所有落地前提及完整1.10末点前无补弹/精确末点唯一receipt/不重复发射均Success。真实WA clock不再因近地context先落地而停滞，自动reload从真实落地端点起算；081524三项有效P2RED在未改测试下转GREEN。不能把这个结果扩写为未测试的全部落地组合或声音/美术通过。

| 实际原件绝对路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/build-editor-20261015-082345.log` | 5713 | `8267f8c420f4827a76ac7a26e1e025fba77493e8e78192d65bd1b367c73d83ce` |
| `F:/Ourgame/UnrealGame/Saved/Bootstrap/first-room-tests-20261015-082722.log` | 226214 | `e4e3e1ccb053a6b30913bd94081d525a0b92a26b0f8a491565b44ea993396941` |
| `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-082722/index.json` | 27331 | `863df72d50e759913a69d2f4542247baf9d08fd369525b2fc25ba2420ea4b962` |

## v020实际快照核验与后续版本限制

独立读并逐项校验 `F:/Ourgame/source-assets/production/backups/2026-10-15_landing-endpoint-UE52-GREEN-v020/compiled-source-manifest.json`：585条payload、copied_files585、51,392,132字节，全部实际bytes/SHA与清单一致，0差异。清单本身136,645字节/SHA `e712828f02a30d16ce68c34fea81ecb02d6617ed2e43f7d72a8344182ab5cd09` 另计，所以物理目录586文件/51,528,777字节；不能把差一个清单误判为少保全或多一份载荷。

快照WA/Fighter/GM/Tests的SHA依次为e8d6d236、4e7dda66、8ec527b1、88fecbea，与上节已独立review的完整候选SHA和未改UE测试完全一致。快照DLL1,370,112字节/SHA `9e3a2ec1462387c26905e45b01fa3c6b5d22fb4bfd64d77aaabe365d84e5d21e`；082722 index也同为上述863df72d原件SHA。该v020明确保存本次新GREEN版本，v017/v018不混代。

v020清单status明确HUD的P2/P3 loader已经编译、P3 assets当时尚未导入；root另报告P2已导入。strict52验证玩法适配，并未运行ArmorComboProof或认证P2/P3美术；root随后改ContentProbe/ArmorLayerProof/PowerShell、rangedproof worker随后新增未编译源码都属于后续工作区，不能称为v020已编译/运行。正常弩杖操作录像与声音/VFX、正式muzzle socket、完整动作/footlock、20搭配、D13同代磁盘和总15单元仍须各自实际证据。
