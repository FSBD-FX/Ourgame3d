# 四甲三段连招：左向原帧独立审看 v001

2026-10-15，Asia/Shanghai。审看者：ranged_review。结论限于下列16张原始静帧：未发现新增具体P1/P2；不代表完整动作、footlock、ROB袖口或听感验收，正式完整内容仍0/15。

## 原件、保全与实际查看

F批：`F:/Ourgame/过程图稿与视频/2026-10-15_四甲实际换装三段连招左右分层运行_v001`。E批：`E:/OurGame/Knight/过程图稿与视频/2026-10-15-OurgameUE-四甲真实换装三段双向连招-v017`。root先确认1276文件/4,696,906,160字节、两遍SHA零差异后，本任务才查看；本任务另确认E目录存在，没有冒充再次全量哈希4.7GB。

选择依据为 `F:/Ourgame/docs/production/first-batch-v2/evidence/2026-10-15_checkpoint-0839/armor-combo-review-selection.json`，SHA256 `2450387f9487e2a6f5a82c73e5d1ceb09a584caa46856a9a6bfdaaae5331020b`。仅取side=-1的16条，全部实际调用view_image、detail=original逐张查看1280×720原件，没有只读路径、看缩略图或生成替代图。

以下数字均为F批 `原件/MovieFrameNNNNN.png` 的电影帧号；active为pose2，recovery为pose5。

| 护甲 | P2 active / recovery | P3 active / recovery | 该四帧的可观察局部 |
| --- | --- | --- | --- |
| LGT | 00417 / 00426 | 00435 / 00445 | 棕色皮革/腰带身份一致；P2向左上出剑及举剑收势、P3向左下出剑及腰前收势可区分，近手覆盖持握处，未见多手或明显剑柄离手。 |
| MED | 00674 / 00683 | 00692 / 00702 | 链甲躯干与手臂表面可辨，HUD为巡路环甲；地面旧轻甲和比较UI未使当前角色回退轻甲。相同四姿势的剑/手遮挡仍可读。 |
| HVY | 00932 / 00941 | 00950 / 00960 | 板片躯干及腿部护片明显区别于链甲，HUD为门栓板甲；P2/P3中圆盔与肢体比例保持一致，未见组件跳成旧整身轻甲或明显画布截断。 |
| ROB | 01194 / 01203 | 01212 / 01222 | 灰色长下摆、腰带与露出的靴子保持法袍身份，HUD为灰烬法袍；上左/下左剑势与收势方向可读，握持附近未见双手重复。袖口与长袖完成度本次不作通过判定。 |

四甲同一姿势的共同头盔、手脚尺寸及画布位置可对照，局部没有明显二次镜像、双剑/多手、全身旧LGT泄露或裁切。所见旧护甲掉落标记和比较面板与当前穿戴身份分离，角色仍保持新甲。静帧只支持P2/P3样本间的身份连续观察，不能代替换装事务或整段运动证明；事务结论另由真实36项及trace支持。

## 已独立读取的运行事实与限制

F批 `原件/runtime-report.json` 的profile为 `armor_idle_walk_primary123_layers_normal_inputs`，passed=true、36 checks、36 declared names、无失败，SHA256 `f3b43db0eaf19eaead58769408f30f29ef3ac382a8f399157a2dfebc93f48323`。批index及native-pixel-verification原件记载：1264电影帧加预热共1265 PNG均匹配源viewport像素CRC；实际wall duration42.2628743015秒，音画时长差0.0015409682秒。此为读取验证原件，不是本任务重新录制、重跑36项或试听。

这16张静帧未覆盖六帧完整连续变化、相邻帧接缝、footlock、所有状态、20搭配、ROB长袖/袖口和声音。root审看右向24帧，本任务没有把它们计作自己看过；也没有把程序36/36写成最终视觉或听感接受。

该ArmorCombo电影属于v021，模块SHA为 `fc2d4a8e910a8dbb9208a162d01935b915d34d6ab715819b35fa6da8af825c93`；它记录的RangedProof源仍是旧f3f8ef8e。后续v022的火线门补强不倒填到此电影。

## 同轮只读核对：Ranged火线门补强

当前及v022快照 `DungeonRangedProof.inl` 均为SHA256 `d24f3a12ea692ae84ebb41f76ef4fd740b854459024dea9f1dad3965abef9b57`，State头仍 `6abc9af082bc6854ec595f11e9a0b1b5e5fcad42f2a82a8d36af7b1f7059d7ab`、20名称未改。phase15现逐一核对前两目标真实DirectHitCommitted：Magic、ActualHPLoss与Issued.Damage相符（.0002容差）、Stagger相同、各一份direct及BurnApplied；第三目标仍400HP且该action零direct。此前指出的“错误直伤仍可凭计数通过”缺口已在QA门补齐，未改生产或旧52测试。

root报告build084549 exit0，独立日志确认4action/24.61秒完成；独立读 `F:/Ourgame/UnrealGame/Saved/Automation/FirstRoom-20261015-084636/index.json` 为严格52/52、failed/notRun/inProcess/succeededWithWarnings及逐组warning/error均0，index SHA `b65ff8bdf6c278de4ca225848167a58dc2bc8716631cd2e4149c1d5bffc2fbf4`。v022清单载明625文件/53,592,583字节；当前Ranged20录像仍在执行，尚无实际结果，本报告不预标其通过。
