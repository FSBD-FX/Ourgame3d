# 怪诞童话盔甲与小尺寸轮廓试样计划 v001

2026-10-16，Asia/Shanghai。依据本轮EV048「保持怪诞方向，增强盔甲和轮廓辨识」，准备下一次native146候选。本文只读源图、已有分层合同及真实六相实录，并实际查看131待机frame-0、v008步态frame-1；没有生成、导入、启动UE、修改Source/媒体/台账。奖励Stage0源码保持冻结。

## 事实、推理与本轮选择

当前公共身体是131的钟形封闭头盔、黑眼窗/琥珀眼、炭灰底衣、棕手套和靴子，双手空着；它有意不带防具或披风。125固定甲/披风旧概念不能替代这个公共身体，也不作为本轮身份参考。131四帧idle和由138/142/143/137/141/145组成的v008六相walk已有真实源文件；旧源README中的「尚未导入」不能覆盖之后batch089的实际运行事实。

[实际步态记录](F:/Ourgame/docs/production/first-batch-v2/runtime-review-fairytale-walk-lookdev-v001.md)与[独立原帧审阅](F:/Ourgame/docs/production/first-batch-v2/independent-fairytale-walk-lookdev-v001-frame-review.md)显示：1280×720/UI关闭时，主角可见高度约70.44–72像素，暖盔/眼/手靴可辨，腹部和上腿接近青灰地面明度，收腿相较容易连成暗簇。固定亮斑锚点图尚未回答暗地面读图；六相抽帧也没有验收脚锁、连续运动或四甲适配。

推理：用胸、肩、护臂、护胫的大块明暗和外轮廓提高读图，比增加内部细纹更值得先试。必须保留暗关节与原有手靴，才能读出活动身体；把四处板甲连成整块金属壳，反而容易失去肢体分离。

root本轮明确选择 **一张轻甲方向穿戴设计参考**。146只做右向空手待机的整身穿戴效果研究图，标记 assembled_fit_concept / not_runtime_component，**不绑定ARM-LGT-001或任何完整装备ID**。既有[防具设计](F:/Ourgame/docs/design/equipment-v1/03-防具.md)将LGT定义为行路短衣，而厚门栓横梁胸板、方宽肩和厚胫甲属于ARM-HVY-001；因此146采用较小胸片、短肩盖、窄护胫和大量可见底衣，不提前吞掉重甲轮廓。若以后要门栓板甲，应另做重甲版本，不能把这张轻甲加深颜色就声称两套完成。

**正式表示仍是同一公共身体加独立防具组件。** 不用146整身图覆盖131公共身体、不把头/手/靴重新画进防具层、不把合成身体复制成front/back/near。方向通过后，才为131同姿势创作真实独立甲面及必要背面/近臂；任何整身烘焙方案要另立明确合同，不能悄悄代替现有组件合同。一张146不能同时交付四甲、六相穿甲、所有动作与20搭配。

## 已核实参考文件

下面长度和SHA256由当前磁盘逐字节读取；PNG模式/尺寸由Pillow只读读取。角色源bbox均为非零alpha的半开区间，不是足底接触测量。生成只传A一张身份/姿势参考；其余用于审核与后续适配，避免把行走姿势混进待机。

| 用途 | 现存绝对路径 | 字节 / PNG | SHA256 |
| --- | --- | --- | --- |
| A：唯一生成参考，131待机相0 | [frame-0.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png) | 117257 / 512×512 RGBA | f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718 |
| 131来源溯源，非本次输入的四格原生页 | [idle.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/raw/idle.png) | 1544183 / 2172×724 RGB | 740a2d5fba74670cf3fa11389c62e968e2a91e81d3e078459df48ab32a4995b1 |
| 六相展开姿态参照，相0 | [frame-0.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-0.png) | 121979 / 512×512 RGBA | 90eb027ee05e289a08aefd613df908c81c450a1f6dd5c14d580ca6e089d415e5 |
| 六相收腿姿态参照，相1 | [frame-1.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-1.png) | 104942 / 512×512 RGBA | a13aaea3963abc6d4973805524be39710c8ef9395290c3e0d7d844ed7d37594e |
| 六相循环末相参照，相5 | [frame-5.png](F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-5.png) | 118064 / 512×512 RGBA | 18364d7b5ea06a1940c91cb204e1e59196194d69d972a123bcbaa956718d2566 |
| 已F/E留档小尺寸收腿上下文，不作生成输入 | [MovieFrame00050.png](F:/Ourgame/过程图稿与视频/2026-10-16_暗黑童话六相步态真实观察_v001/原件/MovieFrame00050.png) | 3693103 / 1280×720 RGBA | 7bf55a9f84c8fc295cd5b6dd01bc322e4e77712935d08f82e7509108a00e3698 |
| 同批次展开上下文，不作生成输入 | [MovieFrame00053.png](F:/Ourgame/过程图稿与视频/2026-10-16_暗黑童话六相步态真实观察_v001/原件/MovieFrame00053.png) | 3693103 / 1280×720 RGBA | facd75a4cc7ba70b56ab344b2416314e44247a027a0b074e2a1881e54811bdc0 |

A的alpha bbox是[146,48,367,464]，高416；walk相0/1/5分别[122,48,384,464]、[149,57,362,464]、[134,51,386,464]。v008六相各83ms，统一缩放而非逐帧自动贴框；已有root展示锚点[256,464]不能被称为已验收足锁。146只是一张静态待机，不沿用六相时间当作新动作。

## 146造型目标与分层约束

保持非纯人类的封闭钟盔身份、粗细略不均的墨线、每种材质两三块手绘明暗。甲片用偏暖的旧铁灰中亮块面，暗接缝/炭灰关节作分隔，少量锈棕连接件呼应手靴；仍带古怪旧器具味道，避免转成写实骑士、未来机甲或满身尖刺。root明确本次使用内置工具原生透明RGBA请求，不使用外部供应商或绿底作为本次输出要求；透明请求不等于已经检查alpha。

| 区域 | 72像素目标中的造型提示 | 必须留下的身份/活动信息 |
| --- | --- | --- |
| 胸 | 一片紧凑可读的胸片，大明暗面与明确边缘；轻量绑带作连接 | 盔下暗领、腰带、腰部弯曲区及一部分底衣可见；胸片不连成头盔的一整块，不用重甲横梁 |
| 肩 | 两个短肩盖，外轮廓比无甲有小而清楚的台阶；近远肩透视不同 | 不扩大头、手、骨长或全身显示比例；不做重甲方宽肩，不遮住眼窗或吞掉颈部 |
| 前臂 | 短护臂的亮面与暗内侧可辨，结束在手套前 | 弯肘露底衣，棕手套/独立手指仍清楚，护臂不等同整条金属胳膊，不把握持手烘进甲 |
| 胫 | 两片窄前胫护片，有清楚顶缘与近远腿区别 | 膝弯和棕靴保留，腿间原有负空间不被裙板填死；不为分腿改动姿势 |

以上是设计意图，不是已经测得的像素门。胸/肩/护臂/胫甲须靠各自大形和明暗区别；缩到72后若只能放大看纹理才辨认，候选应返修。合法收腿/前后腿重叠不能为了造间隙擅改骨架。少量外覆甲片可增加轮廓宽，不能偷偷增大整个主角来改善读图。

沿用[甲层合同](F:/Ourgame/docs/production/first-batch-v2/armor-layer-runtime-plan-v001.md)与[近袖扩展](F:/Ourgame/docs/production/first-batch-v2/armor-sleeves-runtime-plan-v002.md)：可见背层→common body_far→armor_front→独立武器→armor_near（确有近侧覆盖才有）→common body_near。远半身/远臂不被复制到近层；近手覆盖持柄，背面仅画真实可见部分。旧LGT/HVY near=null只描述旧资产，不能据此提前宣布新护臂无需near；若穿甲后近护臂压过武器，须真实独立near片及新绘序证据。没有可见背层可明确null，不能造透明空层骗完整度。

全部新组件须同512画布、同姿势root/grip、同时间、单一父级左右镜像；不逐片/逐帧bbox放大，不独立翻第二次。131新握点/near遮挡需重新按源标记，不能套旧512样例root[256,440]、旧125/126root[256,472]或旧武器多边形。盔甲不能常驻最前层绕过敌我groundY排序；遮挡反馈只依据实际已画alpha，不能用未画背片/隐藏敌当遮挡者，参见[遮挡合同](F:/Ourgame/docs/production/first-batch-v2/occlusion-readability-plan-v002.md)。本轮空手研究图不证明握剑遮挡已完成。

## 单次native146提示词

供root使用内置原生生成/编辑一次，以A作为唯一参考图，工具请求transparent_background=true。此原生路径按root明确指示覆盖外部chroma建议；不请求绿幕。输出保留原生尺寸/格式，不让提示词虚构工具已经严格输出512；原生返回只作rawreference，不是finalsprite。后续若进入生产，按sprite-gen检查真实alpha、提取组件、统一画布，另建候选。原件与展示副本先按项目保全规则F/E留档，再审图；新目录/版本不覆盖131、v008或旧四甲。146由root预留一次，本文不作为已存在生成回执；没有自动追加纠错或外部API调用。

> Create ONE assembled light-armor fit concept of the exact same grotesque dark-fairytale hero in the supplied reference. Use that sole reference for character identity, neutral standing pose, short proportions and right-facing three-quarter view. Preserve the closed bell-shaped helmet, crooked little top bolt, black visor with two amber eyes, charcoal underclothing, brown empty gloves and boots, and original limb lengths. Do not turn the character into a visible human.
>
> Add a compact chest panel, short modest shoulder caps, short forearm bracers and narrow shin guards in worn warm-grey metal. Use broad restrained warm highlights, quiet dark inner faces and a few brown leather fastenings. Make these four armor regions recognizable when the whole visible hero is only 72 pixels tall against a dark blue-grey dungeon floor. Preserve plenty of flexible charcoal clothing and dark collar, elbow, waist and knee gaps. Keep the brown gloves and boots fully recognizable. The far side follows the reference's perspective and partial occlusion; do not expose hidden anatomy or move the arms just to display every plate.
>
> Match the reference's hand-drawn cartoon finish: bold slightly uneven ink outlines and two or three broad painted tones per material. Keep the peculiar, improvised old-world character. Use large readable shapes rather than engraved detail. This is LIGHT armor: no thick full plate shell, door-bar chest beam, oversized square heavy shoulders or hanging metal skirt. Do not enlarge the head, body or character height.
>
> One centered full figure, head to both boot soles visible, generous safe margin, on a truly transparent background with clean alpha edges. No opaque backdrop, painted checkerboard or chroma screen. No photorealism, PBR, glossy 3D render, pixel-art grid, futuristic mech, heroic knight redesign, neon rim or white halo. No cape, skirt, horns, spikes, weapons, shield, exposed skin, extra limbs, scene, floor, cast shadow, UI, text, labels, alternate views or sheet panels. Do not place detached components beside the figure. This is an assembled reference only, not pixel-locked identity or independently separated production armor layers.

## 下一次真实UE暗地面检查

146若源图初审通过，先保全原生图、来源/版本、透明提取报告、原尺寸与统一画布/根测量；旧图不覆盖。用明确独立候选试装支路，记录它是固定穿戴外观研究而非真实换甲；实际导入是否发生、资源路径及Source/DLL绑定须有回执后才写成事实。

1. 与131无甲对照，同1280×720、同镜头/雾/灯光、UI关闭，保持已有可见身高上限72px及单一统一比例。不得按新甲bbox拉满画布而连带改变头/身体尺寸；真实甲片可以增加局部轮廓宽，需记录实际bbox/可见高度。
2. 比较现有亮斑及同场更暗的可走地面，左右各看胸片、肩台阶、护臂—手套、胫甲—靴与腰/肘/膝间隙。记录实际viewport、frame/path、位置、root、canvas、facing与原PNG；暗背景不能临时提亮来帮候选过门。当前固定亮斑锚点并不已有暗处证明，测试需新增真实位置观察。
3. 空手静态阶段仅判身份/轮廓/甲面读图；真实武器持握检查需等独立组件及131握点/near层齐备后再接。六相穿甲须逐姿态创作/分层，之后另做真实循环与转向录像审阅，不能把146平移六次充当步态。
4. 若头/眼/手靴身份漂移、胸肩连成难读的一团、暗处四处甲形消失、alpha杂边/裁边明显或必须放大角色才看清，则保留失败版本，先修本候选。不要靠光晕、常驻白描边、披风/武器/复杂背景掩盖问题，不扩到其余三甲。

## 风险与完成边界

生成器能参考身份但不能保证131像素不变、关节/根精确注册或真实分层。单张穿戴概念只覆盖一次方向试验；后续独立组件、六姿态、持握遮挡、所有状态与四甲20搭配仍有额外制作和审阅量，不能估算成已完成。原生146成功返回也不等于小尺寸或UE验收通过，计费/额度不在本文核实范围。

本计划交付可执行提示词、实存参考及下一次真实读图门。作者未生成146、未更换运行美术、未通过连续动作/脚锁/四甲完整性/听感，也未推进正式完整单元计数。root后续实际生成以其新回执为准，不能从本计划推断已执行。当前完整目标仍0/15；EV048用于细化怪诞方向，不倒签前批风格为最终接受。
