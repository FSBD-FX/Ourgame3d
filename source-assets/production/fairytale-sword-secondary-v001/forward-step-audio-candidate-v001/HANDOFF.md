# 军剑 K 成功进身脚声候选 v001

仅候选，未准入/UE编译/运行/试听。实际 Source/Content/tools/E/status/ledger 改动0，媒体/API调用0。Before五份本地快照逐字节匹配 CM e08bf832e82c6af093650b7ebde3fa4fc25b59aa47bfe465bb239f7308292564；Root实际 Source303/Production1439未由本任务修改。

实际差异只有三个已有源文件、六个精确接点：

- `DungeonWorldProjectiles.cpp`：保持原 EventId 去重、sweep、BatchSkillStepDelta、SetActorLocation/Sync全部原字节。只在sweep前读真实Before，在原提交后读真实After。限定实际player/owner、bound有效Run/Room/Revision、weapon world/journal同scope、真实当前状态时间和batch事件时间、grounded/运行可用；pure helper再核当前/冻结SWD Skill相同真实ActionId与InstanceId、已锁定/实际ForwardStep标志、非中断及有限source时间/位置。实际位移大于0.0001cm才写现有 `AppendActionAudio(HERO_STEP_LIGHT_01)`；请求30cm不是判断依据。无再次移动、BatchDelta累计、直接Play、普通40cm cadence或新时钟。
- `DungeonActionAudioFeedback.h`：原journal record尾加可选 `ForwardStep` DTO，Present默认false、向量明确初始化0；成功append后只给这一新sequence附真实EventId/SubhitId、RequestedSignedDistance、Before/After/CommittedDelta。完整source key由父record的Run/Room/Owner/Action/Instance和DTO EventId/Subhit组成。既有AppendActionAudio签名/逻辑、kernel/EventId、保存Schema不变。
- `DungeonHUD.cpp`：只在原家族音源预载后新增现有 `/Game/Production/HeroLocomotion/v001/Audio/SW_AUD_HERO_STEP_LIGHT_01_v001.SW_AUD_HERO_STEP_LIGHT_01_v001` 映射/强引用，并将此cue gain归为.25，pitch仍1。缺音源继续原有静默消费、不重放。复用既有SoundWave，无新资源或转换/导入。

最终Projected pins见 exact-seams.json：header3108B/a2e121c0a60474919989c75c78c5a64fb0d247b1e4dd764923251c1fed88c9f5；WorldProjectiles27829B/1c94c6fd233bd4dd2bd239623b098a49ffa4e72d6c606f01e5e2d4aa58158310；HUD124031B/72f91ee3c142892a655677ba2ae079475f5d14787609ca3f6949065b77b46b15。

测试：先以“未实现/静默”的最小stub跑16项，RED仅部分/完整正位移2项预期失败；实现后16/0，再补真实左朝向kernel事件为最终17/0。MSVC C++17 /W4 /WX，真实旧weapon kernel和新eligibility生产helper、CoreMinimal host类型shim；覆盖0/partial/full/left/wrongowner/wrongscope-groundedflag/staleAction/Instance/真实pre-active取消/真实post-emission中断/真实空中拒绝/非finite/future/stale事件/错误eventsource。它们不运行UE world碰撞、真实HUD、声音设备或native mix。一次structural脚本开发调用因Windows默认GBK读取含中文HUD失败；改为显式UTF8后通过，投影实现未因该错误改变。最终 `check-candidate.py --against-current` PASS：六接点正反向还原全部原字节，原位置提交仅一次，postcommit后才判断/append，无新移动/cadence调用。

与 runtime-plan-candidate-v001 worker已确认HUD接点互斥。本候选基于原CM HUD，Root应组合两组exact insertions，不能用任一单独projected HUD覆盖另一候选。只准入三个projected源变更；before/host shim/tests脚本不进实际Source。Root编译/full203及新native仍待后续统一执行。

关键读回边界：本脚声在现有 `GetActionAudioState()`/`GetActionAudioPlayReceipts()`，不进入 `GetHeroLocomotionAudioPlayRequestsV001()` 六cue ring，不改变普通StepOrdinal。K native observer需只读序列化DTO Present/sourceKey/requested/committed以及实际request首见墙钟窗口；同名普通走路音不能当K前踏来源。可选DTO其他cue保持Present=false，不把默认0解释为真实事件。请求不等于实际发声；完整原生PCM、当前runtime资产/codec lineage、正常输入、source/readback和因果匹配、听感/延迟均须新运行证明。

冻结只pin本地before/projected/测试证据、稳定CM文件本身、旧音源冻结和只读研究报告，不pin未来会变的actual Source/DLL/last-build。准入前可用 `python check-candidate.py --against-current`；准入后省略该选项验证本地冻结，不把actual工程变化当候选自失效。
