# 石像骑士真实事件反馈接入

状态：真实journal接线已通过UE20/20；FirstUnit16流程检查通过，Root14原帧审阅整体NEEDS_WORK。纯journal真实RED→GREEN25/0。没有生成新图像或调用外部API。

DungeonStoneFeedback::FJournal只接收kernel实际事件，初始化实体ID与下一EventId；去重、原子拒绝非法批次、最多保留64项。恢复使用saved.NextEventId作为下限，不重播旧攻击、音效、奖励。Fighter与GameMode的真实StepTo/ApplyResolvedHit路径需要汇入同一journal，HUD仅const读取；独立kernel实际WakeStarted也已在测试中覆盖。表现不会推进HP、权威时钟、碰撞、资源或随机状态。

HUD按新EventId播放一次候选声音：苏醒→AWAKE，冲锋启动/盾击有效窗→ARMOR_SCRAPE，冲锋截停→CHARGE_BRAKE，实际掉血→既有ImpactLight，破韧/死亡→FRACTURE。声音过期.25秒不补播，新HUD不会放历史音频长串；音量.12–.25，仅该游戏进程。17原候选WAV与已导入SoundWave不改；未作听感验收，也未声称实现全游戏8声部上限。

持续地面预警只读Driver实际状态：.85秒苏醒扩散环、锁向后冲锋方向带、盾击前方提示，冲锋有效阶段尘土。一次性石屑、急停尘团、破韧与死亡碎片由真实事件记录生成，使用表现时钟收尾；不重新随机、不造伤、不延长无敌、也不把视觉边缘当成新判定范围。实际预警路径遇遮挡的可读性仍需实录审查。

近战旧扇形三角扇替为细环状轨迹；候选军剑采用当前帧实际握点和剑角，重剑宽厚暖色、枪使用窄直线穿刺轨迹。它不能修复首攻源帧偏出拳或替代其他武器正式美术；仍保留候选标签。

将执行：全量UE20测试（journal先RED，terminal专项应GREEN），最小真实事件接线，再20项GREEN；随后状态驱动单石骑遭遇原游戏混音录像、原尺寸抽帧审阅并双目录留档。编译、测试和录制三者各有边界，不将其合并称为完整内容验收。

实际验证补充：见 runtime-review-first-unit-v001.md。已记录5类PlaySound2D请求与原游戏音轨，未试听，不是最终特效/声音验收。
