# SceneExplorationPreview：独立Actor反例与验证记录

2026-10-15，ranged_review。独占写入新`Tests/DungeonSceneExplorationAdmissionReviewTests.cpp`及本文件；producer负责GameMode/Fighter/Layout/场景对象和自己的测试，root负责HUD/Probe/脚本与唯一UE构建/运行。不是唯一作者，不回退别人；旧64组与owned石蝠8fea保持不改。

## 事实、推理、风险

已读`scene-exploration-layout-plan-v001.md`、D07清房/免费路线规则、现有装备E/slot selection入口、正常输入fixture及UE Controller注册修正。设计时先请求producer接口声明，随后按实际落盘DTO/API写测试，不以虚构接口或直接改live值伪造行为。

计划需要证明实际输入导致真实source/调查/门事务：仅观察门图、纯探索网格或调用NextRoom不够。新组从有效WorldContext/physics场景、注册World的真实Controller、真实Run与场景来源创建，后续只走InputKey/正常动作和MoveOnGround连续扫掠。不能直接设置liveHP/WeaponId/sourceConsumed/调查latch，也不以SetActorLocation越墙/到门。

预期三组，最终注册数以实际落盘宏和root真实index为准；不能预写67或通过。Scene构造桩须可真实初始化布局/对象/来源，而交互/转场保留semantic RED，这样能区分初始fixture失败和缺失行为。

## 三组独立责任

1. `BoundSourceSelectionConsumesFreshEBeforeDoor`：真实门前可接纳来源优先于门；先正常E填两武器槽，再到真实出口附近的第三来源，E只打开满槽选择，第二E不代替Enter且不换房，Esc取消不改归属；重新E/方向键/Enter完成同实例替换/.35，仍同房。不能同一输入既拾取/选槽又通过出口。
2. `RealWallAndSurveyOnceWithoutReward`：沿实际场景路径移动，真实WorldStatic挡墙必须阻挡身体；为单独验证LOS，可在创建时布置实际近距测试挡板，使玩家/调查对象同时满足range但LOS被墙挡，E不调查/不消费来源。绕墙正常靠近后走真实E上下文（若同点装备先拾装备再调查），调查一次、重复E/同房往返不增次数、金币/物件/实例不暗增。正常移动与显示可见度/探索记忆不代替调查；Actor组不假称Canvas绘制或完整迷雾记忆实录已认证。
3. `RealExitKeepsRunInstancesResourcesAndRoomOwnership`：真实清除本预览唯一敌人后正常走到旧X665，fresh E不能换房；正常走到Layout真实1180出口才可换房。先通过真实来源取得STF并正常技能实际耗Focus/起实例CD，完整动作后立即E，跨房仍同RunGuid/同玩家、同武器实例/绝对CD及合法连续资源，不免费回复HP/Focus/Ammo或重新初始化Run。旧对象/来源保旧Room归属不能串新房，新对象ID须有效；不以直接NextRoom或赋bRoomCleared代替出口。

清房前提拟使用创建时明确关闭本场景敌人的AI，再正常移动和真实SWD攻击杀死它；这样此组验证门/转场，并不重复石骑AI验收。尚待producer确认其场景初始化及测试边界；不在战斗中关闭AI或写HP伪清场。

## 接口协调与证据边界

请求最小readonly事实：当前布局Entry/Exit/Barrier/Survey anchor，场景Enabled/RunGuid/RoomInstanceId、稳定ObjectID/调查次数或已调查latch；真实`BeginSceneExplorationPreview`初始化入口；E路由可通过现有EquipmentView、RoomID与场景对象结果观察，不要求另造一套交易权威。只有明确初始化API写配置，所有getter不得分配ID或修改调查状态。

本轮不写HUD、不从测试造Reveal/调查receipt；实际同房记忆/雾像素仍由root独立正常输入场景proof承担。D07/D08完整路图、奖励源/D13磁盘、收费/隐藏Boss和正式发现奖励未纳入本preview。调查牌零收入；开发QA物件不能冒称N03正式自然来源或H01首次碎片。

## 最终独立三组与RED freeze

root明确允许simulationTime==0时关闭已初始化唯一Knight AI作为初始夹具，后续必须正常移动/SWD真实击杀，不写HP或清房事实。producer负责墙/Survey基础三组；本独立第二组收敛为确认权限，避免重复。退出依据D04采用E打开NeedsConfirmation，下一fresh Enter提交，而非E同时直接换房。

实际新文件17,781字节，SHA256 `0f2e58ee40b8b214feeabc699d9198e802afcfb6396ec3f3a014da86bdf8a8fb`，3宏/3唯一名字：

- `CodexDungeon.Content.SceneAdmissionReview.BoundSourceSelectionConsumesFreshEBeforeDoor`：创建时注册entry XBWAmmo1及exit GSW，正常E取得XBW、Q回SWD并真实杀110HP Knight。到出口满槽来源处，E只能开装备选择，另E不确认/不开门，Esc取消不改source/实例；重新E/Right/Enter后真实.35替换只消费该来源，不能同次Enter过门。
- `CodexDungeon.Content.SceneAdmissionReview.GroundPermissionCancelAndFreshEnterConsumeOneConfirmation`：真实清场/走到门后Jump+E不能开门；真实落地后E才开当前Room出口确认。`ConfirmSceneInteraction(false)`不能消费；正常Esc取消，随后无pending的Enter不旅行；再E后按住Enter跨多个真实Tick最多换一房，不能跳房。
- `CodexDungeon.Content.SceneAdmissionReview.RealExitKeepsSpentFocusAbsoluteCooldownAndRoomObjectHistory`：真实清场后从西侧正常绕到Survey并E一次，核金币/地面物/NextInstance无额外收入；返回entry正常取得STF，665拒门，1180处K真正耗24Focus并起实例绝对CD7。完整动作后E/freshEnter转场，同Run/同玩家实例/HP/实际已耗Focus/Ammo/绝对CD继续，旧Survey一次调查和consumed source仍归旧Room，新房Survey未调查。

有效WorldContext/physics、真实World.AddController与GameMode resolver严格前置；仅初始Player Reset及正式Scene初始化API可定位，后续无SetActorLocation、liveHealth/Weapon/sourceConsumed/bRoomCleared写入，无Capture/Restore。移动走连续MoveOnGround，Enter/E/Q/Esc/Right/K走实际InputKey；清场走真实SWD动作时轴而非调用死亡通知。

DTO身份是(Run,Room,Object)，新房可复用局部Survey1/Exit2，不强加跨房ObjectID单调。`FindSceneRoomView`要求只读旧房事实；本组不伪造HUD Reveal或调查receipt，不能称Canvas记忆像素/全量D07/D08/D13已验。

root收到freeze后启动实际71 RED构建；总候选为原64+producer Scene3+独立Scene3+root XBWBody1，仍以实际注册index核对。尚无本轮编译/行为结果，本任务未UE/UBT；后续必须先核前提再分类，不降低断言迎绿。旧独立石蝠测试重新核SHA仍`8fea8c3e7a4cd6b95166e59f715d4a5f089578c2654f9968c0a5cfbe1c3a0442`。

## 实际71 RED独立分类（11:44）

已独立读取`UnrealGame/Saved/Automation/FirstRoom-20261015-114400/index.json`：实际注册71，Success65、Fail6、succeededWithWarnings0、notRun0。本agent未运行UE/UBT；root报告相应Source/DLL v031已保留为778文件、60,778,796字节，随后才释放producer GREEN。快照数量为root提供的保留记录，本段不将其混称独立逐文件SHA复核。

独立三组的结果与前提分开记录：

| 实际组 | 结果 | 首失败/证明范围 |
| --- | --- | --- |
| BoundSourceSelectionConsumesFreshEBeforeDoor | Success | 原真实装备来源/满槽选择路径正控制通过；同一E/Enter没有穿透成Scene过门。不能因新Scene功能尚缺就预设全部新组必须失败。 |
| GroundPermissionCancelAndFreshEnterConsumeOneConfirmation | Fail | 初始化、真实清场、实际到出口、空中E拒绝及实际落地均已越过，首失败是“Real grounded idle fresh E opens exactly the current exit confirmation”（源码170行）。后面的取消、freshEnter和只换一房尚未执行，不宣称已被此RED证明。 |
| RealExitKeepsSpentFocusAbsoluteCooldownAndRoomObjectHistory | Fail | 初始化、真实Sword清场及西侧到Survey路径已越过，首失败是“Actual optional survey belongs to this room and pays no extra income”（源码199行）。此时调查未实现；后面的STF真实消耗/CD及跨房守恒尚未执行，不能把停在调查的失败称作CD迁移RED。 |

另外四个实际失败分别为producer的真实WorldStatic墙扫掠、真实近距LOS调查拒绝、实际出口E确认，以及root独立XBWBody纯映射stub。原64组均Success。没有fixture Create失败或新warning；本轮不足是尚缺运行行为，而不是把纯核通过当Actor接线完成。

独立测试SHA仍`0f2e58ee40b8b214feeabc699d9198e802afcfb6396ec3f3a014da86bdf8a8fb`，不为迎绿改断言。MoveOnGround验证连续真实扫掠，夹具并不把每段移动距离换算成全程自然输入步行耗时；完整正常输入画面/雾像素与试玩耗时由root后续proof另验。正式15单元状态仍0/15。

## GREEN候选只读审查与独立输入优先级反例freeze

只读核过producer候选GameMode.cpp `27cdf83800503d1abdb83556f35a00e8fae4aa8cfeb8e5a2114ac667fb0d3d60`、Fighter.cpp `821346b3d9c1c2549f400c8aedd046ce847cecbf8d733c433a7f12bf6b6c5586`。Scene请求使NextSimulationBoundary返回实际From，中央依次提交既有世界/敌人/Burn/Bat/新WA造成的同点伤害，之后Validate/CommitSceneInteraction；没有epsilon延迟或Capture/Restore。NextRoom保同Run/同Player，只增Room、清本房攻击、归档对象并搬到Entry，没有ResetFighter。getter不分配ID；旧房调查与来源身份仍按(Run,Room,Object/Source)保存。本轮静态顺序核对不是新增同点致死Actor反例的实际通过证据。

发现新Scene pending分支具体P2：Fighter的Enter/E处理在通用合法闪避、跳跃、主攻之前直接return；同批fresh Shift+Enter或Shift+E会吞合法闪避，Space+Enter或J+Enter也同类。依据D11实时层最高合法world逃离先于确认，不能让确认过门吞掉更高优先的合法请求；非法Shift本身又不能关闭浮层。root授权先追加独立真实反例再实际RED，不在验证前改producer源。

新增第4宏 `CodexDungeon.Content.SceneAdmissionReview.LegalDodgeOutranksPendingExitConfirmation`，文件23,957字节、SHA256 `34587bfb8dd0028df8421e8fd6a0d1fab163d5de84662352b4ed6164d2962a6a`。旧三组文本与v031原件逐段比较相同，0f2e历史原件仍保留；新组各自真实初始化/正常Sword清场/实际到门并E开启pending，不复用已换房夹具：

- Shift+Enter、Shift+E分别严格先证groundidle、Dodge.Time==Game.Time且Time>=ReadyAt，再同一PlayerInput处理代送两次真实InputKey；要求一个真实Dodge记录、关层、不换房。连续调用旧Key helper会在第二次ProcessInputStack抹掉第一fresh edge，因此此反例显式先积累两InputKey再统一处理，且断言两键都WasJustPressed。
- 正常Shift真实建立1.2sCD，完整.4s动作后真实MoveOnGround回门、E开pending，再于Time<ReadyAt新Shift；要求既无新Dodge记录，也不关层/换房，不写ReadyAt。
- Space+Enter、J+Enter各自独立夹具；分别要求真实正H/V跳跃，或新AttackId的SWD ground Stage1接受；同次Enter不能又过门。

4宏使总候选预计72，必须以root实际注册index为准。此freeze未UE/UBT，尚无第4组实际RED结果；不预写通过。旧石蝠8fea及其余原64未编辑。

## 实际72验证与新增优先级RED（12:05）

已独立读取`UnrealGame/Saved/Automation/FirstRoom-20261015-120500/index.json`：实际72注册，Success70、Fail2、succeededWithWarnings0、notRun0。root报告v032已保留780文件/60,954,706字节后释放producer最小输入重排；本agent未UE/UBT或改生产。

独立旧三组全部Success，故当前实际证据已越过调查/确认并真正执行STF24Focus支出、实例绝对7秒CD及同Run房转移守恒；不能继续沿用11:44停在Survey的范围。新第4组Fail：两Shift组合、Space+Enter、J+Enter共8个真实动作/关层不旅行断言均失败；每例初始化、真实清场、pending门、groundidle及同一输入代两fresh边的前提均通过，非法Shift真实CD正控制没有报错。这是本轮新P2的实际Actor行为RED，不是编译失败或输入fixture缺边。

另一个Fail是producer `RealLayoutBlocksAndGroundBypass`：真实nearface挡墙断言已通过，后续MoveAxis只有“Normal movement could not reach intended legal waypoint”泛诊断，尚不能从index判断实际失败轴/起止。只读静态疑点为中央WorldStatic sweep在Time0初接触时不分进入/分离/切向，可能将合法退离也置为WallFraction0；producer须先记录实际坐标、Hit.Time/bStartPenetrating/ImpactNormal/运动点积确认，不能先放宽墙阈值或换路线规避。此点尚未形成已证根因结论。

当前独立4宏文件仍`34587bfb8dd0028df8421e8fd6a0d1fab163d5de84662352b4ed6164d2962a6a`，旧64及8fea不改。新正常输入13项录像还未运行，不因70项通过预写其结论。

## 12:12优先序GREEN与墙退离真实诊断

独立读取`FirstRoom-20261015-121240/index.json`：实际72注册，Success71/Fail1，warnings0/notRun0。新独立优先序4pair及真实CD拒绝正控制现在Success，测试`34587bfb...`未变；相应Fighter候选为`39495cc9a5a114b10817e70a21352e8f14dd4285c215bcf2fa4e7054936e5b8a`。只读核验Esc最高、合法world动作实际成功才关Scene层，Enter/E在其后，非法Q/T等不自行关层，旧非Scene分支仍保原行为。该范围已有真实RED→GREEN，而不止静态审查。

唯一失败Layout诊断明确为Y轴退离，非夹具路线错误：初始/每次停留Y=`44.000000596418943`，实际S目标0，查询ToY=`38.700000714883174`；H.Time=0、bStartPenetrating=1、PenetrationDepth=0、ImpactNormal=(0,-1,0)，deltaDotImpact=`5.2999998815357685`为分离。1600步全部无进展，sim推进至33.996131359832361。因此中央把零深起触的合法分离也当阻挡的根因已由真实运行证据确认。

root释放producer窄修方案为：仅actual WorldStatic UBoxComponent、world rotation严格identity、Time0/startPen/depth0、严格水平单位轴normal且运动dot>=0时忽略这一个起触；正深、未来、向内、非盒、旋转盒或不明确normal仍保守，继续考虑其他Hits。此限域的凸轴对齐盒分离/切向安全性只读未发现具体P1/P2；不能泛化任意mesh仅按dot排除。未来若扩域应使用实际expanded-box slab/独立surface约束。

producer将保原Layout nearface/S0/西绕路线和阈值，在nearface后新增沿面X -940→-920往返、再次W仍受阻的控制；这些控制尚无运行结果，不能倒写为原RED已覆盖。owned独立4宏不改，13项正常输入录像尚未运行。

## 最终实际72 GREEN（12:19）

已独立读取`UnrealGame/Saved/Automation/FirstRoom-20261015-121909/index.json`：72条/72唯一注册名，Success72、Fail0、succeededWithWarnings0、notRun0；7个Scene Actor组与XBWBody纯映射组逐项均Success/errors0/warnings0。原64保持通过。新优先序反例实际RED→GREEN，Layout真实零深退离问题RED→GREEN，追加的切向双向/再次向内仍挡控制也已随原路线通过。没有改独立4宏或降低阈值。

root保留快照`source-assets/production/backups/2026-10-15_scene72-GREEN-primary18-v034`，其781文件/60,963,332字节总量为root保留记录。另独立逐项核对以下7个当前冻结文件与快照路径对应存在且SHA相同，明确是7项核验，不冒称本agent对781文件做了全量对拷：

| 文件 | SHA256 |
| --- | --- |
| GameMode.cpp | `4a03b782b27cbe8c501fee30f80f16f3cbb3d37ccc3f1d81738ee76a825ceb7b` |
| Fighter.cpp | `39495cc9a5a114b10817e70a21352e8f14dd4285c215bcf2fa4e7054936e5b8a` |
| 独立AdmissionReviewTests | `34587bfb8dd0028df8421e8fd6a0d1fab163d5de84662352b4ed6164d2962a6a` |
| producer IntegrationTests | `3d1246f5b1ce7d2a1681692c1caa8ebc3bfa69d22e28b1f9c7233da0643a87f9` |
| SceneProofState.h | `3c619c8100d33626d8c64054711cbc9759785cc1fcafbf3e41e93a5bae739f45` |
| SceneProof.inl | `03bbfba07c8942668ddba4aaf44fc1baad3872acc7fcc30ab9b0b10c09ab9400` |
| UnrealEditor-CodexDungeon.dll | `ce8fc7b1c75d07f19ca9a459538001a6a2fb5658e256deee8561fa80217e9af2` |

本agent未执行UE/UBT。root已开始正常输入Scene13录像；本段仅确证实际Actor72回归，不预判录像13/13、Scene美术/隐藏收入、完整D07/D08/D11或D13。旧QA死亡Pickups仍是真实遗留事实，但Bound入口未接旧prototype拾取分支；不隐去、不称该物件链已完整。所有正式15单元仍0/15。

## 新正常输入Scene录像源（录制前freeze记录）

另获root授权仅新增`DungeonSceneProofState.h`（1,803字节，SHA `3c619c8100d33626d8c64054711cbc9759785cc1fcafbf3e41e93a5bae739f45`）与`DungeonSceneProof.inl`（18,847字节，SHA `03bbfba07c8942668ddba4aaf44fc1baad3872acc7fcc30ab9b0b10c09ab9400`），13稳定RequiredChecks，root负责Probe/PS hook。只phase0 genuine BeginSceneExplorationPreview且实际sim0时关闭唯一Knight AI，之后仅正常键输入；正常预览本身AI保持开启。Menu冻结模拟钟，因此Enter以录像wall时间起边；其余phase读真实模拟钟，单phase12s/总55s，不伪造mask或pass。

真实路线为Entry先D到(-1000,0)，W撞Barrier近面Y44，A退西口、W到220、D到SurveyX、W到300，调查/重复/零收入后先A再S逆向绕墙退回，证明可见度0而旧memory1；随后真实SWD J清场、665E拒门、1180E确认/Esc取消/再次E/freshEnter、同Run实例资源与新房HUD resetserial/旧Survey像素重置。每post-batch trace记录实际world/Run/Room/对象调查次数、source/slot、输入、HUD visibility/memory/camera/reset；初始化后无liveHP/位置/装备/source/survey赋值或NextRoom/Reveal调用。当前只是源freeze，不是13/13运行通过，不是D13/H01或正式场景验收。

## Scene正常输入首录v001失败与recorder v002窄修

root已保留F批`过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v001`及E v026（641文件/2,339,493,617字节，两遍SHA零差）。本agent独立读取原`runtime-report.json`（SHA `cf480cf69481232bbf274661293340a8f6cccd087555eefe3a665940d1569a41`）和index：profile正确，Required13但只实际写8项，前7项true，完成时限false；passed=false，failure=`scene_phase_or_total_deadline`。629电影帧另有prewarm，进程exit0不能替代失败的运行门，未执行的清场/出口/确认/新房检查不冒称通过。

phase12最后实际sim20.7668573/wall20.9732905，Player=(-1224.1647992,-.1744414)、inputA=true、KnightHP110。旧trace缺KnightXY/phase，故不能从此trace独自声称录到冲锋或精确重建追踪轨迹；root另已实际view原帧628确认守卫紧随。代码核对提供机制依据：GameMode只将bAIEnabled用于Frame.CanStartAttack，Driver仍传HasTarget/TargetAlive；Knight纯核Idle119–120仍按185cm/s追踪到X身体间距42。原phase12反复追K.X-70并要求该点静止.20s，追踪足以使目标在等待中继续漂移，Probe反而不断向A后退。先前“关闭AI”的表述不精确：此初始化仅禁自主招式起手，追踪仍然有效，不能称冻结敌人。

root授权仅修改owned recorder后，v002 `DungeonSceneProof.inl`为21,138字节、SHA `2540f499e1f35f81ba5e34eb400b8a24ba7524095145aaf16d2bd36a052d9fd9`，State仍3c619c...未改。phase12读取真实SWD Primary[0] Range135/Depth46/MinRange0和View.Stats.ReachPct，使用public CanHitTarget的实际Facing/独立轴/65 height规则并补同CanContentHit的ForwardEllipse gate；首次合法即正常释放方向键，转phase13正常J，不再追移动靶要求停稳.20。未使用起攻前Action.Range/Depth默认0，也未冻结Knight、改live位置/HP或生产AI。

trace新增Knight actualXY、kernel phase、bAIEnabled、实际Frame.CanStartAttack、目标dx/dy/distance/forward distance及Player.Facing/CanStartAttack。初始化元数据改为`attack_starts_disabled_only_at_sim_zero=true`、`pursuit_remains_active=true`，明确能力而非伪造该帧运动。原13项名字、55s总时限、12s phase时限及其余路径/检查不降。此时新源已freeze交root等待新编译/复录，不能把v001影像倒标为新源或补写13/13。

E保全后，本agent另逐张view_image原尺寸实看v001原件168/180/463/592（未重复root628）。168/180分别对应trace before_survey wall5.639801/after_survey6.039831，最近capture wall5.629875/6.029010；顶部真实文本变为碑文，HP100/金币00保持。贴身时碑牌与部分“调查碎碑”标签被玩家轮廓遮挡，是当前可观察的可读性限制，不据此判Scene美术/界面最终通过。463/592对应phase12 A退行、PlayerX约-208/-1003，灰石骑始终紧随玩家右后侧，和源中pursuit未禁一致；两张静态图不证明冲锋或全运动脚锁。v001没有清场后确认/新房的影像，本补看不补造缺失阶段。

## 正常输入v002实际13/13及独立8原帧

root确认F/E v027保全729文件/2,666,989,428字节、两遍SHA零差后，已独立读v002 runtime-report：profile=`scene_exploration_normal_inputs`，Required13/Checks13全true、passed=true、failure为空；717电影帧另有prewarm。捕获源v035的proof为2540f499...，快照DLL及runtime index均为`7aacdae04df864af46a1e3cbcdd746702a7d42fcc9ab5b466dec478f782c17c6`。这次首次真实覆盖完整正常输入调查/记忆/清场/665拒门/1180确认/取消/新确认/同Run新房，首录v001失败保留，不倒填。

独立逐张view_image 8个distinct原件154/166/509/599/676/688/700/716；root另看49/243，合计10unique，不能说本agent独立看了10张。取消688按真实exit_cancelled wall24.105791匹配最近native capture24.093469，仅补外部记录，不改archive。细节与8原帧SHA在`scene-exploration-visual-review-v002.md`。

确认层、取消后回原房、再次确认及房02/敌1变化可实际辨认；真实RunGuid保持，HUD resetserial2→3，Survey memory1→0，新房调查Count0。当前仍有具体P2：取消/开始旧LastMessage提示过期、贴身碑/文字遮挡、新房visibility=memory=0时碑体名称仍透雾显示。root已安排producer文案与HUD窄修，但尚未对这些新修复构建/复录，不能将v002标为已消除这些问题。旧QA掉落仍显示且Bound拾取链未接，不是正式奖励链。8静帧不认证全运动/frame snapping/脚锁、听感、灰几何美术终验、D07/D08隐藏收入或D13。正式完成仍0/15。

root随后接管新SceneProof.inl追加HUD物件可见性/实际draw路径等只读观测，准备下一版本；本agent本轮只写review docs，不再修改inl，v035/2540冻结原件保留，不以未来working源替代此片来源。
