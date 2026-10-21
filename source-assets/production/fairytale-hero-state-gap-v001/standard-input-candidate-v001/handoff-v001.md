# 新钟盔身体三状态：标准输入候选

事实：本包只含文本、JSON 和候选脚本。没有生成/查看图片，没有 UE/UBT、Source、
工具或 ledger 修改。原审计冻结不动。本包不是美术验收，也没有可导入新纹理。

唯一身份锚是当前实装 `fairytale-sword-v001/run-ready-v002/curated/frame-0.png`，
121133 B、SHA256 `d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5`。
实际解码 RGBA 512×512；源版本、实际像素 SHA、导入 manifest 和生成158血缘均有 pins。
采用 Root 本任务明确认可的这一张 Ready 作为唯一 nativeRight 方向身份。旧 canonical131
原始图只记血缘，不再次附给动作模型；旧 v006 的18张 Dodge/Hurt/Death只记时序来源。

| 行 | 标准输入 | 实际时序边界 |
|---|---|---|
| Dodge | 4个真正姿态、10fps、非循环 | 接受动作到原 Start+.40；.06含到.20不含仅直接接触保护；无障碍462.5 world/s、185 world。受阻保持实际 Travelled，原 End 不变 |
| Hurt | 4个真正姿态、10fps、非循环 | 真非致死玩家 poise-break 设置 .40 Hurt；一般HP损失只有 .22 HitFlash，非致死DoT不创建Hurt/poise/push |
| Death | 5个真正姿态、5fps、非循环 | 倒地关键位0/.2/.4/.6/.8；从.8保持最后尸体，直到真实状态改变。**.8是本轮美术方案，没有gameplay死亡deadline** |

Death 采 `bDead` 与真实 `AnimationTime`；game-over冻结 SimulationTime 后仍由
`AdvanceTerminalPresentation`推进。不能把死亡图又按冻结主时钟采回站立图。死亡阻止
新攻击/动作及live body admission，这不等于本候选关掉Actor碰撞体，也不添掉装备逻辑。
`timing-contract-v001.py` 是可执行采样提案，只读取实际观察事实，不替代kernel。
Dodge保护判断使用源码相同的绝对 Start+边界，避免先相减在长时钟边界改变结果。

`sprite-request.json` 是帧数/fps/loop的数值来源；三个 `prompts/*.txt` 由实际安装
sprite-gen 1.59.0 的 `row_prompt` 生成。没有另写 `durations_ms`：该版本 prepare
会丢弃此键，compose也不会按该键采样。Death标准预览的五帧总长1秒，最后帧从.8起；
真实运行合同应保持它，不能在1秒循环或消失。

`references/layout-guides/*.guide.json` 是精确的标准guide配方：512高、4/4/5等宽格、
48安全边界，每格有动作语义，**无伪造骨架/脚点/握点**。为遵守本轮只写候选、不生成
新图的范围，标准PNG尚未生成。Root可在sprite-gen venv运行下面命令，默认只读核验：

```powershell
& 'C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001/standard-input-candidate-v001/prepare-layouts-root-only-v001.py'
```

Root准备新F批次时加 `--write-guides --out-dir 'F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001/standard-input-candidate-v001/process-batches/2026-10-18-right-body-states-v001'`。
该候选仅调用实际 `draw_guide`，不生成AI素材、不合成新idle、不重写身份、不执行UE。
新guide必须先由Root按E目录README保留 originals/presentation/index，之后才能View或附作生成参考。
生成时每行只附唯一Ready锚和该行guide，使用对应生成的标准prompt。

裸灰/炭灰衣身体必须真正屈伸/反应/倒地；不烘焙军剑、甲、盾、法杖等。近远两臂连续且
分离，手指/拇指真实随腕姿态变化，不把旧握点坐标搬给新空握。Root256,464只记为
当前display pivot。每帧实际floor、身体支撑、Root/Crown、Grip/Axis和hand replay mask
均为null，待真实源像素和测量后填写。倒地bbox变矮不能逐帧放大来“恢复72”。
现有标准非pixel extractor自身按帧fit，`shared_row_scale=true`并非该SDK的执行开关；
后续必须用已pin的项目 `extract-sprite-shared-row-scale.py`，其实际manifest记录单行
共同ratio和 `per_frame_scale_normalization=false`。三行之间还需按真实helmet/肢体比例
与身份锚校准，不能把各行maxbbox归一化结果直接当相同角色尺度。缺帧、黏连、裁切
或scale不合格时重生成，不用slot fallback、局部手绘或Ready复制冒充完成。

先生成同一个nativeRight视角。后续left沿当前运行方式将身体、Root/Grip/Axis、
mask、武器和甲整体镜像**一次**；近远解剖角色不换名。左右仍须实际复核。Dodge本身
允许朝向相反的后撤及深度/斜向移动，不改变Facing；目前真实Shift诊断会向Facing反向
移动，新row只能作为紧凑防御滑步候选，不能提前宣称所有向量无滑步或脚锁通过。

模块适配先限定SWD+None/LGT。身体共用不等于20套装备都可用：20格是5武器×4甲，
None在20格外，目前全状态美术0/20。GSW/SPR/XBW/STF握持、双手、装填/技能轮廓，
MED/HVY硬甲和ROB袖摆都仍需真实源及姿态遮挡数据；不能伸缩LGT或删除Binding白名单。
三状态即使生成成功也未覆盖空中、技能、Q和拾取手势。

可执行下一步：Root核对pins→生成标准guide并E保全→按唯一锚生成三行→保留raw→
标准component extraction/shared ratio→实际支撑/握点/遮挡测量→E保全后审图→最小真实
Shift/poise-break/death回归RED→Source实现→运行图与存续检查。Source补丁、导入路径、
runtime profile和美术接受均不在此文本包中预填。
