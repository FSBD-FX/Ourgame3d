# 三近战既有声音逐动作日志候选 v001

状态：未应用。只新增本候选目录；测试尚未编译/实跑，不能称RED/GREEN或发声已验。依据当前实际源码的逐文件SHA见[baseline-v001.json](baseline-v001.json)。Root正改HUD/绑定，未来准入须按小hunk重定位，不能整份覆盖HUD/GameMode或撤回并行修改。Root先复制新测试、统一UE实际RED并保存来源，之后才准入生产patch。

## 合同与最小范围

沿用现有FDungeonActionAudioRecord/State/播放请求DTO和AppendActionAudio合同，不改Schema、WA/Combat内核、RNG、模拟时钟、库存或旧五cue语义。只迁移**真实Bound玩家**已有声音；原unbound原型路径保持直接播放，敌人/Bat domain后续独立处理，不捏造库存身份。

| 来源 | Cue与原声音 | 实际日志字段 |
| --- | --- | --- |
| Combat ActiveWindow | SWD_WHOOSH_01..03、GSW_WHOOSH_01..03、SPR_THRUST_01..03 | AtTime=Event.AtTime；ActionId=Event.AttackId；InstanceId=Event.Action.WeaponInstanceId；OwnerId=真实Run owner；Revision=当前真实装备view.Revision；OperationId=0 |
| Bound WA独立WindowCreated | 按原逻辑各族03；SPR三个subhit分别沿用SPR_THRUST_03 | AtTime=真实E.AtTime；ActionId/InstanceId=真实WA事件；OwnerId=实际Fighter稳定ID；Revision=已同步真实view.Revision；OperationId=0 |

RunGuid/Room/全局Sequence仍由原AppendActionAudio填写。不得把EventId/SubhitId塞入OperationId，也不加假schema字段。现Schema没有独立domain/EventId/SubhitId：日志必须以Run+Room+Owner+Cue+ActionId+InstanceId+AtTime结合真实IssuedWindows/WA.Issued/world WindowCreated关联；ActionId单独可能在Combat与WA各自计数器重合，不能冒称全局唯一。真实同一角色动作互斥、SPR各subhit时间不同，当前小切片可合法区分，长期全域domain扩展不是本候选。

原九个v001 WAV/SoundWave均已存在，逐源hash和正确包路径见baseline。Primary按现Stage+1选音，技能仍共用原03，没有发明新skill音资产。音量继续.25、pitch1；声音差异/技能专用设计及最终听感尚未验收。原XBW draw/insert/complete及cloth/metal使用原v002路径、gain、取消/提交/seed语义。

最小生产hunk（随后单独给未应用patch）：

1. Fighter AdvanceContentActionTo.ActiveWindow：Bound分支用现friend权限调用Game.AppendActionAudio，删除该Bound路径的旧直播放；unbound else保留原加载/PlaySound2D。音频在同一个原始ActiveWindow点，不改ResolveAttack顺序或伤害。
2. WorldProjectiles.ConsumeBoundWeaponEvents：只在现有去重接纳的新melee WindowCreated分支AppendActionAudio，移除这里原PlaySound2D。既有IssuedKeys/LastEventId保证同源不重复；不增加kernel状态/保存版本。Unbound GameMode.ConsumeWeaponSkillEvents旧路径不迁移。
3. HUD：九音既有预加载处同时登记到ActionAudioSounds；UpdateActionAudioFeedback对这九个cue保持原.25，旧五音继续原分支。消费仍用原sequence/Run/room/.25 age/attachment seed，不增加第二个消费者。只提供具体hunk，绝不回写整份HUD。

## 新真实Actor测试候选（3组）

文件：[DungeonMeleeAudioJournalIntegrationTests.cpp](Tests/DungeonMeleeAudioJournalIntegrationTests.cpp)。准入后放Source/CodexDungeon/Tests以使现relative includes正确。使用真实World/physics/GameMode/registered localController/HUD；World禁音只验证真实请求，不证明声卡/混音。真实Enter开始、唯一QA地面来源、正常E及.35提交；不使用SelectEquipmentSource，不直接写Weapon/Ammo/Focus/库存/clock，不调用AppendActionAudio，不伪造Sound/日志。

- NormalPrimaryThreeFamiliesEachStageOnce：三族各独立正常J三段。前一representable绝对点无声，精确ActiveStart有唯一真实IssuedWindow，日志与请求各1；核Run/Room/Owner/实际武器实例/Revision/Sequence/原SoundWave path/.25 gain。重复8次同点Tick/HUD不重播、不改资源/RNG/ID。整链最终各3条。
- NormalSkillsRealIndependentSubhitsOnce：三族正常K，真实定义1/1/3子窗口；逐个前一点/端点核真实WA.Issued及world WindowCreated=1，再核各实际AtTime日志/请求=1；SPR三条保留各自SubhitId的源验证，不合并成一次声音。完成后计数与定义一致。
- RealPreActivePoiseCancelIsSilentThenFreshPrimaryOnce：真实J后在ActiveStart前一可表示点调用公共ApplyCombatHit产生实际HP损失/破韧，确认旧窗口未发声；正常恢复后freshJ新AttackId仅发1次。此例是前点取消，不冒称同点due-damage、死亡、存档重建或关卡切换已覆盖。

当前baseline没有这些近战日志，预期在真实起攻/真实窗口前提通过后，正向“一条fact/一条request”处语义失败；若先停在初始化、输入、装备、时钟或源窗口，必须判夹具/编译问题而非生产RED并保留。实际组数由Root根据届时全套注册数更新，不能凭本候选假报全套通过。

旧ActionAudioIntegration的7组及其五cue边界/取消/Q/四甲/R/重建HUD/同点Shield对照保持不动。Root统一跑全部回归；实际原生WAV后再做逐声模板/试听，测试receipt不等于声音最终完成。

## Rebase与限制

baseline整文件SHA用于来源定位，patch只采用稳定局部上下文。若Root更改同一预加载/volume/ActiveWindow或WindowCreated，应将新九cue与当前绑定合并，不能恢复baseline整文件。先独立检查当前API/字段是否还匹配；候选测试本轮只做静态对照，未UBT。源版本/旧失败证据不能被候选覆盖。本工作不改Bat、不增加新声音、不将完整首批0/15状态提升。
