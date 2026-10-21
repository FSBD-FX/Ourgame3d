# 猎弩四甲双向运行 v005：独立原帧复核

2026-10-15；审查者 ranged_review。结论：本次实际查看的 24 张唯一原生 PNG 中，换甲期间保持猎弩，未再出现 v004 已证的玩家白剑；四甲双向发射/插箭样本未见新增阻断问题。脚下多来源标签叠字仍然存在。本报告只记录所看像素及对应真实 trace，不替代完整动作、美术或听感验收。

## 事实与来源

原件目录：`F:/Ourgame/过程图稿与视频/2026-10-15_猎弩四甲双向射击装填实际换装运行_v005/原件`。父任务已完成 E 批 `2026-10-15-OurgameUE-四甲换装持弩修正29项-v035` 保全：1,854 文件、6,818,600,123 字节，两遍 SHA 零差；本审查在收到该保全通知后才打开图片，未修改归档。

已独立读取本次 index、runtime report 和独立 equipment-hold 结果。正常输入 profile 为 `xbw_four_armor_socket_normal_inputs`，29/29；8 发、补拍 global0、8 次 reload、最终 Ammo1、猎弩实例2。1,837 movie PNG 加 1 张同步预热共 1,838 张通过原生像素 CRC；唯一文件名、CREATE_NEW reservation、FIFO、队列排空和音画门通过。录制长度 31.398232300 秒，音频与 wall 差 0.004434367 秒，首帧 0.013642602 秒。最大源帧间隔仍有 0.179257300 秒，这些结果不构成性能验收。

本次 index 指向 v047 Source/DLL 快照；父任务记录 1,031 文件、70,009,648 字节，build163126 exit0，严格 UE163306 为 83/83。捕获 DLL SHA256 为 `e58f26b73c5a212578f0d7fbb7fd5b520cdbd934d70e19405715db65a1c315b7`；捕获 HUD SHA256 为 `1ebc5b524cee3f9af8c70588be187369c0f945c41624c17347bd3c81076c543c`。本次没有启动 UE/UBT，也没有改 Source、Tests、脚本或既有归档。

| 已读取证据 | SHA256 |
| --- | --- |
| v005 index.json | `b1ef0f1423dd5ddfb31d68e1eaa7aa21eea294b2cc51af761601d7562021c317` |
| runtime-report.json | `140141406148dae54f4127cce94a0c68f4149d90cc3662782b8558a3e006c4e6` |
| native-frame-pixels.jsonl | `ecf2a0d0dd480331a43687272cbdc4777654bc60d01e50d199f6d6b2ccdaca8a` |
| actual-v005-GREEN.json / 原件 equipment-hold-verification.json | `3e9b2ec3db260bfc2b5bbb7a65f8effe335f8f6c2fb61219ca82657a4f4815c7` |

独立只读 equipment-hold 门检查了四次实际 .50 秒事务的全部 115 条 active trace 行：29/29/29/28 条，覆盖跨度分别 .475828/.470693/.467166/.472310 秒，invalid0。该门核对实际 held XBW2、提交前旧甲身份及精确四层/六层绘制路径；这是 trace 绘制调用证据，不能代替 PNG 像素。本次 8 张事务端点原帧补充了实际显示证据。原29门没有变成30门。

## 实际查看的 24 张唯一 PNG

下表所有文件均逐张调用 `tools.view_image` 实看。没有生成拼图或替换帧；未看父任务另审的中段帧 00076、00518、00962、01404。完整路径、PNG SHA、trace 零基索引、实际甲实例、HUD clock/clip/frame 和原生 capture timestamp 存于同目录证据选择文件 `docs/production/first-batch-v2/evidence/2026-10-15_xbw-four-armor-runtime-v005/independent-review-selection.json`。

| 实际甲 / 实例 | 右发射 frame2 | 左发射 frame2 | 右装填 frame2 | 左装填 frame2 |
| --- | --- | --- | --- | --- |
| LGT / 3 | MovieFrame00180.png | MovieFrame00377.png | MovieFrame00246.png | MovieFrame00444.png |
| MED / 4 | MovieFrame00623.png | MovieFrame00820.png | MovieFrame00689.png | MovieFrame00886.png |
| HVY / 5 | MovieFrame01066.png | MovieFrame01264.png | MovieFrame01133.png | MovieFrame01327.png |
| ROB / 6 | MovieFrame01508.png | MovieFrame01704.png | MovieFrame01574.png | MovieFrame01770.png |

| 换甲事务 | 提交前原帧 / 实际旧甲 | 提交后原帧 / 实际新甲 | HUD sample / 实际 deadline（秒） |
| --- | --- | --- | --- |
| LGT | MovieFrame00090.png / 无甲0 | MovieFrame00092.png / LGT3 | 1.343687 < 1.351193 < 1.383279 |
| MED | MovieFrame00532.png / LGT3 | MovieFrame00534.png / MED4 | 8.975106 < 8.987745 < 9.009157 |
| HVY | MovieFrame00976.png / MED4 | MovieFrame00978.png / HVY5 | 16.484692 < 16.500859 < 16.518039 |
| ROB | MovieFrame01417.png / HVY5 | MovieFrame01419.png / ROB6 | 24.053636 < 24.064660 < 24.091709 |

筛选先要求 trace 的实际 ArmorId/instance、HUD DrawValid、HUD/player Facing 一致、HUD 武器实例2，以及指定 clip/frame2。事务端点取各 variant 最后一条 active 行及提交后首条符合新甲与 valid draw 的行。随后按 `capture_callback_monotonic_s` 选 trace wall 绝对时刻之前最近的 native receipt；不用异步保存完成时间定位画面。候选原帧比 trace 早约 2.75–5.43 毫秒；HUD getter 与捕获回调并非 GPU 同点，所以这些是有上下文的相邻样本，不能声称精确覆盖提交那个浮点时刻。

## 像素观察与判断

核心16帧中，左右弩身、弓臂、托持手和操作手均可辨。发射样本为前伸持弩，装填样本弩身降低并改变两手关系，轮廓没有缺块、重复镜像或玩家剑残留。两侧 QA 靶自己的灰剑仍在，位置与玩家持械区分离，不应误记为白剑回归。角色与枪弩仍是当前较小的画面比例，插箭的细线和机件状态不适合仅凭这16张帧作完整机械可读性认证。

四甲在所查双向发射/插箭帧保留各自局部轮廓：LGT 为棕色短衣，MED 有腿部银色镶边，HVY 下半身银色板片更明显，ROB 为灰白长下摆。盔、上臂和通用金棕身体部分仍明显共用；不由这些局部差异推出四甲全覆盖、法袍完整袖口或最终衣装通过。

事务8帧均仍握弩，没有 v004 的通用白剑。00090/00092 的无甲与轻甲外观差别较弱，但穿戴中/完成的 UI 和真实实例分别为0/3；不能把这对像素单独当成强烈换装造型差异。00532/00534 从棕短衣到中甲腿部镶边，00976/00978 从中甲到重甲银色板片，01417/01419 从重甲到法袍长摆，显示与提交前旧甲、提交后新甲相符。提交前4帧仍有“穿戴”进度及旧身上防具卡，提交后为新防具卡；弩没有随旧甲替换消失。

这些观察连同115条实际绘制 trace 支持本次狭义结论：已证的换甲白剑缺陷在 v005 所查事务与样本中消失，旧 held 甲保持到提交前、提交后按新甲绘制。换甲期间显示的是既有 Ready 持握姿势，身体没有新的穿甲操作；这是持械连续性修复，不能称新增穿戴动画或完整动作流畅性验收。v004 原失败和原审查仍有效，不回填为通过。

## 仍存在的缺口与风险

- **既有 P2：多装备地面标签叠字。** 在 00623、00976、01770 等原帧，脚下数个装备名重合，地面文字难读；右侧当前选中/身上对照卡仍清楚。该 QA 将多来源和旧甲落物放在同一近点，未验证正常布局下的密集物品选择体验。本轮没有修复或隐藏此问题。
- 大圆盔与小身体、细弩机件的比例仍需用户实际游玩审美判断。当前片段有大片暗雾留白与原型绿靶，并非正式敌人/完整场景美术。
- 只实看 frame2 与8张端点，没有重看全部 ready6/primary6/reload4 像素、四甲移动/空中/技能、脚锁、身体遮挡的完整连续运动。程序 mask 和83个自动化组通过不等于这些视觉范围通过。
- 本审查没有试听；音频信号、时长与双流解码门通过不能称听感/混音通过。combat65高度、420射程与真实伤害由已有 Actor 证据承担，不从这24张图反推。D13、正式掉落、15个正式单元完成状态均不在本次结论内。

下一步保留这次持械修复的实际通过证据；密集标签和造型比例继续作为独立可玩性/美术问题处理，不扩写本29正常输入样例的验收范围。
