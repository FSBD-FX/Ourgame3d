# 首单元动作生成第一子批

2026-10-14，EV038。asset-gen 作为参考、动作、抠图与来源记录流程，生成后端依授权改用内置 `image_gen.imagegen`，未调用外部 API。Host 费用未知，不套用 CLI 供应商单价，也不宣称免费。

第一子批调用 **8 次**，包括全部纠错次数；无生成失败或重试。24 次总授权剩 **16 次**。每次调用前已把 requested、完整 prompt、参考路径写入 `generation-ledger.json`；完成后记录工具原件、项目副本、归档副本与 SHA256。原件留在 Codex generated_images，不移动、不覆盖。

2 张中立基准通过内部身份/比例审阅，冒险者为约 2.7–3 头身的固定 3/4 朝右镜头，原成年长身图只作衣服参考。内部锚点接受不等于用户正式画风批准。6 张独立 2×3 动作图集，共 **36 张真实 PNG 动作帧**，均为 512×512、RGBA8、真实 alpha，逐张读取。没有用静态参考或重复占位填帧。

| 动作 | 实际帧 | body_scale_cv | anchor_y_std | 对 idle 尺度偏差 | 状态 |
|---|---:|---:|---:|---:|---|
| hero idle | 6 | .00186 | .01687 | 基准 | 视觉候选 |
| hero walk | 6 | .02070 | .01758 | .01194 | 视觉候选，未实跑 |
| primary_1 body | 6 | .02206 | .01290 | .07007 | 空手身体候选，待剑组装 |
| primary_2 body | 6 | .01049 | .02150 | .01791 | 空手身体候选，待剑组装 |
| primary_3 body | 6 | .01609 | .01920 | .01425 | 空手身体候选，待剑组装 |
| stone wake | 6 | .01328 | .01786 | 无独立 idle profile | 视觉候选，第4帧眼灯回暗需审阅 |

现成 generate2dsprite processor 的严格门槛为 CV≤.08、anchor_y_std≤.05、profile drift≤.08。最终六组均无空帧、原始/输出触边、paste clamp；同组每帧 SHA 不同。冒险者 grounded 帧共用 `hero-scale-profile-matte-v002.json`，固定 preserve .84，未逐动作或逐帧缩放来隐藏漂移。raw 的实际人物高度没有严格服从 prompt 的 66%，统一处理后 idle/walk/前两段约 354–355px，高约69%；第三段有真实俯身，均值约340px。脚点由实际 processor 接触估计得到 **[256,472]**，不是假填 prompt 的 [256,440]；脚底轮廓本身略低于此接触估计。

首次本地处理 .96 导致输出贴边/clamp，完整保留在 `processed/hero-idle-qc-attempt01`。随后选定全局 .84 profile。默认抠色有洋红残边，现成处理器 `--threshold 180 --edge-threshold 260` 改善后的 canonical 目录为 hero 五组 `*-matte-v002`，stone 为 `stone-wake`；旧处理副本保留。每帧仍有0–11个 alpha≥128 的洋红相似边像素（最大占不透明像素约0.02%），没有宣称零残边。Profile 格式未储存抠色阈值，后续命令必须显式带两项阈值。

`generated-subset-manifest.json` 是这第一子批的真实像素/来源快照，明确 `visual_subset_not_runtime_accepted`，不是正式 content-atlas 通过声明。三段绝对 phase/frame 区间仅是按 combo-spec 的绑定计划，GIF 均匀帧延时仅预览用途，图像不定义判定窗口。没有制作虚假 grip/emit 坐标。

衣服烘在 hero body，石像盾/剑烘在全身图；没有 body_far/armor/weapon/body_near 分层，也没有可换甲承诺。空手攻击可读作拳法，必须完成独立军剑、可测握点、手前后遮挡和实际播放后，才可判断军剑动作成立。现有 atlas schema 不支持合法完全隐藏层，本批没有填假透明层或复制整身图绕过它。36 帧仅6动作，不等于完整22动作首单元。

全部展示材料先保存到 `F:/Ourgame/过程图稿与视频/2026-10-14_首单元动作生产_v001/原件` 与 `展示副本`，索引 `index.json`。只运行图像生成、现成处理器与 PIL 只读像素核验；未启动 UE/Blender，未导入或宣称游戏运行通过。第二子批将依 root 新指令继续同一24次总授权，追加 ledger，不覆盖本快照。
