# 灰翼石蝠 source 候选 v002

2026-10-15，Asia/Shanghai。单一写者 `/root/assets_prepare`，仅内置 imagegen；外部 API 0，内置费用未知。本代理未启动 UE/UBT、未改 Actor/HUD/物理尺寸。

事实：`manifests/import-stone-bat-subset-v002.json` SHA `de293cd758a6112e7f3d26e15821ebbb308d203c980b07a7107780254e09cf45` 引用实际 **27 独特 512 RGBA PNG**，相对 v001 新增16；35逻辑播放位置中共享均显式alias。9语义状态为休眠、苏醒、悬飞、啄击、横拍、低位恢复、升高、破韧受击、死亡；低位另分横拍上下文，共10clip键。它们是待运行审阅的source候选，不能算完整敌人/正式画风/连续动作通过。

| 源 | 实际选取 | 边界 |
| --- | --- | --- |
| 94 hover | 0/1/3/4/5，共5PNG | source2翼尖仅2px边距，保留但不导入；5姿势循环仍粗 |
| 96 peck | 6PNG | 真收翼/前啄/低伏；逐帧胸部origin需用v002修订 |
| 97 dormant | 1PNG | 与wake首姿势真实共享，不算两个独特文件 |
| 98 quarter wake | 1PNG | wake4仅此与97两新图，加2张已有hover，非原生连续4采样 |
| 99 wing | 6PNG | 真前翼横拍；active2胸部叉被翼遮，origin±12px；低位腿爪较基准下垂更长，比例待审 |
| 100 hurt | 4PNG | 只给真实0.40s破韧；普通掉HP不强播，仍保低位义务 |
| 101 death | 0/3/4/5，共4PNG | 原1/2有跨格/边缘碎片，拒用且不删原；晚期头石仍有琥珀眼色，灭眼时点待审 |

推理：胸部源origin须跟同一可见金色Y叉。参考hover0叉约[248,271]，旧胸心[256,280]为其+[8,9]；v002据实际20px坐标图统一此定义，记录测量不确定性。v001的若干peck初测偏约16px，本次仅新合同修订，旧PNG/合同/SHA不改。碎裂后已无胸骨，只用估计裂散中心；不伪称骨骼标记或真实落地。

风险：source原格摆放稳定性未全部通过。metadata origin只调整贴图相对实际ActorXYZ的呈现，未逐帧缩放/重绘PNG，未改碰撞或实际Z。建议128canvas仅供root试显，不能据翼幅改变16×12cm身体/独立hurtbox。地影留groundXY，真实Z90/20、body gate40/attack gate65、.80前摇/50%锁点/.25或.20有效/1.80低位+.30升高，全读既有权威；像素不发伤害、补弹、掉落或奖励。

已实际读取27PNG的尺寸、RGBA、alpha0..255与四角透明并核SHA；F/E原件/展示副本共108份同SHA。`reviews/import-stone-bat-subset-v002-verification.json` 为源验证，不是运行录像。所有原始工具C文件、F规范源、F/E原件和展示副本保留，95整行苏醒失败也未覆盖。

右向wake/wing/hurt/death/peck五份source-origin组装页已逐份实看；v002左向诊断页最初翻整张atlas使列序反转，此显示页错误保留并另出`reviews/bat-subset-v002-preview-errata-v001.json`和逐cell镜像的v003左页。冻结单张右PNG、数组次序及“一次镜像”合同没有改变。该更正不算新图像调用。

当前唯一ledger累计101请求，window5为5/24，余19，pending0；EV038另24，不能混作本窗口。window4已真QC并冻结：144原件/工具源/四副本路径和55输入引用SHA一致；本报告不把历史导入或root测试倒填为本素材运行验收。

剩余：root按真实Bat phase导入、左右/高低/攻击/中断/死亡全状态实录；顺滑度、翼下手脚形体、sourceorigin误差、晚期灭眼及死亡停留可读性仍需真实画面判断。完整音效、真实来源/保存与首批15单元目标继续未完成。
