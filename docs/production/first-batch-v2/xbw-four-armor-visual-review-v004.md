# 猎弩四甲双向发射/装填 v004 独立原帧审查

## 事实与来源

本审查实际用view_image逐张查看19个不同原生PNG：四甲×双向×primary frame2/reload frame2的16个组合，另加选择替换、换甲事务及最终loaded共3张。没有拼图、改Source/脚本/原归档或启动UE/UBT。F原件位于 `F:/Ourgame/过程图稿与视频/2026-10-15_猎弩四甲双向射击装填实际换装运行_v004/原件`。root提供E batch `2026-10-15-OurgameUE-四甲双向射击装填29项-v034` 保全1839files/6,770,389,176B、两遍SHA零差；本审查未重复全量保全审计。

已独立读取本批index、runtime-report与native-row：玩法29/29；1824movie+1预热共1825PNG的唯一/fullset/CRC/reservation/FIFO/drain门及音画门报告通过。reserved/enqueued/saved/completed/receipts均1824，失败/拒绝/pending均0；8shots/global0、8reload、最终Ammo1、同一XBW实例2。实际队列峰值53jobs/195,379,200B，仅BGRA拷贝积压，不是总进程RAM或性能认证。录像31.2705130秒，firstFrame .0150604秒，audio差.00415366秒，最大sourcegap .0637808秒；没有因此放宽任何原阈值。未重跑全量PNG解码/CRC或听音。

DLL `66a7460ae28e40b399cdbfef33d497f07b8ad9788a09360933f22cd88b727d3e`，root来源快照v045（960files/67,390,827B）。已独立读取strictUE161022报告83 Success、0 Fail/warnings/notRun，报告SHA `9864fd444a85bfbad792cb2ab3b5ca7b1af8e7c3ea7b3e37bd6ae061ec70df21`。这些程序证据与下面实际可见结论分开。

## 选帧与实际19文件

选帧先要求actualArmor/对应实例3、4、5、6，HUD DrawValid=true、HUD/player Facing一致、真实XBW实例2及指定clip/frame；再以native-row capture_callback_monotonic_s对captureStart+traceWall选nearest prior。16张核心候选与trace相差约2.8–5.5ms。没有使用后台保存完成时刻代替捕获时刻，也不冒称GPU/Actor/音频sample-accurate。所有候选均实际打开确认，无需替换为邻帧。

| 实际甲实例 | primary2右 / 左 | reload2右 / 左 |
|---|---|---|
| LGT3 行路短衣 | MovieFrame00179.png / MovieFrame00372.png | MovieFrame00244.png / MovieFrame00438.png |
| MED4 巡路环甲 | MovieFrame00616.png / MovieFrame00813.png | MovieFrame00682.png / MovieFrame00875.png |
| HVY5 门栓板甲 | MovieFrame01050.png / MovieFrame01247.png | MovieFrame01116.png / MovieFrame01313.png |
| ROB6 灰烛法袍 | MovieFrame01494.png / MovieFrame01691.png | MovieFrame01560.png / MovieFrame01758.png |

额外实际查看：MovieFrame00497.png（MED来源替换确认、旧LGT仍held，左ready3）；MovieFrame00942.png（HVY拾取事务中旧MED仍held）；MovieFrame01823.png（最终ROB左ready4/loaded）。root另外审右ready，不计入本19张，也不按计划次数直接相加。

完整绝对路径、真实trace索引/时戳、draw stack、每PNG SHA与actual viewed标记保存在 `evidence/2026-10-15_xbw-four-armor-runtime-v004/independent-review-selection.json`，SHA `d5fb803cb47570ae1e76330d95125b8b12e6efbb20f6f0a5eb080765680fb223`。原归档index没有修改。

## 可见结果与确定缺口

核心16张中，玩家两手与弩体均存在，前弩弓/后枪托随左右方向一致翻转，未见双重镜像、重复弩体或primary/reload中的白剑残留。primary2可见亮箭位于手持弩口前方，右/左出箭方向正确；reload2的操作手靠近弩上方、枪托向腰侧倾斜，有别于平持射击。16个样本的实际Ammo均为0；插箭姿态只证明图像呈现，不等于补弹成功。最终1823的Ammo1依据真实资源trace/receipt，不能单靠小箭像素认定。

LGT以棕色短衣轮廓为主；MED下身银亮护片/边缘比LGT明显；HVY下身银色板片面积更大；ROB有明显灰白长袍下摆。四种身份与顶栏/真实甲实例相符，左右形状连续。上身仍有较多共同金棕底衣/手臂像素，ROB袖口覆盖也未完整确认；六层draw path和这些局部差异不能替代全衣装覆盖验收。当前约110像素高的角色中，弦、细箭和手指很小；圆盔显大、衣层差别主要集中下身，仍须后续比例与识别度定稿。

**P2：换甲事务中持弩身份回退白剑。** 00942实际像素中玩家握白剑，而顶栏仍为枪机猎弩。对应trace数组zero-based941（第942条）：phase5，wall16.301958799362183、sim16.095323398709297；真实装备action active，Start15.886169899255037、Deadline16.386169899255037，旧MED实例4仍held，WA与slot武器均XBW2、Ammo1。HUD clip空/frame−1/action0/instance0、DrawValid=false、draw stack空；native捕获比该trace早.00386159867秒。trace没有AnimationName/anim字段，不能猜具体动作名。此缺口在真实换甲交易表现，不能与核心16张无剑残留的结论混淆，也不能用29通过声称换甲时XBW全状态身份已完成。root已接收问题，后续修复/新片另立版本，不回填v004。

**P2：同点QA来源地面标签叠印。** 179、616、1050、1823等原帧脚下多个名称重叠，难以读出各物件；右侧当前selected卡片仍清楚。该堆叠来自本次五来源/掉出旧甲的同点QA布局，不能将此片当正式战利品布局验收。497的“Enter替换防具/Esc取消”提示清楚，942的拾取提示清楚；但942手持白剑与真实武器不符。

## 未覆盖范围

抽帧未见明显缺头或靴底大幅离地，仍不能认证连续机械动作、后坐/装填插值、足锁、完整衣层遮挡或所有状态。脚下标签/QA标记也削弱了接地细节判断。场景雾圈内角色与靶可读，上半屏拱廊/侧边留白与大卡片仍是QA展示环境。没有审四甲walk/skill/air/受击死亡、全部20组合、正式来源/掉落、D13、听感或完整15单元；程序29及83通过不改变这些未完成范围。v001/v002短窗失败、v003同名覆盖失败均保留，未用v004替写旧结果。

归档锚点SHA：index `168749a58f6edafc4289abb9bffc68321b5bcf7739075332677a6d42d2809467`；runtime-report `7abb08861dfbbfc1081efc38d73f16d10bac4b4cff8d4b30a909f34cfcc84860`；native jsonl `cca11e3c1a290577f73a43d80d17f7317e345b2cbbb05d4c2de82f117df74b90`。
