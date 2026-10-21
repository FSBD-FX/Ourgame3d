# 钟盔轻甲落地动作优先级 v143

沿用首批内容完整制作目标，本项补足v142已列出的落地J/Shift实景验证，不新增玩法。当前事实为Source296/Production1419/CM52f906、D3D11完整203严格通过；v003左右三跳207/183帧与正确棕皮Ready身份通过。v013仅为LIMITED_WIP试玩，原速播放与试听未完成，正式内容0/15、搭配0/20。

## 行为

分别录制左/右朝向的落地J和落地Shift，四个独立新进程场景。正常Enter、E及真实0.50秒换装完成回调后，正常Space起跳；完成四个空中物理姿态后，第一次真实Land4回调H=V=0、age[0,.06)时，在后继Tick发正常J或Shift。InputKey按排队语义记录，不要求即刻出现动作。

动作实际StartTime必须仍在原landing[0,.12)内。第一实际动作回调需证明J为grounded新Primary1、Shift为新Dodge action，owner/run/room/epoch/gear绑定不变；非攻击Air Query拒绝且其Out不变，实际Air部件为零。允许后继画面回调age已推进，不能冒充enqueue或action start时间。

J正常完成当前Primary1六姿态并回Ready；Shift记录既有0.40秒Dodge和真实碰撞/iframe阶段、九层/33资源并回Ready，不修改持续时间或碰撞结果。场景必须通过正常WASD选择合法闪避路径；禁止位置、HP、H/V、landing age、时间和AI写入。前置Knight仅保留明确CLI授权的既有public ApplyCombatHit诊断，不能冒正常整房通关。

## 美术与记录

实际启动必须保留EquipmentBound、LeatherReady、LeatherPrimary1/2/3、Walk/Hurt/Death/Dodge/Air以及Guard既有flag；避免重现v142灰甲参数遗漏。观察器从完成DrawHUD截图回调记录，不能用前一Tick的旧画面。

沿用原生PNG CRC/FIFO/独占文件名和真实MainSubmix录音：录制原点与末回调Stop、完整WAV/视频、资源和实际draw记录分开保留。需要记录Air、Ready、Primary1或Dodge的实际资源/层与既有源码身份；不得以静态配置替代真实绘制。新独立核验器须拒绝旧/缺失输入、跨owner/epoch、窗口外Start、Air仍绘制、错误clip/甲片及不完整输出。已通过的203测试不改。

## 执行边界

Root独占实际Source/Content/tools/E/ledger/UE。Worker仅NEW landing-priority-observer-candidate-v001中的源候选、只读整合片段、核验器和小型有意义反例；不启动UE，不生成图片，不制造Root批准。Root审阅后统一接入GameMode并排除其他proof共跑，构建并跑203，之后四场真实实录。先F原件/展示副本/索引，再E双SHA保全后View；浏览器策略拒绝不得绕过，完整实时播放/试听保持如实未完成。完整目标继续。
