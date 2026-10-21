# Guard presentation v001 独立只读审查

结论：发现1个P2终端死亡材质时钟问题，未发现P1；最小修复和独立第四组UE回归已冻结。
其余已审的原生选择、受阻距离、恢复、加载门、镜像和单层斧头路径，在本轮16图partial
范围内有对应源码依据。此结论不是UE编译/纹理实载/画面比例验收；本审查未运行UE、
UBT或native测试。Root报告原3组已经真实semantic RED，各1error/0warning；本审查
只核合法前置及代码路径，不把worker的standalone结果算成UE结果。

## P2：终端死亡帧推进，受击材质色却永久冻结

位置：候选 `production-source/DungeonFairytaleGuardPose.h:37` 和 `:48`；实际调用
`production-source/DungeonFairytaleGuardPresentation.cpp:35`，Tint应用在`:87`。

事实：MaterialHit取 `S.Time - Damaged.AtTime < .22`。Dead分支另取
`max(S.Time-Died.AtTime, TerminalDeathAge)` 来推进Death。实际GameMode.cpp:1889–1894
在game-over只推进terminal presentation；Fighter.cpp:1799–1805推进AnimationTime而
不推进kernel/资源。原生Guard.cpp:664在真实HP损失发出Damaged，`:670–675`在同一
S.Time发出唯一Died。若Guard致死后不超过.22秒玩家也死亡，kernel clock冻结，之后
死亡末帧已经到达，MaterialHit却永久true，wholebody corpse始终暖色。

推理与范围：这不是缺少Death图本身。v001的Death行仍关闭，所以不阻挡目前16图
partial试装；但一旦合法登记Death源，同一可执行renderer会暴露问题。Root已要求
本轮预先修复，避免后续接入继承错误。普通活体暂停仍应冻结其native材质/动作，不应
把所有材质计时改成wall clock。

最小修复：只在Dead已有Age归一后，Age>=.22清MaterialHit和MaterialEventId。
真实致死正HP损失Damaged与Died同AtTime，因此使用同一死亡display age即可结束该
有限tint。修复不改变事件、kernel、NativeDeadline、位移、音频或恢复格式。新增2行
含注释，反向删除严格还原原5723-byte header；before/after SHA见独立freeze。

第四组 `TerminalDeathMaterialClockReview` 使用真实kernel：Wake到.5→实际1HP普通伤，
先证实活体传入late terminal age仍是Wake3、同native material、同Time/Event；再实际
184HP致死，同boundary保持真实死亡历史；.219仍暖/.22端点过期/.8与2秒保持Death5；
真实Kernel Restore同事件、同Time且无新伤害。未修改FState或mock profile。未修版
应在.22的首个新断言一次失败并return；Root必须实际记录RED，之后才准入修复。
该测试验证selector API及native死亡历史，不代替GameMode/Canvas/RootV2实际录像。

## 已核对的路径与边界

| 项目 | 源码事实与判断 |
|---|---|
| Wake与动作时钟 | Pose:59–70读真实WakeStartedAt/WakeEnd与Action.Start/ActiveAt，不设私有deadline。Guard.cpp:531–533与TryStartAttack建立这些字段。Active/Recovery按真实ActiveAt/ActiveEnd/RecoveryEnd选择；不延长伤害窗口 |
| Movement尾事件 | Guard.cpp:642先Advance(End)再Emit Movement，因此AtTime是接受完成边界，EndTime也是该End。MoveIdle受阻/进入范围可随后Advance(To)，此时末次移动早于最终Time；Pose:90正确回Ready。零距离Movement不更新positive LastMove；blocked时间推进后旧positive AtTime不等于新Time。累计仅真实Movement XY长度，暂停/无移动不添distance |
| 中断恢复 | Pose:53–56先Stunned，:72–76仅真stun结束且original OccupiedUntil未到/未Completed时InterruptedRecovery。原kernel Pump:540–564保留原deadline，若原deadline先到仍在stun，结束后不会补伪recovery；无新增Active |
| 死亡与恢复 | Pose:46–51认唯一真实Died。正常player活着时GameMode:2018–2022仍推进dead Guard kernel；global game-over才使用terminal age。Fighter Restore:501–504恢复完整Guard及feedback尾；:549恢复AnimationTime，:561恢复LastGuardSyncTime，不由selector重置死亡。第四测试另覆盖真实Kernel Restore，真实RootV2 terminal恢复仍须运行证明 |
| 纹理门 | Profile:26–39必须SourcePoseApproved、Root TrialAllowed/非空记录、真实注册数量/尺度/512square/源pin。Presentation:13无flag不加载；:15–23仅打开行preload；:51–59整行资源/尺寸先验通过，实际当前纹理path一致才画。缺图、未登记或错误尺寸保留明确MissingReason并走程序化003。Source pin字符串不等于UAsset来源验证，Root导入须独立核 |
| SourcePivot/镜像 | Plan:55以512-Px对应负UV；Presentation:62–63先扣镜像pivot×同一row scale，再Screen/UIScale；:89–90 UV反向一次。对源连续坐标x，left的位移=(Px-x)×scale，正好是right相反；不额外翻转一次或互换近远角色 |
| whole axe单层 | Plan:56仅1个wholebody source，Presentation:48要求1层；:89只有一次DrawTexture，:95仅已有finite feedback，:96 return。HUD narrowpatch在旧DrawGuardFeedback/程序化body之前接入；成功时旧斧头和body均被跳过，失败才只走原程序化路径 |
| body大小 | Data各行实际固定100.8/415、100.8/398、100.8/273，对应注册evidence所述身体crown/nearsole，不用抬斧alpha最高点。整行同scale，真实每帧pivot是鞋支撑提案；不是骨骼COM或双脚锁证明。数值/来源相符不证明Ready→Windup真实head比例无跳变，Root录屏仍须看 |
| UE编译边界 | 新DrawState在HUD.generated.h前；member方法可访问私有Frames/FActorQuad；Profile inline定义与Data include顺序闭合，Stage0无需ClipName。标准UE/stdlib调用与现HUD用法一致。未看到静态明确编译阻断，只有Root UBT结果能确认编译 |

## 原三组测试是否有意义

三组Stage0/production测试字节相同，都是实际Guard kernel生产合法事件后调用待实现
Select：真实Wake0、实际128world六相移动、实际85 poise break Stunned0。空selector
使各组首见证语义失败，不依赖Canvas、纹理导入或手造State；合法前置在实际Guard
definition与动作范围内。production增加实际active/recovery边界、无距blocked、同事件
death restore、原occupied结束以及静态实际profile/pivot/单层/gap政策，所以并非只测
常量占位。它们覆盖selector/presentation policy，不验证真正DrawTexture、纹理实载、
asset bytes或可见fit；HANDOFF已经明确此边界。

v001中Move明确缺源，第三组测试断言它仍是Move gap。这在本partial合同内成立，
不把缺行报成bug。后续v2实际登记Move或扩展Follow数量时必须在NEW测试候选更新
这些范围断言；原v001 freeze及54-count历史合同保留，不将旧断言当永久产品规格。

## Root接入顺序与证据

1. 原v001 Stage0三RED证据由Root保留。先准入**未修**v001 production和本目录独立
   第四测试，期待原3成功/新1失败；记录实际3GREEN/1RED，不能跳过。
2. 只准入`production-repair-v002/DungeonFairytaleGuardPose.h`，或同目录722-byte窄patch。
   before是v001 production header；不能对Stage0空header直接套这个patch。
3. Root实际4组GREEN/full180后，再独立登记源/导入/开partial TrialAllowed；Death行
   本轮仍是未登记gap，测试不偷开放它。
4. 真实镜像、切阶段大小、wholebody/telegraph/feedback、texture loaded path、终端恢复
   以及活体暂停的最终证明仍来自运行游戏，不能靠本只读报告宣称通过。

本次只读核验实际执行了原candidate verifier（Source/art/freeze pins与相同三tests）
exit0，及HUD窄patch `git apply -p0 --check --ignore-space-change` exit0。没有执行
standalone exe、UE/UBT或新增测试；没有View新媒体。所有输入pins及其核验范围另见
`review-input-pins-v001.json`，原candidate与本审查目录分别冻结，不互相覆盖。
