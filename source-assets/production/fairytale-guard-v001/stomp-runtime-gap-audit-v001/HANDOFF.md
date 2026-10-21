# Stomp gap audit / bounded overlay Stage0 candidate v001

事实：基线为实际v138-HeroDeath190G，257 Source、1326 Production、190注册测试。此次重新逐一核257个Source SHA，全部等于该snapshot。已有StompWindup222六个包，StompActive/Recovery包为0。没有运行UE/UBT、导入或View媒体。候选没有写入实际Source。

事实：Root在本轮E515后实际视审旧224首接222末，报告眼窗横跳29.6display px、bodyroot/近鞋滑移29.3px，拒绝join。这个新决定来自本任务parent消息；本audit没有独立打开E515保全receipt或View原图。旧224/225的sourcepose曾获查看/提取许可，不等于runtime接缝批准。Root正在准备纠错Active源；最终source ID、Recovery是否重做、注册、trial批准和导入都未在此预判。历史6 PNG仅只读解码核SHA/RGBA，明确不是本次准入素材。

推理：selector、kernel与renderer已经支持Stomp三阶段。当前缺口是两行资源/配准/试样权限，不能通过改时长、移动actor或把缺行替换Ready解决。最小安全接入为新opt-in overlay，共用已有selector/Plan/绘制算法，旧Known44模式继续固定原13行44unique。直接扩充旧ProfileFull会撞到三个旧probe的Unique==44以及旧checker精确合同；不能放宽它们。

风险：原WU222只有artist NEAR-support传播注册，并未证明真实footlock。100.8px是Guard standing-equivalent目标，70world是kernel ExtremelyCloseRadius，主角目标72px；这些不是同一单位。此次不改显示比例。旧计算的WU5→A0眼相对支撑横移29.6926927px已与Root实际视审拒绝吻合；新的源仍需实际join和两侧镜像审查。Recovery接回Ready时Ready时钟未重置，不保证回Ready0。

## 原有真实行为

| 项目 | 实际位置与合同 |
|---|---|
| 极近触发 | DungeonStoneGuard.h:33 policy70world；cpp:505 ChooseAttack由真实距离/范围/冷却决定Stomp |
| 原始时序 | cpp:477/480、728：WU.9s、lock.45s、Active.15s、Recovery1.5s、cooldown3s；OccupiedUntil=原RecoveryEnd，IdleReadyAt=RecoveryEnd+.3 |
| 锁定 | cpp:569：.45锁原Position为LockedCenter；仅Axe在此重选Facing，Stomp保持attack-start Facing |
| 原窗口 | cpp:580：ActiveAt真实Issued ActiveWindow及FDamageWindow；ActiveEnd真实RecoveryStarted；RecoveryEnd完成。仅一个原Stomp窗口 |
| 命中 | cpp:750：半开[ActiveAt,ActiveEnd)，160×90椭圆、height65、每AttackId/Target一次receipt。画面与新增row不改变此逻辑 |
| WU222 | DungeonFairytaleGuardPose.h:67，原Start+0/.15/.3/.45/.6/.75各相；Start≤Time<ActiveAt，lock边界正好frame3 |
| Active2 | FullPoseV003.h:46，原ActiveAt+0/.075；ActiveAt≤Time<ActiveEnd |
| Recovery4 | 同文件:59，原ActiveEnd+0/.375/.75/1.125；ActiveEnd≤Time<RecoveryEnd |
| 优先级 | Dead/Stunned先于行动；真实打断后仅正[StunUntil,OccupiedUntil)显示IR，绝不新Active或显示普通StompRecovery |
| 事件身份 | FullPoseV003.h:70：WU取AttackStarted.EventId，A取ActiveWindow.EventId，R取RecoveryStarted.EventId，均匹配同Action.AttackId；EventId不能当AttackId |
| Ready | Pose.h:88，锚WakeEnd/InitialTime，1s循环四相，行动中时钟继续；不在恢复结束重置 |

## 当前closed门与fallback

FullDataV003.inl:79–91已批准WU222，388body basis、100.8/388尺度、6原pivots，Root已批准trial而FinalAccepted=false。93–101的A/R仍NativeSourceId0、SourcePoseApproved=false、TrialAllowed=false、Frames空，仅Pending224/225历史说明。FullProfileV003.h:22的门要求完整row、明确Root trial record、body-only basis与source/registration SHA。Import并不是单独打开此门的条件。

FullPresentationV003.cpp:14启动遍历已批准row预载；:40实际driver只读SelectFull→PlanFull，验证整row驻留和exact path，然后仅提交1张含固定斧整身texture；SourceFloorPivot左向用512−x一次镜像。新两行应复用这一条，不增加独立axe/grip。不完整/未批准时Draw返回false并记录原requested clip/gap；HUD.cpp:1065在full启用时不尝试partial Ready，而进入既有Guard程序body/axe与有限feedback。原HeroDeath/Hurt分发及默认rangeOff保持。

## 候选文件与Stage0准入

仅candidate/stage0/new-source三文件可作为新增Source：

- DungeonFairytaleGuardStompProfileV004.h：唯一namespace `DungeonFairytaleGuardStompV004`，入口`ProfileStompV004()`、`PlanStompV004(FullV003::FSelection)`。
- DungeonFairytaleGuardStompDataV004.inl：Stage0直接返回原44 profile，故新两行仍closed；没有伪造registration literal、Root批准或40/50资源驻留。
- Tests/DungeonFairytaleGuardStompV004Tests.cpp：三组测试，下述TARGET每组首先遇到即return。测试预期可注入新的已批准source，不硬绑242或后续RecoveryID；旧224/225当前不获runtime批准；测试不为未来Root重新决策硬编码source ID黑名单，正向必须实际source-approved/Root-trial-gated新row。

candidate/patches四个最小patch（`git apply -p0`）：

1. FullProfileV003.h提取`FindRowFullInProfile`/`PlanFullInProfile`共享实现。旧FindRowFull与PlanFull仍固定ProfileFull，算法逐行不变。
2. FullPresentationV003.cpp在独立`-DungeonFairytaleGuardStompPreview`选择overlay并启用已有full分发，复用既有loader/SelectFull/Draw；旧full flag选原44。
3. HUD.h增加独立bool及只读IsFairytaleGuardStompPreviewEnabled。HUD.cpp无需改绘制路径。
4. FullDrawStateV003.h仅增加ProfileId，旧`GuardKnown44FullV003` / 新`GuardStomp50V004`。实际quad驻留readback由独立observer代理提供，Root后续窄merge，未包含在本patch。

实际Source257保持不变，四patch已以`git apply --check -p0 --ignore-space-change`静态检查exit0；没有声称C++编译或测试RED。一次初始host check漏-p0，仅路径剥离错误，未应用任何patch，校正后exit0。

三完整名称：

1. `CodexDungeon.Content.FairytaleGuardStompV004.RealNativeHalfOpenClockAndEventIdentity`
2. `CodexDungeon.Content.FairytaleGuardStompV004.Versioned50BindingsAndAtomicMirroredFloor`
3. `CodexDungeon.Content.FairytaleGuardStompV004.RealActorReceiptRecoveryAndInterruptedExclusion`

预计Stage0三TARGET各1 semantic error，须由Root实际核实：目标依次为真实Active0新plan、overlay精确50、真实actor正常Stomp命中后Recovery1新plan。前提若失败须保留，不能当目标RED。第一组直接使用实际FGuardKernel两向、半开前邻double/边界、Issued/Window/once-hit/原Ready时钟；第二组完整fieldwise核其余11行不变及坏非当前frame/权限/record/registration闭门；第三组复用现真实FGuardWorld+publicSpawn65测试fixture，正常GameMode clock自然Stomp/真实玩家receipt，然后独立原85打断/IR无新Active。该publicSpawn只是测试fixture，不称正式房间on-screen全战。没有人工构造FState/pose frame，没有改真实sim。

## 真RED之后的最小实现与资源

只替换新DataV004的stub：静态复制原ProfileFull13行，替换两行；不改base table。新A2/R4逐frame填Root批准后的新source ID、TexturePath、PNG/RGBA SHA、artist floor authority/pivot；每row单独body standing basis与ONE scale，TargetBodyHeight仍100.8；RegistrationEvidence/SourceIndex两64SHA、明确两行独立TrialApprovalRecord、TrialAllowed由Root实际记录打开，FinalAccepted=false。当前candidate故意没有这些批准。

资源准确预算：新增6 Texture2D512（A2/R4），原44精确保留；50unique、51logical含Dormant alias、13rows/57logical合同不变，Move仍6gap。如果只有这6新增，Production1326→1332；Source count由Root实际admission报告，不把未来observer计入既成事实。新namespace建议`/Game/Production/FirstBatch/GuardWhole_stomp_v004/{StompActive,StompRecovery}/...`，以真实新sourceID命名，Root最终决定。不要导入历史224/225冒充新源。

不需要改kernel、时长、driver、Fighter、audiojournal、reward/inventory、HeroDeath/Hurt、旧partial、旧三个probe、旧checker或旧190测试。最小候选3newSource+4existing窄patch；独立native probe/启动接口和新50 prereg/checker另行准入。回归应保留原190并新增3，实际registry由Root报告确认，不预标193GREEN。

## 后续真实on-screen证明门

正式三敌房间计划出生Guard，正常Enter/WASD到两侧合法近点（world距离≤70，避免与真实body重叠）；只通过实际policy启动Stomp，不TryStartAttack/manualTick/SetState/写HP/time/teleport。清Knight/Bat若用公开诊断damage需明确scope；Guard不publicdamage。Ready→WU6→A2→R4→真实Ready需同一run/restart/entity/首个原Stomp AttackId，完整Issued/EventId及window EndTime/Center/Facing匹配。WU在ActiveAt缺63立即fail，A在ActiveEnd缺3立即fail，R在RecoveryEnd缺15立即fail，不由后续cycle补相、不延长原窗。

Ready返回样本按实际原Readyclock核；全row驻留50、完整新资源源链、单层固定斧、实际quad/一次镜像/白色正常材质及default range0均由独立observer/checker核。两向记录真实空间关系、HP/receipt，正常一窗口一次命中或真实miss均不得伪造。保留WU5→A0、A1→R0、R3→实际Readyframe的原相邻draw joins，按原PTS录像。RootE保全后实际View判断比例/root/鞋滑/斧方向，成功metadata不能代替join验收。75ms Active相仍可能被实机stall漏掉，按真实failure保留，不改clock。
