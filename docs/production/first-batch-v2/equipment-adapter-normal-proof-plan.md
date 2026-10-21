# 真实装备正常输入实录方案

2026-10-15，Asia/Shanghai。原29项＋新增9项Actor组先取得真实RED，再实现GREEN；本录像不能代替38项回归，也不改变原Explore26合同。

显式 `-EquipmentAdapter` 配置仅初始化IntegrationPreview与三个真实QA地面来源：GSW(-480,0)、混合词条LGT(-360,0)、SWD+1(-240,0)。这些是明确登记的开发测试对象，实际转移所有权，但不认证N03/N04掉落/商店来源。之后所有技能、拾取、换槽、确认与行走都通过PlayerController普通K/E/Q/Right/Enter/A/D边沿，不直接调用传递/确认/切换API、不写捕获快照。

录像依次验证初始SWD唯一实例与3个来源、正常K一次锁点/一次暴击游标和CD、E武器.35s完成前保旧装、Q.35s/保实例与CD、E甲.50s/最终Stats一次截HP且加上限不回血、满槽E不自动替换、Right/Enter替换备用且旧GSW完整落地、走近旧GSW再次正常拾取同实例。9个必需检查名同时冻结于C++与脚本，不接受缺项、重复或宽松计数。当前还未运行，不预报通过。

呈现使用新圆盔候选与真实装备只读HUD；当前GSW动作/地面图标/可拆甲层未完成，不能将通过规则录像标成美术完成。不得把原型axe改名为GSW，也不把全部武器改成军剑姿态。磁盘续档、非零弹药的真实射击/装填和战斗中取消由各自后续实际运行补齐。

证据沿用实际delta/t.MaxFPS30、完成预热截图后再起电影及游戏主Submix录音、原生PNG逐帧像素CRC、原始PCM保全及标准头副本、首帧/整段音画门和完整双流解码。达到失败条件保存失败实录，不覆盖旧版本或补造事件。所有媒体先保全F/E原件与展示副本，再视觉审阅；按时间索引查看进度、装备比较、左右角色与遮挡。

独立新入口：`verify-content-combat.ps1 -EquipmentAdapter -CandidateSprites -FastLosslessCapture -Version v001`。其他FirstUnit flags与此互斥；旧9/16/19/26检查和输入未改变。
