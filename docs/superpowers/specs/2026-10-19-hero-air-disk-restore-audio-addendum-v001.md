# v144 target audio policy addendum

补充边界（源码核实）：玩家Walk/StartJump/自然落地当前没有专属声音事件；source E成功提交有CLOTH声，target安装清空Records并恢复游标，不会重播旧E/出手。target因此可能合法全零PCM，也可能有未来自然敌人声音。Root批准NEW target wrapper复用冻结audio checker已有 require_non_silent=False 参数，capture receipt/设备/绑定/volume/完整WAV-PCM/时序/时长门保持原值；source仍原audit非零。缺文件、零时长、错绑定／时序继续拒绝，不加测试音或伪事件。最终音频审计报告pin另附。
