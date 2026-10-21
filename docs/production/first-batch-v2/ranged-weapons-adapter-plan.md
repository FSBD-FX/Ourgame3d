# 弩、杖与短枪子窗口：真实世界接入验证计划

日期：2026-10-15，Asia/Shanghai。承接 `weapon-actions-adapter-plan.md` Task 4；本轮是玩法适配测试，首批正式内容完成数仍为0/15。

当前已认证结果：root统一构建082345 exit0；082722严格52/52 Success，原38与新增14全部通过，逐组warnings/errors均0，包含未改88fecbea测试中的XBW真实落地完整1.10装填case。有效P1与P2 RED→GREEN及旧080108基线均按各版原件保留，不扩大范围。v020的585份载荷/51,392,132字节已独立逐项bytes/SHA核对零差异；后续工作区改动另算。

## 事实、推理与风险

**事实。** 当前基线为原38个 `CodexDungeon.Content` 自动化组，最近根线程给定严格GREEN证据为 `UnrealGame/Saved/Automation/FirstRoom-20261015-064514/index.json`。装备Actor已有来源注册、E拾取、.35秒提交、Q切换、实例Ammo/CD、唯一WA Focus和锁点暴击游标；此前报告明确未认证非零弹药射击/装填。实际预检源码的bound `BeginAttack` 拒绝非近战；`TryBeginWeaponSkill` 拒绝XBW/STF；`ConsumeWeaponSkillEvents` 只消费近战窗口、不创建真实飞行弹；SPR技能窗口对所有合法目标循环扣伤。

**推理。** 必须从真实GameMode装备来源和角色入口驱动测试，并同时检查权威动作、世界发射/接触、实际生命损失及消费凭据。只查WA的 `Issued`、直接构造投射物或篡改Capture不能证明UE适配成功。新测试独立注册，不修改原38的行为预期。

**风险与边界。** 目前WeaponMuzzle尚无正式美术socket。root裁定使用真实USceneComponent读world XY/高度，默认相对偏移0，允许测试作者设置真实组件偏移验证采样；不凭空定一个家族固定偏移改变射程，也不把默认0称为rig完成。默认武器投射物没有另一个作者半径，按点轨迹与实际受击矩形连续扫掠，并保留条目的目标中心硬边界。新Run Actor ID须单调、Run归属，不能把UObject地址或旧QA石骑核ID直接作为新journal实体身份。此世界状态只是Run内存事实，不代表D13磁盘同代保存、HUD、正式美术或正常输入录像已完成。

## 冻结规范

| 项 | 冻结要求 | 依据 |
| --- | --- | --- |
| XBW001主攻 | 34物理/12削韧，950cm/s；.16发射，.04窗，.48后摇，完整.68后才自动1.10装填；1发弹匣 | `docs/design/equipment-v1/weapons.json` XBW001；`DungeonContentCombat.h` |
| XBW001技能 | .55发射、.05窗、.55后摇；50/24物理、1100cm/s、最多两目标、第二目标直伤和削韧×.6；锁点+.22起CD6秒；耗1发 | 同上secondary |
| STF001主攻 | 24魔法/8削韧、600cm/s、10Focus、.22/.05/.40、无默认燃烧 | 同上STF001 |
| STF001火线 | 18魔法/6削韧；24Focus；.45/.12/.45；地面240×±35矩形、LOS、目标高度≤65；各合法目标一次 | 同上secondary |
| 固定燃烧 | raw2魔法/s×3s；首次+1/+2/+3，末跳包含到期点；读受者当跳抗性/易伤；不暴击/吸血/削韧/授予无敌，也不被已有直接无敌挡；同目标共享槽，相等刷新期限但保NextTick | `docs/design/items-v1/states.json`；`01-消耗与战斗道具.md:84`；root复核 `consumables.json` |
| SPR001技能 | [.18,.22)、[.28,.32)、[.38,.42)，每段只取当前最近一个合法目标，各12物理/6削韧，45..240×±16，收杆间隔不判定 | weapons.json SPR001secondary；原Task4 |
| 共用动作 | 40%锁向/整轮预留；实际发射才花费；失败起招不消费任何域；每离地只接受一次主攻；取消不还空攻；真实发射高度、固定水平朝向、无下瞄/纵深追踪；落地不重启动作 | D02 `player-combat-rules.json` attack/jump/input；D03共同规则 |
| 装填取消 | T新边沿、合法dodge、Q可取消装填；丢全部进度不补弹；取消同点不可再起主攻/技能/装填；Q本身仍完整.35秒；实例Ammo/CD不重置 | D02；D04；WA冻结核 |

## 所有权与RED/GREEN顺序

- `ranged_review`仅写新 `Tests/DungeonRangedWeaponsAdapterTests.cpp` 与本plan/report；不改原38、Actor、HUD、Probe、纯核、构建/门禁脚本，不启UE/UBT。
- `ranged_adapter`负责Actor六文件和新独立世界投射物模块；先冻结公开可编译空桩和DTO，真实行为RED后才能实现GREEN。
- root唯一执行统一构建、自动化、正常输入实录和证据归档。任何编译错误只计编译失败，不称行为RED。实际注册数量从测试宏和UE报告核对，不预先写通过。
- 失败后先核对规范与实际因果，再由各owner修责任文件；不删除、减弱断言或放松严格门以求GREEN。

公开接口为Fighter `TryBeginReload(bool FreshPress=true)`、`GetWeaponMuzzleComponent()`、`GetWeaponMuzzleOrigin()`；GameMode `GetWeaponWorldState()` 只读。`DungeonWorldProjectiles.h` 固定weapon-actions-v1域，key带Run所辖Owner/Room/Action/Event/Subhit；world DTO含发射实体、窗口、接触receipt、burn和仅由实际提交产生的journal。现有 `GetWeaponActionsState` 观察预算、锁点、实例资源和CD。

## 实际建立的13组

以下均为 `CodexDungeon.Content.RangedWeaponsAdapter.` 的唯一后缀，来自实际新测试源码，非预设进度。

| 组 | 关键实际路径与反例 |
| --- | --- |
| CrossbowPrimaryTimelineWorldAndReload | E/Q取得弩，真实主攻、锁点预留/暴击、世界单弹/单伤害、完整末弹后摇、自动1.10装填、禁止抢射、库存镜像 |
| CrossbowSkillNearestTwoAndPhysicalDefense | 倒序Enemies仍按真实路径先后命中两目标，第三无伤，第二50/24×.6；真实石骑Armor45减伤 |
| ProjectileWallsCenterBoundsAndHeight | 实际注册WorldStatic墙、中心超420但受击体伸入、中心纵深14.001、真实高跳、房间硬边界 |
| FractionalContactsUseActualMuzzleAndCausalTime | 真muzzle组件相对24/7、角色真实移动后采发射点、受击体X18连续接触的分数时刻、journal/消费去重与Run ID |
| StaffPrimaryMagicFocusAndNoImplicitBurn | 真火球600/24/8、锁点预留10、发射扣10、真实石骑Ward20、无burn、最后消耗后1秒才单次12/s恢复 |
| FirelineFixedBurnIgnoresDirectMultipliersAndIframes | 实际grade3+伤害25%与seed22真实暴击产生37.8直伤，burn仍raw2；Ward20逐跳、真实先存伤害无敌、3跳含到期、无新hurt/削韧；第二法杖E替换备用/Q技能相等刷新保原tick |
| FirelineFullWindowLateEntryLOSAndGroundHeight | 真实AI目标在.12窗内晚进入仍命中；矩形角点/中心超界；实际墙LOS及真跳全窗高度>65拒绝直伤/状态 |
| ReloadCancellationNoRefillAndFreshRestart | 真实+25%装填速度；held/fresh T；取消不补弹/不留进度/同点拒绝；合法dodge、Q roundtrip仍保空匣；仅完整reload补弹 |
| FailedResourceReloadAndAirSkillPreserveDomains | 实际-20%Focus成本，7不足8/19.2，主攻/技能/杖装填拒绝且各域不耗；恢复1后真实空中主攻耗8 |
| AirPrimaryCancellationDoesNotRefundToken | 真起跳→接纳主攻→锁前反向移动取消→不发弹/不扣Focus但不能再空攻；下一真实起跳才更新token |
| AirEmissionUsesActualHeightWithoutDownAim | 真弹道起跳，发射高度不同于起招高度；ground目标漏空、真正跳跃目标命中；旧弹高度/Y固定 |
| SpearSkillNearestOnePerIndependentSubhit | 三个12HP目标按每次死亡重新选最近；死区/纵深外不伤；收杆间隔无判定；同一目标三段不被自己第一段无敌吞掉 |
| ControllerAliasesHeldEdgesAndManualT | 真local Controller J/鼠标左、K/鼠标右别名，每边沿一动作，held不重发；真实T取消/重新装填 |

fixture注册有效WorldContext，清障不调用contextless DestroyActor。仅初始QA位置/HP、实际组件偏移和明确来源为fixture；绑定后不直接改WeaponId、Ammo、CD或kernel快照。E/Q和正常角色方法可证明生产调用链，不能替代完整控制器E/Q录像。

## 冻结与执行待点

2026-10-15首次测试freeze：43,339字节，SHA256 `1696097c2b3ed497b70cd03fd0ad7df4c3e7b7c0ed353e087c7a73f22971cde2`。实际宏13、唯一测试名13，旧38不改，因此候选总数51；最终以root编译后的注册/运行报告核对。此时仅完成文本静态核对，无新UE行为结果。

下一步：root编译空桩→实际新组RED且旧38保留→允许owner最小GREEN→新13及原38严格全绿→独立candidate只读审查→正常输入proof、录制和媒体F/E保存核对。完整D13保存、正式来源、20搭配和最终视觉声音仍沿总目标独立推进。

## 首次运行后的夹具修正

首次统一构建exit0与51组实际报告已取得，但新13全停在Create：E空槽已自动激活新武器，单Q反而回starter；初始XBW来源默认Ammo0也不符合测试的loaded前提。root许可仅修fixture为明确Ammo1、E→正常Q starter→正常Q acquired的真实roundtrip，并增加Create失败阶段诊断；不改生产或后置断言。修后仍13组，44,437字节/SHA256 `ace5824a0c2db9144a8637267363f18a58d01c012c51570bc734a6549c0bf7ca`。第一个报告如实保留为fixture失败，待第二轮实际行为RED后再释放owner实现。

第二次 `build-editor-20261015-072344.log` exit0、`FirstRoom-20261015-072535/index.json` 实际51为原38 Success/新13 Fail、warnings0。全部Create通过；9项明确ranged准入失败、3项由bareguard定位ranged准入失败、SPR真正进入窗口后6项后置失败，已取得真正行为RED。Tests保持ace5824a冻结，后续只读candidate审查/实际日志分类，不改弱门或旧测试。

## 新增第14组：端点同点伤害与未发成本

owner候选只读审查发现P1：真实WA在端点先发射花费，随后敌同点破韧/死亡使世界Deferred不消费，出现未生成弹却已扣Ammo/Focus。root许可只在owned新Tests追加独立 `SamePointPoiseOrDeathPreventsUnemittedCost`，要求取得真实RED后owner再修，不修改原13。

四case为XBW/STF×真实Shield非致死破韧/致死。实际E/Q取得武器，石骑X80正常苏醒并排入Shield；公开伤害入口仅建立29点未破韧积累/.65旧无敌，低HP为明确QA前置；按真实ActiveAt减冻结windup起攻，严格验证相同double端点，再由实际Shield receipt/HP证明命中。沿当前damage-first策略，未生成弹不得生成实际发射Issued/消耗凭据，Ammo/Focus及已发锁点事实必须一致。

当前测试实际14宏/14唯一名、48,650字节/SHA256 `b96ef11b1a1d0c9969c18de29fe40a798498632091847a60546c7b7a52bffa59`，候选总52，待root实际注册/报告核对。新增边界未运行，不预写RED/GREEN。

首版52实际074508为48 Success/4 Fail：3项XBW世界接触失败由owner修解析接触重建的一ULP根因，不放宽几何；第14真实Shield准入复合前置失败，不能认证边界P1RED。root许可仅提前公开预击到Tick(.86)留无敌结束余量、Impact−.001实查CanReceive以及拆分诊断，原14核心断言不改。当前50,033字节/SHA256 `1a7c137bc2a9683a6a63963ad75c7612bd109c8661ebdf9dcc58aed68f24a1aa`，14组，待新实际运行。

第二版075033实际52=51 Success/1 Fail、全部warnings0：原38和原13全绿，第14四case均真实Shield准入、HP86/0、Interrupted、世界发射0，端点同一double2.5999999999999996却XBWAmmo0/STFFocus90/Issued1，已取得有效P1RED。root许可合法WA `InterruptAt` 与批次排序修复；不改测试、不人工退款或改Capture，后续独立审查新API再跑52。

## 最终严格GREEN与交接边界

root执行 `build-editor-20261015-075915.log` exit0，独立读原件28action全部完成，耗时65.64秒。`FirstRoom-20261015-080108/index.json` 实际注册52、succeeded52、succeededWithWarnings0、failed0、notRun0、inProcess0，逐组warnings/errors均0；实际新增14名称及原38全部Success。端点四case仍有实际Shield同double命中、HP86/0、Interrupted、无世界弹体，现在XBWAmmo1/STFFocus100/Issued0，证明同一未改测试由有效P1RED转GREEN。

合法 `InterruptAt` 候选复制后推进到当前下一deadline以内并中断、验证后原子安装；拒绝请求不改活态，精确End终止payload合法。Actor在bound批先提交旧世界/敌伤害，再唯一推进WA，未改Capture或伪造退款。纯核边界45/0与原179/0证据已逐条核对字节/SHA，但UE结论仍来自上述52真实运行。源码版本、运行原件SHA详见report；v017源/DLL快照发生在端点修复前，不能标为本次新GREEN DLL。

本切片完成真实玩法适配验证，下一步由root继续正常输入弩杖proof、声音/VFX实际运行审查及其F/E保全。四甲v002独立抽查左向walk/P1共10张保全原件，未发现新增P1/P2；不扩写为连续动作、footlock或20搭配认证。正式美术socket、D13同代磁盘、全部正式来源及总15单元仍未由本切片完成。

另保留一个未包含在52中的源码时序边界：空中XBW立即主攻的.68结束早于.70落地，可能留下AutoReloadPending；当前落地批先NotifyLand，随后StepTo开头按旧S.Time启动自动装填，故Start可能早于实际落地一个≤.005的批步。此为独立源码推理，尚无真实UE反例；已报root，按其本轮指令不改冻结测试或生产，交接后另取实际证据。不能将当前52GREEN声称覆盖该组合。

## 后续许可：既有空中组追加XBW落地装填反例

root保全v018真实52GREEN源码后，许可仅在既有 `AirEmissionUsesActualHeightWithoutDownAim` 追加真实XBW case，原14组所有断言不改，组数仍14/总52。新的测试freeze为55,512字节/SHA256 `88fecbea5fa633f22dabd060e457e080f1e52bcfc77a51a94e01dc2f1e6046b3`；本轮仍只完成静态检查，尚未编译/运行，不称真实P2RED。

case正常StartJump立即BeginAttack，先到完整.68 End实查仍空中/主攻Completed/Ammo0/AutoReloadPending；按公开H/V计算当前ballistic剩余时间，仅正常float Tick向下取可表示步接近实际root，root已舍入为当前clock才前进一个相邻double，循环上限128。首次WA Grounded必须同时真实H0/V0/落地视觉age0，记录前后绝对clock、WA clock、H/V与装填Start/End；不写任何timer或Capture。期望实际首次落地时才起完整1.10装填，末点前一个double仍无补弹、精确末点只有一份真实ReloadCompleted receipt，空攻仍只有一次世界发射。

新生产owner `landing_reload_adapter` 已只读核对前提，保持生产基线等待root实际RED；包括近地H≤KINDA但尚非H0可能令context/预算Grounded不一致的事实也由日志区分。080108历史52GREEN仍仅覆盖当时1a7c源码范围，不能回写成新增case通过。

081327实际构建日志4action完成/35.95秒；081524实际注册仍52、51 Success/1 Fail、逐组warnings0，仅新case3 errors。真实firstgrounded为1.7500000080812783、H0/V0/age0，前一相邻时刻仍H1.59857479e-15/V−630，但WA clock落后到1.7449999996647239；真实reload Start沿旧WA clock、End2.8449999996647239，正确完整grounded末点应2.8500000080812784。因此已真实证明约.0050000084秒提前起装填/补弹，而非fixture未落地或停滞。旧STF空攻及其他51组全部通过；Tests88fecbea不改，生产owner待root明确GREEN许可再修。

owner获许可后的冻结候选已只读复核：`LandAt` 验证旧air状态/clock/context/下一deadline，候选StepTo(Now,Air)后才Grounded并从同一Now起pending reload，ValidState后原子安装；Actor bound context沿WA真实Grounded，NotifyLand延到同点伤害提交之后，不重启仍进行的空中主攻。纯落地43checks从23fail到0、旧179/45日志SHA前后一致；stub/baseline/未改pure测试有原件。未发现新增具体P1/P2，但UE结论仍待root对未改88fecbea真实52运行。

## 082722真实52项GREEN与v020版本冻结

root执行082345构建exit0，独立日志28action/81.91秒完成；独立完整读082722 Automation：tests52、succeeded52、succeededWithWarnings0、failed0、notRun0、inProcess0，逐组warnings/errors均0。新增XBW落地case前提和全部完整装填断言Success：最后空中sim/WA clock同为1.7500000080812781，首次真实grounded及Reload.Start同为1.7500000080812783，Reload.End与landing+1.10同为2.8500000080812784，age0；末点前一double无补弹、末点唯一receipt/不重发也通过。测试仍55,512字节/88fecbea，未改弱断言。

独立核对v020 `source-assets/production/backups/2026-10-15_landing-endpoint-UE52-GREEN-v020`：585份payload/51,392,132字节全部与manifest bytes/SHA一致；另manifest136,645字节单独计，共586物理文件。快照WA e8d6d236、Fighter4e7dda66、GM8ec527b1、Tests88fecbea精确匹配已审查候选和本次运行；DLL/报告原件保全。v020 HUD含P2/P3加载器编译，root报告当时P2导入而P3尚未导入；不能由strict52认证P2/P3外观/Combo表现。新rangedproof worker后续未编译源码与root后续ArmorComboProof属于下一版本，不回写成v020已运行事实。正常弩杖录像、声音/VFX、正式socket、D13/20搭配/总15单元范围仍待各自证据。
