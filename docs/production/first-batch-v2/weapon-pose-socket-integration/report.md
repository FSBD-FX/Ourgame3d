# 猎弩 Actor-owned 手持发射口：RED scaffold v001

2026-10-15。producer拥有Fighter、新`DungeonWeaponPoseSocket.h`、新增生产者Actor测试及本文；root拥有HUD/Probe和唯一UE/UBT运行权，ranged_review独立新增测试，assets_prepare拥有美术。共享目录，不修改旧72测试、WA或其它作者文件。本文尚无本候选UE编译/RED结果。

## 事实与合同判断

权威基线为root v036与实际`FirstRoom-20261015-125946/index.json`严格72GREEN。现有`GetWeaponMuzzleOrigin()`来自真实SceneComponent，但默认组件XY零偏移、Z只有JumpHeight；HUD独自按握点/刚体旋转计算native emit，故现有弩矢从足点高度显示。冻结primary manifest `79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f`、ready `21c8ff90c59c411bfdbcabcfee0292881d77e4e652cc2fde46cab35e99373813`、reload `9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8`位于`source-assets/production/first-batch-weapon-actions-v001/manifests`，此任务未改素材合同。

主线程裁定默认实际combat XY使用Actor native手持口，保留公开组件的显式custom override；旧测试直接`SetRelativeLocation({24,7,0})`是合法自定义口，不能无条件覆写或加QA分支。combat Height仍为实际Jump，65cm规则不加图片手部高度；另设PresentationOrigin.Height，真实物理组件Z取该显示/手部坐标。默认socket由Actor更新，HUD只读同一pose；发射时冻结同点样本，不能由HUD回写组件或事后读移动后的Actor。

当前显示坐标合同为body root(256,472)、尺寸160、512方画布；Ground X比例0.65、显示高度比例0.7。primary实际ActiveAt采frame2，冻结emit=(423.5311940307165,224.3741693502523)，所以默认world X前移`(423.5311940307165−256)×160/512/0.65`约80.54cm，显示高度偏移`(472−224.3741693502523)×160/512/0.7`约110.55cm。镜像在同一root处应用一次。ready emit=(395.40740934629025,287.0306226992487)。reload早期近手是操作手，必须使用冻结support anchor/刚体矩阵，不能冒充枪托Grip；root独占扩展现有BodyPose sampler。

两项实际兼容风险已报root，root随后明确本轮合同，仍待真实验证：

- 旧72 `ProjectileWallsCenterBoundsAndHeight`要求目标中心X430超出420硬界而拒伤；默认口前移后，若仍从socket量420，该目标进入射程。root裁定默认XBW的独立RangeAnchor冻结为本次发射Actor groundXY，420cm仍从角色前方量，扣掉发射前移段后的剩余范围才供外射；custom仍从原组件origin量。D02共同规则未明确X脚点/枪口锚，这是本轮明确决策，不能称旧文本已保证，也不改统计或旧断言。
- 发射者至前移socket之间的真实墙/近身body不能被前置起点越过。root授权真实actor→socket launch-clearance，按本次发射时刻最早空间接触结算一次Stop/Hit，资源仍只由原emission消费。被挡短段保留原Source.Origin事实，以LaunchObstructed区分，不冒称正常外射飞弹。

世界接线ownership已扩为`DungeonWorldProjectiles.h/.cpp`及必要GM世界接线；root不碰这些。拟定外射PositionAt仍从真实Source.Origin以速度推进，Traveled只计外射，RangeEnd=AtTime+(Range−LaunchForwardDistance)/Speed；launch阻挡时Position=真实短段contact、Traveled=0、LaunchObstructed=true，无正常外射。collision/admission/损伤优先与去重仍需真实反例，当前没有实施。

## 精确接口与行为桩

`DungeonWeaponPoseSocket::FResolved`含Supported/CustomOverride/GroundPoseFallback、Clip(None/Ready/Primary/Reload)、Frame、SampleTime、InstanceId、ActionId、Facing、RootX/Y、BodySize、GripX/Y、SupportX/Y、ComponentSupportX/Y、ComponentEmitX/Y、EmitX/Y、Angle、Scale、CombatOrigin、PresentationOrigin。Support为body anchor、ComponentSupport为对应源点；reload不以操作手冒充枪托。Fighter新增public `GetWeaponPoseSocket() const`与`UseAuthoredWeaponPoseSocket()`。

RED桩保留真实既有GetMuzzle、组件、WA与世界发射；getter返回真实旧combat origin/当前时钟身份，但Supported=false、不伪造native姿态。恢复自动口API暂为无行为桩。未实施自动组件接线、外部变更检测、姿态时钟取样或世界presentation快照；需root先保留实际RED后释放GREEN。特别是WA StepTo前的状态时钟可能仍在From，native姿态必须按真实事件AtTime取样，不能把旧From帧当发射帧。

World RED仅加数据字段，未修改查询/消费行为：Projectile含HasPoseSocket/PoseSocket/RangeAnchor/UsesActorRangeAnchor/LaunchForwardDistance/LaunchClearancePending/LaunchObstructed；HitReceipt含HasPoseSocket/PoseSocket/RangeAnchor；WorldEvent含HasPoseSocket/PoseSocket/RangeAnchor/LaunchObstructed。所有默认false/零，既有发射不被伪造成已接手部快照。该Run-local观察DTO不是D13保存schema。

## 生产者新增三组

完整名均以前缀`CodexDungeon.Content.WeaponPoseSocketIntegration.`开始：

1. `PrimaryUsesCurrentActorAndAcceptedPhase`：真实Run/QA来源、World.AddController、正常E完成拾取，正常J与D在未锁前移动；实际发射/资源前提通过后，核当前Actor与冻结frame2的真实组件XY/Z、独立combat/display高度、action/instance/subhit时间。
2. `ClockAndPendingReloadNeverCommitFromPose`：同一真实Actor按实际primary半开阶段取1..5帧，重复只读不分配任何身份或资源receipt；完整恢复后实际自动reload，四个真实时间区间按冻结support/emit几何取样，stage3与末点前均无补弹，只有真正完成补一弹并回ready。
3. `EmptyAndSwitchCannotRetainAnotherInstanceSocket`：真实初始Ammo0来源，正常J/K无动作/发射/资源receipt；空弩仍只读ready姿态；正常Q的.35事务切SWD拒旧弩pose，切回原空实例不补弹、不重播。

所有夹具先走真实controller/来源/动作，再断言未实现socket；没有live HP/Ammo/位置写、Capture/Restore、HUD调用或raw kernel state安装。独立reviewer另做normal双向/custom/air与世界高度样本，组数按其冻结与root实际注册统计。当前仅producer新增3，root另新增Reload sampler组，故72+1+3=76，独立新增尚未计入最终值，不冒称实际已注册。

## owned Source freeze

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| DungeonWeaponPoseSocket.h | 961 | `596b553de30be27d6582c6ee1e2af137ae284ae393f50d17ad1f3a5a1c3c512c` |
| DungeonFighter.h | 9,206 | `4757d290828dd4b3f401cb0636a99c5c5a680f7c81fef2747a9599c983704b8e` |
| DungeonFighter.cpp | 58,277 | `780c038d971679c5df9662b89893ea336194f6ff4433ddbb1eebe7de288f4af6` |
| Tests/DungeonWeaponPoseSocketIntegrationTests.cpp | 13,564 | `e7b90f8fcf20a6a99e09b4283331d960a319d655508fa4be8e0aecfa86922c01` |
| DungeonWorldProjectiles.h | 4,448 | `6b656d7da7cb9f9266b34571129804936daadc2d39a6bb2bbb917218b35b5de8` |

World.cpp仍为`5e142b7ff7186e34a4bd5f33c92daa7f05ef6faa32f9ff73db3bc26804c2088e`；GM.cpp仍`297bc39de1b422a9ddb2add8368a88d17c966f335f330935278bc86c5e1b97d8`；WA仍为`e8d6d2366c26b87eecc14b660b8020b31a4e7c674c7256479a536ba8d2b91586`。未运行UE/UBT；未把静态候选称为真实RED/GREEN或手持发射通过。当前RED固定既有neutral ready/primary几何；root另推进真实loaded/empty组件生命周期，新的4PNG测量合同交付前不猜pivot或混用neutral坐标，需另记后续测试版本。美术reload、四甲兼容、声音、正式来源与D13均不是本桩证据。

## 实际80 RED与生命周期合同 v002

root `build133021` exit0，实际`FirstRoom-20261015-133252/index.json`为72 Success/8 Fail/0 warning/notRun。原72全部通过，producer3、独立4及root Reload sampler1均在预期新socket/clock/snapshot断言失败，真实来源、controller、动作和Issued前提成立，无编译或初始化失败。root v037完整冻结810文件/62,749,839B的源码、DLL和reload16后才释放GREEN。

source owner随后冻结`weapon-state-lifecycle-v001.json` SHA256 `94f2d3b6163f620babe8d5d550cacbeb7204ca69f8b3942ebdc27f512e72fffe`，零新增生成。root明确初次Ammo1沿用原neutral；实际Emission后empty0，实际ReloadCompleted后loaded3，Q往返保实例真实history，取消不得凭视觉stage3装弹。新state0/1 stock(138,308)、support(344,320)、virtualEmit(506,263)；2/3 stock(138,274)、support(344,286)、virtualEmit(506,229)，共享stock→emit=(368,−45)。virtualEmit并非每态不透明点，手部残差和机械候选限制沿原manifest保留。旧neutral pivot(128,253)不得套新四图。

根任务不批准让`GetWeaponMuzzleOrigin`同点偷偷返回历史值以保旧断言。当前组件/当前口保持真实；新增明确`FindWeaponEmissionPoseSocket(ActionId,SubhitId)`只读发射时样本，World Source与事件快照依该实际样本冻结。neutral→empty口变化与旧“post口==pre发射口”的假设确有冲突，旧72及独立177220ff仍保持原样交下一实际候选运行；若实际证明为该假设，root才明确版本化，并保留失败，不能宣称原测试未改或提前降低覆盖。

## GREEN候选 v002：尚待实际81

Actor使用同一纯resolver采冻结primary/ready与root Reload sampler。FResolved新增WeaponStateIndex、ComponentGripX/Y及ActorOrigin；真实库存/history决定组件state，矩阵决定握点/support/virtualEmit，再统一映射世界坐标。物理组件包含手部Z，默认combat Height只取Jump。直接外改组件相对transform作为一般custom覆盖检测，`UseAuthoredWeaponPoseSocket`显式恢复自动口，不加QA分支。初始位置、朝向、换装、动作接纳/结束同步组件；只读查询不分配或消费。

发射前按真实Now准备native pose，实际WA只在原权限和资源门后发射。仅当实际E的clock/action/instance/origin与准备样本严格一致，Actor才登记immutable emission socket；World随后复制该pre-spend快照。post-spend当前empty口单独更新，不重写已发Source。默认RangeAnchor直接取该snapshot的ActorOrigin，不每帧追Owner；custom继续原origin/range语义。Actor/World新增数据为Run内存证据，WA状态版本与D13格式均未改。

世界先对Actor→mouth短段做真实墙/身体/实际高度/入伤权限最早空间接触；短段接触在实际emission时刻只结算一次Hit/Stop，Traveled0并明确LaunchObstructed，不伪装成外射速度运动。正常外射从Source.Origin推进，剩余420扣掉已前移段，中心硬界仍量冻结Actor anchor；近身穿透各段服从原maxTargets/receipt去重。事件与hit receipt复制同一pose/range/launch事实，当前口、转身、落地或换房均不得反写它。

producer测试升为明确v002：旧实际RED3文件e7b90f8f完整保存在`evidence/2026-10-15_actual80-RED-neutral-v001/DungeonWeaponPoseSocketIntegrationTests.cpp`。当前primary组独立核pre-neutral发射与post-empty组件，并补真实K fallback和空场剩余射程最后representable/精确stop；clock组按新94f2期望真正完成后loaded3。新增第四组`RealReloadLifecycleSurvivesSwitchAndCancellation`，正常J→完整reload→Q往返loaded3→第二次真实emission冻结loaded3/currentempty0→stage3前T取消无refill/refund→再Q保empty0及两发原事实。root预计总81=原72+root1+producer4+独立4，实际注册/结果待其index。

另新增实际left J→完整恢复→autoReload四stage的Actor/Socket Facing−1反例。只读发现WA reload action无意义默认Facing+1被Actor无条件抄回；root要求先保错误生产行为跑下一实际RED，再窄修Actor reload保当前朝向，不改WA。该候选仍故意保留此赋值；80 RED没有覆盖这个新反例，不倒填为已复现。

纯MSVC `/std:c++17 /W4 /WX`实际编译运行19/19，证据`evidence/2026-10-15_GREEN-candidate-v002/compile.log`与`run.log`。核初始neutral、真实pre-emission frame2、实际empty0、四reload support/emit、视觉不补弹、真正完成loaded3、过去/NaN时钟拒绝、异武器拒绝。该纯核验证不覆盖UE组件/世界碰撞或证明81GREEN。

七个owned源的冻结清单`evidence/2026-10-15_GREEN-candidate-v002/source-freeze-sha256.json` SHA256 `369c396817eaf056092abea5d3ab9654efc45bc654414a43c6569f838ec5ea81`：helper080734e3…、Fighter.h13241cc6…、Fighter.cpp ee06f0cd…、World.h06a87489…、World.cpp9f3ac527…、GM.cpp930d3ae9…、producer4tests71551e21…。Source已停，root统一UE构建/实际验证；可能出现新left RED或旧post口假设失败，不能预称完整GREEN、正式机械/美术、四甲、音效、来源或D13通过。一般custom口可有意偏离冻结native手位，本轮保存其物理覆盖权限，不宣称任意自定义口与原图手部对齐。

冻结后的独立只读审查又发现launch与外射同点排序相反：launch same-fraction选Rank较小的body2，普通外射same-time选较大的wall4/bounds3。该静态P2未由80 RED或当前81范围证明；root保持candidate Source不改，计划当前81实际运行/快照后追加独立第五组，使后续82，先取得真实tie RED再统一优先级。实际夹具需证明原生墙Hit.Time与解析hurt入口确为同fraction，不能只把数学近似同边当同点。此时尚无该反例实际结果。

## 实际81与left窄修 v003

producer独立读取`FirstRoom-20261015-135821/index.json`，SHA256 `a361213a0de7478eee03e7094b0b9c78d6be8e5030e5617885651944104724b2`：76 Success/5 Fail/0 notRun/inProcess，root确认零warning，build135355 exit0。root v038完整冻结899文件/65,348,010B保存此来源后释放窄修。新增生命周期、真实K口、空场剩余射程末点、实际默认420硬界与launch墙/近身的本轮门已通过，不能将五个失败掩去而称81GREEN。

clock组四条left reload stage0..3的Actor/Socket面对断言全部失败，正常A/J左射与真实完整恢复→autoReload前提成立。原StoneBat high-height组有一条复合muzzle断言失败；独立NativePrimary/PublicOverride/RealJump三组涉及post-current emit与immutable source比较失败，其正式归因仍交独立审查，未因预判改生产Getter或旧测试。

root只授权修已实际证明的left：`SyncWeaponSkillAction`仍将Primary/Skill朝向取acceptedAction.Facing，但Reload不再将默认+1抄回真实Actor。因此装填保当前面对方向，合法装填移动的转向亦不会被无意义字段覆盖。Fighter.cpp新冻结61,239B，SHA256 `e36cc2915b1367057f32e25054eb6356c37e4569cddc3d619738afaa52df9a60`。其余candidate v002源不改，World.cpp仍9f3ac527…，producer4仍71551e21…，旧72与独立177220ff原断言保持。尚待下一次实际运行，不提前声称left GREEN。

launch rank翻转继续保错误生产，等待root追加独立第五组使82并取得真实tie RED。该问题不倒填为80/81已证；Source再次停写，所有UE/UBT由root执行。

## 实际83：tie有效RED、death夹具失败与窄修 v004

root实际`build-editor-20261015-141619.log` exit0；producer独立读取`FirstRoom-20261015-142136/index.json`，SHA256 `45df5ea509d7160c7c7bcaa33c4e4bd7f5a2078f39c661a66355732a01024d8f`：81 Success/2 Fail/0 warning/notRun/inProcess。root v039完整冻结950文件/66,913,527B。producer四组包括新增left四stage全部Success；独立原四组及显式版本化的StoneBat复合口断言也Success。此处历史post-current与pre-emission假设的版本化由其各自owner完成，原80/81源和失败仍由root快照留存，不能称旧断言完全未改。

独立第五组`ExactLaunchWallBodyTieStopsAtWall`在两个Facing均真实测得原生WallFraction=.5、BodyEntry=.5；near target初始1000实际被降至966，四条wall-shield/no-delayed-damage断言失败。这是墙与hurt完全同点时错误选择body的有效生产RED。root释放后，本owner只将LaunchContact同fraction判断从`Rank<Priority`改为`Rank>Priority`，与普通外射既有wall4、bounds3、body2排序一致。最早fraction和同rank稳定target ID规则不变，无范围/伤害/资源/几何调整。

独立第六组`OldBurnDeathBeforeNewEmissionCannotBlockLiveRearTarget`实际停在line479的正常Enter换槽前提，尚未执行同点burn死亡与新发射，不能称死尸阻弹已复现。另只读核得STF cycle为.45+.12+.45=1.02，随后Q .35完成早于首次burn .45+1=1.45；需要通过真实推进到actual FirstTick后再要求HP2，不能写HP或放宽门。此夹具由独立owner修订；fresh-emission过滤current-dead的生产方案仍冻结，未改GM或World该部分。

本次窄修后World.cpp为24,653B，SHA256 `e3daa075b656ecc793690669ea8721e12f4f432e2a5a67b5cba6448fb6ed192c`；Fighter.cpp仍`e36cc291…`、GM.cpp仍`930d3ae9…`，其余owned七源沿candidate v002。尚待root统一实际运行验证tie GREEN；本owner未运行UE/UBT，不将helper19/19或已有81个Success当作全83、完整发射表现或正式美术验收。

## 实际83第二轮：tie GREEN、有效旧伤死亡RED与窄修 v005

producer独立读取`FirstRoom-20261015-142649/index.json`，SHA256 `8a215e4b4a9128b80b74279b8eea89cd1b23c19412f8938b61678baca96b16de`：82 Success/1 Fail/0 warning/notRun/inProcess。root v040完整冻结950文件/66,914,931B。双向完全同fraction的wall/body tie组已Success。

独立death组新版本cc1620ca…改用正常E→Left选0→Enter，保留XBW1；真实cycle1.02、Qcomplete2.4299999997764825、FirstBurn2.5099999997764826，此时HP4再正常推进至FirstTick才为HP2。SecondTick=3.5099999997764826，Jstart=3.3499999997764824；实际旧burn死亡Sequence8早于新发射Sequence11，近敌HP0/dead且发射时间严格相同。全部因果前提已通过，失败为line546新弩箭被旧尸体观测挡住、line560后方活目标未收到弩伤。这一轮才是有效死尸阻弹生产RED，不能倒填上轮夹具失败。

root保留实际RED后释放窄修。`ConsumeBoundWeaponEvents`的实现位于World.cpp：只有本次真正新增Projectile，才复制SkillBatchBodies，并将实际Fighter已dead的该局部body设bAlive=false，供新发射后的To/To零时刻查询；旧区间使用的Bodies/共享SkillBatchBodies、已受理HitReceipt/PendingDamage、原damage-first顺序均不改，非新发射分支仍用原视图。该门覆盖launch短段及mouth内的外射零时刻接触，避免仅在launch忽略尸体后仍由外射入口再次阻挡。未改几何、时钟、范围、资源或原WA状态。

本次World.cpp冻结25,155B，SHA256 `0bc43aaf55c8576b93f8fde87cd8db92f04153d682ba332aa2620ac547687fb9`；Fighter.cpp仍e36cc291…、GM.cpp仍930d3ae9…，Source再次停写。候选仅待root实际83结果，当前82/1与新代码不得写作83GREEN。未启动UE/UBT，原有纯helper19验证无变更，不重复跑作引擎证据。

## 实际83 GREEN与剩余运行边界

root `build142939` exit0；producer独立读取`FirstRoom-20261015-143046/index.json`，SHA256 `5f23830c316ff1e21d726c7d92571540b62c81fb912f4692705fa8c8a85a2577`：实际注册83、83 Success、0 Fail/warning/error/notRun/inProcess。producer四组、独立六组及根Reload sampler全部Success，包括left完整装填、双向native当前口/不可变发射口、custom覆盖恢复、独立combat/presentation高度、420硬门与发射短段、完全同fraction墙优先、旧燃烧死亡先于新发射后的活后靶命中。root随后才将默认ExpectedTests更新为83，并冻结v041的950文件/66,914,427B源码/DLL/765 production textures/import receipts。

World.cpp仍为0bc43aaf…，Fighter.cpp仍e36cc291…，GM.cpp仍930d3ae9…；全部Source继续冻结。上面的fixture失败、有效RED及各自快照不删改，不能把最终83通过倒填到旧80/81或首次83。helper19与Actor83是不同层证据；正在由root录制的无甲normal-input20尚无本节实际结果，不预称运行画面或正式美术已验收。

四甲ready48/primary48/reload32已实际导入，但其源合同仍标runtime_verified=false及semantic_full_armor_acceptance=false；无甲normal20不能替代四甲运行证据。只读建议独立29门profile：common3、每甲6门×4、全程真实history/同XBW实例1门、55s总门1门。每甲覆盖正常E .50换装（首次空槽直接接纳，其后三次occupied须独立freshEnter）、双向ready63/primary63/reload15六层stack、双向真实bolt/frozen socket和真正完成loaded3。保原无甲20合同，采用真实Tab/移动处理掉下旧甲后的目标展示，不以直接Select或写ArmorId替代输入。三射重试若按每侧重复会超过55s，应给全局有限补拍预算并让缺帧真实失败；只允许初始化合理高HP静态靶，不在运行中补HP。该方案尚未实施，不覆盖完整服装、四甲技能/行走/音效或正式来源。
