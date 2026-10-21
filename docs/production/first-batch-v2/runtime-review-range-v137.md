# v137：默认范围线清理、装备动作源继续推进

事实：UE5.5.4 实际构建 `build-editor-20261018-165839.log` 成功，完整注册187项在 `FirstRoom-20261018-170150/index.json` 严格通过。Source246／Production1286，快照 `v137-range187G` 包含2186份输入；最终4372次live文件核对、1102次快照副本核对，差异0。其余242份Source与v136相同。新版手动入口使用v008，显式转发当前Root checkpoint，实际ValidateOnly通过。

四份Source修改只涉及Guard范围线显示开关与只读计数。默认不提交范围线；显式 `-DungeonCombatRangeDebug` 才显示；`-DungeonCombatRangeProof` 仅输出本轮核验日志。原攻击几何、HP、碰撞、时间窗、输入、受击和装备逻辑保持原字节或调用参数。传统HUD隐藏、小比例保持。六个调用点涵盖Full/Partial/procedural的斧击与跺击，本轮实际原生正反对照是斧击；不宣称已完成跺击美术或声音验收。

| 原生样本 | PID／实际帧／HUD日志 | AttackId1蓄力／Active | 范围线 |
| --- | --- | --- | --- |
| 默认左侧 | 9892／359／385 | 30／6 | 全部enabled0、lines0 |
| 默认右侧 | 43368／388／414 | 30／6 | 全部enabled0、lines0 |
| 显式调试左侧 | 57928／359／377 | 30／6 | 蓄力和Active实际各4线 |

三次均由守卫正常重斧触发主角真实受击，HP loss21.052627563476562，Hurt四相／12次draw、Ready2、Walk4和约38.16实际移动通过。沿用原官方HP／时钟／固定光学／quad／PNG CRC FIFO断言，没有调阈值。场景前置Knight/Bat清理使用已有诊断设置，主角和Guard没有公开注入伤害；不能把该片段称为全程正常J清场。

独立工具对三份archive只读重跑，结果逐字段等于原receipt，原件前后SHA无变化。Root实际审过三样本蓄力/Active各一张，共六张原幅图：两侧默认无黄色矩形，调试样本可见黄色矩形。两侧完整静音录像已在本地播放器到达结尾，error=null／loop=false，时长11.937741和12.902032秒；终局截图已审。

- [左右默认独立核验](../../../source-assets/production/fairytale-guard-v001/combat-range-debug-runtime-review-v001/default-two-side-review-freeze-v001.json)
- [调试对照独立核验](../../../source-assets/production/fairytale-guard-v001/combat-range-debug-runtime-debug-review-v001/debug-and-six-samples-review-freeze-v001.json)
- [最终输入及视审记录](evidence/combat-range-cleanup-v001/root-checkpoint-v137-v001/current-inputs-and-visible-review-v001.json)
- [当前试玩](../../../钟盔轻甲受击试玩.cmd)
- [右侧原生实录](../../../过程图稿与视频/2026-10-18_钟盔范围线关闭右侧实录_v001/hero-Hurt4-native-DIAGNOSTIC-silent-v001.mp4)

推理：这组对照能支持“默认关闭Guard范围线且显式调试仍有效”，同时确认此次显示修改未破坏原受击回接。它不支持所有攻击动作、无跳变、自然握柄、足锁、音效或完整装备单元已经通过。

装备源方面新增内置请求234–239：闪避Chest／Near／Far各四相，死亡各五相，共27个组件姿态。六条均已按官方提取、compose、curated、preview、inspect处理，保持单行共享缩放，原motion warnings保留。Chest/Near最低512；Far仍使用同一Far187微小薄片的历史256门，生成239前已锁定修正依据（原Far187非零alpha367、core275、bbox20×28），没有放大或厚化凑512。未导入新增Production。

风险及下一步：闪避234完整试拼中的灰横带源于错误的灰领前景归属，已拒绝；恢复原helmet-only并做有限整数平移后，phase1/2腋孔和腰扣仍无法同时配准，最大误差下界约18.25／19.78 source像素，故当前Chest234不准入。下一步只纠正胸衣几何，复用身体218、肩甲235/236和军剑。死亡220晚3/4的铜盔／棕手像素语义分区在独立修正，精确重组成立仍不能替代实际遮挡审查；五相完整轻甲试装与原生导入验收随后推进。

本检查点图像请求239，窗口10用23余1，累计263（另有最初3张）；外部API0，内置费用未知。请求234在实际调用后才补记reservation，真实调用仅一次；时间差已单独如实记录于 `generation-control-v001/native234-late-accounting-audit-v001.json`，其后均先记reservation再调用。自动授权EV040/041持续有效。

新媒体均先F保存原件/展示副本/来源索引，再E两次size/SHA核对后View；E469–E497，三原生archive为E479/E481/E486无损ZIP，F原件不动，E根README不改。留档不表示接受。

正式完整仍0/15，完整装备搭配0/20，目标active。军剑/轻甲最终握柄、扣位、动作衔接、闪避/死亡全状态，Guard Move／跺击、美术反馈与声音，以及其余首批内容继续推进。

后续补记：纠错胸衣240已真实生成（fde13431…efc9cd）并按原512/128×100门完成五步共享提取；新sourcefit继续审，不因提取通过而准入。累计请求240／窗口10用24余0／累计264，自动后续批次授权仍有效，本轮未另开新批次。E498死亡五相完整源试拼、E499/500/501纠错胸衣输入/原件/提取已双SHA保全。Root已审死亡full5和late2–4单幅、v004盔/近手边界；近臂中旧腰带/灰背误归和落剑与掌投影重叠仍在NEW候选内修正，不改旧原件。

最终源准备补记：Root实际审过E502的240完整四相及best整数控制，低姿态仍有21.19／16.42 source像素同时配准残差，240未准入。改为对原240作一次局部EDIT241，按实际裁切/rounded resize逆变换提供原图孔位目标，固定腰扣；原件d6bd73b0…03d8f78已E507保全，实际保护区与配准复核继续，不将“编辑”字样当作像素保持成功。窗口10实际24原件双SHA封存，依据EV040/041持续自动授权开window11；当前请求241，用1余23、累计265，本轮共8次内置调用。

死亡候选采用唯一v005自身分区＋覆盖控制v003的15甲＋clear-releasev002，Root已审E503–E505的full5及2/3/4前后控制，允许有限原生准备。40源manifest/五相九槽/41原子预加载/白材质/terminal age合同已冻结为 `Death40-native-ready-author-candidate-v002`（5f6506b6…4ef788c），[Root有限源审查记录](../../../source-assets/production/fairytale-hero-state-gap-v001/Root-Death40-source-review-native-preparation-v001.json)。未导入、未运行Death5。另实际查明当前Fairytale dead分支仍裸Ready0、而terminal clock已有；[接入计划](../../superpowers/plans/2026-10-18-hero-Death40-native-integration.md)以真实HP0、优先级、时钟停止/展示继续及装备完整性为语义验证重点，不改变库存/真实掉落。正式0/15和0/20保持。
