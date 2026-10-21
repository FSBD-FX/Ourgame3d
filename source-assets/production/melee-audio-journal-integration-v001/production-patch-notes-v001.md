# 未应用生产patch与静态边界 v001

[production-v001.patch](production-v001.patch)只含Fighter、WorldProjectiles、HUD三个局部diff，不含整份文件。依赖SHA见[production-patch-baseline-v001.json](production-patch-baseline-v001.json)，测试/计划初版SHA另保[baseline-v001.json](baseline-v001.json)。没有写ActualSource；没有UE/UBT或实际RED/GREEN结论。

计划术语更正：plan.md中“既有IssuedKeys/LastEventId”应准确读为当前WorldProjectiles的`LastSkillEventId`门与`SameEmission`遍历真实Projectiles/Windows门（当前270–290）。patch的Append发生在这些门之后、原新WindowCreated分支内，不新增或重置任何计数器，不发明名为IssuedKeys的变量。此更正不改测试或合同。

Bound primary在原ActiveWindow点由真实Fighter friend权限调用既有Game.AppendActionAudio；旧直播放仅保留在互斥unbound else。Bound skill在原接纳的独立WindowCreated处删除PlaySound2D并Append，三次枪刺仍3条03/各AtTime。原unbound技能GameMode直播放保持，绝不将Enemy/Bat伪装成库存实例。

HUD利用原九音预加载，只增加ActionAudioSounds键；新九cue原.25gain，五旧cue原.55/.32、路径、seed/sequence/Run/room/age门不动。共同consumer仍是现HUD Tick，重建会seed尾序号不重播旧历史，`.25s`陈旧声音门同样用于新九cue；大tick跨过较早窗口时是否丢弃陈旧onset需另留实际边界证据，本候选不冒称全FPS发声保持。无HUD场景不产生该统一消费链的声音请求；Actor测试使用真实HUD。

Record Schema不变，没有独立source EventId/SubhitId/domain字段。关联键必须含Cue和AtTime，不可只按ActionId。每次真实primary ActiveWindow唯一，技能由已有事件/世界去重门保证源唯一；测试要先核这些源前提再断言audio。听感与技能独立音设计没有解决，仍使用原03素材；不新增声音资源。

所有生产hunk必须等Root实际RED保存后才准入。若并行绑定已改变同一hunk，按当前Code重定位并重新记录SHA，不能整份恢复baseline或原HUD。回归旧五cue7组、正常事件取消/资源/RNG不变，再由Root录原生混音核逐声；当前静态与request测试不是WAV/试听证据。
