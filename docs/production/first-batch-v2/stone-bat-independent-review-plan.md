# 灰翼石蝠独立 Actor 接纳测试计划

2026-10-15，Asia/Shanghai。范围为真实UWorld/GameMode/Fighter与新石蝠driver接入，不修改原52项、生产owner的integrationTests或纯核。正式完整内容仍0/15。

预检事实：已独立读取 `docs/design/enemies-v1/01-石像与森林敌人.md` STN-002、`stone-forest.json`、现有 `DungeonStoneBat.h`/Standalone及中央Actor批次。预检时纯核存在完整规则与独立测试，中央Actor只接石骑；后续版本与实际结果分节记录，不能据纯核通过称石蝠Actor已通过。

推理：采用有效WorldContext/真实physics场景和权威GameMode；正常BeginEquipmentRun及注册来源/E取得武器，真实SpawnStoneBat、GameMode.Tick、玩家BeginAttack/StartJump/MoveOnGround驱动。只读观察driver State/Issued/HitReceipts/ReceivedHits与实际Actor HP/高度/位置、Game死亡奖励，不直接driver起招、不改Capture/资源/跳高timer。公开实际伤害入口仅用于明确的致死case预置，仍按真实防御和receipt结算。

风险与边界：两招没有冻结随机权重，已与owner协调正常AI首Peck、之后交替合法招的明确实现选择，待root裁定；测试不暗造权重。RED初始化应真实构造55HP/Z90/Dormant与稳定Run实体，行为留桩，避免所有测试停在Create而冒充行为RED。测试的死亡奖励仅认证当前Actor原型一次提交，不认证N03正式掉落、资产/声音、D13磁盘或遭遇投放完成。

## 冻结规则

| 项目 | D05实际要求 |
| --- | --- |
| 定义与高度 | HP55、armor15/ward10、poise25、move220；身体与受击半值16×12；高Z90、低Z20，实际高度差≤65；高位无地面身体，Z≤40才阻挡 |
| 苏醒 | 近180×85椭圆且LOS，或正HP损失；.80完整警告，无早攻；休眠仍可受伤/计清房；已接纳战斗12s或其他已接纳敌全灭兜底，不重置HP |
| Peck | .80风up，+.40锁点，.25有效，2.10恢复，启动CD3.70；12物理/10削韧，Rx80/Ry30；有效时Z90→20，实际Z>65不伤地面 |
| Wing | .80风up，+.40锁点，后半风up下降，.20有效，2.10恢复，启动CD3.60；10物理/12削韧，Rx80/Ry35；active开始已Z20 |
| 低位义务 | 接受攻击即pending；命中/失手/打断都保留，从实际合法Z20且有效段结束起固定1.80，随后.30升高；不追踪，不被破韧跳过；死亡正常终止 |
| 同点与去重 | 真实伤害/破韧/死亡先于该同点未处理事件；每attack/target一击；死亡与奖励一次，不把新无敌拒绝当作去重证明 |

## 计划六组真实接纳反例

1. `DormantLOSAndFullWake`：实际墙遮挡近触、关碰撞后完整.80警告、远触12s兜底；期间无attack/hit、休眠仍阻清房。
2. `ActualHighHeightRejectsGroundAndAcceptsJump`：地面SWD完整窗口漏过高90，真实起跳SWD在同一生产窗口命中高位，按实际冻结damage/armor15结算，不免费回HP。
3. `PeckActualZ65BoundaryAndSingleContact`：玩家距60真实首Peck，active起点90不伤；实际Z65时刻前一个double无伤、精确点12物理/10削韧与单receipt，后续不重打。
4. `FullAnchoredLowRecoveryAndRealWingHeight`：Peck实际低20后满1.80无XY追踪，.30实际升高；正常下一Wing半风up55/active20及单次10/12。
5. `SamePointPlayerPoiseOrDeathPreemptsBatWindow`：真实玩家Jump+GSW命中窗口与首Peck ActiveAt严等，42真实削韧或致死先提交；不产生同点蝠window/hit，不伪退款/篡改核。
6. `ActualLowCounterKillClaimsRewardOnce`：真实低位两次GSW命中杀死，读取实际Died/RewardClaimed各1；重复Game死亡通知和后续Tick不增奖励/命中。

名字及组数以实际落盘测试宏为准。先冻结可编译公共接口和测试→root唯一构建/实际RED（明确区分fixture/编译错误）→root释放owner最小GREEN→未改测试真实通过。此时尚未写完测试或执行UE，不能预写RED/通过数。

## 实际测试freeze

已实际落盘 `F:/Ourgame/UnrealGame/Source/CodexDungeon/Tests/DungeonStoneBatAdmissionReviewTests.cpp`：17,561字节，SHA256 `de4259972b9e3382edb288386a498aaf4430221f96050174aeaf557f23af99b9`，6宏/6唯一 `CodexDungeon.Content.StoneBatAdmissionReview.*` 名称，正是上列六组。文本检查无错误，未运行UE/UBT，不预写任何通过。旧52加owner4加本独立6，候选总62仍须真实注册核对。

owner已落盘真实初始RED API：Bound GameMode `SpawnStoneBat(FVector2D)` 先Run admission分配稳定ID再初始化；Fighter `InitializeStoneBat(uint64,double)`/`GetStoneBatDriver() const`；driver `State() const`。RED初始55HP/Z90/Dormant/CombatStarted事实正常构造，Step/Apply/Claim和中央接入留桩。默认AI首Peck、之后交替合法招且遵守2.4 eligible上限已由root同意；测试仅正常Tick等待，不直接请求driver起招。未见需要先修的明显纯核规范冲突，纯核本轮没有由本任务执行。

fixture只调用Spawn一次，不重复Add；有明确Create失败stage和有效WorldContext。武器通过真实来源E空槽自动激活，绑定后不改WeaponId/Ammo/HP或Capture。Z65使用实际核double时间及前一个可表示时刻，不把Actor float显示高度当许可；升高末点按现有pure实际RiseOrigin/rate计算，检查末点前仍未完成。same-point组真实跳跃GSW窗口对齐蝠ActiveAt，致死case仅以公开实际25物理伤害作为前置，随后实际GSW结算/42削韧及ReceivedHits证明准入；没有人工写HP、造receipt或取消事件。

测试源码现在冻结，等待root统一编译和实际RED分类。所有后置结论须先验证真实醒/起招/命中前提；初始化或时间前提失败不能冒称对应战斗行为已复现。若失败来自测试规范错误，必须报root后窄许可修fixture，不能改弱断言求绿。

## 首次真实Actor RED：091905

root报告build091556 exit0；独立完整读取 `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-091905/index.json`：实际62项、succeeded52、failed10、succeededWithWarnings/notRun/inProcess均0，逐组warnings总0/errors15。原52全部Success；owner4和独立6全部Fail。独立6的Create均成功，无fixture stage错误，故不是不可构造桩导致的假RED。

| 独立组 | 实际运行到的失败范围 |
| --- | --- |
| DormantLOSAndFullWake | 墙内休眠/无早攻等前置通过，关实际碰撞后没有真实wake；远12s子例尚未运行 |
| ActualHighHeightRejectsGroundAndAcceptsJump | ground完整窗口后的实际高90/miss事实、jump实际armor/receipt、wake保持HP三项后置失败 |
| PeckActualZ65BoundaryAndSingleContact | 真实首Peck准入失败，尚未执行Z65后置 |
| FullAnchoredLowRecoveryAndRealWingHeight | 真实首Peck准入失败，尚未执行完整低位/次Wing后置 |
| SamePointPlayerPoiseOrDeathPreemptsBatWindow | 真实首attack前提失败，尚未对齐或证明同点damage-first反例 |
| ActualLowCounterKillClaimsRewardOnce | 真实首AI前提失败，尚未进入低位反杀/一次奖励后置 |

owner4的三个起招组也停在实际AI准入；初始组有formal stats、中央clock/高度、实际armor15伤害入核、拒绝重复初始化保HP/ID四项后置失败。该报告证明Actor中央接线/配置消费尚缺；不能把尚未进入的每条后置写成已复现。

| 原件 | 字节 | SHA256 |
| --- | ---: | --- |
| `UnrealGame/Saved/Bootstrap/build-editor-20261015-091556.log` | 7737 | `8e5975c9f0da2bdf246e7009e0b13c63c372a9b6377d02dc17147acf70efacdb` |
| `UnrealGame/Saved/Bootstrap/first-room-tests-20261015-091905.log` | 246239 | `3ec877441fbccaa2df4593422ac7a6db91b3225cd142ca530fdf473a8cca42e3` |
| `UnrealGame/Saved/Automation/FirstRoom-20261015-091905/index.json` | 38016 | `37034364856209f8917a77f005d71ffdef9948c73f54ac9364a099296663e485` |

后续source只读另发现高蝠hurt与ground-body参与条件需要分开：WorldProjectiles当前以bBlocksBody跳过目标，D05高90不挡ground body仍应可被合法高度弹命中；默认generic18×16也不同于蝠16×12。root/owner已协调在本次RED原件/快照保全后，向既有HighHeight组增加正常Air XBW/STF来源E/真实起跳发射子例，不增组；当前de425997仍冻结，尚未写入该追加子例，不把当前RED扩大为投射物分支已验证。

## RED保全后追加真实空中弹子例

root先保全v023首次Actor RED，以及修Sword资源readiness后的v024近袖proof源码719文件；092504第二实际报告仍为旧52通过/新10失败。随后root明确释放测试窗口，才修改owned新Tests，不覆盖或倒填de425997的RED来源。

本任务也独立读取092504完整index，62项/52 Success/10 Fail、warnings0/errors15，index SHA256 `088e60f4833f59d185e9dac2ce157a68209c70a73be391c02bf8594739625aa0`；与首版相同范围，不把近袖HUD修正误称石蝠行为GREEN。

新freeze：21,114字节/SHA256 `183086d40bf40772f619a759209e0e4b60dc5ef8a28beae50c3d76d91464628f`，仍6宏/6唯一组，候选总62。只在既有HighHeight组追加XBW/STF两个子例及fixture的明确XBW初始来源Ammo1，旧六组全部核心断言保留。此版本尚无真实运行结果，不预标空中弹RED/GREEN。

每个新子例真实来源E取得对应实例，玩家以实际MoveOnGround连续扫掠通过高Z90蝠下方，再正常返回/微D转向、真实StartJump和BeginAttack。按实际Issued与WeaponMuzzle采样核对发射高度，要求与90相差≤65；不向kernel塞假Origin或写live高度。目标仍实际高90/原XY，世界弹必须在独立hurt半X16对应分数接触时刻命中（1e−7秒容差，能区别旧generic18），读取实际magic、按armor15/ward10的HP损失、driver ReceivedHits及唯一发射/世界命中。地面body参与条件与飞行hurt参与条件分别受到实际路径检查，不能靠把高蝠重新设成地面阻挡来迎合测试。

source/Tests后续freeze由root统一编译；v024近袖录像在旧冻结DLL运行，不将新增空中弹测试或producer后续GREEN回写成该片已验证内容。

## 独立静态P2与地面弹追加freeze

候选只读审查定位 `DungeonWorldProjectiles.cpp` 的实际高度原只参与 `LegalDamage`，XY相交后仍无条件 `BlockedBody`：新增高蝠hurt参与后，Z0地面弹会在Z90蝠处无伤停止，不能继续到后方地面目标。D05:22/162要求按实际高度判断身体相交。producer独立同时定位并已落盘修复：只对bat把实际height差[-65,65]纳入接触区间，`Inside(Time)`重建同样复核高度；独立16×12 hurt与ground-body参与分开。此次仅为静态P2发现，没有该额外分支的真实UE RED；root明确禁止为造RED冒险回滚已经落盘的候选。091905/092504主体RED保持原范围。

root随后授权在原HighHeight组追加ground XBW/STF两个子例，不新增宏、不改旧断言。新freeze：24,816字节，SHA256 `8fea8c3e7a4cd6b95166e59f715d4a5f089578c2654f9968c0a5cfbe1c3a0442`，实际6宏/6唯一名称，总候选62。此版本尚无真实执行结果。

夹具通过正常E取得武器；前方真实SpawnStoneBat在X180/Z90，后方真实地面Actor在X300/Z0，后者仅初始化MaxHP/Reset后由正常Tick准入不同Run ID。地面BeginAttack后读取实际Issued与MuzzleHeight0，要求单一弹穿高蝠并在后方ground hurt半X18对应时刻实际扣血；蝠真实HP55/ReceivedHits空、世界BatHit0。验证后方命中而非仅验证蝠未受伤，能捕获无伤停弹错误。测试停止写入等待root统一构建/运行；不把此静态修复预标GREEN。

## GREEN候选独立只读审查范围与未证边界

已读新StoneBatDriver、Fighter、GameMode与WorldProjectiles的当前接线，对照冻结D05和本六组的真实前提。中央先收玩家既有近战/世界窗口/弹与燃烧伤害，按bat target聚合同点实际减伤后的loss/stagger，经单次driver `StepTo(...,Hits)` 先交纯核，再处理bat Pump；deferred bound WA emission保持在其后。Driver用候选副本作预览、合法接触查询与最后原子提交，未以Capture/Restore回写修状态。`GetCombatHeight`保double观察与float呈现分离，65/40边界进入中央deadline；高位hurt16×12独立于ground body。低位只在实际合法Z20且有效段结束/真实中断后开始，固定1.80锚定后再.30rise；死亡通过kernel Claim与Actor bDeathReported防重复奖励。这些是源码接线事实，尚不等于新62实际通过。

额外静态混合遭遇P2：`DungeonGameMode.cpp`的`PredictMotionBodies`令下降蝠 `bBlocksBody=StartHeight<=40 || EndHeight<=40`。普通玩家的`QueryResolvedMovement`进一步按实际height裁剪；旧`DungeonStoneKnightDriver.cpp`约235的`BodyContact`仅检查该整段bool，没有bat height clip。因此石骑charge与蝠下降跨Z40的最后≤.005秒batch相交时，可能在实际Z仍>40的更早点被蝠身体阻挡。已向root/producer报告，未有真实Actor复现、未修改旧driver或测试；现6+4组不覆盖此混合遭遇，不能由它们GREEN消除此边界。

producer另提全局同点边界，独立读源码确认其排序前提：`CommitPendingDamage`先聚合并Step bat targets，后逐份提交generic/player伤害，bat Frame仍含旧`TargetAlive`。若同点既有bat入伤又有玩家致死旧伤，bat可能在玩家死亡提交前记录新Start/Active。当前明确合同与same-point组验证的是bat自身入伤/破韧/死亡先于自己的新输出；尚未有真实case证明上述全局目标死亡路径影响，故仅记未证边界，不冒称有效RED/P1，也不把它写成已通过。

root报告095542候选构建出现Driver.cpp117 `MakeBox`初始化列表歧义，producer只修显式FVector后再冻；这是编译问题，非行为RED。root另报告本新8fea测试已编译无diagnostics，本任务未运行UE/UBT或复跑旧52；后续结果必须另引实际index，不能预写62GREEN。
